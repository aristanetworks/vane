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

"""Utilities for using PyTest in network testing"""

import os
import json
import re
import logging
from pathlib import Path
import datetime
from mdutils.mdutils import MdUtils

logging.basicConfig(
    level=logging.INFO,
    filename="vane.log",
    filemode="w",
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


class TestStepClient:
    """Creates instance of Test Step Client."""

    def __init__(self, test_dir):
        """Initializes the Test Step Client

        Args:
            test_dir (str): directory of test cases for which to generate
            test steps
        """

        self._test_dirs = test_dir

    def write_test_steps(self):
        """starts the execution of writing test steps"""
        self.walk_dir()

    def walk_dir(self):
        """Walks through each directory"""
        for test_dir in self._test_dirs:
            test_files = []
            for root, _dirs, files in os.walk(test_dir, topdown=False):
                test_files.extend(
                    os.path.join(root, name)
                    for name in files
                    if name.startswith("test_")
                    and name.endswith(".py")
                    or name.endswith("_test.py")
                )
            self.parse_file(test_files)

    def parse_file(self, test_files):
        """Parses Files for Test Steps & Definitions

        Args:
            test_files (list): List of test file names collected directory walk
        """
        for test_file in test_files:
            comments = []
            with open(test_file, "r", encoding="utf_8") as infile:
                content = infile.read()
            # Pattern to match to extract TS/TD
            pattern = re.compile('(T[SD]:.*?)(?:"""|Args:)', re.DOTALL)
            # Find all matches to pattern
            comments = pattern.findall(content)
            # Format each item in list
            comments = [x.strip() for x in comments]
            if not comments:
                comments.append("N/a no Test Steps found")
            now = (datetime.datetime.now()).strftime("%d/%m/%Y %H:%M:%S")
            comments.insert(0, now)
            self.output_json({test_file: comments})
            self.output_md({test_file: comments})

    def output_json(self, test_comments):
        """Outputs Test steps & definitions to json file

        Args:
            test_comments (list): List of test steps or descriptions from test
        """
        for key in test_comments:
            # Creates file with original filename into json directory
            with open(f"{os.path.splitext(key)[0]}.json", "w+", encoding="utf_8") as outfile:
                json.dump({key: test_comments.get(key)}, outfile)

    def output_md(self, test_comments):
        """Output Test steps & definitions to MD File

        Args:
            test_comments (list): List of test steps or descriptions from test
        """
        for key in test_comments:
            steps = test_comments.get(key)
            md_file = MdUtils(file_name=f"{os.path.splitext(key)[0]}.md", title=Path(key).stem)
            md_file.new_line(f"Date generated: {steps[0]}")
            test_steps_list = []
            for step in steps:
                # Create Title for Test Definition
                if step.startswith("TD:") and test_steps_list:
                    # Add Test steps to Document where
                    # there are more than one TD
                    md_file.new_list(test_steps_list, marked_with="1")
                    test_steps_list = []
                    md_file.new_header(level=1, title=step.lstrip("TD:"))
                # Add Test steps to list to be added to file
                elif step.startswith("TS:"):
                    test_steps_list.append(step.lstrip("TS:"))
                # Add Test Steps to document when at end of items
                if step == steps[-1]:
                    md_file.new_list(test_steps_list, marked_with="1")
                    test_steps_list = []
                if step.startswith("N/a"):
                    md_file.new_line(step)
            md_file.create_md_file()
