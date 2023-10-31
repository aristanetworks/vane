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

""" Testcases to validate filesystem."""

import pytest
from pyeapi.eapilib import EapiError
from vane import tests_tools, test_case_logger
from vane.config import dut_objs, test_defs


TEST_SUITE = __file__
LOG_FILE = {"parameters": {"show_log": "show_output.log"}}

dut_parameters = tests_tools.parametrize_duts(TEST_SUITE, test_defs, dut_objs)
test1_duts = dut_parameters["test_if_files_on_"]["duts"]
test1_ids = dut_parameters["test_if_files_on_"]["ids"]

logging = test_case_logger.setup_logger(__file__)


@pytest.mark.demo
@pytest.mark.nrfu
@pytest.mark.base_feature
@pytest.mark.filesystem
@pytest.mark.virtual
@pytest.mark.physical
class FileSystemTests:
    """EOS File System Test Suite"""

    @pytest.mark.parametrize("dut", test1_duts, ids=test1_ids)
    def test_if_files_on_(self, dut, tests_definitions):
        """TD: Verify filesystem is correct and expected files are present

        Args:
          dut (dict): Encapsulates dut details including name, connection
          tests_definitions (dict): Test parameters
        """

        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)

        files = tops.test_parameters["files"]

        for file_name in files:
            try:
                """
                TS: Run show command 'show file information' on dut
                """

                show_cmd = f"show file information {file_name}"
                self.output = tops.run_show_cmds([show_cmd])
                assert self.output, "File information not collected."
                logging.info(
                    f"On device {tops.dut_name} output of {show_cmd} command is: {self.output}"
                )

                tops.actual_output = self.output[0]["result"]["isDir"]

            except (
                AssertionError,
                AttributeError,
                LookupError,
                EapiError,
            ) as exception:
                logging.error(
                    f"Error occurred during the testsuite execution on dut: {tops.dut_name}"
                    f" is {str(exception)}"
                )
                tops.actual_output = str(exception)

            if tops.actual_output == tops.expected_output:
                tops.output_msg += (
                    f"\nOn router {tops.dut_name}: {file_name} file isDir "
                    f"state is {tops.actual_output} which is the correct state.\n"
                )

            else:
                tops.output_msg += (
                    f"\nOn router {tops.dut_name}: {file_name} file isDir the"
                    f"actual state is {tops.actual_output}, while the expected state is "
                    f"{tops.expected_output}.\n"
                )

            tops.actual_results.append(tops.actual_output)
            tops.expected_results.append(tops.expected_output)

        tops.actual_output, tops.expected_output = (
            tops.actual_results,
            tops.expected_results,
        )

        tops.parse_test_steps(self.test_if_files_on_)
        tops.test_result = tops.actual_output == tops.expected_output
        tops.generate_report(tops.dut_name, self.output)
        assert tops.actual_output == tops.expected_output
