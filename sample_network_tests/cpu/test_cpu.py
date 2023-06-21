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

""" Tests to validate CPU process utilization status."""

import pytest
from pyeapi.eapilib import EapiError
from vane.config import dut_objs, test_defs
from vane import tests_tools
from vane.vane_logging import logging


TEST_SUITE = __file__
LOG_FILE = {"parameters": {"show_log": "show_output.log"}}

dut_parameters = tests_tools.parametrize_duts(TEST_SUITE, test_defs, dut_objs)

test1_duts = dut_parameters["test_1_sec_cpu_utlization_on_"]["duts"]
test1_ids = dut_parameters["test_1_sec_cpu_utlization_on_"]["ids"]

test2_duts = dut_parameters["test_1_min_cpu_utlization_on_"]["duts"]
test2_ids = dut_parameters["test_1_min_cpu_utlization_on_"]["ids"]

test3_duts = dut_parameters["test_5_min_cpu_utlization_on_"]["duts"]
test3_ids = dut_parameters["test_5_min_cpu_utlization_on_"]["ids"]


@pytest.mark.demo
@pytest.mark.nrfu
@pytest.mark.platform_status
@pytest.mark.cpu
@pytest.mark.virtual
@pytest.mark.physical
class CPUTests:
    """CPU Test Suite"""

    @pytest.mark.parametrize("dut", test1_duts, ids=test1_ids)
    def test_1_sec_cpu_utlization_on_(self, dut, tests_definitions):
        """TD: Verify 1 second CPU % is under specificied value

        Args:
          dut (dict): Encapsulates dut details including name, connection
          tests_definitions (dict): Test parameters
        """

        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)

        try:
            """
            TS: Collecting the output of 'show processes' command from DUT
            """
            self.output = dut["output"][tops.show_cmd]["json"]
            assert (self.output.get("timeInfo")).get(
                "loadAvg"
            ), "Show process details are not found"
            logging.info(
                f"On device {tops.dut_name} output of {tops.show_cmd} command is: {self.output}"
            )

            tops.actual_output = self.output["timeInfo"]["loadAvg"][0]

            """
            TS: Comparing Switch's 1 second utilization to expected utilization
            """
            if tops.actual_output < tops.expected_output["cpu_utilization"]:
                tops.test_result = True
                tops.output_msg = (
                    f"{tops.dut_name} 1 sec CPU utilization is {tops.actual_output}% and "
                    f"under the acceptable utilization: {tops.expected_output['cpu_utilization']}%"
                )
            else:
                tops.test_result = False
                tops.output_msg = (
                    f"{tops.dut_name} 1 sec CPU utilization: {tops.actual_output}% and "
                    f"over the acceptable utilization: {tops.expected_output['cpu_utilization']}%"
                )

        except (AttributeError, LookupError, EapiError) as exp:
            tops.actual_output = str(exp)
            logging.error(
                f"On device {tops.dut_name}: Error while running testcase on DUT is: {str(exp)}"
            )

        """
        TS: Creating test report based on results
        """
        tops.parse_test_steps(self.test_1_sec_cpu_utlization_on_)
        tops.generate_report(tops.dut_name, self.output)
        assert tops.actual_output < tops.expected_output["cpu_utilization"]

    @pytest.mark.parametrize("dut", test2_duts, ids=test2_ids)
    def test_1_min_cpu_utlization_on_(self, dut, tests_definitions):
        """TD: Verify 1 minute CPU % is under specificied value

        Args:
          dut (dict): Encapsulates dut details including name, connection
          tests_definitions (dict): Test parameters
        """

        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)

        try:
            """
            TS: Collecting the output of 'show processes' command from DUT
            """
            self.output = dut["output"][tops.show_cmd]["json"]
            assert (self.output.get("timeInfo")).get(
                "loadAvg"
            ), "Show process details are not found"
            logging.info(
                f"On device {tops.dut_name} output of {tops.show_cmd} command is: {self.output}"
            )

            tops.actual_output = self.output["timeInfo"]["loadAvg"][1]

            """
            TS: Comparing Switch's 1 minute utilization to expected utilization
            """
            if tops.actual_output < tops.expected_output["cpu_utilization"]:
                tops.test_result = True
                tops.output_msg = (
                    f"{tops.dut_name} 1 minute CPU utilization is {tops.actual_output}% and "
                    f"under the acceptable utilization: {tops.expected_output['cpu_utilization']}%"
                )
            else:
                tops.test_result = False
                tops.output_msg = (
                    f"{tops.dut_name} 1 minute CPU utilization: {tops.actual_output}% and "
                    f"over the acceptable utilization: {tops.expected_output['cpu_utilization']}%"
                )

        except (AttributeError, LookupError, EapiError) as exp:
            tops.actual_output = str(exp)
            logging.error(
                f"On device {tops.dut_name}: Error while running testcase on DUT is: {str(exp)}"
            )

        """
        TS: Creating test report based on results
        """
        tops.parse_test_steps(self.test_1_min_cpu_utlization_on_)
        tops.generate_report(tops.dut_name, self.output)
        assert tops.actual_output < tops.expected_output["cpu_utilization"]

    @pytest.mark.parametrize("dut", test3_duts, ids=test3_ids)
    def test_5_min_cpu_utlization_on_(self, dut, tests_definitions):
        """TD: Verify 5 minute CPU % is under specificied value

        Args:
          dut (dict): Encapsulates dut details including name, connection
          tests_definitions (dict): Test parameters
        """

        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)

        try:
            """
            TS: Collecting the output of 'show processes' command from DUT
            """
            self.output = dut["output"][tops.show_cmd]["json"]
            assert (self.output.get("timeInfo")).get(
                "loadAvg"
            ), "Show process details are not found"
            logging.info(
                f"On device {tops.dut_name} output of {tops.show_cmd} command is: {self.output}"
            )

            tops.actual_output = self.output["timeInfo"]["loadAvg"][2]

            """
            TS: Comparing Switch's 5 minute utilization to expected utilization
            """
            if tops.actual_output < tops.expected_output["cpu_utilization"]:
                tops.test_result = True
                tops.output_msg = (
                    f"{tops.dut_name} 5 minute CPU utilization is {tops.actual_output}% and "
                    f"under the acceptable utilization: {tops.expected_output['cpu_utilization']}%"
                )
            else:
                tops.test_result = False
                tops.output_msg = (
                    f"{tops.dut_name} 5 minute CPU utilization: {tops.actual_output}% and "
                    f"over the acceptable utilization: {tops.expected_output['cpu_utilization']}%"
                )

        except (AttributeError, LookupError, EapiError) as exp:
            tops.actual_output = str(exp)
            logging.error(
                f"On device {tops.dut_name}: Error while running testcase on DUT is: {str(exp)}"
            )

        """
        TS: Creating test report based on results
        """
        tops.parse_test_steps(self.test_5_min_cpu_utlization_on_)
        tops.generate_report(tops.dut_name, self.output)
        assert tops.actual_output < tops.expected_output["cpu_utilization"]
