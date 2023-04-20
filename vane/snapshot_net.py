#!/usr/bin/env python3
#
# Copyright (c) 2019, Arista Networks EOS+
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
# * Neither the name of the Arista nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

""" Utility script for taking a snapshot of the operational data within a network and converting
    it into Ansible-AVD structured data.  Ansible-AVD structured data is then written to 
    config.yml file for use with Vane test cases        
"""

import argparse
import sys
import jinja2
import yaml
from vane import tests_tools
from jsonpath_ng import jsonpath, parse
import vane.config
from pathlib import Path
from jinja2 import FileSystemLoader
from jinja2.sandbox import SandboxedEnvironment
from pprint import pprint


def parse_cli():
    """Parse cli options.

    Returns:
        args (obj): An object containing the CLI arguments.
    """
    parser = argparse.ArgumentParser(
        description="Utility snapshots network data for use with " "Vane test cases"
    )

    parser.add_argument(
        "--definitions-file",
        default=vane.config.DEFINITIONS_FILE,
        help="Specify the name of the definitions file",
    )

    parser.add_argument(
        "--duts-file",
        default=vane.config.DUTS_FILE,
        help="Specify the name of the duts file",
    )

    return parser.parse_args()


def setup_snapshots():
    """Use definitions file to discover sections of config to snapshot

    Returns:
        dict: Snapshot data structure of EOS commands
    """

    print(" - Setting up network snapshot")

    # Load input data files
    vane.config.test_defs = tests_tools.yaml_read(vane.config.DEFINITIONS_FILE)
    vane.config.test_duts = tests_tools.yaml_read(vane.config.DUTS_FILE)
    # TODO: Get rid of hard coding
    snap_data = tests_tools.yaml_read("snapshot.yml")

    snapshot = snap_data.get("snapshots")

    if not snapshot:
        print("No data to snapshot exiting...")
        sys.exit(1)

    return snap_data


def take_snapshots(snap_data):
    """Connect to each DUT, run snapshot commands, aggregate snapshot data

    Args:
        snap_data (snap_data): Snapshot data structure of EOS commands

    Returns:
        list: List of show commands used in snapshot
    """

    print(" - Taking network snapshot")

    show_cmds = []

    for snap_stanza in snap_data:
        if snap_stanza in snap_data["snapshots"]:
            jsonpath_expr = parse(f"{snap_stanza}[*].eos")
            show_cmds += [match.value for match in jsonpath_expr.find(snap_data)]

    # TODO: Move functionality from tests_client to tests_tools
    render_eapi_cfg()
    vane.config.dut_objs = tests_tools.init_duts(
        show_cmds, vane.config.test_defs, vane.config.test_duts
    )


# TODO: Make generic function but need to change eapi template
def render_eapi_cfg():
    """Render .eapi.conf file so pytests can log into devices"""

    eapi_template = vane.config.test_defs["parameters"]["eapi_template"]
    eapi_file = vane.config.test_defs["parameters"]["eapi_file"]
    duts = vane.config.test_duts["duts"]

    try:
        with open(eapi_template, "r", encoding="utf-8") as jinja_file:
            jinja_template = jinja_file.read()
            resource_file = (
                jinja2.Environment(autoescape=True).from_string(jinja_template).render(duts=duts)
            )
    except IOError as err_data:
        print(f"eAPI template ({eapi_template}) not found: {err_data}, exiting...")
        sys.exit(1)

    # TODO: create generic text write in tests_tools
    try:
        with open(eapi_file, "w", encoding="utf-8") as fname:
            fname.write(resource_file)
    except OSError as err:
        print(f"Unable to write file ({eapi_file}): {err}, exiting...")
        sys.exit(1)


def process_snapshots(snap_data):
    """Convert snapshot data to AVD structured data

    Args:
        show_cmds (list): List of show commands used in snapshot

    Returns:
        dict: AVD structured data
    """

    print(" - Processing network snapshot")

    snap_mappings = []

    # find snapshot mappings in snapshot.yml
    for snap_stanza in snap_data:
        if snap_stanza in snap_data["snapshots"]:
            snap_mappings = snap_mappings + snap_data[snap_stanza]

    snapshot = {}

    # create avd structured data for each DUT
    for dut in vane.config.dut_objs:
        name = dut.get("name")

        if name:
            snapshot[name] = {}

            # process snapshot mappings for each show command
            for snap_mapping in snap_mappings:
                map_show_cmd(snapshot[name], name, snap_mapping)

    return snapshot


def map_show_cmd(snapshot, name, snap_mapping):
    # get show output for dut
    output = get_show_cmd(snap_mapping["eos"], name)

    # process each snapshot mapping for show command
    for mapping in snap_mapping["mappings"]:
        ptr_dict = snapshot
        var_flag = False

        # build avd structured data for dut
        for avd_key in mapping["avd"].split("."):
            # create dictionary key, value entries
            if avd_key != "var" and not var_flag:
                # Initialize key, value entries
                ptr_dict.setdefault(avd_key, {})
                ptr_dict = ptr_dict[avd_key]

            # Map parameter to key, value entry
            elif var_flag:
                # find unique key, values in eos command
                mapping_parts = mapping["eos"].split(".'var'.")
                jsonpath_expr = parse(mapping_parts[0])
                eos_vars = [match.value for match in jsonpath_expr.find(output)]

                # iterate thru unique key, values in eos command
                for var in eos_vars[0]:
                    # substitue unique key into jpath expression
                    jexpr = mapping["eos"].replace("var", var)
                    jsonpath_expr = parse(jexpr)
                    # find unique value in eos command
                    ops_state = [match.value for match in jsonpath_expr.find(output)]

                    # set unique value in avd structured data
                    ptr_dict.setdefault(var, {})
                    ptr_dict[var][avd_key] = ops_state[0]

            # skip processing
            else:
                var_flag = True


def get_show_cmd(show_cmd, name):
    """Parse DUT Object for show command

    Args:
        show_cmd (str): Operational command used for snapshot
        name (str): DUT Name

    Returns:
        dict: Show command output
    """
    for dut in vane.config.dut_objs:
        if dut["name"] == name:
            return dut["output"][show_cmd]["json"]


def output_snapshots(snapshot):
    """Output AVD structured data to file

    Args:
        snapshot (dict): AVD structured data
    """

    print(" - Outputting network snapshot")

    # TODO: Hard coded value
    # TODO: Create test tools module to do this
    with open("configs.yml", "w") as outfile:
        yaml.dump(snapshot, outfile, default_flow_style=False)


def main():
    """main function"""

    print("Start Network Snapshot ... ")

    args = parse_cli()

    if args.definitions_file:
        vane.config.DEFINITIONS_FILE = args.definitions_file

    if args.duts_file:
        vane.config.DUTS_FILE = args.duts_file

    snap_data = setup_snapshots()
    take_snapshots(snap_data)
    snapshot = process_snapshots(snap_data)
    output_snapshots(snapshot)

    print("Network Snapshot Complete")


if __name__ == "__main__":
    main()
