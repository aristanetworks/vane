#!/usr/bin/env python3
#
# Copyright (c) 2023, Arista Networks EOS+
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

"""Utilities for NRFU testing"""
import getpass
import os
import sys
import readline
import urllib3
from prompt_toolkit import prompt
from prompt_toolkit.completion import PathCompleter
from cvprac.cvp_client import CvpClient
from cvprac.cvp_api import CvpApi
from vane.vane_logging import logging
from vane.tests_tools import export_yaml


class NrfuClient:
    """Creates an instance of the NRFU Client."""

    def __init__(self):
        """NrfuClient initialisation"""

        # initialise default values
        self.definitions_file = "nrfu_tests/definitions_nrfu.yaml"
        self.duts_file = "nrfu_tests/duts_nrfu.yaml"
        self.username = ""
        self.password = ""
        self._detailed_report = False  # generate only summary report by default

        logging.info("Starting the NRFU client")
        self.setup()

    def setup(self):
        """Starts the flow of nrfu client and makes the necessary calls"""

        # Disabling the unverified HTTPS requests warning
        urllib3.disable_warnings()

        # Configure readline to enable arrow key navigation
        readline.parse_and_bind("set editing-mode vi")  # Use 'vi' mode for navigation

        # Getting credentials from user
        self.get_credentials()

        # Determine if Vane is running as CVP application
        cvp = self.determine_if_cvp_application()

        # Depending on if it is CVP application or not,
        # get the device data to generate duts.yaml file
        if cvp:
            device_data, source = self.cvp_application()
        else:
            device_data, source = self.not_cvp_application()

        # Ask the level of report details
        self.ask_report_detail()

        # Generate duts_nrfu.yaml file from the duts data gathered above
        self.generate_duts_file(device_data, source)

        # Generate definitions_nrfu.yaml file from preset definitions data structure
        self.generate_definitions_file()

        # Run Vane with the generated duts and definitions file
        print("\x1b[32m\nStarting Execution of NRFU tests via Vane\x1b[0m")

    def ask_report_detail(self):
        """Ask user if summary or detailed report
        Puts the user's choice in self._report_detail_level
        """
        self._detailed_report = False  # default set to generate only summary report
        user_choice = input(
            "Do you want detailed report?(Anything other than y/yes defaults to 'no') [y/yes/n/no]:"
        )
        if user_choice and user_choice in ["y", "yes"]:
            self._detailed_report = True  # summary + detailed report
        elif user_choice not in ["n", "no"]:
            print("You did not input 'y/yes/n/no', defaulting to 'no'.")

    def get_credentials(self):
        """Ask user to enter credentials for EOS/CloudVision

        Returns:
        username (string): EOS/CloudVision username
        password (string): EOS/CloudVision password
        """

        self.username = input("Please input Arista device username: ")
        self.password = getpass.getpass("Please input Arista device password: ")

    def determine_if_cvp_application(self):
        """Determine if Vane is running as CVP application

        Returns:
        boolean: flag indicating if Vane is running as CVP application
        """

        logging.info("Determining if Vane is running as a CVP application")
        if os.environ.get("VANE_CVP"):
            logging.info("Vane is running as a CVP application")
            return True

        logging.info("Vane is not running as a CVP application")
        return False

    def cvp_application(self):
        """Steps to take if Vane is running as CVP application

        Returns:
        device_data (list(list)): Device data read from CVP
        source (string): flag indicating the source of device data
        """

        ip_address = "127.0.0.1"
        source = "cvp"
        logging.info("Using CVP to gather duts data")
        print("\x1b[32mUsing CVP to gather duts data\x1b[0m")
        device_data = self.get_duts_data(ip_address)
        return device_data, source

    def not_cvp_application(self):
        """Steps to take if Vane is not running as CVP application

        Returns:
        device_data (list(list) or list): Device data read from either CVP or device file
        source (string): flag indicating the source of device data
        """

        user_choice = ""
        device_data = []
        while user_choice not in ("y", "yes", "n", "no"):
            user_choice = input("Do you wish to use CVP for DUTs [y/yes/n/no]: ")
            user_choice = user_choice.lower()

        if user_choice in ("y", "yes"):
            source = "cvp"
            ip_address = input("Please input CVP IP address: ")
            device_data = self.get_duts_data(ip_address)

        else:
            source = "non-cvp"
            device_list_file = ""
            text_flag = False
            while not text_flag:
                device_list_file = prompt(
                    "Please input Name/Path of device list file (.txt)"
                    " (Use tab for autocompletion): ",
                    completer=PathCompleter(),
                )
                text_flag = self.is_valid_text_file(device_list_file)
            device_data = self.read_device_list_file(device_list_file)
        return device_data, source

    def get_duts_data(self, ip_address):
        """Gets inventory data from CVP

        Args:
        ip_address (string): CVP's ip address

        Returns:
        device_data (list(list)): Device data gathered from CVP
        """

        logging.info("Connecting to CVP to gather duts data")

        device_data = []
        client = CvpClient()
        client.connect([ip_address], self.username, self.password)
        cvp_api = CvpApi(client)

        # Get the inventory using get_inventory API call
        inventory = cvp_api.get_inventory()

        # Process inventory data as specified to generate duts.yaml
        for device in inventory:
            if device["streamingStatus"] == "active" and device["containerName"] != "Undefined":
                current_device_data = [device["hostname"], device["ipAddress"]]
                device_data.append(current_device_data)
        return device_data

    def read_device_list_file(self, device_list_file):
        """Read IP addresses per DUT

        Args:
        device_list_file (str): Name of the DUT ip file

        Returns:
        device_data (list): Device data in the form of list of DUT ips"""

        device_data = []
        try:
            with open(device_list_file, "r", encoding="utf-8") as text_in:
                logging.info("Reading in dut ip data from device list file")
                line = text_in.readline()
                while line:
                    # ensure no empty lines or lines starting with # are read
                    if line.strip() and not line.strip().startswith("#"):
                        device_data.append(line.strip())
                    line = text_in.readline()
        except OSError as err:
            logging.error(f"ERROR OPENING DEVICE LIST FILE: {err}")
            sys.exit(1)

        return device_data

    def generate_duts_file(self, device_data, source):
        """Processes the duts data to be written to the duts.yaml file

        Args:
        device_data (list): Device data provided by source
        source (string): flag indicating if source of data is cvp or not
        """

        logging.info("Generating duts file for nrfu testing")

        duts_yaml_data = []

        for device in device_data:
            # device data in this case is a list of [device hostnames, device ips]
            if source == "cvp":
                name = device[0]
                ip_address = device[1]
            # device data in this case is a list of device ips
            else:
                ip_address = name = device
            current_device_data = {
                "mgmt_ip": ip_address,
                "name": name,
                "neighbors": [],
                "password": self.password,
                "transport": "https",
                "username": self.username,
                "role": "unknown",
            }
            duts_yaml_data.append(current_device_data)
        final_duts_data = {"duts": duts_yaml_data}

        export_yaml(self.duts_file, final_duts_data)

    def generate_definitions_file(self):
        """Generate definitions_nrfu.yaml file from parameters needed
        for NRFU testing"""

        logging.info("Generating definitions file for nrfu testing")

        test_dir = "nrfu_tests"
        user_choice = ""

        while user_choice not in ("y", "yes", "n", "no"):
            user_choice = input("Do you want to specify a custom test case directory [y|n]:")
            user_choice = user_choice.lower()

        if user_choice in ("y", "yes"):
            test_dir = ""
            while not os.path.exists(test_dir) or not os.path.isdir(test_dir):
                test_dir = prompt(
                    "Please specify test case directory <path/to/test case dir>"
                    " (Use tab for autocompletion):",
                    completer=PathCompleter(),
                )

        definitions_data = {
            "parameters": {
                "html_report": "reports/report",
                "json_report": "reports/report",
                "generate_test_definitions": True,
                "generate_detailed_report": self._detailed_report,
                "master_definitions": "nrfu_tests/master_def.yaml",
                "mark": None,
                "processes": None,
                "report_dir": "reports",
                "results_file": "result.yml",
                "results_dir": "reports/results",
                "setup_show": False,
                "show_log": "show_output.log",
                "continue_when_unreachable": True,
                "stdout": False,
                "test_cases": "All",
                "test_dirs": [test_dir],
                "verbose": True,
                "template_definitions": "test_definition.yaml.j2",
                "test_definitions": "test_definition.yaml",
                "report_summary_style": "modern",
                "self_contained": True,
            }
        }

        export_yaml(self.definitions_file, definitions_data)

    def is_valid_text_file(self, file_path):
        """Utility function to check for validity of file input"""
        # Check if the file exists
        if not os.path.exists(file_path):
            return False

        # Check if the file is a regular file (not a directory)
        if not os.path.isfile(file_path):
            return False

        try:
            # Attempt to open and read the file as text
            with open(file_path, "r", encoding="utf-8") as file:
                file.read()
            return True
        except UnicodeDecodeError:
            # If the file is not a valid text file, UnicodeDecodeError will be raised
            return False
