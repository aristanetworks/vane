# Copyright (c) 2023 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.

""" Testcases for the verification of port channel members interfaces details """

import pytest
from pyeapi.eapilib import EapiError
from vane import tests_tools, test_case_logger
from vane.config import dut_objs, test_defs

TEST_SUITE = "nrfu_tests"
logging = test_case_logger.setup_logger(__file__)


@pytest.mark.nrfu_test
@pytest.mark.interfaces
class PortChannelMemberInterfacesTests:
    """Testcases for the verification of port channel members interfaces details"""

    dut_parameters = tests_tools.parametrize_duts(TEST_SUITE, test_defs, dut_objs)
    test_duts = dut_parameters["test_port_channel_member_interface_details"]["duts"]
    test_ids = dut_parameters["test_port_channel_member_interface_details"]["ids"]

    @pytest.mark.parametrize("dut", test_duts, ids=test_ids)
    def test_port_channel_member_interface_details(self, dut, tests_definitions):
        """
        TD: Testcases to verify that port channel members interfaces should
        be collecting and distributing.
        Args:
          dut(dict): Details related to the switches
          tests_definitions(dict): Test suite and test case parameters
        """
        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)
        self.output = ""
        tops.actual_output = {"port_channels": {}}
        tops.expected_output = {"port_channels": {}}
        # Forming output message if test result is pass
        tops.output_msg = "All the port channel members interfaces are collecting and distributing."

        try:
            """
            TS: Running `show lacp interface all-ports` on DUT and verifying that the
            port channel members interfaces are collecting and distributing.
            """
            output = dut["output"][tops.show_cmd]["json"]
            logging.info(
                f"On device {tops.dut_name}, output of {tops.show_cmd} command is:\n{output}\n",
            )
            self.output = f"\nOutput of {tops.show_cmd} command is: \n{output}"

            # Skipping testcase if port channel details are not found on DUT.
            if not output.get("portChannels"):
                pytest.skip("Port-Channels are not found hence skipped the testcase.")

            expected_partner_port_state = {
                "partner_port_state": {"collecting": True, "distributing": True}
            }

            for port_channel in output.get("portChannels"):
                tops.expected_output["port_channels"].update({port_channel: {"interfaces": {}}})
                tops.actual_output["port_channels"].update({port_channel: {"interfaces": {}}})
                interface_data = output["portChannels"][port_channel].get("interfaces")

                for interface in interface_data:
                    tops.expected_output["port_channels"][port_channel]["interfaces"].update(
                        {interface: expected_partner_port_state}
                    )
                    partner_port_state = interface_data[interface].get("partnerPortState", {})
                    interface_partner_port_state = {
                        "partner_port_state": {
                            "collecting": partner_port_state.get("collecting"),
                            "distributing": partner_port_state.get("distributing"),
                        }
                    }
                    tops.actual_output["port_channels"][port_channel]["interfaces"].update(
                        {interface: interface_partner_port_state}
                    )

            # Forming output message if test result is fail
            if tops.actual_output != tops.expected_output:
                tops.output_msg = "\n"

                # Iterating over port channels details.
                for port_channel, port_channel_data in tops.actual_output["port_channels"].items():
                    not_collecting_interfaces = []
                    not_distributing_interfaces = []
                    output = ""

                    for interface, interface_data in port_channel_data["interfaces"].items():
                        collecting_state = interface_data["partner_port_state"]["collecting"]
                        distributing_state = interface_data["partner_port_state"]["distributing"]

                        if not collecting_state:
                            not_collecting_interfaces.append(interface)

                        if not distributing_state:
                            not_distributing_interfaces.append(interface)

                    if not_collecting_interfaces:
                        output = (
                            "Following members interfaces are not having the collecting state:"
                            f" {', '.join(not_collecting_interfaces)}.\n"
                        )

                    if not_distributing_interfaces:
                        output += (
                            "Following members interfaces are not having the distributing state:"
                            f" {', '.join(not_distributing_interfaces)}.\n"
                        )

                    if output:
                        tops.output_msg += f"For {port_channel}:\n{output}\n"

        except (AttributeError, LookupError, EapiError) as excp:
            tops.actual_output = tops.output_msg = str(excp).split("\n", maxsplit=1)[0]
            logging.error(
                f"On device {tops.dut_name}: Error occurred while running testcase"
                f" is:\n{tops.actual_output}"
            )

        tops.test_result = tops.expected_output == tops.actual_output
        tops.parse_test_steps(self.test_port_channel_member_interface_details)
        tops.generate_report(tops.dut_name, self.output)
        assert tops.expected_output == tops.actual_output
