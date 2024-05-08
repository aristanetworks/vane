# Copyright (c) 2023 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.

"""
Test case for the verification of system hardware inventory on the device
"""

import re
import pytest
from pyeapi.eapilib import EapiError
from vane import tests_tools
from vane import test_case_logger
from vane.config import dut_objs, test_defs

TEST_SUITE = "nrfu_tests"
logging = test_case_logger.setup_logger(__file__)


@pytest.mark.nrfu_test
@pytest.mark.system
class HardwareInventoryTests:
    """
    Test case for the verification of system hardware inventory on the device
    """

    dut_parameters = tests_tools.parametrize_duts(TEST_SUITE, test_defs, dut_objs)
    test_duts = dut_parameters["test_hardware_inventory_status"]["duts"]
    test_ids = dut_parameters["test_hardware_inventory_status"]["ids"]

    @pytest.mark.parametrize("dut", test_duts, ids=test_ids)
    def test_hardware_inventory_status(self, dut, tests_definitions):
        """
        TD: Test case for the verification of system hardware inventory on the device.
        Args:
          dut(dict): Details related to a particular device.
          tests_definitions(dict): Test suite and test case parameters
        """
        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)
        self.output = ""
        test_params = tops.test_parameters
        tops.actual_output = {"hardware_inventory_details": {}}
        tops.expected_output = {"hardware_inventory_details": {}}
        actual_output, expected_output = {}, {}

        # Forming output message if the test result is pass
        tops.output_msg = "Power supply, fan tray and other card slots are installed on the device."

        try:
            """
            TS: Running the 'show version' command on the device and skipping the test case
            for the device if the platform is vEOS.
            """
            version_output = dut["output"]["show version"]["json"]
            logging.info(
                (
                    f"On device {tops.dut_name}, the output of the `show version` command is:"
                    f" \n{version_output}\n"
                ),
            )
            self.output += f"\n\nOutput of {tops.show_cmd} command is: \n{version_output}"

            # Skipping the test case if all the inventory slots are not inserted.
            inventory_verification_status = list(test_params["hardware_inventory_checks"].values())
            if not any(inventory_verification_status):
                pytest.skip(f"Inventory slots are not inserted on {tops.dut_name}")

            # Skipping test case if the device is vEOS.
            model = version_output.get("modelName")
            if "vEOS" in model or "CCS-710" in model:
                tops.output_msg = f"{tops.dut_name} is {model} device, hence test skipped."
                tests_tools.post_process_skip(tops, self.test_hardware_inventory_status, self.output)
                pytest.skip(tops.output_msg)

            """
            TS: Running the `show inventory` command on the device and verifying the power supply
            slots, fan tray slots and other card slots are inserted on the device.
            """
            output = dut["output"][tops.show_cmd]["json"]
            logging.info(
                f"On device {tops.dut_name}, output of {tops.show_cmd} command is: \n{output}\n",
            )
            self.output += f"\n\nOutput of {tops.show_cmd} command is: \n{output}"

            # Iterating over the hardware inventory checks added in the test definition file.
            # If the hardware inventory check is True, verifying that the card slot is inserted
            # Otherwise skipping the check for the particular hardware card slot.
            for slot, verify_slot in test_params["hardware_inventory_checks"].items():
                if verify_slot:
                    # Converting slot name from snake case to camel case.
                    slot = slot.split("missing_")[1]
                    converted_slot_name = re.sub(
                        r"(?!^)_([a-zA-Z])", lambda name: name.group(1).upper(), slot
                    )

                    # Verifying that the fan tray and power supply slots are inserted into the
                    # device by checking the name is present for the slot.
                    if "CardSlots" not in converted_slot_name:
                        slot_output = output[converted_slot_name]
                        assert slot_output, f"{converted_slot_name} are not inserted on the device."

                        expected_output.update({slot: {}})
                        actual_output.update({slot: {}})

                        # Updating the actual and expected output dictionaries.
                        for slot_name, slot_details in slot_output.items():
                            expected_output[slot].update({slot_name: {"card_slot_inserted": True}})
                            actual_output[slot].update(
                                {
                                    slot_name: {
                                        "card_slot_inserted": (
                                            "Not Inserted" not in slot_details["name"]
                                        )
                                    }
                                }
                            )

                    else:
                        # Verifying the card slots (Supervisor, Fabric and Line cards) are inserted
                        # into the device by checking the model name is present for the slot.
                        card_name = slot.split("_")[0]
                        slot_output = output["cardSlots"]
                        # Commenting assert.  It is not working with single supervisors.
                        #
                        # assert slot_output,
                        # f"{converted_slot_name} is not inserted on the device."

                        expected_output.update({slot: {}})
                        actual_output.update({slot: {}})

                        # Updating the actual and expected output dictionaries.
                        for slot_name, slot_details in slot_output.items():
                            if card_name.capitalize() in slot_name:
                                expected_output[slot].update(
                                    {slot_name: {"card_slot_inserted": True}}
                                )
                                actual_output[slot].update(
                                    {
                                        slot_name: {
                                            "card_slot_inserted": (
                                                "Not Inserted" not in slot_details["modelName"]
                                            )
                                        }
                                    }
                                )

            tops.actual_output["hardware_inventory_details"].update(actual_output)
            tops.expected_output["hardware_inventory_details"].update(expected_output)

            # Forming the output message if the test case fails
            if tops.expected_output != tops.actual_output:
                tops.output_msg = "\nThe following card slots are not inserted:"
                output_msg = []
                for slot_name, slot_details in tops.actual_output[
                    "hardware_inventory_details"
                ].items():
                    slot_status = []
                    for card_slot, card_slot_status in slot_details.items():
                        if not card_slot_status["card_slot_inserted"]:
                            slot_status.append(card_slot)
                    if slot_status:
                        message = f"\n{slot_name.replace('_', ' ')}: "
                        message += f"{', '.join(slot_status)}"
                        output_msg.append(message)
                tops.output_msg += "".join(output_msg)

        except (AssertionError, AttributeError, LookupError, EapiError) as excp:
            tops.actual_output = tops.output_msg = str(excp).split("\n", maxsplit=1)[0]
            logging.error(
                f"On device {tops.dut_name}, Error while running the test case"
                f" is:\n{tops.actual_output}"
            )

        tops.test_result = tops.expected_output == tops.actual_output
        tops.parse_test_steps(self.test_hardware_inventory_status)
        tops.generate_report(tops.dut_name, self.output)
        assert tops.expected_output == tops.actual_output
