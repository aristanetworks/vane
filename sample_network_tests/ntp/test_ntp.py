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

""" Tests to validate ntp functionality."""

import pytest
from pyeapi.eapilib import EapiError
from vane import tests_tools
from vane.config import dut_objs, test_defs
from vane.vane_logging import logging


TEST_SUITE = __file__
LOG_FILE = {"parameters": {"show_log": "show_output.log"}}

dut_parameters = tests_tools.parametrize_duts(TEST_SUITE, test_defs, dut_objs)

test1_duts = dut_parameters["test_if_ntp_is_synchronized_on_"]["duts"]
test1_ids = dut_parameters["test_if_ntp_is_synchronized_on_"]["ids"]

test2_duts = dut_parameters["test_if_ntp_associated_with_peers_on_"]["duts"]
test2_ids = dut_parameters["test_if_ntp_associated_with_peers_on_"]["ids"]

test3_duts = dut_parameters["test_if_process_is_running_on_"]["duts"]
test3_ids = dut_parameters["test_if_process_is_running_on_"]["ids"]

test4_duts = dut_parameters["test_ntp_configuration_on_"]["duts"]
test4_ids = dut_parameters["test_ntp_configuration_on_"]["ids"]

test5_duts = dut_parameters["test_if_ntp_servers_are_reachable_on_"]["duts"]
test5_ids = dut_parameters["test_if_ntp_servers_are_reachable_on_"]["ids"]


@pytest.mark.nrfu
@pytest.mark.base_feature
@pytest.mark.ntp
@pytest.mark.virtual
@pytest.mark.physical
class NTPTests:
    """NTP Test Suite"""

    @pytest.mark.parametrize("dut", test1_duts, ids=test1_ids)
    def test_if_ntp_is_synchronized_on_(self, dut, tests_definitions):
        """TD: Verify ntp is synchronized

        Args:
          dut (dict): Encapsulates dut details including name, connection
        """

        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)

        try:
            """
            TS: Run show command `show ntp status` on dut
            """
            self.output = dut["output"][tops.show_cmd]["json"]
            assert self.output, "NTP server status details are not collected."
            logging.info(
                f"On device {tops.dut_name} output of {tops.show_cmd} command is: {self.output}"
            )

            tops.actual_output = self.output["status"]

            if tops.actual_output == tops.expected_output:
                tops.test_result = True
                tops.output_msg = (
                    f"\nOn router {tops.dut_name} NTP "
                    f"synchronized status is {tops.actual_output} "
                    f"which is correct.\n"
                )
            else:
                tops.test_result = False
                tops.output_msg = (
                    f"\nOn router {tops.dut_name} NTP "
                    f"synchronized status is {tops.actual_output} "
                    f"while the correct status is {tops.expected_output}.\n"
                )

        except (AttributeError, LookupError, EapiError) as exception:
            logging.error(
                f"On device {tops.dut_name}: Error while running testcase on DUT is: "
                f"{str(exception)}"
            )
            tops.actual_output = str(exception)
            tops.output_msg += (
                f"EXCEPTION encountered on device {tops.dut_name}, while "
                f"investigating if ntp is synchronized. Vane recorded error: {exception}"
            )

        """
        TS: Creating test report based on results
        """
        tops.parse_test_steps(self.test_if_ntp_is_synchronized_on_)
        tops.generate_report(tops.dut_name, self.output)
        assert tops.actual_output == tops.expected_output

    @pytest.mark.parametrize("dut", test2_duts, ids=test2_ids)
    def test_if_ntp_associated_with_peers_on_(self, dut, tests_definitions):
        """TD: Verify there are at least expected number of ntp peers

        Args:
          dut (dict): Encapsulates dut details including name, connection
        """

        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)

        try:
            """
            TS: Run show command `show ntp associations` on dut
            """
            self.output = dut["output"][tops.show_cmd]["json"]["peers"]
            assert self.output, "No NTP association details to collect."
            logging.info(
                f"On device {tops.dut_name} output of {tops.show_cmd} command is: {self.output}"
            )

            tops.actual_output = len(self.output)

            if tops.actual_output >= tops.expected_output:
                tops.test_result = True
                tops.output_msg = (
                    f"\nOn router {tops.dut_name} has "
                    f"{tops.actual_output} NTP peer associations, "
                    f"which is correct"
                )
            else:
                tops.test_result = False
                tops.output_msg = (
                    f"\nOn router {tops.dut_name} has "
                    f"{tops.actual_output} NTP peer associations, "
                    f"while the correct associations is {tops.expected_output}"
                )

        except (AttributeError, LookupError, EapiError) as exception:
            logging.error(
                f"On device {tops.dut_name}: Error while running testcase on DUT is: "
                f"{str(exception)}"
            )
            tops.actual_output = str(exception)
            tops.output_msg += (
                f"EXCEPTION encountered on device {tops.dut_name}, while "
                f"investigating if ntp peers are correct. Vane recorded error: {exception}"
            )

        """
        TS: Creating test report based on results
        """
        tops.parse_test_steps(self.test_if_ntp_associated_with_peers_on_)
        tops.generate_report(tops.dut_name, self.output)
        assert tops.actual_output >= tops.expected_output

    @pytest.mark.parametrize("dut", test3_duts, ids=test3_ids)
    def test_if_process_is_running_on_(self, dut, tests_definitions):
        """TD: Verify there are at least expected number of ntp processes running

        Args:
          dut (dict): Encapsulates dut details including name, connection
        """

        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)

        try:
            """
            TS: Run show command `show processes` on dut
            """
            processes = tops.test_parameters["processes"]

            self.output = dut["output"][tops.show_cmd]["json"]["processes"]
            assert self.output, "NTP processes details not collected."
            logging.info(
                f"On device {tops.dut_name} output of {tops.show_cmd} command is: {self.output}"
            )

            process_list = []

            for process_num in self.output:
                process_list.append(self.output[process_num]["cmd"])

            for process in processes:
                results = [i for i in process_list if process in i]

                tops.actual_output = len(results)

                if tops.actual_output >= tops.expected_output:
                    tops.output_msg = (
                        f"\nOn router {tops.dut_name} has "
                        f"{tops.actual_output} NTP processes running, "
                        "which is correct.\n"
                    )
                else:
                    tops.output_msg = (
                        f"\nOn router {tops.dut_name} has "
                        f"{tops.actual_output} NTP processes, "
                        " while correct processes is equal to or greater "
                        f"{tops.expected_output}.\n"
                    )

                tops.actual_results.append(tops.actual_output)
                tops.expected_results.append(tops.expected_output)

            tops.actual_output, tops.expected_output = (
                tops.actual_results,
                tops.expected_results,
            )

        except (AttributeError, LookupError, EapiError) as exception:
            logging.error(
                f"On device {tops.dut_name}: Error while running testcase on DUT is: "
                f"{str(exception)}"
            )
            tops.actual_output = str(exception)
            tops.output_msg += (
                f"EXCEPTION encountered on device {tops.dut_name}, while "
                f"investigating if ntp processes are running. Vane recorded error: {exception}"
            )
        """
        TS: Creating test report based on results
        """

        tops.parse_test_steps(self.test_if_process_is_running_on_)
        tops.test_result = all(
            x >= y for x, y in zip(tops.actual_output, tops.expected_output)
        )
        tops.generate_report(tops.dut_name, self.output)
        assert tops.test_result

    @pytest.mark.parametrize("dut", test4_duts, ids=test4_ids)
    def test_ntp_configuration_on_(self, dut, tests_definitions):
        """TD: Verifies NTP configuration matches the recommended practices

        Args:
          dut (dict): Encapsulates dut details including name, connection
        """

        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)

        try:
            """
            TS: Run show command `show running-config section ntp` on dut
            """

            self.output = dut["output"][tops.show_cmd]["text"]
            assert self.output, "NTP configuration details not collected."
            logging.info(
                f"On device {tops.dut_name} output of {tops.show_cmd} command is: {self.output}"
            )

            ntp_servers = tops.test_parameters["ntp_servers"]
            ntp_vrf = tops.test_parameters["ntp_vrf"]
            ntp_intf = tops.test_parameters["ntp_intf"]
            ntp_cfg = tops.show_cmd_txt
            vane_ntp_cfg = ""

            if ntp_servers:
                for ntp_server in ntp_servers:
                    if ntp_vrf:
                        ntp_server_cfg = f"ntp server vrf {ntp_vrf} {ntp_server}"
                    else:
                        ntp_server_cfg = f"ntp server {ntp_server}"

                    vane_ntp_cfg += f"{ntp_server_cfg}\n"
                    tops.actual_output = ntp_server_cfg in ntp_cfg
                    tops.actual_results.append(tops.actual_output)
                    tops.expected_results.append(tops.expected_output)

                if ntp_intf and ntp_vrf:
                    ntp_server_cfg = f"ntp source vrf {ntp_vrf} {ntp_intf}"
                elif ntp_intf:
                    ntp_server_cfg = f"ntp source {ntp_intf}"
                else:
                    ntp_server_cfg = None

                if ntp_server_cfg:
                    tops.actual_output = ntp_server_cfg in ntp_cfg
                    tops.actual_results.append(tops.actual_output)
                    tops.expected_results.append(tops.expected_output)
                    vane_ntp_cfg += f"{ntp_server_cfg}\n"

            ntp_cfg_length = len(ntp_cfg.split("\n"))
            vane_ntp_cfg_length = len(vane_ntp_cfg.split("\n"))
            tops.actual_output = ntp_cfg_length == vane_ntp_cfg_length
            tops.actual_results.append(tops.actual_output)
            tops.expected_results.append(tops.expected_output)

            if tops.actual_results == tops.expected_results:
                tops.test_result = True
                tops.output_msg += (
                    f"{tops.dut_name} has the ntp config "
                    f"{ntp_cfg} which is correct.\n\n"
                )
            else:
                tops.test_result = False
                tops.output_msg += (
                    f"{tops.dut_name} has the ntp config "
                    f"{ntp_cfg}, while the correct ntp config is "
                    f"{vane_ntp_cfg}.\n\n"
                )

            tops.actual_output, tops.expected_output = (
                tops.actual_results,
                tops.expected_results,
            )

        except (AttributeError, LookupError, EapiError) as exception:
            logging.error(
                f"On device {tops.dut_name}: Error while running testcase on DUT is: "
                f"{str(exception)}"
            )
            tops.actual_output = str(exception)
            tops.output_msg += (
                f"EXCEPTION encountered on device {tops.dut_name}, while "
                f"investigating ntp configuration. Vane recorded error: {exception}"
            )

        """
        TS: Creating test report based on results
        """
        tops.parse_test_steps(self.test_ntp_configuration_on_)
        tops.generate_report(tops.dut_name, self.output)
        assert tops.actual_output == tops.expected_output

    @pytest.mark.parametrize("dut", test5_duts, ids=test5_ids)
    def test_if_ntp_servers_are_reachable_on_(self, dut, tests_definitions):
        """TD: Verifies DNS servers are reachable via ping

        Args:
          dut (dict): Encapsulates dut details including name, connection
        """

        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)

        try:
            ntp_servers = tops.test_parameters["ntp_servers"]
            ntp_vrf = tops.test_parameters["ntp_vrf"]

            for ntp_server in ntp_servers:
                if ntp_vrf:
                    show_cmd = f"ping vrf {ntp_vrf} ip {ntp_server}"
                else:
                    show_cmd = f"ping {ntp_server}"

                """
                TS: Run ping command on dut
                """
                self.output = tops.run_show_cmds([show_cmd], encoding="text")
                assert self.output, "Details from Ping command on dut not collected."
                logging.info(
                    f"On device {tops.dut_name} output of {tops.show_cmd} command is: {self.output}"
                )

                tops.actual_output = "bytes from" in self.output[0]["result"]["output"]
                if tops.actual_output == tops.expected_output:
                    result = True
                    tops.output_msg += (
                        f"\nOn router {tops.dut_name}, verifying NTP "
                        f"server reachability for {ntp_server} is "
                        f"{result}.\n"
                    )
                else:
                    result = False
                    tops.output_msg += (
                        f"\nOn router {tops.dut_name}, verifying NTP "
                        f"server reachability for {ntp_server} is "
                        f"{result}.\n"
                    )

                tops.actual_results.append(tops.actual_output)
                tops.expected_results.append(tops.expected_output)

            tops.actual_output, tops.expected_output = (
                tops.actual_results,
                tops.expected_results,
            )

        except (AttributeError, LookupError, EapiError) as exception:
            logging.error(
                f"On device {tops.dut_name}: Error while running testcase on DUT is: "
                f"{str(exception)}"
            )
            tops.actual_output = str(exception)
            tops.output_msg += (
                f"EXCEPTION encountered on device {tops.dut_name}, while "
                f"investigating if dns servers are reachable. Vane recorded error: {exception}"
            )

        """
        TS: Creating test report based on results
        """
        tops.parse_test_steps(self.test_if_ntp_servers_are_reachable_on_)
        tops.test_result = tops.actual_output == tops.expected_output
        tops.generate_report(tops.dut_name, tops.output_msg)
        assert tops.actual_output == tops.expected_output
