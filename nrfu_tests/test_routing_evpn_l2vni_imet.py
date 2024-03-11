# Copyright (c) 2023 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.

"""Test case for verification of L2 VNI VXLAN interface functionality"""

import pytest
from pyeapi.eapilib import EapiError
from vane import tests_tools
from vane import test_case_logger
from vane.config import dut_objs, test_defs

TEST_SUITE = "nrfu_tests"
logging = test_case_logger.setup_logger(__file__)


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
        test_params = tops.test_parameters
        no_imet_routes_advertised = {}
        skip_on_command_unavailable_check = test_params["input"][
            "skip_on_command_unavailable_check"
        ]

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
            show_bgp_command = "show bgp evpn summary"
            evpn_summary = tops.run_show_cmds([show_bgp_command])
            logging.info(
                f"On device {tops.dut_name}, Output of {show_bgp_command} command"
                f" is:\n{evpn_summary}\n"
            )
            self.output += (
                f"On device {tops.dut_name}, Output of {show_bgp_command} is:\n{evpn_summary}\n"
            )
            vrf_details = evpn_summary[0]["result"].get("vrfs")

            evpn_running = False
            for vrf in vrf_details:
                if vrf_details[vrf].get("peers"):
                    evpn_running = True
                    break

            if evpn_running:
                pytest.skip(f"EVPN is not configured on {tops.dut_name}.")

            bgp_evpn_peer = ""
            for vrf in vrf_details:
                no_imet_routes_advertised[vrf] = []
                tops.actual_output["vrfs"][vrf] = {"virtual_network_identifiers": {}}
                tops.expected_output["vrfs"][vrf] = {"virtual_network_identifiers": {}}
                for peer in vrf_details[vrf].get("peers"):
                    peer_state = vrf_details[vrf].get("peers")[peer].get("peerState")
                    if peer_state == "Established":
                        bgp_evpn_peer = peer
                        break

                assert bgp_evpn_peer, "None of the BGP evpn peer's state is Established."

                """
                TS: Running `show interfaces <vxlan interface>` command and verifying L2 VNIs are
                configured on the device.
                """
                vxlan_interface = "Vxlan1"
                show_vxlan_command = f"show interfaces {vxlan_interface}"
                vxlan_details = tops.run_show_cmds([show_vxlan_command])
                logging.info(
                    f"On device {tops.dut_name}, Output of {show_vxlan_command} command"
                    f" is:\n{vxlan_details}\n"
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
                assert vxlan_details, "VLAN to VNI mapping is not found in vxlan command details."

                for vlan in vxlan_details:
                    if not vxlan_details[vlan].get("source"):
                        vni = vxlan_details[vlan].get("vni")
                        tops.expected_output["vrfs"][vrf]["virtual_network_identifiers"][
                            str(vni)
                        ] = {"imet_routes_being_advertised": True}

                        """
                        TS: Running `show bgp neighbors <bgp evpn peer> evpn advertised-routes
                        route-type imet vni <vni>` command and verifying VNI is advertising
                        imet out.
                        """
                        route_show_command = (
                            f"show bgp neighbors {bgp_evpn_peer} evpn advertised-routes route-type"
                            f" imet vni {vni}"
                        )
                        advertised_route_details = tops.run_show_cmds([route_show_command])
                        logging.info(
                            f"On device {tops.dut_name}, Output of {route_show_command} command"
                            f" is:\n{advertised_route_details}\n"
                        )
                        self.output += (
                            f"On device {tops.dut_name}, Output of"
                            f" {route_show_command} is:\n{advertised_route_details}\n"
                        )
                        advertised_route_details = advertised_route_details[0]["result"].get(
                            "evpnRoutes"
                        )
                        if not advertised_route_details:
                            no_imet_routes_advertised[vrf].append(vni)

                        tops.actual_output["vrfs"][vrf]["virtual_network_identifiers"][str(vni)] = {
                            "imet_routes_being_advertised": bool(advertised_route_details)
                        }

            # forming output message if test result is fail
            if tops.actual_output != tops.expected_output:
                tops.output_msg = "\n"
                for vrf, vnis in no_imet_routes_advertised.items():
                    if vnis:
                        tops.output_msg += (
                            f"For vrf {vrf}, following VNIs has no IMET routes being"
                            f" advertised: {', '.join(vnis)}\n"
                        )

        except (AssertionError, AttributeError, LookupError, EapiError) as excep:
            if skip_on_command_unavailable_check:
                if (show_bgp_command and "Not supported") in str(excep):
                    tops.output_msg = (
                        f"{show_bgp_command} command unavailable, device might be in ribd mode."
                    )
                    pytest.skip(
                        f"{show_bgp_command} command unavailable, device might be in ribd mode."
                        " hence test skipped."
                    )

            if "Interface does not exist" in str(excep):
                tops.output_msg = f"{vxlan_interface} interface does not exist / no L2 VNIs."
                pytest.skip(
                    f"{vxlan_interface} interface does not exist / no L2 VNIs. hence test skipped."
                )

            tops.actual_output = tops.output_msg = str(excep).split("\n", maxsplit=1)[0]
            logging.error(
                f"On device {tops.dut_name}: Error while running the testcase"
                f" is:\n%{tops.actual_output}"
            )

        tops.test_result = tops.expected_output == tops.actual_output
        tops.parse_test_steps(self.test_routing_evpn_l2vni_imet)
        tops.generate_report(tops.dut_name, self.output)
        assert tops.expected_output == tops.actual_output
