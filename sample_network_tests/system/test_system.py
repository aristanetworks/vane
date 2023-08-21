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

""" Testcases to validate agent log crashes and eos versions on devices."""

import pytest
from pyeapi.eapilib import EapiError
from vane import tests_tools
from vane.vane_logging import logging
from vane.config import dut_objs, test_defs

TEST_SUITE = __file__
LOG_FILE = {"parameters": {"show_log": "show_output.log"}}

dut_parameters = tests_tools.parametrize_duts(TEST_SUITE, test_defs, dut_objs)
test1_duts = dut_parameters["test_if_there_is_agents_have_crashed_on_"]["duts"]
test1_ids = dut_parameters["test_if_there_is_agents_have_crashed_on_"]["ids"]

test2_duts = dut_parameters["test_if_eos_version_is_correct_on_"]["duts"]
test2_ids = dut_parameters["test_if_eos_version_is_correct_on_"]["ids"]


@pytest.mark.demo
@pytest.mark.nrfu
@pytest.mark.base_feature
@pytest.mark.system
@pytest.mark.virtual
@pytest.mark.physical
class CrashTests:
    """Crash Test Suite"""

    @pytest.mark.parametrize("dut", test1_duts, ids=test1_ids)
    def test_if_there_is_agents_have_crashed_on_(self, dut, tests_definitions):
        """TD: Verifies the agents logs crash is empty

        Args:
          dut (dict): Encapsulates dut details including name, connection
        """

        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)
        try:
            """
            TS: Run show command `show agent logs crash` on dut
            """
            self.output = dut["output"][tops.show_cmd]
            assert self.output, "Agent logs crash are are not collected."
            logging.info(
                f"On device {tops.dut_name} output of {tops.show_cmd} command is: {self.output}"
            )

            show_cmd_txt = self.output["text"]
            lines = show_cmd_txt.split("\n")
            tops.actual_output = len(lines) - 1

        except (AssertionError, AttributeError, LookupError, EapiError) as exception:
            logging.error(
                f"Error occurred during the testsuite execution on dut: {tops.dut_name}"
                f" is {str(exception)}"
            )
            tops.actual_output = str(exception)

        if tops.actual_output <= tops.expected_output:
            tops.test_result = True
            tops.output_msg = (
                f"\nOn router {tops.dut_name} number of agent crashes is "
                f"{tops.actual_output} which is correct.\n"
            )
        else:
            tops.test_result = False
            tops.output_msg = (
                f"\nOn router {tops.dut_name} the actual number of agent crashes is "
                f"{tops.actual_output} while "
                "the expected number of agent crashes is "
                f"{tops.expected_output}.\n"
            )

        tops.parse_test_steps(self.test_if_there_is_agents_have_crashed_on_)
        tops.generate_report(tops.dut_name, self.output)
        assert tops.actual_output <= tops.expected_output


@pytest.mark.demo
@pytest.mark.nrfu
@pytest.mark.platform_status
@pytest.mark.system
@pytest.mark.virtual
@pytest.mark.physical
class SystemTests:
    """System Test Suite"""

    @pytest.mark.parametrize("dut", test2_duts, ids=test2_ids)
    def test_if_eos_version_is_correct_on_(self, dut, tests_definitions):
        """TD: Verifies EOS version running on the device

        Args:
            dut (dict): Encapsulates dut details including name, connection
            tests_definitions (dict): Test parameters
        """

        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)

        try:
            """
            TS: Run show command `show version` on dut
            """
            self.output = dut["output"][tops.show_cmd]["json"]
            assert self.output, "EOS Version details are not collected."
            logging.info(
                f"On device {tops.dut_name} output of {tops.show_cmd} command is: {self.output}"
            )

            tops.actual_output = self.output["version"]

        except (AssertionError, AttributeError, LookupError, EapiError) as exception:
            logging.error(
                f"Error occurred during the testsuite execution on dut: {tops.dut_name}"
                f" is {str(exception)}"
            )
            tops.actual_output = str(exception)

        if tops.actual_output == tops.expected_output:
            tops.test_result = True
            tops.output_msg = (
                f"On router {tops.dut_name} EOS version is "
                f"{tops.actual_output}% which is correct."
            )
        else:
            tops.test_result = False
            tops.output_msg = (
                f"On router {tops.dut_name} the actual EOS version is "
                f"{tops.actual_output}%, while the expected EOS version is "
                f"{tops.expected_output}%"
            )
        tops.parse_test_steps(self.test_if_eos_version_is_correct_on_)
        tops.generate_report(tops.dut_name, self.output)
        assert tops.actual_output == tops.expected_output
