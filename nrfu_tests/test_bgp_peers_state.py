# Copyright (c) 2023 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.

"""
Testcase for verification of BGP IPv4 peers state.
"""

import pytest
from pyeapi.eapilib import EapiError
from vane.logger import logger
from vane.config import dut_objs, test_defs
from vane import tests_tools

TEST_SUITE = "nrfu_tests"


@pytest.mark.nrfu_test
@pytest.mark.routing
class BgpIpPeersStatusTests:
    """
    Testcase for verification of BGP IPv4 peers state.
    """

    dut_parameters = tests_tools.parametrize_duts(TEST_SUITE, test_defs, dut_objs)
    test_duts = dut_parameters["test_bgp_ipv4_peers_state"]["duts"]
    test_ids = dut_parameters["test_bgp_ipv4_peers_state"]["ids"]

    @pytest.mark.parametrize("dut", test_duts, ids=test_ids)
    def test_bgp_ipv4_peers_state(self, dut, tests_definitions):
        """
        TD: Testcase for verification of BGP IPv4 peers state.
        Args:
            dut(dict): details related to a particular DUT
            tests_definitions(dict): test suite and test case parameters.
        """
        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)
        tops.expected_output = {"bgp_peers": {}}
        tops.actual_output = {"bgp_peers": {}}
        self.output = ""

        # forming output message if test result is passed
        tops.output_msg = "All BGP IPv4 peers are in established state."

        try:
            """
            TS: Running `show ip bgp summary vrf all` command and verifying
            state of BGP IPv4 peers.
            """
            output = dut["output"][tops.show_cmd]["json"]
            logger.info(
                "On device %s, output of %s command is:\n%s\n",
                tops.dut_name,
                tops.show_cmd,
                output,
            )
            self.output = f"Output of {tops.show_cmd} command is:\n{output}\n"
            bgp_peers = output.get("vrfs")
            assert bgp_peers, "BGP peer details are not found."

            # Collecting actual and expected output.
            for vrf in bgp_peers:
                for peer in bgp_peers.get(vrf).get("peers"):
                    tops.expected_output["bgp_peers"].update({peer: {"state": "Established"}})
                    peer_state = bgp_peers.get(vrf).get("peers").get(peer).get("peerState")
                    tops.actual_output["bgp_peers"].update({peer: {"state": peer_state}})

            # Forming output message if test result is fail.
            if tops.actual_output != tops.expected_output:
                tops.output_msg = "\n"
                for interface, peer_state in tops.expected_output["bgp_peers"].items():
                    actual_peer_state = tops.actual_output["bgp_peers"].get(interface).get("state")
                    expected_peer_state = peer_state.get("state")
                    if expected_peer_state != actual_peer_state:
                        tops.output_msg += (
                            f"For the BGP peer {interface}:\nExpected peer state is"
                            f" '{expected_peer_state}', however actual is found as"
                            f" '{actual_peer_state}'.\n\n"
                        )

        except (AssertionError, AttributeError, LookupError, EapiError) as excep:
            tops.output_msg = tops.actual_output = str(excep).split("\n", maxsplit=1)[0]
            logger.error(
                "On device %s, Error while running the testcase is:\n%s",
                tops.dut_name,
                tops.actual_output,
            )

        tops.test_result = tops.expected_output == tops.actual_output
        tops.parse_test_steps(self.test_bgp_ipv4_peers_state)
        tops.generate_report(tops.dut_name, self.output)
        assert tops.expected_output == tops.actual_output
