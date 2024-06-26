#!/usr/bin/env python3
#
# Copyright (c) 2024, Arista Networks EOS+
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

""" Utilities for creating test catalog files. """

import os
import re
import sys
import yaml
from vane.vane_logging import logging
from vane.utils import get_timestamp_in_seconds, write_to_csv


# pylint: disable=broad-exception-caught
class TestCatalogClient:
    """
    Creates an instance of a test catalog client.
    """

    def __init__(self, test_dir, test_def_file):
        """
        Initializes the test catalog client
        Args:
            test_dir (list): Directory of test cases for which the test catalog needs to be
            generated.
        """
        logging.info("Creating the test catalog client object")
        logging.debug(f"Setting the test catalog client object directories to {test_dir}")
        self.test_dirs = test_dir
        self.test_def_file = test_def_file
        self.test_file_data = {}
        self.test_def_data = {}

    def write_test_catalog(self):
        """
        Starts writing of the test catalog.
        """
        logging.info("Started writing the test catalog file")
        self.walk_dir()

        # Collecting the header and data rows
        folder_name = "test_catalog"
        header_row = ["Test Suite", "Test Case ID", "Test Case", "Description", "Test Steps"]
        data_rows = self.get_data_rows(self.test_def_data)

        # No data will be written in the CSV file if data rows are empty.
        if not data_rows:
            print(f"\033[91mNo tests found in the directory {self.test_dirs}.\033[0m")
            sys.exit(0)

        # Inserting the header at first index
        data_rows.insert(0, header_row)

        # Collecting the current timestamp.
        file_timestamp = get_timestamp_in_seconds()

        # Creating test catalog directory
        folder_path = os.path.join(os.getcwd(), folder_name)
        os.makedirs(folder_path, exist_ok=True)

        # Forming the file path for the test catalog file.
        file_name = f"test_catalog_{file_timestamp}.csv"
        file_path = os.path.join(folder_path, file_name)

        write_to_csv(data_rows, file_path)
        logging.info("Finished writing the test catalog file")

    def walk_dir(self):
        """
        Walks through each of the directories
        """
        test_files = []
        for test_dir in self.test_dirs:
            logging.info(f"Walking directory {test_dir} for the test cases")
            for root, _dirs, files in os.walk(test_dir, topdown=False):
                # sort the files
                files.sort()
                test_files.extend(
                    os.path.join(root, name)
                    for name in files
                    if name.startswith("test_")
                    and name.endswith(".py")
                    or name.endswith("_test.py")
                    or name == self.test_def_file
                )

        logging.debug(f"Discovered test files: {test_files} for parsing")

        if not test_files:
            print(f"\033[91mNo test files found in directory {self.test_dirs}.\033[0m")
            sys.exit(0)

        self.parse_test_data(test_files)

    def parse_test_data(self, test_files):
        """
        Utility to collect the parsed test data from test definitions and Python files.
        Args:
            test_files (list): List of python and yaml files to collect the test data.
        """

        for test_file in test_files:
            logging.info(
                f"Opening {test_file} file to collect details required for the test catalog."
            )

            try:
                with open(test_file, "r", encoding="utf_8") as infile:
                    if ".py" in test_file:
                        content = infile.read()
                        self.parse_python_file(content, test_file)

                    elif ".yaml" in test_file:
                        yaml_data = yaml.safe_load(infile)
                        if not yaml_data:
                            raise ValueError(
                                "\033[91mTest case details are not found in the"
                                f" {test_file} file.\033[0m"
                            )

                        for test_data in yaml_data:
                            test_suite = test_data["name"].replace(".py", "")
                            test_cases = test_data["testcases"]
                            self.test_def_data[test_suite] = {}
                            for test_case in test_cases:
                                self.test_def_data[test_suite].update(
                                    {
                                        test_case["name"]: {
                                            "test_id": test_case.get("test_id", "No test ID found")
                                        }
                                    }
                                )
            except BaseException as base_exp:
                print(
                    "\033[91mError while collecting test case information from"
                    f" {test_file} file: {base_exp}\033[0m"
                )

        logging.info("Collected test data required for formation of the test catalog.")
        self.correlate_test_data()

    def parse_python_file(self, content, test_file):
        """
        Utility to parse Python files and collect the test suite, test case name,
        test description(TD), and test steps(TS) for each of the test cases
        within the Python file.
        Args:
            content (str): Collected Python file data in string format.
            test_file (str): Name of Python file.
        """
        # Pattern to collect test suite, test case name, TS and TD from python file.
        test_suite_regex = r"TEST_SUITE\s*=\s*(.*?)\n"
        test_case_regex = r"def\s+(test_\w+)\(.*?"
        test_step_regex = rf'{test_suite_regex}|{test_case_regex}|(T[SD]:.*?)(?:"""|Args:)'

        # Checking if the above patterns are collected from a Python file.
        pattern = re.compile(test_step_regex, re.DOTALL)
        comments = pattern.findall(content)

        # Iterating over the collected patterns and forming
        # the test case data dictionary.
        final_test_suite = test_file.split("/")[-1].replace(".py", "")
        final_test_case_name = ""

        for test_suite, test_case_name, test_description in comments:
            if test_suite:
                # Test suite pattern is __file__ in some cases and "abc" in some
                # cases hence handled both.
                if test_suite != "__file__":
                    final_test_suite = test_suite.replace('"', "")

            self.test_file_data.setdefault(final_test_suite, {})

            if test_case_name:
                final_test_case_name = test_case_name
                self.test_file_data[final_test_suite].update(
                    {
                        final_test_case_name: {
                            "test_steps": [],
                            "test_description": "Description is not found in the Python file.",
                        }
                    }
                )

            if test_description:
                # Removing the \n and multiple spaces from the description.
                test_description = re.sub(r"\n\s+", " ", test_description)
                test_description = test_description.strip()

                # Collecting the test description.
                if "TD: " in test_description:
                    test_description = test_description.replace("TD: ", "")

                    if not final_test_case_name:
                        final_test_case_name = final_test_suite
                        self.test_file_data[final_test_suite].update(
                            {
                                final_test_case_name: {
                                    "test_steps": [],
                                    "test_description": test_description,
                                }
                            }
                        )
                    else:
                        self.test_file_data[final_test_suite][final_test_case_name].update(
                            {"test_description": test_description}
                        )

                else:
                    # Collecting the test steps.
                    test_steps = test_description.replace("TS: ", "")
                    self.test_file_data[final_test_suite][final_test_case_name][
                        "test_steps"
                    ].append(test_steps)

    def correlate_test_data(self):
        """
        Utility to correlate the test data (data correlated between the test definitions
        and the Python file).
        """

        # Iterating over the data collected from the test definitions file.
        for test_suite, test_cases in self.test_def_data.items():
            test_file_info = self.test_file_data.get(test_suite, {})

            # Correlating the test case data.
            for test_case in test_cases:
                default_step_msg = ["Test steps are not collected from the Python file"]
                default_test_description = "Test description is not collected from the Python file"
                test_steps = test_file_info.get(test_case, {}).get("test_steps", default_step_msg)
                test_description = test_file_info.get(test_case, {}).get(
                    "test_description", default_test_description
                )
                test_cases[test_case].update(
                    {"test_steps": test_steps, "test_description": test_description}
                )

        logging.info("Completed data correlation between test definitions and Python file.")

    def get_data_rows(self, final_data):
        """
        Utility to collect the data rows from the correlated test definitions and Python file.
        Args:
           final_data (dict): Dictionary containing the test case details.

        Returns:
           data rows (list): List of data rows having test case details.
        """
        data_rows = []
        for test_suite, test_data in final_data.items():
            for test_name, test_details in test_data.items():
                test_steps = ""
                for step_number, step in enumerate(test_details["test_steps"], start=1):
                    test_steps += f"{step_number}. {step}\n"

                local_data = [
                    test_suite,
                    test_details["test_id"],
                    test_name,
                    test_details["test_description"],
                    test_steps,
                ]
                data_rows.append(local_data)

        return data_rows
