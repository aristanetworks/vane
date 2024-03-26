# Copyright (c) 2024 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.

"""
Test case for verification of BGP EVPN functionality.
"""

import pytest
from pyeapi.eapilib import EapiError, CommandError
from vane.config import dut_objs, test_defs
from vane import tests_tools, test_case_logger

TEST_SUITE = "nrfu_tests"
logging = test_case_logger.setup_logger(__file__)


@pytest.mark.nrfu_test
@pytest.mark.routing
class BgpEvpnTests:
    """
    Test case for verification of BGP EVPN functionality.
    """

    dut_parameters = tests_tools.parametrize_duts(TEST_SUITE, test_defs, dut_objs)
    test_duts = dut_parameters["test_routing_bgp_evpn_peers_state"]["duts"]
    test_ids = dut_parameters["test_routing_bgp_evpn_peers_state"]["ids"]

    @pytest.mark.parametrize("dut", test_duts, ids=test_ids)
    def test_routing_bgp_evpn_peers_state(self, dut, tests_definitions):
        """
        TD: Test case for verification of BGP EVPN functionality.
        Args:
            dut(dict): details related to a particular DUT
            tests_definitions(dict): test suite and test case parameters.
        """

        # Creating Testops class object and initializing the variables
        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)
        self.output = ""
        tops.actual_output = {"bgp_peers": {}}
        tops.expected_output = {"bgp_peers": {}}
        input_parameters = tops.test_parameters["input"]
        skip_on_command_unavailable = input_parameters["skip_on_command_unavailable"]
        show_cmd = "show bgp evpn summary"
        evpn_output = {}

        # Forming output message if the test result is passed
        tops.output_msg = "All BGP EVPN peers' state is established."

        try:
            """
            TS: Running `show bgp evpn summary` command on the device and verifying all the BGP EVPN
            peers state is established.
            """

            try:
                evpn_output = tops.run_show_cmds([show_cmd])

            except CommandError:
                # Checking for the condition whether to skip the test case or
                # check the assert statement
                if skip_on_command_unavailable:
                    tops.output_msg = (
                        f"Skipping test case on {tops.dut_name} as {show_cmd} command is"
                        " unavailable or device might be in ribd mode."
                    )
                    tests_tools.post_process_skip(
                        tops, self.test_routing_bgp_evpn_peers_state, self.output
                    )
                    pytest.skip(tops.output_msg)
                else:
                    assert False, (
                        f"On device {tops.dut_name}, command is unavailable, device might be in"
                        " ribd mode."
                    )

            logging.info(
                f"On device {tops.dut_name}, output of {tops.show_cmd} command is:\n{evpn_output}\n"
            )
            self.output += (
                f"On device {tops.dut_name}, output of {tops.show_cmd} command is:\n{evpn_output}\n"
            )
            bgp_evpn_neighbors = evpn_output[0].get("result", {}).get("vrfs")
            assert bgp_evpn_neighbors, "VRFs details are not found in the output."

            # Collecting peer details and forming expected and actual output dictionaries
            # with the peer state
            for vrf in bgp_evpn_neighbors:
                bgp_evpn_peers = bgp_evpn_neighbors.get(vrf, {}).get("peers")
                assert bgp_evpn_peers, f"For VRF {vrf}, BGP EVPN peers are not configured."

                for peer in bgp_evpn_peers:
                    peer_state = bgp_evpn_peers.get(peer, {}).get("peerState")
                    tops.expected_output["bgp_peers"].update({peer: {"peer_state": "Established"}})
                    tops.actual_output["bgp_peers"].update({peer: {"peer_state": peer_state}})

            # Forming output message if the test result is failed
            if tops.expected_output != tops.actual_output:
                tops.output_msg = (
                    "\nExpected state for not all BGP EVPN peers is Established as following peers"
                    " are in a different state:"
                )
                for peer, peer_state in tops.expected_output["bgp_peers"].items():
                    actual_peer_state = (
                        tops.actual_output.get("bgp_peers", {}).get(peer, {}).get("peer_state")
                    )
                    expected_peer_state = peer_state.get("peer_state")
                    if actual_peer_state != expected_peer_state:
                        tops.output_msg += f"\nPeer {peer} is in '{actual_peer_state}' state."

        except (AssertionError, AttributeError, LookupError, EapiError) as excep:
            tops.output_msg = tops.actual_output = str(excep).split("\n", maxsplit=1)[0]
            logging.error(
                f"On device {tops.dut_name}, Error while running the test case"
                f" is:\n{tops.actual_output}"
            )

        tops.test_result = tops.expected_output == tops.actual_output
        tops.parse_test_steps(self.test_routing_bgp_evpn_peers_state)
        tops.generate_report(tops.dut_name, self.output)
        assert tops.expected_output == tops.actual_output
