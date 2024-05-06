# Copyright (c) 2023 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.

"""
Test cases for verification of NTP functionality
"""

import pytest
import sys
from pyeapi.eapilib import EapiError
from vane.config import dut_objs, test_defs
from vane import tests_tools, test_case_logger
from ipaddress import IPv4Address, ip_interface


TEST_SUITE = "new_tests"
logger = test_case_logger.setup_logger(__file__)


class TestRoutingProtocol:
    """ Test cases for verification of routing protocol """

    test_data_exists = tests_tools.is_test_data_present("test_routing_protocol_model")
    test_duts, test_ids = tests_tools.get_duts_n_ids("test_routing_protocol_model")

    @pytest.mark.skipif(not test_data_exists, 
                        reason="Test not in catalog")

    @pytest.mark.parametrize("dut", test_duts, ids=test_ids)
    def test_routing_protocol_model(self, dut, tests_definitions):
        """
        TD: Test case for verification of the configured routing protocol model is the one we expect
        Args:
          dut(dict): Details related to a particular device
          tests_definitions(dict): Test suite and test case parameters
        """

        # Creating the Testops class object and initialize the variables.
        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)
        self.output = ""
        test_params = tops.test_parameters
        show_cmd = tops.show_cmd
        inputs = test_params["inputs"][tops.dut_name]
        tops.expected_output =  {"configuredProtoModel": inputs[0]["model"],
                                 "operatingProtoModel": inputs[0]["model"],}

        # Forming an output message if a test result is passed.
        tops.output_msg = ("The routing model is correctly configured.")

        try:
            """
            TS: Running `show ip route summary` command on device and verifying that ,
            routing model is correctly configured
            """
            command_output = dut["output"][show_cmd]["text"]
            command_output_lines = command_output.splitlines()
            configured_model = operating_model = ""
            for line in command_output_lines:
                if line.startswith("Operating routing protocol model: "):
                    configured_model = line.split("Operating routing protocol model: ")[1]
                elif line.startswith("Configured routing protocol model: "):
                    operating_model = line.split("Configured routing protocol model: ")[1]
                else:
                    continue

            tops.actual_output = {"configuredProtoModel": configured_model,
                                  "operatingProtoModel": operating_model,}

            logger.info(
                "On device %s, output of '%s' command is:\n%s\n",
                tops.dut_name,
                show_cmd, command_output
            )
            self.output += (
                f"\n\nOn device {tops.dut_name}, output of command {show_cmd} is:"
                f" \n{command_output}"
            )

            # Forming an output message if a test result is failed
            if tops.actual_output != tops.expected_output:
                tops.output_msg = (f"routing model is misconfigured: configured: {configured_model} - operating: {operating_model} - expected: {inputs[tops.dut_name]['model']}")

        except (AssertionError, AttributeError, LookupError, EapiError) as excep:
            tops.actual_output = tops.output_msg = str(excep).split("\n", maxsplit=1)[0]
            logger.error(
                "On device %s: Error occurred while running the test case is:\n%s",
                tops.dut_name,
                tops.actual_output,
            )

        tops.test_result = tops.expected_output == tops.actual_output
        tops.parse_test_steps(self.test_routing_protocol_model)
        tops.generate_report(tops.dut_name, self.output)
        assert tops.expected_output == tops.actual_output

class TestRoutingTable:
    """
    Test cases for verification of Routing Table
    """

    test_data_exists = tests_tools.is_test_data_present("test_routing_table_entry")

    test_duts, test_ids = tests_tools.get_duts_n_ids("test_routing_table_entry")

    @pytest.mark.skipif(not test_data_exists, 
                        reason="Test not in catalog")

    @pytest.mark.parametrize("dut", test_duts, ids=test_ids)
    def test_routing_table_entry(self, dut, tests_definitions):
        """
        TD: Test case for verification of the provided routes are present in the routing table of a specified VRF.
        Args:
          dut(dict): Details related to a particular device
          tests_definitions(dict): Test suite and test case parameters
        """

        # Creating the Testops class object and initialize the variables.
        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)
        self.output = ""
        test_params = tops.test_parameters
        inputs = test_params["inputs"][tops.dut_name]
        show_cmds_dict = {}
        for test_input in inputs:
            vrf = test_input.get('vrf', 'default')
            route = test_input['routes'][0]
            show_cmd = f"show ip route vrf {vrf} {route}"
            if show_cmd not in show_cmds_dict:
                show_cmds_dict[show_cmd] = {"vrf": vrf, "route": route}

        # Forming an output message if a test result is passed.
        tops.output_msg = ("All required routes present")

        try:
            """
            TS: Running `show ip route vrf {vrf} {route}` commands on device and verifying that ,
            all required routes are present
            """
            missing_routes = []
    
            for cmd, val in show_cmds_dict.items():
                cmd_output = dut["output"][cmd]["json"]
                vrf, route = val["vrf"], ip_interface(val["route"]).ip
                if len(routes := cmd_output["vrfs"][vrf]["routes"]) == 0 or route != ip_interface(next(iter(routes))).ip:
                    missing_routes.append(str(route))
                logger.info(
                    "On device %s, output of '%s' command is:\n%s\n",
                    tops.dut_name,
                    cmd, cmd_output
                )
                self.output += (
                    f"\n\nOn device {tops.dut_name}, output of command {cmd} is:"
                    f" \n{cmd_output}"
                )

            # Updating expected output dictionary.
            tops.expected_output = []

            # Updating actual output dictionary.
            tops.actual_output = missing_routes

            # Forming an output message if a test result is failed
            if tops.actual_output != tops.expected_output:
                tops.output_msg = "The device does not have all required routes present"

        except (AssertionError, AttributeError, LookupError, EapiError) as excep:
            tops.actual_output = tops.output_msg = str(excep).split("\n", maxsplit=1)[0]
            logger.error(
                "On device %s: Error occurred while running the test case is:\n%s",
                tops.dut_name,
                tops.actual_output,
            )

        tops.test_result = tops.expected_output == tops.actual_output
        tops.parse_test_steps(self.test_routing_table_entry)
        tops.generate_report(tops.dut_name, self.output)
        assert tops.expected_output == tops.actual_output

class TestBGPPeers:
    """
    Test cases for verification of health of BGP peers
    """

    test_data_exists = tests_tools.is_test_data_present("test_bgp_specific_peers")

    test_duts, test_ids = tests_tools.get_duts_n_ids("test_bgp_specific_peers")

    @pytest.mark.skipif(not test_data_exists, 
                        reason="Test not in catalog")

    @pytest.mark.parametrize("dut", test_duts, ids=test_ids)
    def test_bgp_specific_peers(self, dut, tests_definitions):
        """
        TD: Test case for verifies that the BGP session is established and all message queues for this BGP session are empty for the given peer(s).
        Args:
          dut(dict): Details related to a particular device
          tests_definitions(dict): Test suite and test case parameters
        """

        # Creating the Testops class object and initialize the variables.
        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)
        self.output = ""
        test_params = tops.test_parameters
        inputs = test_params["inputs"][tops.dut_name]
        show_cmds_data = []
        for test_input in inputs:
            af = test_input["address_families"][0]
            vrf = af.get('vrf', 'default')
            peer = af['peers'][0]
            afi = af['afi']
            safi = af.get('safi', '')
            if afi in ["ipv4", "ipv6"] and safi != "sr-te":
                show_cmd = f"show bgp {afi} {safi} summary vrf {vrf}"
            elif afi in ["ipv4", "ipv6"] and safi == "sr-te":
                show_cmd = f"show bgp {safi} {afi} summary vrf {vrf}"
            elif afi not in ["ipv4", "ipv6"]:
                show_cmd = f"show bgp {afi} summary"
            show_cmds_data.append({"show_cmd": show_cmd, "vrf": vrf, "peer": peer, 'afi': afi, 'safi': safi})


        # Forming an output message if a test result is passed.
        tops.output_msg = ("All required routes present")

        try:
            """
            TS: Running `show bgp {afi} {safi} summary vrf {vrf}` and `show bgp {afi} summary`  commands on device and verifying that 
            the BGP session is established and all messages queues are empty for each given peer
            """
            failures: dict[tuple[str, Any], dict[str, Any]] = {}

            for data in show_cmds_data:
                command = data["show_cmd"]
                command_output = dut["output"][command]["json"]

                afi = data["afi"]
                safi = data["safi"]
                afi_vrf = data["vrf"] 

                # Swapping AFI and SAFI in case of SR-TE
                if afi == "sr-te":
                    afi, safi = safi, afi

                peer = data["peer"]
                if not (vrfs := command_output.get("vrfs")):
                    _add_bgp_failures(failures=failures, afi=afi, safi=safi, vrf=afi_vrf, issue="Not Configured")
                    continue

                peer_issues = {}
                peer_data = vrfs[afi_vrf]["peers"][peer]
                issues = _check_peer_issues(peer_data)
                if issues:
                    peer_issues[peer_ip] = issues

                if peer_issues:
                    _add_bgp_failures(failures=failures, afi=afi, safi=safi, vrf=afi_vrf, issue=peer_issues)

                logger.info(
                    "On device %s, output of '%s' command is:\n%s\n",
                    tops.dut_name,
                    command, command_output
                )
                self.output += (
                    f"\n\nOn device {tops.dut_name}, output of command {command} is:"
                    f" \n{command_output}"
                )

            # Updating expected output dictionary.
            tops.expected_output = {}

            # Updating actual output dictionary.
            tops.actual_output = failures

            # Forming an output message if a test result is failed
            if tops.actual_output != tops.expected_output:
                tops.output_msg = "The device BGP peers health check failed"

        except (AssertionError, AttributeError, LookupError, EapiError) as excep:
            tops.actual_output = tops.output_msg = str(excep).split("\n", maxsplit=1)[0]
            _, _, exc_tb = sys.exc_info()
            logger.error(
                "On device %s: Error occurred while running the test case is:\n%s %s",
                tops.dut_name,
                tops.actual_output,
                exc_tb.tb_lineno
            )

        tops.test_result = tops.expected_output == tops.actual_output
        tops.parse_test_steps(self.test_bgp_specific_peers)
        tops.generate_report(tops.dut_name, self.output)
        assert tops.expected_output == tops.actual_output


def _add_bgp_failures(failures, afi, safi, vrf, issue):
    key = (afi, safi)

    failure_entry = failures.setdefault(key, {"afi": afi, "safi": safi, "vrfs": {}}) if safi else failures.setdefault(key, {"afi": afi, "vrfs": {}})

    failure_entry["vrfs"][vrf] = issue

def _check_peer_issues(peer_data):
    if peer_data is None:
        return {"peerNotFound": True}

    if any(key not in peer_data for key in ["peerState", "inMsgQueue", "outMsgQueue"]):
        msg = "Provided BGP peer data is invalid."
        raise ValueError(msg)

    if peer_data["peerState"] != "Established" or peer_data["inMsgQueue"] != 0 or peer_data["outMsgQueue"] != 0:
        return {"peerState": peer_data["peerState"], "inMsgQueue": peer_data["inMsgQueue"], "outMsgQueue": peer_data["outMsgQueue"]}

    return {}
