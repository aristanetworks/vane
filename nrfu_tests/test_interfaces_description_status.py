# Copyright (c) 2023 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.

"""
Test case for verification of interface description status.
"""

import pytest
from pyeapi.eapilib import EapiError
from vane.config import dut_objs, test_defs
from vane import tests_tools, test_case_logger

TEST_SUITE = "nrfu_tests"
logging = test_case_logger.setup_logger(__file__)


@pytest.mark.nrfu_test
@pytest.mark.interfaces
class InterfacesDescriptionStatusTests:
    """
    Test case for verification of interface description status.
    """

    dut_parameters = tests_tools.parametrize_duts(TEST_SUITE, test_defs, dut_objs)
    test_duts = dut_parameters["test_interfaces_description_status"]["duts"]
    test_ids = dut_parameters["test_interfaces_description_status"]["ids"]

    @pytest.mark.parametrize("dut", test_duts, ids=test_ids)
    def test_interfaces_description_status(self, dut, tests_definitions):
        """
        TD: Test case for verification of interface description status.
        Args:
            dut(dict): details related to a particular DUT
            tests_definitions(dict): test suite and test case parameters.
        """

        # Collecting test parameters and initializing parameters
        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)
        self.output = ""
        tops.actual_output = {
            "interfaces": {
                "descriptions_to_ignore": [],
                "descriptions_found": {},
            }
        }
        tops.expected_output = {
            "interfaces": {
                "descriptions_to_ignore": [],
                "descriptions_found": {},
            }
        }
        test_parameters = tops.test_parameters
        input_parameters = test_parameters["input"]
        descriptions_to_ignore = input_parameters["descriptions_to_ignore"]
        fail_on_no_description = input_parameters["fail_on_no_description"]
        dynamic_vlans = []
        description_not_found = []

        # Forming output message if the test result is passed
        tops.output_msg = (
            "Except for the interfaces with description to ignore, all other interfaces' status is"
            " up and have a description."
        )

        try:
            """
            TS: Running `show interfaces description` command on the device and verifying the
            interfaces have a description and their status is up.
            """
            interface_output = dut["output"][tops.show_cmds[tops.dut_name][0]]["json"]
            logging.info(
                f"On device {tops.dut_name}, output of {tops.show_cmds[tops.dut_name][0]} command"
                f" is:\n{interface_output}\n"
            )
            self.output += (
                f"\nOn device {tops.dut_name}, output of {tops.show_cmds[tops.dut_name][0]} command"
                f" is:\n{interface_output}\n"
            )

            interfaces = interface_output.get("interfaceDescriptions")
            assert interfaces, "Interfaces details are not found in the output."

            """
            TS: Running `show vlan` command on the device and collecting the dynamic vlans from the
            output.
            """
            vlan_output = dut["output"][tops.show_cmds[tops.dut_name][1]]["json"]
            logging.info(
                f"On device {tops.dut_name}, output of {tops.show_cmds[tops.dut_name][1]} command"
                f" is:\n{vlan_output}\n"
            )
            self.output += (
                f"\nOn device {tops.dut_name}, output of {tops.show_cmds[tops.dut_name][1]} command"
                f" is:\n{vlan_output}\n"
            )

            vlans = vlan_output.get("vlans", [])

            # Collecting dynamic VLANs from the output
            for vlan in vlans:
                if vlans.get(vlan, {}).get("dynamic"):
                    dynamic_vlans.append(vlan)

            for interface in interfaces:
                status = interfaces.get(interface, {}).get("interfaceStatus")
                description = interfaces.get(interface, {}).get("description")

                # Skipping the interfaces which are dynamic VLANs
                if interface.lstrip("Vlan") in dynamic_vlans:
                    continue

                # Flag to check if the description is to be ignored or not
                description_to_ignore_flag = any(
                    description_to_ignore in description.lower()
                    for description_to_ignore in descriptions_to_ignore
                )

                # Checking for the interfaces with description requirements and forming
                # expected and actual output accordingly.
                # Checking if the description needs to be ignored or not, with test case fail
                # condition
                if (description or fail_on_no_description) and not description_to_ignore_flag:
                    # Forming actual output based on whether the test case needs to fail when
                    # description is not found
                    if not description:
                        tops.expected_output["interfaces"]["descriptions_found"].update(
                            {interface: {"description_found": True}}
                        )
                        tops.actual_output["interfaces"]["descriptions_found"].update(
                            {interface: {"description_found": False}}
                        )
                    # Getting status for the interfaces whose description is found
                    else:
                        tops.expected_output["interfaces"]["descriptions_found"].update(
                            {interface: {"description": description, "status": "up"}}
                        )
                        tops.actual_output["interfaces"]["descriptions_found"].update(
                            {interface: {"description": description, "status": status}}
                        )
                elif description_to_ignore_flag or not fail_on_no_description:
                    tops.expected_output["interfaces"]["descriptions_to_ignore"].append(interface)
                    tops.actual_output["interfaces"]["descriptions_to_ignore"].append(interface)

            # Forming output message if the test result is failed
            if tops.expected_output != tops.actual_output:
                tops.output_msg = ""

                # Checking if the test case needs to fail or not, based on the description
                # requirement and forming output messages accordingly.
                for interface, interface_details in tops.expected_output["interfaces"][
                    "descriptions_found"
                ].items():
                    actual_interface_details = (
                        tops.actual_output.get("interfaces", {})
                        .get("descriptions_found", {})
                        .get(interface, {})
                    )
                    if "description" in actual_interface_details.keys():
                        actual_interface_description = actual_interface_details.get("description")
                        actual_interface_status = actual_interface_details.get("status")
                    else:
                        actual_interface_description = actual_interface_details.get(
                            "description_found"
                        )
                    expected_interface_status = interface_details.get("status")

                    if not actual_interface_description:
                        description_not_found.append(interface)
                    elif actual_interface_status != expected_interface_status:
                        tops.output_msg += (
                            f"\nFor interface {interface}, expected status is"
                            f" '{expected_interface_status}', however, actual is found as"
                            f" '{actual_interface_status}' with description"
                            f" '{actual_interface_description}'"
                        )

                if description_not_found:
                    description_not_found = ", ".join(description_not_found)
                    tops.output_msg += (
                        "\nFor the following interfaces description was expected, however, it is"
                        f" not found:\n{description_not_found}\n"
                    )

        except (AssertionError, AttributeError, LookupError, EapiError) as excep:
            tops.output_msg = tops.actual_output = str(excep).split("\n", maxsplit=1)[0]
            logging.error(
                f"On device {tops.dut_name}, Error while running the test case"
                f" is:\n{tops.actual_output}"
            )

        tops.test_result = tops.expected_output == tops.actual_output
        tops.parse_test_steps(self.test_interfaces_description_status)
        tops.generate_report(tops.dut_name, self.output)
        assert tops.expected_output == tops.actual_output
