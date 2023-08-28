# Copyright (c) 2023 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.

"""
Test case for verification of system power supply voltage sensor status on the device.
"""

import pytest
from pyeapi.eapilib import EapiError
from vane.logger import logger
from vane.config import dut_objs, test_defs
from vane import tests_tools


TEST_SUITE = "nrfu_tests"


@pytest.mark.nrfu_test
@pytest.mark.system
class PowerSupplyVoltageTests:
    """
    Test case for verification of system power supply voltage sensor status on the device.
    """

    dut_parameters = tests_tools.parametrize_duts(TEST_SUITE, test_defs, dut_objs)
    test_duts = dut_parameters["test_system_hardware_power_supply_voltage_status"]["duts"]
    test_ids = dut_parameters["test_system_hardware_power_supply_voltage_status"]["ids"]

    @pytest.mark.parametrize("dut", test_duts, ids=test_ids)
    def test_system_hardware_power_supply_voltage_status(self, dut, tests_definitions):
        """
        TD: Test case for verification of system power supply voltage sensor status on the device.
        Args:
            dut(dict): details related to a particular DUT
            tests_definitions(dict): test suite and test case parameters.
        """

        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)
        self.output = ""
        tops.actual_output = {"power_supply_voltage_sensors": {}}
        tops.expected_output = {"power_supply_voltage_sensors": {}}

        # Output message if test result is passed
        tops.output_msg = "Status of all power supply voltage sensors is 'Ok'"

        try:
            """
            TS: Running 'show version' command on device and skipping the test case
            for device if platform is vEOS.
            """
            version_output = dut["output"]["show version"]["json"]
            logger.info(
                "On device %s, output of show version command is:\n%s\n",
                tops.dut_name,
                version_output,
            )
            self.output += f"\nOutput of {tops.show_cmd} command is:\n{version_output}\n"

            # Skipping testcase if device is vEOS.
            if "vEOS" in version_output.get("modelName"):
                pytest.skip(f"{tops.dut_name} is vEOS device, hence test skipped.")

            """
            TS: Running `show system environment power voltage` command on the device and
            verifying status for all power supply voltage sensor should be 'OK'.
            """
            power_supply_cmd = "show system environment power voltage"
            voltage_cmd_output = tops.run_show_cmds([power_supply_cmd])
            logger.info(
                "On device %s, output of %s command is: \n%s\n",
                tops.dut_name,
                power_supply_cmd,
                voltage_cmd_output,
            )
            self.output += f"\nOutput of {power_supply_cmd} command is:\n{voltage_cmd_output}\n"
            voltage_sensors = voltage_cmd_output[0]["result"].get("voltageSensors")

            # Collecting power supply sensors from list of sensor
            power_voltage_sensor = [
                {sensor: sensor_data}
                for sensor, sensor_data in voltage_sensors.items()
                if "PowerSupply" in sensor
            ]
            assert (
                power_voltage_sensor
            ), "Power supply voltage sensor details are not found on the device."

            # Updating actual and expected state of power supply sensor
            for voltage_sensor in power_voltage_sensor:
                for sensor, sensor_data in voltage_sensor.items():
                    tops.expected_output["power_supply_voltage_sensors"].update({sensor: "ok"})
                    tops.actual_output["power_supply_voltage_sensors"].update(
                        {sensor: sensor_data.get("status")}
                    )

            # Forming output message in case of test case failure
            if tops.output_msg != tops.expected_output:
                unhealthy_power_supplies = []
                for power_supply_sensor, expected_status in tops.expected_output[
                    "power_supply_voltage_sensors"
                ].items():
                    actual_status = tops.actual_output["power_supply_voltage_sensors"][
                        power_supply_sensor
                    ]
                    if actual_status == expected_status:
                        continue
                    unhealthy_power_supplies.append(f"{power_supply_sensor} - {actual_status}")
                if unhealthy_power_supplies:
                    power_supply_status = "\n".join(unhealthy_power_supplies)
                    tops.output_msg = (
                        "Status for following power supply voltage sensors is not found as 'OK'"
                        f" and current status on them is found as follows:\n{power_supply_status}"
                    )

        except (AssertionError, AttributeError, LookupError, EapiError) as excep:
            tops.output_msg = tops.actual_output = str(excep).split("\n", maxsplit=1)[0]
            logger.error(
                "On device %s, Error while running the testcase is:\n%s",
                tops.dut_name,
                tops.actual_output,
            )

        tops.test_result = tops.expected_output == tops.actual_output
        tops.parse_test_steps(self.test_system_hardware_power_supply_voltage_status)
        tops.generate_report(tops.dut_name, self.output)
        assert tops.expected_output == tops.actual_output
