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

""" A weather vane is an instrument used for showing the direction of the wind.
Just like a weather vane, Vane is a network certification tool that shows a
network's readiness for production based on validation tests. """

import argparse
from io import StringIO
from contextlib import redirect_stdout
from datetime import datetime
import shutil
import os
import yaml
import pytest
from vane import tests_client
from vane import report_client
from vane import tests_tools
from vane import test_step_client
import vane.config
from vane.vane_logging import logging
from vane import nrfu_client


logging.info("Starting vane.log file")

# global color variables
YELLOW = "\x1b[33m"
GREEN = "\x1b[32m"
DEFAULT = "\x1b[0m"


def parse_cli():
    """Parse cli options.

    Returns:
        args (obj): An object containing the CLI arguments.
    """
    parser = argparse.ArgumentParser(description="Network Certification Tool")

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

    parser.add_argument(
        "--environment",
        default=vane.config.ENVIRONMENT,
        help="Specify the test execution environment",
    )

    parser.add_argument(
        "--generate-duts-file",
        help="Create a duts file from topology and inventory file",
        nargs=2,
        metavar=("topology_file", "inventory_file"),
    )

    parser.add_argument(
        "--generate-duts-from-topo",
        help="Generate a duts file from an ACT topology file.",
        nargs=1,
        metavar=("topology_file"),
    )

    parser.add_argument(
        "--generate-test-steps",
        help=(
            "Generate test steps for all the tests in"
            " the test directory mentioned in the definitions file"
        ),
        nargs=1,
        metavar=("test_dir"),
    )

    parser.add_argument(
        "--markers",
        help=("List of supported technology tests. Equivalent to pytest --markers"),
        action="store_true",
    )

    parser.add_argument(
        "--nrfu",
        help=("Starts NRFU tests and will prompt users for required input."),
        action="store_true",
    )

    args = parser.parse_args()

    return args


def setup_vane():
    """Do tasks to setup test suite"""
    logging.info("Starting Test Suite setup")

    vane.config.test_duts = tests_tools.import_yaml(vane.config.DUTS_FILE)
    vane.config.test_parameters = tests_tools.import_yaml(vane.config.DEFINITIONS_FILE)

    logging.info("Discovering show commands from definitions")

    vane.config.test_defs = tests_tools.return_test_defs(vane.config.test_parameters)

    show_cmds = tests_tools.return_show_cmds(vane.config.test_defs)

    print(f"{YELLOW}\nRunning Show Commands on Initialized Duts\n{DEFAULT}")
    vane.config.dut_objs = tests_tools.init_duts(
        show_cmds, vane.config.test_parameters, vane.config.test_duts
    )

    logging.debug(f"Return to test suites: \nduts: {vane.config.dut_objs}")


def run_tests(definitions_file, duts_file):
    """Make request to test client to run tests

    Args:
        definitions_file (str): Path and name of definition file
        duts_file (str): Path and name of duts file
    """
    logging.info("Using class TestsClient to create vane_tests_client object")

    vane_tests_client = tests_client.TestsClient(definitions_file, duts_file)
    vane_tests_client.generate_test_definitions()
    vane_tests_client.setup_test_runner()
    setup_vane()
    vane_tests_client.test_runner()


def write_results(definitions_file):
    """Write results document

    Args:
        definitions_file (str): Path and name of definition file
    """
    logging.info("Using class ReportClient to create vane_report_client object")

    vane_report_client = report_client.ReportClient(definitions_file)
    vane_report_client.write_result_doc()


def write_test_steps(test_dir):
    """Writes the test steps for the given test directory tests

    Args: test_dir (str): Path and name of test directory"""

    vane_test_step_client = test_step_client.TestStepClient(test_dir)
    vane_test_step_client.write_test_steps()


def show_markers():
    """Returns the list of supported markers.

    Returns:
        marker_list (list): supported markers list.
    """
    inbuilt_list = [
        ")",
        "'",
        "trylast",
        "forked",
        "no_cover",
        "filterwarnings(warning)",
        "skip(reason=None)",
        "skipif(condition, ",
        "xfail(condition, ",
        "parametrize(argnames, argvalues)",
        "usefixtures(fixturename1, fixturename2, ",
        "tryfirst",
    ]

    temp_stdout = StringIO()

    with redirect_stdout(temp_stdout):
        _ = pytest.main(["--markers"])

    stdout_str = temp_stdout.getvalue()
    marker_list = []

    for i in stdout_str.split("\n"):
        if "pytest" in i:
            marker_name = i.split(": ")[0].split(".")[2]
            marker_description = i.split(": ")[1]

            if marker_name not in inbuilt_list:
                marker_list.append({"marker": marker_name, "description": marker_description})

    return marker_list


def create_duts_from_topo(topology_file):
    """
    Util function responsible for reading in topology file,
    calling on test tools to create duts file from the data
    gathered from the topo file.

    Args:
        topology_file (str): Path and name of topology file
    """
    # Open the topology file in read only
    try:
        with open(topology_file, "r", encoding="utf-8") as file:
            topology = yaml.safe_load(file)
    except FileNotFoundError:
        print("No valid topology file provided.")
        return

    # Output data to duts file
    if topology["nodes"]:
        username = topology["veos"]["username"]
        password = topology["veos"]["password"]
        topo_name = topology_file.split(".yml")[0]
        output_file = topo_name + "_duts.yaml"

        with open(output_file, "w", encoding="utf-8") as file:
            file.write("duts: \n")
            for node in topology["nodes"]:
                tests_tools.generate_duts_file(node, file, username, password)


def download_test_results():
    """
    function responsible for creating a zip of the
    TEST RESULTS folder and storing it in TEST RESULTS ARCHIVE folder.
    """
    logging.info("Downloading a zip file of the TEST RESULTS folder")

    now = datetime.now()
    dt_string = now.strftime("%d-%m-%Y %H:%M:%S")

    source = "reports/TEST RESULTS"
    destination = "reports/TEST RESULTS ARCHIVES/" + dt_string
    if os.path.exists(source):
        shutil.make_archive(destination, "zip", source)


def main():
    """main function"""
    logging.info("Reading in input from command-line")

    args = parse_cli()

    print(f"{GREEN}\nStarting Vane{DEFAULT}\n")

    if args.markers:
        print(f"{show_markers()}")

    elif args.generate_test_steps:
        logging.info(
            f"Generating test steps for test cases within {args.generate_test_steps} "
            f"test directory\n"
        )
        write_test_steps(args.generate_test_steps)

    else:
        if args.nrfu:
            logging.info("Invoking the Nrfu client to run Nrfu tests")
            nrfu = nrfu_client.NrfuClient()
            vane.config.DEFINITIONS_FILE = nrfu.definitions_file
            vane.config.DUTS_FILE = nrfu.duts_file

        else:
            if args.definitions_file:
                logging.warning(f"Changing Definitions file name to {args.definitions_file}")
                vane.config.DEFINITIONS_FILE = args.definitions_file

            if args.duts_file:
                logging.warning(f"Changing DUTS file name to {args.duts_file}")
                vane.config.DUTS_FILE = args.duts_file

            if args.generate_duts_file:
                logging.info(
                    f"Generating DUTS File from topology: {args.generate_duts_file[0]} and "
                    f"inventory: {args.generate_duts_file[1]} file.\n"
                )
                vane.config.DUTS_FILE = tests_tools.create_duts_file(
                    args.generate_duts_file[0], args.generate_duts_file[1]
                )

            if args.environment:
                vane.config.ENVIRONMENT = args.environment

            if args.generate_duts_from_topo:
                logging.info(
                    f"Generating DUTS File from topology: {args.generate_duts_from_topo[0]} file.\n"
                )
                create_duts_from_topo(args.generate_duts_from_topo[0])

        run_tests(vane.config.DEFINITIONS_FILE, vane.config.DUTS_FILE)

        print(f"{YELLOW}\nGenerating Reports from the Test Run\n{DEFAULT}")
        write_results(vane.config.DEFINITIONS_FILE)
        download_test_results()

        print(f"{GREEN}\nVANE has completed without errors\n{DEFAULT}")
        logging.info("\n\n!VANE has completed without errors!\n\n")


if __name__ == "__main__":
    main()
