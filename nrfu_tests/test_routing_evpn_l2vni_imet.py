# Copyright (c) 2023 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.

"""Test case for verification of L2 VNI VXLAN interface functionality"""

import pytest
from pyeapi.eapilib import EapiError
from vane import tests_tools
from vane.logger import logger
from vane.config import dut_objs, test_defs

TEST_SUITE = "nrfu_tests"


@pytest.mark.nrfu_test
@pytest.mark.routing
class EvpnRoutingTests:

    """Test case for verification of L2 VNI VXLAN interface functionality"""

    dut_parameters = tests_tools.parametrize_duts(TEST_SUITE, test_defs, dut_objs)
    test_duts = dut_parameters["test_routing_evpn_l2vni_imet"]["duts"]
    test_ids = dut_parameters["test_routing_evpn_l2vni_imet"]["ids"]

    @pytest.mark.parametrize("dut", test_duts, ids=test_ids)
    def test_routing_evpn_l2vni_imet(self, dut, tests_definitions):
        """
        TD: Test case for verification of L2 VNI VXLAN interface functionality.
        Args:
          dut(dict): Details related to the switches
          tests_definitions(dict): Test suite and test case parameters
        """

        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)
        self.output = ""
        tops.expected_output = {"vrfs": {}}
        tops.actual_output = {"vrfs": {}}
        vxlan_interface = tops.test_parameters["input"]["vxlan_interface"]

        # Forming output message if test result is pass
        tops.output_msg = (
            "Inclusive multicast Ethernet tag (IMET) routes are advertised for all VNI identifiers"
            " on device."
        )

        try:
            """
            TS: Running `show bgp evpn summary` command and verifying EVPN is configured
            on the device.
            """
            evpn_summary = tops.run_show_cmds(["show bgp evpn summary"])
            logger.info(
                "On device %s, Output of %s command is:\n%s\n",
                tops.dut_name,
                tops.show_cmd,
                evpn_summary,
            )
            self.output += (
                f"On device {tops.dut_name}, Output of {tops.show_cmd} is:\n{evpn_summary}\n"
            )
            vrf_details = evpn_summary[0]["result"].get("vrfs")
            assert vrf_details, "VRF details are not found in EVPN bgp route summary."

            evpn_running = False
            for vrf in vrf_details:
                if vrf_details[vrf].get("peers"):
                    evpn_running = True
                    break

            assert evpn_running, "EVPN is not configured on the device."

            bgp_evpn_peer = ""
            for vrf in vrf_details:
                tops.actual_output["vrfs"][vrf] = {"virtual_network_identifiers": {}}
                tops.expected_output["vrfs"][vrf] = {"virtual_network_identifiers": {}}
                for peer in vrf_details[vrf].get("peers"):
                    peer_state = vrf_details[vrf].get("peers")[peer].get("peerState")
                    if peer_state == "Established":
                        bgp_evpn_peer = peer
                        break

                assert bgp_evpn_peer, "No established EVPN peer found."

                """
                TS: Running `show interfaces <vxlan interface>` command and verifying L2 VNIs are
                configured on the device.
                """
                show_vxlan_command = f"show interfaces {vxlan_interface}"
                vxlan_details = tops.run_show_cmds([show_vxlan_command])
                logger.info(
                    "On device %s, Output of %s command is:\n%s\n",
                    tops.dut_name,
                    show_vxlan_command,
                    vxlan_details,
                )
                self.output += (
                    f"On device {tops.dut_name}, Output of"
                    f" {show_vxlan_command} is:\n{vxlan_details}\n"
                )
                vxlan_details = (
                    vxlan_details[0]["result"]
                    .get("interfaces", {})
                    .get(vxlan_interface, {})
                    .get("vlanToVniMap")
                )
                assert vxlan_details, "No vlan to VNI mapping found in vxlan command details."

                for vlan in vxlan_details:
                    if not vxlan_details[vlan].get("source"):
                        vni = vxlan_details[vlan].get("vni")
                        tops.expected_output["vrfs"][vrf]["virtual_network_identifiers"][
                            str(vni)
                        ] = {"imet_routes_being_advertised": True}

                        """
                        TS: Running `show bgp neighbors <bgp evpn peer> evpn advertised-routes
                        route-type imet vni <vni>` command and verifying EVPN is configured
                        on the device.
                        """
                        route_show_command = (
                            f"show bgp neighbors {bgp_evpn_peer} evpn advertised-routes route-type"
                            f" imet vni {vni}"
                        )
                        advertised_route_details = tops.run_show_cmds([route_show_command])
                        logger.info(
                            "On device %s, Output of %s command is:\n%s\n",
                            tops.dut_name,
                            route_show_command,
                            advertised_route_details,
                        )
                        self.output += (
                            f"On device {tops.dut_name}, Output of"
                            f" {show_vxlan_command} is:\n{advertised_route_details}\n"
                        )
                        advertised_route_details = advertised_route_details[0]["result"].get(
                            "evpnRoutes"
                        )

                        tops.actual_output["vrfs"][vrf]["virtual_network_identifiers"][str(vni)] = {
                            "imet_routes_being_advertised": bool(advertised_route_details)
                        }

            # forming output message if test result is fail
            if tops.actual_output != tops.expected_output:
                tops.output_msg = "\n"
                for vrf in tops.actual_output["vrfs"]:
                    no_imet_routes_advertised = []
                    for vni in tops.actual_output["vrfs"][vrf]["virtual_network_identifiers"]:
                        if not tops.actual_output["vrfs"][vrf]["virtual_network_identifiers"][vni][
                            "imet_routes_being_advertised"
                        ]:
                            no_imet_routes_advertised.append(vni)
                    if no_imet_routes_advertised:
                        tops.output_msg += (
                            f"For vrf {vrf}, following VNIs has no IMET routes being"
                            f" advertised:\n{', '.join(no_imet_routes_advertised)}\n"
                        )

        except (AssertionError, AttributeError, LookupError, EapiError) as excep:
            if "Not supported" in str(excep):
                tops.output_msg = "Command unavailable, device might be in ribd mode."
                pytest.skip(
                    "Command unavailable, device might be in ribd mode. hence test skipped."
                )

            tops.actual_output = tops.output_msg = str(excep).split("\n", maxsplit=1)[0]
            logger.error(
                "On device %s: Error while running the testcase is:\n%s",
                tops.dut_name,
                tops.actual_output,
            )

        tops.test_result = tops.expected_output == tops.actual_output
        tops.parse_test_steps(self.test_routing_evpn_l2vni_imet)
        tops.generate_report(tops.dut_name, self.output)
        assert tops.expected_output == tops.actual_output
