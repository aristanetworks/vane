#!/usr/bin/env python3
#
# Copyright (c) 2022, Arista Networks EOS+
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

"""
Python script to obtain device inventory information from
CVP and generate a DUTS file for Vane

reqs: cvprac, pyeapi, yaml, urllib3

Run: python3 gen_duts_from_cvp.py
"""

import argparse
import sys
import yaml
import pyeapi
from cvprac.cvp_client import CvpClient
from cvprac.cvp_client_errors import (
    CvpApiError,
    CvpLoginError,
    CvpRequestError,
    CvpSessionLogOutError,
)
import urllib3
from requests.exceptions import HTTPError, ReadTimeout, Timeout, TooManyRedirects


def create_duts_file_from_cvp(cvp_ip, cvp_username, cvp_password, duts_file_name):
    """
    create_duts_file_from_cvp function:
        (1) Function to retrieve the inventory from cvp.
        (2) Also retrieves all the neighbors for each device by running lldp cmd on
        devices.
        (3) All this info is dumped in file 'duts_file_name'.
    Args:
        cvp_ip: ip address for CVP
        cvp_username: username for CVP
        cvp_password: password for CVP
        duts_file_name: name of the duts file to be written
    """

    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    try:
        clnt = CvpClient()
        clnt.connect([cvp_ip], cvp_username, cvp_password)
        print(f"Pull the inventory from CVP: {cvp_ip}")
        inventory = clnt.api.get_inventory()
    except (
        CvpLoginError,
        CvpApiError,
        CvpSessionLogOutError,
        CvpRequestError,
        HTTPError,
        ReadTimeout,
        Timeout,
        TooManyRedirects,
        TypeError,
        ValueError,
    ) as err:
        msg = f"Could not get CVP inventory info: {err}"
        sys.exit(msg)

    dut_file = {}
    dut_properties = []
    for dev in inventory:
        if dev["ztpMode"]:
            continue
        dut_properties.append(
            {
                "mgmt_ip": dev["ipAddress"],
                "name": dev["hostname"],
                "password": cvp_password,
                "transport": "https",
                "username": cvp_username,
                "role": "unknown",
                "neighbors": [],
            }
        )

    if dut_properties:
        dut_file.update({"duts": dut_properties})

    lldp_cmd = "show lldp neighbors | json"
    show_cmds = [lldp_cmd]
    workers = len(dut_properties)
    print(f"Run 'show lldp neighbors' on {workers} duts")
    for dut in dut_properties:
        dut_worker(dut, show_cmds)

    neighbors_matrix = {}
    for dut in dut_properties:
        neighbors = dut["output"][lldp_cmd]["result"][0]["lldpNeighbors"]
        for neighbor in neighbors:
            del neighbor["ttl"]
            fqdn = neighbor["neighborDevice"]
            neighbor["neighborDeivce"] = fqdn.split(".")[0]
        neighbors_matrix[dut["name"]] = neighbors

    for dut_property in dut_properties:
        dut_property["neighbors"] = neighbors_matrix[dut_property["name"]]
        del dut_property["output"]
        del dut_property["connection"]

    if dut_properties:
        dut_file.update({"duts": dut_properties})
        with open(duts_file_name, "w", encoding="utf-8") as yamlfile:
            yaml.dump(dut_file, yamlfile, sort_keys=False)
            print(f"Yaml file {duts_file_name} created")


def dut_worker(dut, show_cmds):
    """Execute 'show_cmds' on dut. Update dut structured data with show
    output.

    Args:
      dut(dict): structured data of a dut output data, hostname, and
      connection
    """

    eos = {
        "device_type": "arista_eos",
        "ip": dut["mgmt_ip"],
        "username": dut["username"],
        "password": dut["password"],
        "secret": dut["password"],
    }

    dut["output"] = {}

    dut["connection"] = pyeapi.connect(
        host=eos["ip"], username=eos["username"], password=eos["password"]
    )

    for show_cmd in show_cmds:
        output = dut["connection"].execute(show_cmd)
        dut["output"][show_cmd] = output


def main():
    """main function"""

    args = parse_cli()

    if args.generate_cvp_duts_file:
        create_duts_file_from_cvp(
            args.generate_cvp_duts_file[0],
            args.generate_cvp_duts_file[1],
            args.generate_cvp_duts_file[2],
            args.generate_cvp_duts_file[3],
        )


def parse_cli():
    """Parse CLI options.

    Returns:
      args (obj): An object containing the CLI arguments.
    """

    parser = argparse.ArgumentParser(
        description=(
            "Script to generate duts.yaml for vane from CVP and devices. Does not work for ACT env."
        )
    )

    parser.add_argument(
        "--generate-cvp-duts-file",
        help="Create a duts file from CVP inventory",
        nargs=4,
        metavar=("cvp_ip_address", "cvp_username", "cvp_password", "duts_file_name"),
    )
    args = parser.parse_args()

    return args


if __name__ == "__main__":
    main()
