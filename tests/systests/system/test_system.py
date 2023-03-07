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
import logging
import pytest
from vane import tests_tools


TEST_SUITE = __file__


@pytest.mark.demo
@pytest.mark.nrfu
@pytest.mark.base_feature
@pytest.mark.system
@pytest.mark.virtual
@pytest.mark.physical
@pytest.mark.eos424
class CrashTests:
    """Crash Test Suite"""

    def test_if_there_is_agents_have_crashed_on_(self, dut, tests_definitions):
        """Verifies the agents logs crash is empty

        Args:
          dut (dict): Encapsulates dut details including name, connection
        """

        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)
        tops.return_show_cmd("show agent logs crash")
        lines = tops.show_cmd_txt.split("\n")
        tops.actual_output = len(lines) - 1

        tops.test_result = tops.actual_output <= tops.expected_output

        tops.output_msg = (
            f"\nOn router |{tops.dut_name}| has "
            f"|{tops.actual_output}| agent crashes"
            " correct number of agent crashes is "
            f"|{tops.expected_output}|.\n"
        )

        tops.post_testcase()

        assert tops.actual_output <= tops.expected_output


@pytest.mark.demo
@pytest.mark.nrfu
@pytest.mark.platform_status
@pytest.mark.system
@pytest.mark.virtual
@pytest.mark.physical
@pytest.mark.eos424
class SystemTests:
    """System Test Suite"""

    def test_if_eos_version_is_correct_on_(self, dut, tests_definitions):
        """Verifies EOS version running on the device

        Args:
            dut (dict): Encapsulates dut details including name, connection
            tests_definitions (dict): Test parameters
        """

        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)

        tops.actual_output = dut["output"][tops.show_cmd]["json"]["version"]
        tops.test_result = tops.actual_output == tops.expected_output

        tops.output_msg = (
            f"On router |{tops.dut_name}| EOS version is "
            f"|{tops.actual_output}%|, version should be "
            f"|{tops.expected_output}%|"
        )

        tops.post_testcase()

        assert tops.actual_output == tops.expected_output
