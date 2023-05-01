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

""" Tests to validate TACACS functionality."""

import pytest
from pyeapi.eapilib import EapiError
from vane import tests_tools
from vane.vane_logging import logging
from vane.config import dut_objs, test_defs


TEST_SUITE = __file__
LOG_FILE = {"parameters": {"show_log": "show_output.log"}}

dut_parameters = tests_tools.parametrize_duts(TEST_SUITE, test_defs, dut_objs)
test1_duts = dut_parameters["test_if_tacacs_is_sending_messages_on_"]["duts"]
test1_ids = dut_parameters["test_if_tacacs_is_sending_messages_on_"]["ids"]

test2_duts = dut_parameters["test_if_tacacs_is_receiving_messages_on_"]["duts"]
test2_ids = dut_parameters["test_if_tacacs_is_receiving_messages_on_"]["ids"]


@pytest.mark.nrfu
@pytest.mark.base_feature
@pytest.mark.tacacs
class TacacsTests:
    """AAA TACACS Test Suite"""

    @pytest.mark.parametrize("dut", test1_duts, ids=test1_ids)
    def test_if_tacacs_is_sending_messages_on_(self, dut, tests_definitions):
        """TD:  Verify tacacs messages are sending correctly

        Args:
          dut (dict): Encapsulates dut details including name, connection
          tests_definitions (dict): Test parameters
        """

        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)

        tacacs_servers = tests_tools.verify_tacacs(dut)

        if tacacs_servers:
            try:
                """
                TS: Run show command `show tacacs` on dut
                """
                self.output = dut["output"][tops.show_cmd]["json"]
                assert self.output, "TACACS details are not collected."
                logging.info(
                    f"On device {tops.dut_name} output of {tops.show_cmd} command is: {self.output}"
                )

                eos_messages_sent_1 = self.output["tacacsServers"][0]["messagesSent"]

                """
                TS: Run `show tacacs` on dut again in order to see if messagesSent increments
                """
                self.output = tops.run_show_cmds(tops.show_cmd, "text")[0]["result"]
                assert self.output, "TACACS details are not collected."
                logging.info(
                    f"On device {tops.dut_name} output of {tops.show_cmd} command is: {self.output}"
                )

                eos_messages_sent_2 = self.output["tacacsServers"][0]["messagesSent"]

                if eos_messages_sent_1 < eos_messages_sent_2:
                    tops.test_result = True
                    tops.output_msg = (
                        f"\nOn router {tops.dut_name} TACACS messages2 sent: "
                        f"{eos_messages_sent_2} increments from TACACS "
                        f"messages1 sent: {tops.actual_output}"
                    )
                else:
                    tops.test_result = False
                    tops.output_msg = (
                        f"\nOn router {tops.dut_name} TACACS messages2 sent: "
                        f"{eos_messages_sent_2} doesn't increments from "
                        f"TACACS messages1 sent: {eos_messages_sent_1}"
                    )
                assert eos_messages_sent_1 < eos_messages_sent_2

            except (
                AssertionError,
                AttributeError,
                LookupError,
                EapiError,
            ) as exception:
                logging.error(
                    f"""Error occurred during the testsuite execution on dut: {tops.dut_name}
                     is {str(exception)}"""
                )
        else:
            """
            TS: TACACS servers are not configured on the dut hence terminating the test
            """
            tops.actual_output = "N/A"
            tops.expected_output = "N/A"
            tops.test_result = True
            self.output = (
                f"\nOn router {tops.dut_name} does not have TACACS servers configured"
            )
            tops.comment = (
                f"\nRouter {tops.dut_name} does not have TACACS servers configured"
            )
            tops.output_msg = (
                f"\nOn router {tops.dut_name} does not have TACACS servers configured"
            )

        tops.parse_test_steps(self.test_if_tacacs_is_sending_messages_on_)
        tops.generate_report(tops.dut_name, self.output)

    @pytest.mark.parametrize("dut", test2_duts, ids=test2_ids)
    def test_if_tacacs_is_receiving_messages_on_(self, dut, tests_definitions):
        """TD: Verify tacacs messages are received correctly

        Args:
          dut (dict): Encapsulates dut details including name, connection
          tests_definitions (dict): Test parameters
        """

        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)

        tacacs_servers = tests_tools.verify_tacacs(dut)

        if tacacs_servers:
            try:
                """
                TS: Run show command `show tacacs` on dut
                """
                self.output = dut["output"][tops.show_cmd]["json"]["tacacsServers"]
                assert self.output, "TACACS details are not collected."
                logging.info(
                    f"On device {tops.dut_name} output of {tops.show_cmd} command is: {self.output}"
                )

                eos_messages_received_1 = self.output[0]["messagesReceived"]

                """
                TS: Run `show tacacs` on dut again in order to see if messagesSent increments
                """
                self.output = tops.run_show_cmds(tops.show_cmd, "text")[0]["result"]
                assert self.output, "TACACS details are not collected."
                logging.info(
                    f"On device {tops.dut_name} output of {tops.show_cmd} command is: {self.output}"
                )

                eos_messages_received_2 = self.output["tacacsServers"][0][
                    "messagesReceived"
                ]

                if eos_messages_received_1 < eos_messages_received_2:
                    tops.test_result = True
                    tops.output_msg = (
                        f"\nOn router {tops.dut_name} TACACS messages2 "
                        f"received: {eos_messages_received_2} increments "
                        "from TACACS messages1 received: "
                        f"{eos_messages_received_1}"
                    )
                else:
                    tops.test_result = False
                    tops.output_msg = (
                        f"\nOn router {tops.dut_name} TACACS messages2 "
                        f"received: {eos_messages_received_2} doesn't "
                        "increments from TACACS messages1 received: "
                        f"{eos_messages_received_1}"
                    )
                assert eos_messages_received_1 < eos_messages_received_2
            except (
                AssertionError,
                AttributeError,
                LookupError,
                EapiError,
            ) as exception:
                logging.error(
                    f"""Error occurred during the testsuite execution on dut: {tops.dut_name}
                     is {str(exception)}"""
                )
        else:
            """
            TS: TACACS servers are not configured on the dut hence terminating the test
            """
            tops.actual_output = "N/A"
            tops.expected_output = "N/A"
            tops.test_result = True
            self.output = (
                f"\nOn router {tops.dut_name} does not have TACACS servers configured"
            )
            tops.comment = (
                f"\nRouter {tops.dut_name} does not have TACACS servers configured"
            )
            tops.output_msg = (
                f"\nOn router {tops.dut_name} does not have TACACS servers configured"
            )

        tops.parse_test_steps(self.test_if_tacacs_is_receiving_messages_on_)
        tops.generate_report(tops.dut_name, self.output)
