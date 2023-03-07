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
from vane.fixtures import dut, tests_definitions


TEST_SUITE = __file__

@pytest.mark.nrfu
@pytest.mark.base_feature
@pytest.mark.ntp
@pytest.mark.virtual
@pytest.mark.physical
@pytest.mark.eos424
class NTPTests:
    """NTP Test Suite"""

    def test_if_ntp_is_synchronized_on_(self, dut, tests_definitions):
        """Verify ntp is synchronzied

        Args:
          dut (dict): Encapsulates dut details including name, connection
        """

        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)
        tops.actual_output = dut["output"][tops.show_cmd]["json"]["status"]
        tops.test_result = tops.actual_output == tops.expected_output

        tops.output_msg = (
            f"\nOn router |{tops.dut_name}| NTP "
            f"synchronised status is |{tops.actual_output}| "
            f" correct status is |{tops.expected_output}|.\n"
        )

        print(f"{tops.output_msg}\n{tops.comment}")

        tops.post_testcase()

        assert tops.actual_output == tops.expected_output

    def test_if_ntp_associated_with_peers_on_(self, dut, tests_definitions):
        """Verify ntp peers are correct

        Args:
          dut (dict): Encapsulates dut details including name, connection
        """

        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)
        tops.actual_output = dut["output"][tops.show_cmd]["json"]["peers"]
        tops.actual_output = len(tops.actual_output)
        tops.test_result = tops.actual_output >= tops.expected_output

        tops.output_msg = (
            f"\nOn router |{tops.dut_name}| has "
            f"|{tops.actual_output}| NTP peer associations, "
            f"correct associations is |{tops.expected_output}|"
        )

        print(f"{tops.output_msg}\n{tops.comment}")

        tops.post_testcase()

        assert tops.actual_output == tops.expected_output

    def test_if_process_is_running_on_(self, dut, tests_definitions):
        """Verify ntp processes are running

        Args:
          dut (dict): Encapsulates dut details including name, connection
        """

        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)
        processes = tops.test_parameters["processes"]
        process_nums = dut["output"][tops.show_cmd]["json"]["processes"]

        process_list = []

        for process_num in process_nums:
            process_list.append(process_nums[process_num]["cmd"])

        for process in processes:
            results = [i for i in process_list if process in i]
            tops.actual_output = len(results)

            tops.output_msg = (
                f"\nOn router |{tops.dut_name}| has "
                f"{tops.actual_output} NTP processes, "
                " correct processes is equal to or greater "
                f"|{tops.expected_output}|.\n"
            )

            tops.test_result = tops.actual_output >= tops.expected_output

            print(f"{tops.output_msg}\n{tops.comment}")

            tops.post_testcase()

            assert tops.actual_output == tops.expected_output

    def test_ntp_configuration_on_(self, dut, tests_definitions):
        """Verifies NTP configuration matches the recommended practices

        Args:
          dut (dict): Encapsulates dut details including name, connection
        """

        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)
        tops.return_show_cmd("show running-config section ntp")

        tops.actual_output = tops.show_cmd_txt
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

        tops.test_result = tops.actual_results == tops.expected_results
        tops.output_msg += (
            f"|{tops.dut_name}| has the ntp config "
            f"|{ntp_cfg}|, expect the ntp config "
            f"|{vane_ntp_cfg}|.\n\n"
        )

        print(f"{tops.output_msg}\n{tops.comment}")

        tops.actual_output, tops.expected_output = (
            tops.actual_results,
            tops.expected_results,
        )
        tops.post_testcase()
        assert tops.actual_results == tops.expected_results

    def test_if_ntp_servers_are_reachable_on_(self, dut, tests_definitions):
        """Verifies DNS servers are reachable via ping

        Args:
          dut (dict): Encapsulates dut details including name, connection
        """

        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)
        ntp_servers = tops.test_parameters["ntp_servers"]
        ntp_vrf = tops.test_parameters["ntp_vrf"]

        for ntp_server in ntp_servers:
            if ntp_vrf:
                show_cmd = f"ping vrf {ntp_vrf} ip {ntp_server}"
            else:
                show_cmd = f"ping {ntp_server}"

            tops.return_show_cmd(show_cmd)
            tops.actual_output = "bytes from" in tops.show_cmd_txt
            tops.test_result = tops.actual_output is tops.expected_output

            tops.output_msg += (
                f"\nOn router |{tops.dut_name}|, verifying NTP "
                f"server reachability for |{ntp_server}| is "
                f"|{tops.test_result}|.\n"
            )

            tops.actual_results.append(tops.actual_output)
            tops.expected_results.append(tops.expected_output)

        tops.actual_output, tops.expected_output = (
            tops.actual_results,
            tops.expected_results,
        )
        tops.post_testcase()

        assert tops.actual_results == tops.expected_results
