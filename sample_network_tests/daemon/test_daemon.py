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

""" Tests to validate daemon status."""

import pytest
from pyeapi.eapilib import EapiError
from vane import tests_tools
from vane.vane_logging import logging
from vane.config import dut_objs, test_defs


TEST_SUITE = __file__
LOG_FILE = {"parameters": {"show_log": "show_output.log"}}

dut_parameters = tests_tools.parametrize_duts(TEST_SUITE, test_defs, dut_objs)
test1_duts = dut_parameters["test_if_daemons_are_running_on_"]["duts"]
test1_ids = dut_parameters["test_if_daemons_are_running_on_"]["ids"]

test2_duts = dut_parameters["test_if_daemons_are_enabled_on_"]["duts"]
test2_ids = dut_parameters["test_if_daemons_are_enabled_on_"]["ids"]


@pytest.mark.demo
@pytest.mark.nrfu
@pytest.mark.base_feature
@pytest.mark.daemons
@pytest.mark.virtual
@pytest.mark.physical
class DaemonTests:
    """EOS Daemon Test Suite"""

    @pytest.mark.parametrize("dut", test1_duts, ids=test1_ids)
    def test_if_daemons_are_running_on_(self, dut, tests_definitions):
        """TD: Verify a list of daemons are running on DUT

        Args:
          dut (dict): Encapsulates dut details including name, connection
          tests_definitions (dict): Test parameters
        """

        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)

        daemons = tops.test_parameters["daemons"]

        for daemon in daemons:
            try:
                """
                TS: Collecting the output of 'show daemon' command from DUT
                """
                self.output = dut["output"][tops.show_cmd]["json"]
                assert (
                    (self.output.get("daemons")).get(daemon).get("running")
                ), "Show daemon details are not found"
                logging.info(
                    f"On device {tops.dut_name} output of {tops.show_cmd} command is: {self.output}"
                )

                actual_output = self.output["daemons"][daemon]["running"]

            except (AttributeError, LookupError, EapiError) as exp:
                actual_output = str(exp)
                logging.error(
                    f"On device {tops.dut_name}: Error while running testcase on DUT is: {str(exp)}"
                )
                tops.output_msg += (
                    f" EXCEPTION encountered on device {tops.dut_name}, while "
                    f"investigating daemon: {daemon}. Vane recorded error: {exp} "
                )

            """
            TS: Verify daemons are running on DUT
            """
            if actual_output == tops.expected_output["daemon_running"]:
                tops.output_msg += (
                    f"{tops.dut_name}'s {daemon} daemon has expected running "
                    f"state: {actual_output}. "
                )
            else:
                tops.output_msg += (
                    f"{tops.dut_name}'s {daemon} daemon has unexpected running state: "
                    f"{actual_output} and should be in running state: "
                    f"{tops.expected_output['daemon_running']}. "
                )

            tops.actual_results.append(actual_output)
            tops.expected_results.append(tops.expected_output["daemon_running"])

        tops.actual_output, tops.expected_output = (
            tops.actual_results,
            tops.expected_results,
        )

        """
        TS: Creating test report based on results
        """
        tops.parse_test_steps(self.test_if_daemons_are_running_on_)
        tops.test_result = tops.actual_output == tops.expected_output
        tops.generate_report(tops.dut_name, self.output)
        assert tops.actual_output == tops.expected_output

    @pytest.mark.parametrize("dut", test2_duts, ids=test2_ids)
    def test_if_daemons_are_enabled_on_(self, dut, tests_definitions):
        """TD: Verify a list of daemons are enabled on DUT

        Args:
          dut (dict): Encapsulates dut details including name, connection
          tests_definitions (dict): Test parameters
        """

        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)

        daemons = tops.test_parameters["daemons"]

        for daemon in daemons:
            try:
                """
                TS: Collecting the output of 'show daemon' command from DUT
                """
                self.output = dut["output"][tops.show_cmd]["json"]
                assert (
                    (self.output.get("daemons")).get(daemon).get("enabled")
                ), "Show daemon details are not found"
                logging.info(
                    f"On device {tops.dut_name} output of {tops.show_cmd} command is: {self.output}"
                )

                actual_output = self.output["daemons"][daemon]["enabled"]

            except (AttributeError, LookupError, EapiError) as exp:
                actual_output = str(exp)
                logging.error(
                    "On device %s: Error while running testcase on DUT is: %s",
                    tops.dut_name,
                    str(exp),
                )
                tops.output_msg += (
                    f" EXCEPTION encountered on device {tops.dut_name}, while "
                    f"investigating daemon: {daemon}. Vane recorded error: {exp} "
                )

            """
            TS: Verify daemons are enabled on DUT
            """
            if actual_output == tops.expected_output["daemon_enabled"]:
                tops.output_msg += (
                    f"{tops.dut_name}'s {daemon} daemon has expected enabled "
                    f"state: {actual_output}. "
                )
            else:
                tops.output_msg += (
                    f"{tops.dut_name}'s {daemon} daemon has unexpected enabled state: "
                    f"{actual_output} and should be in enabled state: "
                    f"{tops.expected_output['daemon_enabled']}. "
                )

            tops.actual_results.append(actual_output)
            tops.expected_results.append(tops.expected_output["daemon_enabled"])

        """
        TS: Creating test report based on results
        """
        tops.parse_test_steps(self.test_if_daemons_are_enabled_on_)
        tops.generate_report(tops.dut_name, self.output, "results")
        assert tops.actual_output == tops.expected_output
