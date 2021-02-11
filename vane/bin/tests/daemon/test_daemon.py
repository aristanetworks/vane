#!/usr/bin/python3
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
import tests_tools


TEST_SUITE = __file__
LOG_FILE = {"parameters": {"show_log": "show_output.log"}}

@pytest.mark.demo
@pytest.mark.nrfu
@pytest.mark.base_feature
@pytest.mark.daemons
class DaemonTests:
    """EOS Daemon Test Suite"""

    def test_if_daemons_are_running_on_(self, dut, tests_definitions):
        """Verify a list of daemons are running on DUT

        Args:
          dut (dict): Encapsulates dut details including name, connection
          tests_definitions (dict): Test parameters
        """

        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)
        daemons = tops.test_parameters["daemons"]

        for daemon in daemons:
            dut_ptr = dut["output"][tops.show_cmd]["json"]["daemons"]
            tops.actual_output = dut_ptr[daemon]["running"]
            tops.test_result = tops.actual_output == tops.expected_output

            tops.output_msg += (
                f"\nOn router |{tops.dut_name}|, daemon running "
                f"state is |{tops.actual_output}| correct"
                f" state is |{tops.expected_output}|.\n"
            )
            tops.comment += (
                f"TEST is {daemon} daemon running on "
                f"|{tops.dut_name}|.\n"
                f"GIVEN expected {daemon} running state: "
                f"|{tops.expected_output}|.\n"
                f"WHEN {daemon} device running state is "
                f"|{tops.actual_output}|.\n"
                f"THEN test case result is |{tops.test_result}|.\n"
            )

            tops.actual_results.append(tops.actual_output)
            tops.expected_results.append(tops.expected_output)

        tops.comment += (
            f"OUTPUT of |{tops.show_cmd}| is :\n\n{tops.show_cmd_txt}.\n"
        )
        print(f"{tops.output_msg}\n{tops.comment}")

        tops.actual_output, tops.expected_output = (
            tops.actual_results,
            tops.expected_results,
        )
        tops.post_testcase()

        assert tops.actual_results == tops.expected_results

    def test_if_daemons_are_enabled_on_(self, dut, tests_definitions):
        """Verify a list of daemons are enabled on DUT

        Args:
          dut (dict): Encapsulates dut details including name, connection
          tests_definitions (dict): Test parameters
        """

        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)
        daemons = tops.test_parameters["daemons"]

        for daemon in daemons:
            dut_ptr = dut["output"][tops.show_cmd]["json"]["daemons"]
            tops.actual_output = dut_ptr[daemon]["enabled"]
            tops.test_result = tops.actual_output == tops.expected_output

            tops.output_msg += (
                f"\nOn router |{tops.dut_name}|, daemon enabled "
                f"state is |{tops.actual_output}| correct"
                f" state is |{tops.expected_output}|.\n"
            )
            tops.comment += (
                f"TEST is {daemon} daemon enabled on "
                f"|{tops.dut_name}|.\n"
                f"GIVEN expected {daemon} enabled state: "
                f"|{tops.expected_output}|.\n"
                f"WHEN {daemon} device enabled state is "
                f"|{tops.actual_output}|.\n"
                f"THEN test case result is |{tops.test_result}|.\n"
            )

            tops.actual_results.append(tops.actual_output)
            tops.expected_results.append(tops.expected_output)

        tops.comment += (
            f"OUTPUT of |{tops.show_cmd}| is :\n\n{tops.show_cmd_txt}.\n"
        )
        print(f"{tops.output_msg}\n{tops.comment}")

        tops.actual_output, tops.expected_output = (
            tops.actual_results,
            tops.expected_results,
        )
        tops.post_testcase()

        assert tops.actual_results == tops.expected_results
