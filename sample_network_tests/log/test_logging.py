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

""" Tests to validate logging system message entries."""

import pytest
from pyeapi.eapilib import EapiError
from vane import tests_tools
from vane.vane_logging import logging
from vane.config import dut_objs, test_defs


TEST_SUITE = __file__
LOG_FILE = {"parameters": {"show_log": "show_output.log"}}

dut_parameters = tests_tools.parametrize_duts(TEST_SUITE, test_defs, dut_objs)
test_duts = dut_parameters["test_if_log_messages_appear_on_"]["duts"]
test_ids = dut_parameters["test_if_log_messages_appear_on_"]["ids"]


@pytest.mark.demo
@pytest.mark.nrfu
@pytest.mark.base_feature
@pytest.mark.platform_status
@pytest.mark.logging
@pytest.mark.virtual
@pytest.mark.physical
class LoggingTests:
    """Logging Test Suite"""

    @pytest.mark.parametrize("dut", test_duts, ids=test_ids)
    def test_if_log_messages_appear_on_(self, dut, tests_definitions):
        """TD: Verify local log messages entries

        Args:
          dut (dict): Encapsulates dut details including name, connection
          tests_definitions (dict): Test parameters
        """

        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)

        sys_msgs = tops.test_parameters["sys_msgs"]

        for sys_msg in sys_msgs:
            try:
                """
                TS: Collecting the output of 'show logging' command from DUT
                """
                logging.info(
                    f"On device {tops.dut_name} output of {tops.show_cmd} command is: "
                    f"{tops.show_cmd_txt}"
                )

                """
                TS: Verifying if DUT's system logs have messages
                """
                if sys_msg in tops.show_cmd_txt:
                    actual_output = True
                    tops.output_msg += (
                        f"{tops.dut_name} system logs contains message: {sys_msg}. "
                    )
                else:
                    actual_output = False
                    tops.output_msg += (
                        f"{tops.dut_name} system logs does NOT contains message: "
                        f"{sys_msg}. "
                    )

                tops.actual_results.append({sys_msg: actual_output})
                tops.expected_results.append({sys_msg: tops.expected_output})

            except (AttributeError, LookupError, EapiError) as exp:
                actual_output = str(exp)
                logging.error(
                    f"On device {tops.dut_name}: Error while running testcase on DUT is: {str(exp)}"
                )
                tops.output_msg += (
                    f" EXCEPTION encountered on device {tops.dut_name}, while "
                    f"investigating logging: {sys_msg}. Vane recorded error: {exp} "
                )

        tops.actual_output, tops.expected_output = (
            tops.actual_results,
            tops.expected_results,
        )

        """
        TS: Creating test report based on results
        """
        tops.parse_test_steps(self.test_if_log_messages_appear_on_)
        tops.test_result = tops.actual_output == tops.expected_output
        tops.generate_report(tops.dut_name, tops.show_cmd_txt)
        assert tops.actual_output == tops.expected_output
