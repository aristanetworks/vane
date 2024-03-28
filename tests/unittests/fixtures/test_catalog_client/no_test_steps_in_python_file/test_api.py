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

""" Tests to validate base feature status."""

import pytest
from pyeapi.eapilib import EapiError
from vane.config import dut_objs, test_defs
from vane import tests_tools, test_case_logger

TEST_SUITE = "api_tests"
LOG_FILE = {"parameters": {"show_log": "show_output.log"}}

dut_parameters = tests_tools.parametrize_duts(TEST_SUITE, test_defs, dut_objs)
test1_duts = dut_parameters["test_if_management_https_api_server_is_running_on_"]["duts"]
test1_ids = dut_parameters["test_if_management_https_api_server_is_running_on_"]["ids"]


logging = test_case_logger.setup_logger(__file__)


@pytest.mark.physical
class APITests:
    """API Test Suite"""

    @pytest.mark.parametrize("dut", test1_duts, ids=test1_ids)
    def test_if_management_https_api_server_is_running_on_(self, dut, tests_definitions):
        """TD: Verify management api https server is running
        Args:
         dut (dict): Encapsulates dut details including name, connection
         tests_definitions (dict): Test parameters
        """

        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)

        try:
            self.output = dut["output"][tops.show_cmd]["json"]
            assert (self.output.get("httpsServer")).get(
                "running"
            ), "Show management api http-commands details are not found"
            logging.info(
                f"On device {tops.dut_name} output of {tops.show_cmd} command is: {self.output}"
            )

            tops.actual_output = {"https_server_running": self.output["httpsServer"]["running"]}

        except (AttributeError, LookupError, EapiError) as exp:
            tops.actual_output = str(exp)
            logging.error(
                f"On device {tops.dut_name}: Error while running testcase on DUT is: {str(exp)}"
            )
            tops.output_msg += (
                f" EXCEPTION encountered on device {tops.dut_name}, while "
                f"investigating HTTP Server. Vane recorded error: {exp} "
            )

        if tops.actual_output == tops.expected_output:
            tops.test_result = True
            tops.output_msg = (
                f"On router {tops.dut_name} HTTPS Server is correctly in running state: "
                f"{tops.actual_output['https_server_running']}"
            )
        else:
            tops.test_result = False
            tops.output_msg = (
                f"On router {tops.dut_name} HTTPS Server is incorrectly in running state: "
                f"{tops.actual_output['https_server_running']}, should be in state "
                f"{tops.expected_output['https_server_running']}"
            )

        tops.parse_test_steps(self.test_if_management_https_api_server_is_running_on_)
        tops.generate_report(tops.dut_name, self.output)
        assert tops.actual_output == tops.expected_output
