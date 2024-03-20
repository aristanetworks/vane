# Copyright (c) 2024 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.

"""
Test case for verification of system temperature sensors
"""

import pytest
from pyeapi.eapilib import EapiError
from vane import tests_tools, test_case_logger
from vane.config import dut_objs, test_defs

TEST_SUITE = "nrfu_tests"
logging = test_case_logger.setup_logger(__file__)


@pytest.mark.nrfu_test
@pytest.mark.system
class SystemHardwareTemperatureTests:
    """
    Test case for verification of system temperature sensors
    """

    def get_sensor_detail(self, sensor_detail, temp_sensor=False):
        """
        Utility to get temperature and hardware status for power supply and temperature sensors
        Args:
            sensor_detail(dict): Power supply and temperature sensor details.
            temp_sensor(bool): Flag to check the hardware status of the temperature sensor.
            If it is set to True then the hardware status for a particular sensor will check
        Return:
            dict: Actual output of hardware status
            dict: Current and overheat threshold temperature detail for power supply
            and temperature sensors
        """
        actual_output = {}
        temperature_details = {}
        current_temperature = sensor_detail["currentTemperature"]
        threshold_temperature = sensor_detail["overheatThreshold"]
        actual_output["overheat_threshold_met"] = current_temperature + 5 >= threshold_temperature

        temperature_details.update(
            {
                "current_temperature": current_temperature,
                "threshold_temperature": threshold_temperature,
            }
        )
        if temp_sensor:
            actual_output["hardware_status"] = sensor_detail["hwStatus"]

        return actual_output, temperature_details

    def get_output_message_for_system_temperature_sensors(
        self, actual_output, expected_output, current_threshold_temp_detail
    ):
        """
        Utility to get failure error output message for system temperature sensors
        Args:
            actual_output(dict): Actual output of test case
            expected_output(dict): Expected output of test case
            current_threshold_temp_detail(dict): Current and threshold temperature details
            for power supply and temperature sensors
        Return:
            (string): Output message for test case failure scenario. This message will be
            added in the observation section of the docx report
        """

        output_msg = ""
        if expected_output["system_status"] != actual_output["system_status"]:
            output_msg += (
                f"\nExpected system status is '{expected_output['system_status']}'"
                " however in actual it is found as "
                f"'{actual_output['system_status']}'.\n"
            )

        if expected_output.get("power_supplies_sensors") != actual_output.get(
            "power_supplies_sensors"
        ):
            for sensor, sensor_details in expected_output.get("power_supplies_sensors").items():
                actual_sensor_details = actual_output.get("power_supplies_sensors").get(sensor)
                if sensor_details == actual_sensor_details:
                    continue
                output_msg += (
                    f"\nFor {sensor.replace('_', ' ')}, following sensors are in erroneous state:\n"
                )

                for sensor_detail, expected_sensor_details in sensor_details.items():
                    actual_sensor_info = actual_sensor_details.get(sensor_detail)
                    temperature_detail = (
                        current_threshold_temp_detail["power_supplies_sensors"]
                        .get(sensor)
                        .get(sensor_detail)
                    )
                    if expected_sensor_details == actual_sensor_info:
                        continue
                    output_msg += f"{sensor_detail}:"
                    if (
                        expected_sensor_details["hardware_status"]
                        != actual_sensor_info["hardware_status"]
                    ):
                        output_msg += (
                            " Expected hardware status should be"
                            f" '{expected_sensor_details['hardware_status']}' however in actual it"
                            f" is found as '{actual_sensor_info['hardware_status']}'\n"
                        )
                        continue
                    output_msg += (
                        " Current sensor temperature is"
                        f" '{temperature_detail['current_temperature']}(c)' which is greater"
                        " than threshold temperature"
                        f" '{temperature_detail['threshold_temperature']}(c)'\n"
                    )

        if expected_output.get("temperature_sensors") != actual_output.get("temperature_sensors"):
            temperature_msgs = []
            for sensor, sensor_details in expected_output.get("temperature_sensors").items():
                actual_sensor_details = actual_output["temperature_sensors"].get(sensor)
                if actual_sensor_details["overheat_threshold_met"]:
                    temperature_detail = current_threshold_temp_detail["temperature_sensors"].get(
                        sensor
                    )
                    temperature_msgs.append(
                        f"{sensor}: Current sensor temperature is"
                        f" '{temperature_detail['current_temperature']}(c)' which is greater"
                        " than threshold temperature"
                        f" '{temperature_detail['threshold_temperature']}(c)'.\n"
                    )
            if temperature_msgs:
                output_msg += f"\nFor Temperature sensors:\n{''.join(temperature_msgs)}"

        return output_msg

    dut_parameters = tests_tools.parametrize_duts(TEST_SUITE, test_defs, dut_objs)
    test_duts = dut_parameters["test_system_temperature_sensors"]["duts"]
    test_ids = dut_parameters["test_system_temperature_sensors"]["ids"]

    @pytest.mark.parametrize("dut", test_duts, ids=test_ids)
    def test_system_temperature_sensors(self, dut, tests_definitions):
        """
        TD: Test case for verification of system temperature sensors
        Args:
            dut(dict): details related to a particular DUT
            tests_definitions(dict): test suite and test case parameters.
        """
        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)
        self.output = ""
        tops.expected_output = {"power_supplies_sensors": {}, "temperature_sensors": {}}
        tops.actual_output = {"power_supplies_sensors": {}, "temperature_sensors": {}}

        # Forming output message if the test result is passed
        tops.output_msg = (
            "System temperature is 'ok'. Hardware status of all sensors are 'ok' and overheat"
            " threshold are not met."
        )

        try:
            """
            TS: Running "show version" commands on DUT.
            Verifying the 'vEOS' device is not present in the output.
            """
            self.version_output = dut["output"]["show version"]["json"]
            logging.info(
                (
                    f"On device {tops.dut_name}, Output of 'show version' command is:"
                    f" \n{self.version_output}\n"
                ),
            )
            self.output += f"\nOutput of 'show version' command is: \n{self.version_output}"

            # Skipping test case if the device is vEOS.
            model = self.version_output.get("modelName")
            if "vEOS" in model or "7010" in model:
                tops.output_msg = f"Skipping test case on {tops.dut_name} as it is {model} device."
                tests_tools.post_process_skip(
                    tops, self.test_system_temperature_sensors, self.output
                )
                pytest.skip(tops.output_msg)

            """
            TS: Running the "show system environment temperature" command on DUT and
            Verifying the system status, power supply sensors and temperature sensors details
            are present in the output.
            """
            output = dut["output"][tops.show_cmd]["json"]
            logging.info(
                f"On device {tops.dut_name}, output of {tops.show_cmd} command is: \n{output}\n",
            )
            self.output += f"\n\nOutput of {tops.show_cmd} command is: \n{output}"
            power_supplies_sensors = output.get("powerSupplySlots")
            temperature_sensors = output.get("tempSensors")
            assert (
                power_supplies_sensors
            ), "Power supplies sensor details are not found on the device."
            assert temperature_sensors, "Temperature sensors detail are not found on the device."

            tops.expected_output.update({"system_status": "temperatureOk"})
            tops.actual_output.update({"system_status": output.get("systemStatus")})
            current_threshold_temp_detail = {
                "power_supplies_sensors": {},
                "temperature_sensors": {},
            }

            # Checking for hardware status, current and threshold temperature details
            # for power supply sensors
            for sensor in power_supplies_sensors:
                tops.expected_output["power_supplies_sensors"][
                    f"power_supplies_slot_{sensor['relPos']}"
                ] = {}
                tops.actual_output["power_supplies_sensors"][
                    f"power_supplies_slot_{sensor['relPos']}"
                ] = {}
                current_threshold_temp_detail["power_supplies_sensors"][
                    f"power_supplies_slot_{sensor['relPos']}"
                ] = {}

                for sensor_detail in sensor["tempSensors"]:
                    name = sensor_detail["name"]
                    tops.expected_output["power_supplies_sensors"][
                        f"power_supplies_slot_{sensor['relPos']}"
                    ].update({name: {"hardware_status": "ok", "overheat_threshold_met": False}})
                    actual_sensor_detail, temperature_details = self.get_sensor_detail(
                        sensor_detail, temp_sensor=True
                    )

                    tops.actual_output["power_supplies_sensors"][
                        f"power_supplies_slot_{sensor['relPos']}"
                    ].update({name: actual_sensor_detail})
                    current_threshold_temp_detail["power_supplies_sensors"][
                        f"power_supplies_slot_{sensor['relPos']}"
                    ][name] = temperature_details

            # Checking for current and threshold temperature details
            # for temperature sensors
            for sensor_detail in temperature_sensors:
                if "PhyAlaska" not in sensor_detail["description"]:
                    tops.expected_output["temperature_sensors"][sensor_detail["name"]] = {
                        "overheat_threshold_met": False
                    }
                    actual_sensor_detail, temperature_details = self.get_sensor_detail(
                        sensor_detail, temp_sensor=False
                    )
                    tops.actual_output["temperature_sensors"][
                        sensor_detail["name"]
                    ] = actual_sensor_detail
                    current_threshold_temp_detail["temperature_sensors"][
                        sensor_detail["name"]
                    ] = temperature_details

            # Forming output message in case of test case failure
            if tops.actual_output != tops.expected_output:
                tops.output_msg = self.get_output_message_for_system_temperature_sensors(
                    tops.actual_output, tops.expected_output, current_threshold_temp_detail
                )

        except (AssertionError, AttributeError, LookupError, EapiError) as excep:
            tops.output_msg = tops.actual_output = str(excep).split("\n", maxsplit=1)[0]
            logging.error(
                f"On device {tops.dut_name}, Error while running the test case"
                f" is:\n{tops.actual_output}"
            )

        tops.test_result = tops.expected_output == tops.actual_output
        tops.parse_test_steps(self.test_system_temperature_sensors)
        tops.generate_report(tops.dut_name, self.output)
        assert tops.expected_output == tops.actual_output
