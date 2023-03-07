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

""" Tests to validate base feature status."""

import inspect
import pytest
from vane import tests_tools


TEST_SUITE = __file__
LOG_FILE = {"parameters": {"show_log": "show_output.log"}}


@pytest.mark.demo
@pytest.mark.nrfu
@pytest.mark.base_feature
@pytest.mark.filesystem
@pytest.mark.virtual
@pytest.mark.physical
@pytest.mark.eos424
class FileSystemTests:
    """EOS File System Test Suite"""

    def test_if_files_on_(self, dut, tests_definitions):
        """Verify filesystem is correct and expected files are present

        Args:
          dut (dict): Encapsulates dut details including name, connection
          tests_definitions (dict): Test parameters
        """

        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)

        files = tops.test_parameters["files"]

        for file_name in files:
            show_cmd = f"show file information {file_name}"
            show_output, show_cmd_txt = tests_tools.return_show_cmd(
                show_cmd, dut, tops.test_case, LOG_FILE
            )
            if show_output:
                tops.actual_output = show_output[0]["isDir"]
            elif show_cmd_txt:
                tops.actual_output = json.loads(show_cmd_txt[0]["output"])["isDir"]

            tops.output_msg += (
                f"\nOn router |{tops.dut_name}|: {file_name} file isDir "
                f"state is |{tops.actual_output}|, correct state is "
                f"|{tops.expected_output}|.\n"
            )

            tops.test_result = tops.actual_output is tops.expected_output

            tops.actual_results.append(tops.actual_output)
            tops.expected_results.append(tops.expected_output)

        print(f"{tops.output_msg}\n{tops.comment}")

        tops.actual_output, tops.expected_output = (
            tops.actual_results,
            tops.expected_results,
        )
        tops.post_testcase()

        assert tops.actual_results == tops.expected_results
