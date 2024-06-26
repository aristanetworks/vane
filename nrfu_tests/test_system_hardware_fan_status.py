# Copyright (c) 2024 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.

"""
Testcase for verification of fan status in the system.
"""

import re
import pytest
from pyeapi.eapilib import EapiError
from vane.config import dut_objs, test_defs
from vane import tests_tools, test_case_logger

TEST_SUITE = "nrfu_tests"
logging = test_case_logger.setup_logger(__file__)


@pytest.mark.nrfu_test
@pytest.mark.system
class SystemHardwareFanStatusTests:
    """
    Testcase for verification of fan status in the system.
    """

    dut_parameters = tests_tools.parametrize_duts(TEST_SUITE, test_defs, dut_objs)
    test_duts = dut_parameters["test_system_hardware_fan_status"]["duts"]
    test_ids = dut_parameters["test_system_hardware_fan_status"]["ids"]

    @pytest.mark.parametrize("dut", test_duts, ids=test_ids)
    def test_system_hardware_fan_status(self, dut, tests_definitions):
        """
        TD: Testcase for verification of fan status in the system.
        Args:
            dut(dict): details related to a particular DUT
            tests_definitions(dict): test suite and test case parameters.
        """
        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)
        tops.expected_output = {"fans_slots": {}}
        tops.actual_output = {"fans_slots": {}}
        self.output = ""
        fan_speed_details = {}

        # Forming output message if the test result is passed.
        tops.output_msg = "For all fans, status is ok and speed is stable."

        try:
            """
            TS: Running `show version` command on the device and skipping the test case if device
            platform is 'vEOS'.
            """
            self.show_version_command = "show version"
            output = dut["output"][self.show_version_command]["json"]
            logging.info(
                f"On device {tops.dut_name}, Output of {self.show_version_command} command is:"
                f" \n{output}\n"
            )
            self.output = (
                f"on device {tops.dut_name}, output of {self.show_version_command} is:\n{output}"
            )

            # Skipping test case if the device is vEOS.
            model = output.get("modelName")
            if "vEOS" in model or "CCS-710" in model:
                tops.output_msg = f"{tops.dut_name} is {model} device, hence test skipped."
                tests_tools.post_process_skip(
                    tops, self.test_system_hardware_fan_status, self.output
                )
                pytest.skip(tops.output_msg)

            """
            TS: Running `show system environment cooling` command and verifying
            fan status and speed stability details.
            """
            output = tops.run_show_cmds([tops.show_cmd])
            logging.info(
                f"On device {tops.dut_name}, output of {tops.show_cmd} command is:\n{output}\n"
            )
            self.output = f"\nOutput of {tops.show_cmd} command is:\n{output}\n"
            self.fan_slot_details = output[0]["result"]

            # Checking power supply slot and Fan tray slot details.
            self.power_supply_slots = self.fan_slot_details.get("powerSupplySlots")
            self.fan_tray_slots = self.fan_slot_details.get("fanTraySlots")
            if "7010" not in model:
                assert (
                    self.power_supply_slots
                ), "Power supply slot details are not found in the output."

            assert self.fan_tray_slots, "Fan tray slot details are not found in the output."

            # Collecting actual and expected output.
            for fans_slots in ("powerSupplySlots", "fanTraySlots"):
                # Converting fan slot name from camel case.
                converted_slot_name = re.sub("([A-Z])", r"_\1", fans_slots).lower()
                tops.expected_output["fans_slots"].update({converted_slot_name: {}})
                tops.actual_output["fans_slots"].update({converted_slot_name: {}})

                for fan_details in self.fan_slot_details.get(fans_slots):
                    for fan_data in fan_details["fans"]:
                        tops.expected_output["fans_slots"][converted_slot_name].update(
                            {
                                fan_data["label"]: {
                                    "fan_status": "ok",
                                    "speed_stability_status": True,
                                }
                            }
                        )

                        if fan_data.get("configuredSpeed"):
                            fan_stability = int(fan_data.get("configuredSpeed")) < 80
                        else:
                            fan_stability = None
                        tops.actual_output["fans_slots"][converted_slot_name].update(
                            {
                                fan_data["label"]: {
                                    "fan_status": fan_data["status"],
                                    "speed_stability_status": fan_stability,
                                }
                            }
                        )
                        fan_speed_details.update({fan_data["label"]: fan_data["configuredSpeed"]})

            # Forming output message if the test result is failed.
            if tops.expected_output != tops.actual_output:
                tops.output_msg = "\nFollowing power supply slots, fans are in erroneous state :\n"
                for slots, slot_details in tops.expected_output["fans_slots"].items():
                    if slot_details != tops.actual_output["fans_slots"].get(slots):
                        tops.output_msg += f"For {slots.replace('_', ' ')}:\n"
                        for fan_label, fan_details in slot_details.items():
                            for fan_status_key, fan_status_value in fan_details.items():
                                actual_fan_status = (
                                    tops.actual_output["fans_slots"]
                                    .get(slots)
                                    .get(fan_label)
                                    .get(fan_status_key)
                                )
                                if fan_status_value != actual_fan_status:
                                    if actual_fan_status is None:
                                        tops.output_msg += f"{fan_label}: Fan status is 'Not ok'.\n"
                                    else:
                                        if fan_status_key == "speed_stability_status" and (
                                            int(fan_speed_details[fan_label]) > 80
                                        ):
                                            tops.output_msg += (
                                                f"{fan_label}: Fan status is 'ok', however current"
                                                f" fan speed '{fan_speed_details.get(fan_label)}'"
                                                " is higher than the threshold fan speed '80'.\n"
                                            )
                    tops.output_msg += "\n"

        except (AssertionError, AttributeError, LookupError, EapiError) as excep:
            tops.output_msg = tops.actual_output = str(excep).split("\n", maxsplit=1)[0]
            logging.error(
                (
                    f"On device {tops.dut_name}, Error while running the testcase"
                    f" is:\n{tops.actual_output}"
                ),
            )

        tops.test_result = tops.expected_output == tops.actual_output
        tops.parse_test_steps(self.test_system_hardware_fan_status)
        tops.generate_report(tops.dut_name, self.output)
        assert tops.expected_output == tops.actual_output
