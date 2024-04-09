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
from importlib import metadata
import shutil
import os
import pytest
from vane import tests_client
from vane import report_client
from vane import tests_tools
from vane import test_step_client
import vane.config
from vane.vane_logging import logging
from vane import nrfu_client


logging.info("Starting vane.log file")


def parse_cli():
    """Parse cli options.

    Returns:
        args (obj): An object containing the CLI arguments.
    """
    parser = argparse.ArgumentParser(description="Network Certification Tool")
    main_command_group = parser.add_argument_group("Main Command Options")

    main_command_group.add_argument(
        "--version",
        "--v",  # Alias for version
        help=("Current Version of Vane"),
        action="store_true",
    )

    main_command_group.add_argument(
        "--definitions-file",
        default=vane.config.DEFINITIONS_FILE,
        help="Specify the name of the definitions file",
    )

    main_command_group.add_argument(
        "--duts-file",
        default=vane.config.DUTS_FILE,
        help="Specify the name of the duts file",
    )

    main_command_group.add_argument(
        "--generate-duts-file",
        help="Create a duts file from topology and inventory file",
        nargs=3,
        metavar=("topology_file", "inventory_file", "duts_file"),
    )

    main_command_group.add_argument(
        "--generate-test-steps",
        help=(
            "Generate test steps for all the tests in"
            " the test directory mentioned in the definitions file"
        ),
        nargs=1,
        metavar=("test_dir"),
    )

    main_command_group.add_argument(
        "--markers",
        help=("List of supported technology tests. Equivalent to pytest --markers"),
        action="store_true",
    )

    # Define a subcommand "nrfu" with its argument group
    nrfu_sub_parser = parser.add_subparsers(
        dest="subcommand", help="`vane nrfu --help` for more options"
    )
    nrfu_parser = nrfu_sub_parser.add_parser(
        "nrfu", help="Executes NRFU testing with default options"
    )
    nrfu_command_group = nrfu_parser.add_argument_group("NRFU Command Options")

    # Define optional arguments for "nrfu"
    nrfu_command_group.add_argument(
        "--hardware-appendix",
        help="Enables the hardware appendix and prints it to report. Default value is False.",
        action="store_true",
    )
    nrfu_command_group.add_argument(
        "--software-appendix",
        help="Enables the software appendix and prints it to report. Default value is False.",
        action="store_true",
    )
    nrfu_command_group.add_argument(
        "--topology-appendix",
        help="Enables the topology appendix and prints it to report. Default value is False.",
        action="store_true",
    )
    nrfu_command_group.add_argument(
        "--configuration-appendix",
        help="Enables the configuration appendix and prints it to report. Default value is False.",
        action="store_true",
    )
    nrfu_command_group.add_argument(
        "--detailed-test-section",
        help="Enables the detailed test case result sections. Default value is True",
        action="store_true",
    )
    nrfu_command_group.add_argument(
        "--only-detailed-test-fails",
        help="Only publish detailed test case failures in the results section."
        "Default value is False",
        action="store_true",
    )
    nrfu_command_group.add_argument(
        "–-no-html-report",
        help="Disables HTML report and prints to reports directory.",
        action="store_true",
    )
    nrfu_command_group.add_argument(
        "--no-excel-report",
        help="Disables Excel report and prints to reports directory. ",
        action="store_true",
    )
    nrfu_command_group.add_argument(
        "--no-doc-report",
        help="Disables Word Doc report and prints to reports directory.",
        action="store_true",
    )
    nrfu_command_group.add_argument(
        "--no-stdout-report",
        help="Disables standard output reporting.",
        action="store_true",
    )
    nrfu_command_group.add_argument(
        "--no-md-report",
        help="Disables MarkDown report and prints to reports directory.",
        action="store_true",
    )

    # Parse the command-line arguments
    args = parser.parse_args()

    # The parsed arguments can be accessed like this:
    # if args.subcommand == "nrfu":
    #     print(f"nrfu software_reporting: {args.software_reporting}")
    #     print(f"nrfu hardware_reporting: {args.hardware_reporting}")

    return args


def setup_vane():
    """Do tasks to setup test suite"""
    logging.info("Starting Test Suite setup")

    vane.config.test_duts = tests_tools.import_yaml(vane.config.DUTS_FILE)
    vane.config.test_parameters = tests_tools.import_yaml(vane.config.DEFINITIONS_FILE)

    logging.info("Discovering show commands from definitions")

    vane.config.test_defs = tests_tools.return_test_defs(vane.config.test_parameters)
    show_cmds = tests_tools.return_show_cmds(vane.config.test_defs)
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

    if args.markers:
        print(f"{show_markers()}")

    elif args.generate_duts_file:
        logging.info(
            f"Generating DUTS File from topology: {args.generate_duts_file[0]} and "
            f"inventory: {args.generate_duts_file[1]} file.\n"
        )
        tests_tools.create_duts_file(
            args.generate_duts_file[0], args.generate_duts_file[1], args.generate_duts_file[2]
        )

    elif args.generate_test_steps:
        logging.info(
            f"Generating test steps for test cases within {args.generate_test_steps} "
            f"test directory\n"
        )
        write_test_steps(args.generate_test_steps)

    elif args.version:
        print(f"Vane Framework Version: {metadata.version(__package__)}")

    else:
        if args.subcommand == "nrfu":
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

        run_tests(vane.config.DEFINITIONS_FILE, vane.config.DUTS_FILE)
        write_results(vane.config.DEFINITIONS_FILE)
        download_test_results()

        logging.info("\n\n!VANE has completed without errors!\n\n")


if __name__ == "__main__":
    main()
