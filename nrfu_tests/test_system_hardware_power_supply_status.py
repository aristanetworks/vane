# Copyright (c) 2024 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.

"""
Test case for the verification of system hardware power supply status.
"""

import pytest
from pyeapi.eapilib import EapiError
from vane import tests_tools, test_case_logger
from vane.config import dut_objs, test_defs


TEST_SUITE = "nrfu_tests"
logging = test_case_logger.setup_logger(__file__)


@pytest.mark.nrfu_test
@pytest.mark.system
class SystemHardwarePowerSupplyTests:
    """
    Test case for the verification of system hardware power supply status.
    """

    dut_parameters = tests_tools.parametrize_duts(TEST_SUITE, test_defs, dut_objs)
    test_duts = dut_parameters["test_system_hardware_power_supply_status"]["duts"]
    test_ids = dut_parameters["test_system_hardware_power_supply_status"]["ids"]

    @pytest.mark.parametrize("dut", test_duts, ids=test_ids)
    def test_system_hardware_power_supply_status(self, dut, tests_definitions):
        """
        TD: Test case for the verification of system hardware power supply status.
        Args:
            dut(dict): details related to a particular DUT
            tests_definitions(dict): test suite and test case parameters.
        """

        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)
        self.output = ""
        tops.actual_output = {"power_supplies": {}}
        tops.expected_output = {"power_supplies": {}}

        # Output message if the test result is passed
        tops.output_msg = "Status of all power supplies are 'Ok'."

        try:
            """
            TS: Running `show version` command on the device and skipping the test case
            for the device if the platform is vEOS.
            """
            version_output = dut["output"]["show version"]["json"]
            logging.info(
                (
                    f"On device {tops.dut_name}: Output of 'show version' command is:"
                    f" \n{version_output}\n"
                ),
            )
            self.output += f"Output of 'show version' command is: \n{version_output}"

            # Skipping test case if the device is vEOS.
            model = version_output.get("modelName")
            if "vEOS" in model or "CCS-710P-12" in model:
                tops.output_msg = f"{tops.dut_name} is {model} device, hence test skipped."
                tests_tools.post_process_skip(
                    tops, self.test_system_hardware_power_supply_status, self.output
                )
                pytest.skip(tops.output_msg)

            """
            TS: Running `show system environment power` command on the device and
            verifying status for all power supplies should be 'OK'.
            """
            power_supplies_output = dut["output"][tops.show_cmd]["json"]
            logging.info(
                (
                    f"On device {tops.dut_name}, output of {tops.show_cmd} command is:"
                    f" \n{power_supplies_output}\n"
                ),
            )
            self.output += f"\nOutput of {tops.show_cmd} command is: \n{power_supplies_output}"
            power_supplies = power_supplies_output.get("powerSupplies")
            assert power_supplies, "Power supplies are not found on the device."

            for power_supply, power_supply_info in power_supplies.items():
                tops.expected_output["power_supplies"].update({power_supply: {"status": "ok"}})
                tops.actual_output["power_supplies"].update(
                    {power_supply: {"status": power_supply_info["state"]}}
                )

            # Forming output message in case of test case failure
            if tops.actual_output != tops.expected_output:
                bad_power_supplies = []
                for power_supply, expected_state in tops.expected_output["power_supplies"].items():
                    actual_status = tops.actual_output["power_supplies"][power_supply]
                    if actual_status == expected_state:
                        continue
                    bad_power_supplies.append(f"{power_supply}: {actual_status['status']}")

                if bad_power_supplies:
                    power_supply_status = "\n".join(bad_power_supplies)
                    tops.output_msg = (
                        "For the following power supplies status is not found as 'OK'. current"
                        f" status on them is as follows:\n{power_supply_status}"
                    )

        except (AssertionError, AttributeError, LookupError, EapiError) as excep:
            tops.output_msg = tops.actual_output = str(excep).split("\n", maxsplit=1)[0]
            logging.error(
                (
                    f"On device {tops.dut_name}, Error while running the test case"
                    f" is:\n{tops.actual_output}s"
                ),
            )

        tops.test_result = tops.expected_output == tops.actual_output
        tops.parse_test_steps(self.test_system_hardware_power_supply_status)
        tops.generate_report(tops.dut_name, self.output)
        assert tops.expected_output == tops.actual_output
