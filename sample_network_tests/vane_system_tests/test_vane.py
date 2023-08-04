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

""" Tests to validate vane functionality."""

import pprint
import pytest
from pyeapi.eapilib import EapiError
from vane import tests_tools
from vane.vane_logging import logging


TEST_SUITE = __file__
LOG_FILE = {"parameters": {"show_log": "show_output.log"}}


@pytest.mark.vane_system_tests
class VaneTests:
    """Vane Test Suite"""

    def test_if_remove_comments_work(self, dut, tests_definitions):
        """TD: Verifies if setup comments work

        Args:
          dut (dict): Encapsulates dut details including name, connection
        """

        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)

        try:
            """
            TS: Run cmds 'show hostname' again
            """
            self.output = tops.run_show_cmds(tops.show_cmd)

            tops.actual_output = self.output[0]["result"]["hostname"]

        except (AttributeError, LookupError, EapiError) as exception:
            logging.error(
                f"On device {tops.dut_name}: Error while running testcase on DUT is: "
                f"{str(exception)}"
            )
            tops.actual_output = str(exception)
            tops.output_msg += (
                f"EXCEPTION encountered on device {tops.dut_name}, while "
                f"investigating if setup commnets can be specified. "
                f"Vane recorded error: {exception}"
            )

        """
        TS: Compare latest o/p with expected output
        """
        tops.parse_test_steps(self.test_if_remove_comments_work)
        tops.test_result = tops.actual_output == tops.expected_output
        tops.generate_report(tops.dut_name, tops.output_msg)
        assert tops.actual_output == tops.expected_output

    def test_if_ssh_json_cmds_run(self, dut, tests_definitions):
        """TD: Verifies cmds run using ssh and output is same as eapi

        Args:
          dut (dict): Encapsulates dut details including name, connection
        """

        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)

        try:
            tops.show_cmds[tops.dut_name] = ["show ntp status", "show bgp summary"]

            """
            TS: Run cmds using eapi and ssh using json encoding
            """
            eapi_output = tops.run_show_cmds(tops.show_cmds[tops.dut_name], conn_type="eapi")
            ssh_output = tops.run_show_cmds(tops.show_cmds[tops.dut_name], conn_type="ssh")

            """
            TS: Compare eapi and ssh outputs
            """
            tops.actual_output, tops.expected_output = (
                ssh_output,
                eapi_output,
            )

        except (AttributeError, LookupError, EapiError) as exception:
            logging.error(
                f"On device {tops.dut_name}: Error while running testcase on DUT is: "
                f"{str(exception)}"
            )
            tops.actual_output = str(exception)
            tops.output_msg += (
                f"EXCEPTION encountered on device {tops.dut_name}, while "
                f"investigating if ssh can be used to run cmds. Vane recorded error: {exception}"
            )

        tops.parse_test_steps(self.test_if_ssh_json_cmds_run)
        tops.test_result = tops.actual_output == tops.expected_output
        tops.generate_report(tops.dut_name, tops.output_msg)
        assert tops.actual_output == tops.expected_output

    def test_if_ssh_text_cmds_run(self, dut, tests_definitions):
        """TD: Verifies cmds run using ssh and output is same as eapi

        Args:
          dut (dict): Encapsulates dut details including name, connection
        """

        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)

        try:
            tops.show_cmds[tops.dut_name] = ["show ntp status", "show bgp summary"]

            """
            TS: Run cmds using eapi and ssh using text encoding
            """
            eapi_output = tops.run_show_cmds(
                tops.show_cmds[tops.dut_name], conn_type="eapi", encoding="text"
            )
            ssh_output = tops.run_show_cmds(
                tops.show_cmds[tops.dut_name], conn_type="ssh", encoding="text"
            )

            """
            TS: Compare eapi and ssh outputs
            """
            tops.actual_output, tops.expected_output = (
                pprint.pprint(ssh_output),
                pprint.pprint(eapi_output),
            )

        except (AttributeError, LookupError, EapiError) as exception:
            logging.error(
                f"On device {tops.dut_name}: Error while running testcase on DUT is: "
                f"{str(exception)}"
            )
            tops.actual_output = str(exception)
            tops.output_msg += (
                f"EXCEPTION encountered on device {tops.dut_name}, while "
                f"investigating if ssh can be used to run cmds. Vane recorded error: {exception}"
            )

        tops.parse_test_steps(self.test_if_ssh_text_cmds_run)
        tops.test_result = tops.actual_output == tops.expected_output
        tops.generate_report(tops.dut_name, tops.output_msg)
        assert tops.actual_output == tops.expected_output

    def test_if_ssh_can_run_show_tech_support(self, dut, tests_definitions):
        """TD: Verifies cmds run using ssh and output is same as eapi

        Args:
          dut (dict): Encapsulates dut details including name, connection
        """

        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)

        try:
            """
            TS: Run 'show tech-support' using ssh conn and text encoding
            """
            tops.show_cmds[tops.dut_name] = ["show tech-support"]

            tops.actual_output = tops.run_show_cmds(
                tops.show_cmds[tops.dut_name], conn_type="ssh", encoding="text"
            )

        except (AttributeError, LookupError, EapiError) as exception:
            logging.error(
                f"On device {tops.dut_name}: Error while running testcase on DUT is: "
                f"{str(exception)}"
            )
            tops.actual_output = str(exception)
            tops.output_msg += (
                f"EXCEPTION encountered on device {tops.dut_name}, while "
                f"investigating if ssh can be used to run cmds. Vane recorded error: {exception}"
            )

        """
        TS: Verify 'show tech-support' output should be non-empty
        """
        tops.parse_test_steps(self.test_if_ssh_can_run_show_tech_support)
        tops.test_result = tops.actual_output != ""
        tops.generate_report(tops.dut_name, tops.output_msg)
        assert tops.actual_output != ""

    def test_if_ssh_can_run_ping_cmd(self, dut, tests_definitions):
        """TD: Verifies cmds run using ssh and output is same as eapi

        Args:
          dut (dict): Encapsulates dut details including name, connection
        """

        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)

        try:
            """
            TS: Run 'ping x.x.x.x' using ssh conn and text encoding
            """
            cmd = f"ping {tops.test_parameters['input']['ping_ip']}"
            tops.show_cmds[tops.dut_name] = [cmd]

            tops.actual_output = tops.run_show_cmds(tops.show_cmds[tops.dut_name], conn_type="ssh")

        except (AttributeError, LookupError, EapiError) as exception:
            logging.error(
                f"On device {tops.dut_name}: Error while running testcase on DUT is: "
                f"{str(exception)}"
            )
            tops.actual_output = str(exception)
            tops.output_msg += (
                f"EXCEPTION encountered on device {tops.dut_name}, while "
                f"investigating if ssh can be used to run cmds. Vane recorded error: {exception}"
            )

        """
        TS: Verify ping output should be non-empty
        """
        tops.parse_test_steps(self.test_if_ssh_can_run_ping_cmd)
        tops.test_result = tops.actual_output != ""
        tops.generate_report(tops.dut_name, tops.output_msg)
        assert tops.actual_output != ""

    def test_if_ssh_run_commands_func(self, dut, tests_definitions):
        """TD: Verifies ssh connection run_commands() func

        Args:
          dut (dict): Encapsulates dut details including name, connection
        """

        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)

        try:
            tops.show_cmds[tops.dut_name] = ["show ntp status", "show bgp summary"]

            """
            TS: Run cmds using eapi and ssh run_commands
            """
            run_commands_op = dut["ssh_conn"].run_commands(tops.show_cmds[tops.dut_name])
            eapi_output = tops.run_show_cmds(tops.show_cmds[tops.dut_name], conn_type="eapi")
            eapi_op = []
            for output in eapi_output:
                eapi_op.append(output["result"])

            """
            TS: Compare eapi and ssh outputs
            """
            tops.actual_output, tops.expected_output = (run_commands_op, eapi_op)

        except (AttributeError, LookupError, EapiError) as exception:
            logging.error(
                f"On device {tops.dut_name}: Error while running testcase on DUT is: "
                f"{str(exception)}"
            )
            tops.actual_output = str(exception)
            tops.output_msg += (
                f"EXCEPTION encountered on device {tops.dut_name}, while "
                f"investigating if ssh can be used to run cmds. Vane recorded error: {exception}"
            )

        tops.parse_test_steps(self.test_if_ssh_run_commands_func)
        tops.test_result = tops.actual_output == tops.expected_output
        tops.generate_report(tops.dut_name, tops.output_msg)
        assert tops.actual_output == tops.expected_output

    def test_if_setup_fail_is_handled(self):
        """TD: Verifies if invalid cmd in setup is handled properly"""

        """ This function is never called since the setup fails"""
