# Copyright (c) 2024 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.

"""
Testcase for verification of BGP IPv4 peers state.
"""

import pytest
from pyeapi.eapilib import EapiError
from vane.config import dut_objs, test_defs
from vane import tests_tools, test_case_logger

TEST_SUITE = "nrfu_tests"
logging = test_case_logger.setup_logger(__file__)


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
        bgp_peers_found = False

        # forming output message if test result is passed
        tops.output_msg = "All BGP IPv4 peers are in established state."

        try:
            """
            TS: Running `show ip bgp summary vrf all` command on dut and verifying
            state for all BGP IPv4 peers.
            """
            output = dut["output"][tops.show_cmd]["json"]
            logging.info(
                f"On device {tops.dut_name}, output of {tops.show_cmd} command is:\n{output}\n"
            )
            self.output = f"Output of {tops.show_cmd} command is:\n{output}\n"
            bgp_peers = output.get("vrfs")

            # Skipping, if BGP is not configured.
            if not bgp_peers:
                tops.output_msg = (
                    f"BGP is not configured on device {tops.dut_name}, hence skipping the test"
                    " case."
                )
                tests_tools.post_process_skip(tops, self.test_bgp_ipv4_peers_state, self.output)
                pytest.skip(tops.output_msg)

            # Failing the test case if BGP peers are not found.
            for vrf in bgp_peers:
                if bgp_peers.get(vrf).get("peers"):
                    bgp_peers_found = True
                    break
            assert bgp_peers_found, "BGP peers are not found for any VRFs."

            # Collecting actual and expected output.
            for vrf in bgp_peers:
                for peer in bgp_peers.get(vrf).get("peers"):
                    tops.expected_output["bgp_peers"].update({peer: {"state": "Established"}})
                    peer_state = bgp_peers.get(vrf).get("peers").get(peer).get("peerState")
                    tops.actual_output["bgp_peers"].update({peer: {"state": peer_state}})

            # Forming output message if test result is fail.
            if tops.actual_output != tops.expected_output:
                tops.output_msg = "\nBGP neighbors state for following peers is not Established:\n"
                for interface, peer_state in tops.expected_output["bgp_peers"].items():
                    actual_peer_state = tops.actual_output["bgp_peers"].get(interface).get("state")
                    expected_peer_state = peer_state.get("state")
                    if expected_peer_state != actual_peer_state:
                        tops.output_msg += f"Neighbor {interface} state is {actual_peer_state}.\n"

        except (AssertionError, AttributeError, LookupError, EapiError) as excep:
            tops.output_msg = tops.actual_output = str(excep).split("\n", maxsplit=1)[0]
            logging.error(
                f"On device {tops.dut_name}, Error while running the testcase"
                f" is:\n{tops.actual_output}"
            )

        tops.test_result = tops.expected_output == tops.actual_output
        tops.parse_test_steps(self.test_bgp_ipv4_peers_state)
        tops.generate_report(tops.dut_name, self.output)
        assert tops.expected_output == tops.actual_output
