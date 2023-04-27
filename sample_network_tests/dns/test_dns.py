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
from vane import tests_tools
from vane.config import dut_objs, test_defs

TEST_SUITE = __file__
LOG_FILE = {"parameters": {"show_log": "show_output.log"}}

dut_parameters = tests_tools.parametrize_duts(TEST_SUITE, test_defs, dut_objs)

test1_duts = dut_parameters["test_if_dns_resolves_on_"]["duts"]
test1_ids = dut_parameters["test_if_dns_resolves_on_"]["ids"]

test2_duts = dut_parameters["test_if_dns_servers_are_reachable_on_"]["duts"]
test2_ids = dut_parameters["test_if_dns_servers_are_reachable_on_"]["ids"]

test3_duts = dut_parameters["test_dns_configuration_on_"]["duts"]
test3_ids = dut_parameters["test_dns_configuration_on_"]["ids"]


@pytest.mark.nrfu
@pytest.mark.base_feature
@pytest.mark.dns
@pytest.mark.virtual
@pytest.mark.physical
class DNSTests:
    """DNS Test Suite"""

    @pytest.mark.parametrize("dut", test1_duts, ids=test1_ids)
    def test_if_dns_resolves_on_(self, dut, tests_definitions):
        """Verify DNS is running by performing pings and verifying name resolution

        Args:
         dut (dict): Encapsulates dut details including name, connection
        """

        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)

        urls = tops.test_parameters["urls"]

        for url in urls:
            show_cmd = f"ping {url}"
            tops.show_cmds.append(show_cmd)

            print(show_cmd)
            show_cmd_txt = tops.run_show_cmds([show_cmd], encoding="text")
            show_cmd_txt = show_cmd_txt[0]["result"]["output"]

            tops.actual_output = "Name or service not known" not in show_cmd_txt
            tops.test_result = tops.actual_output is tops.expected_output

            tops.output_msg += (
                f"\nOn router {tops.dut_name}, DNS resolution is"
                f"{tops.test_result} for {url}.\n"
            )

            tops.actual_results.append(tops.actual_output)
            tops.expected_results.append(tops.expected_output)

        print(f"{tops.output_msg}\n{tops.comment}")

        tops.actual_output, tops.expected_output = (
            tops.actual_results,
            tops.expected_results,
        )

        tops.generate_report(tops.dut_name, tops.output_msg)

        assert tops.actual_results == tops.expected_results

    @pytest.mark.parametrize("dut", test2_duts, ids=test2_ids)
    def test_if_dns_servers_are_reachable_on_(self, dut, tests_definitions):
        """Verifies DNS servers are reachable via ping

        Args:
          dut (dict): Encapsulates dut details including name, connection
        """

        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)
        dns_servers = tops.test_parameters["dns_servers"]
        dns_vrf = tops.test_parameters["dns_vrf"]

        for dns_server in dns_servers:
            if dns_vrf:
                show_cmd = f"ping vrf {dns_vrf} ip {dns_server}"
            else:
                show_cmd = f"ping {dns_server}"

            output = tops.run_show_cmds([show_cmd], "text")[0]["result"]["output"]
            tops.actual_output = "bytes from" in output
            tops.test_result = tops.actual_output is tops.expected_output

            tops.output_msg += (
                f"\nOn router {tops.dut_name}, verifying DNS "
                f"server reachability for {dns_server} is "
                f"{tops.test_result}.\n"
            )

            tops.actual_results.append(tops.actual_output)
            tops.expected_results.append(tops.expected_output)

        print(f"{tops.output_msg}\n{tops.comment}")

        tops.actual_output, tops.expected_output = (
            tops.actual_results,
            tops.expected_results,
        )

        tops.generate_report(tops.dut_name, tops.output_msg)
        assert tops.actual_results == tops.expected_results

    @pytest.mark.parametrize("dut", test3_duts, ids=test3_ids)
    def test_dns_configuration_on_(self, dut, tests_definitions):
        """Verifies DNS configuration matches the recommended practices

        Args:
          dut (dict): Encapsulates dut details including name, connection
        """

        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)
        output = tops.run_show_cmds(["show running-config section name-server"], "text")

        dns_servers = tops.test_parameters["dns_servers"]
        dns_vrf = tops.test_parameters["dns_vrf"]
        dns_intf = tops.test_parameters["dns_intf"]
        dn_name = tops.test_parameters["dn_name"]
        dns_cfg = output[0]["result"]["output"]
        vane_dns_cfg = ""

        if dns_servers:
            for dns_server in dns_servers:
                if dns_vrf:
                    dns_server_cfg = f"ip name-server vrf {dns_vrf} {dns_server}"
                else:
                    dns_server_cfg = f"ip name-server {dns_server}"

                vane_dns_cfg += f"{dns_server_cfg}\n"
                tops.actual_output = dns_server_cfg in dns_cfg
                tops.actual_results.append(tops.actual_output)
                tops.expected_results.append(tops.expected_output)

            if dns_intf and dns_vrf:
                dns_server_cfg = (
                    f"ip domain lookup vrf {dns_vrf} source-interface {dns_intf}"
                )
            elif dns_intf:
                dns_server_cfg = f"ip domain lookup source-interface {dns_intf}"
            else:
                dns_server_cfg = None

            if dns_server_cfg:
                tops.actual_output = dns_server_cfg in dns_cfg
                tops.actual_results.append(tops.actual_output)
                tops.expected_results.append(tops.expected_output)
                vane_dns_cfg += f"{dns_server_cfg}\n"

            if dn_name:
                dns_server_cfg = f"ip domain-name {dn_name}"

            if dns_server_cfg:
                tops.actual_output = dns_server_cfg in dns_cfg
                tops.actual_results.append(tops.actual_output)
                tops.expected_results.append(tops.expected_output)
                vane_dns_cfg += f"{dns_server_cfg}\n"

        dns_cfg_length = len(dns_cfg.split("\n"))
        vane_dns_cfg_length = len(vane_dns_cfg.split("\n"))
        tops.actual_output = dns_cfg_length == vane_dns_cfg_length
        tops.actual_results.append(tops.actual_output)
        tops.expected_results.append(tops.expected_output)

        tops.test_result = tops.actual_results == tops.expected_results
        tops.output_msg += (
            f"{tops.dut_name} has the dns config "
            f"{dns_cfg}, expect the dns config "
            f"{vane_dns_cfg}.\n\n"
        )

        print(f"{tops.output_msg}\n{tops.comment}")

        tops.actual_output, tops.expected_output = (
            tops.actual_results,
            tops.expected_results,
        )
        tops.generate_report(tops.dut_name, tops.output_msg)
        assert tops.actual_results == tops.expected_results
