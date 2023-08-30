# Copyright (c) 2023 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.

"""
Testcase for verification of system hardware fan status.
"""

import re
import pytest
from pyeapi.eapilib import EapiError
from vane.logger import logger
from vane.config import dut_objs, test_defs
from vane import tests_tools

TEST_SUITE = "nrfu_tests"


@pytest.mark.nrfu_test
@pytest.mark.system
class SystemHardwareFanStatusTests:
    """
    Testcase for verification of system hardware fan status.
    """

    dut_parameters = tests_tools.parametrize_duts(TEST_SUITE, test_defs, dut_objs)
    test_duts = dut_parameters["test_system_hardware_fan_status"]["duts"]
    test_ids = dut_parameters["test_system_hardware_fan_status"]["ids"]

    @pytest.mark.parametrize("dut", test_duts, ids=test_ids)
    def test_system_hardware_fan_status(self, dut, tests_definitions):
        """
        TD: Testcase for verification of system hardware fan status.
        Args:
            dut(dict): details related to a particular DUT
            tests_definitions(dict): test suite and test case parameters.
        """
        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)
        test_params = tops.test_parameters
        tops.expected_output = {"fan_status_details": {}}
        tops.actual_output = {"fan_status_details": {}}
        self.output = ""
        unstable_fans, notok_fans = {}, {}

        # forming output message if test result is passed
        tops.output_msg = "For all fans, status is ok and speed is stable."

        try:
            """
            TS: Running `show version` commands on DUT.
            Verifying the 'vEOS' device is not present in output.
            """
            show_version_command = "show version"
            output = dut["output"][show_version_command]["json"]
            logger.info(
                "On device %s, Output of %s command is: \n%s\n",
                tops.dut_name,
                show_version_command,
                output,
            )
            self.output = (
                f"on device {tops.dut_name}, output of {show_version_command} is:\n{output}"
            )
            model_name = output.get("modelName")

            # Skipping testcase if device is vEOS.
            if "vEOS" in model_name:
                pytest.skip(f"{tops.dut_name} is vEOS device, hence test skipped.")

            """
            TS: Running `show system environment cooling detail` command and verifying
            fan status and speed stability details.
            """
            output = tops.run_show_cmds([tops.show_cmd])
            logger.info(
                "On device %s, output of %s command is:\n%s\n",
                tops.dut_name,
                tops.show_cmd,
                output,
            )
            self.output = f"\nOutput of {tops.show_cmd} command is:\n{output}\n"
            power_supplies = output[0]["result"]

            # Checking power supply slot and Fan tray slot details.
            power_supply_slots = power_supplies.get("powerSupplySlots")
            fan_tray_slots = power_supplies.get("fanTraySlots")
            assert power_supply_slots, "Power supply slot details are not found."

            assert fan_tray_slots, "Fan tray slot details are not found."

            # Splitting power slots with name, and updating actual and expected output.
            for power_slots in ("powerSupplySlots", "fanTraySlots"):
                splitted_power_slots = re.sub("([A-Z])", r"_\1", power_slots).lower()
                notok_fans.update({splitted_power_slots: []})
                unstable_fans.update({splitted_power_slots: []})
                tops.expected_output["fan_status_details"].update({splitted_power_slots: {}})
                tops.actual_output["fan_status_details"].update({splitted_power_slots: {}})
                for power_supply in power_supplies.get(power_slots):
                    for fan_data in power_supply["fans"]:
                        tops.expected_output["fan_status_details"][splitted_power_slots].update(
                            {
                                fan_data["label"]: {
                                    "fan_status": "ok",
                                    "speed_stability_status": True,
                                }
                            }
                        )

                        tops.actual_output["fan_status_details"][splitted_power_slots].update(
                            {
                                fan_data["label"]: {
                                    "fan_status": fan_data["status"],
                                    "speed_stability_status": (
                                        int(fan_data["configuredSpeed"])
                                        < test_params["fan_speed_limit"]
                                    ),
                                }
                            }
                        )
                        # Collecting fan which is not stable and ok
                        if fan_data["status"] != "ok":
                            notok_fans[splitted_power_slots].append(fan_data["label"])
                        if int(fan_data["configuredSpeed"]) > test_params["fan_speed_limit"]:
                            unstable_fans[splitted_power_slots].append(fan_data["label"])

            # Forming output message if test result is fail.
            if tops.expected_output != tops.actual_output:
                tops.output_msg = "\n"
                for slots, slot_details in tops.expected_output["fan_status_details"].items():
                    if slot_details != tops.actual_output.get("fan_status_details").get(slots):
                        tops.output_msg += f"For {slots}:\n"
                    if notok_fans[slots]:
                        fan_label = ", ".join(notok_fans[slots])
                        tops.output_msg += f"State of following fans is not ok: {fan_label}.\n"
                    if unstable_fans[slots]:
                        fan_label = ", ".join(unstable_fans[slots])
                        tops.output_msg += (
                            f"Speed of following fans is not stable: {fan_label}, and their speed"
                            f" is greater than {test_params['fan_speed_limit']}.\n\n"
                        )

        except (AssertionError, AttributeError, LookupError, EapiError) as excep:
            tops.output_msg = tops.actual_output = str(excep).split("\n", maxsplit=1)[0]
            logger.error(
                "On device %s, Error while running the testcase is:\n%s",
                tops.dut_name,
                tops.actual_output,
            )

        tops.test_result = tops.expected_output == tops.actual_output
        tops.parse_test_steps(self.test_system_hardware_fan_status)
        tops.generate_report(tops.dut_name, self.output)
        assert tops.expected_output == tops.actual_output
