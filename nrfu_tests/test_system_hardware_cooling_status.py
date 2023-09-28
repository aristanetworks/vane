# Copyright (c) 2023 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.

"""
Testcase for the verification of system cooling status.
"""

import pytest
from pyeapi.eapilib import EapiError
from vane import tests_tools, test_case_logger
from vane.config import dut_objs, test_defs

TEST_SUITE = "nrfu_tests"
logging = test_case_logger.setup_logger(__file__)


@pytest.mark.nrfu_test
@pytest.mark.system
class SystemCoolingStatusTests:
    """
    Testcase for the verification of system cooling status.
    """

    dut_parameters = tests_tools.parametrize_duts(TEST_SUITE, test_defs, dut_objs)
    test_duts = dut_parameters["test_system_hardware_cooling_status"]["duts"]
    test_ids = dut_parameters["test_system_hardware_cooling_status"]["ids"]

    @pytest.mark.parametrize("dut", test_duts, ids=test_ids)
    def test_system_hardware_cooling_status(self, dut, tests_definitions):
        """
        TD: Testcase for the verification of system cooling status.
        Args:
            dut(dict): details related to a particular DUT
            tests_definitions(dict): test suite and test case parameters.
        """
        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)
        tops.actual_output = {}
        self.output = ""

        # forming output message if test result is passed
        tops.output_msg = "System cooling status is 'coolingOk'"

        try:
            """
            TS: Running `show version` command on device and skipping the test case
            for device if platform is vEOS.
            """
            version_output = dut["output"]["show version"]["json"]
            logging.info(
                (
                    f"On device {tops.dut_name}: Output of 'show version' command is:"
                    f" \n{version_output}\n"
                ),
            )
            self.output += f"Output of 'show version' command is: \n{version_output}"

            # Skipping testcase if device is vEOS.
            if "vEOS" in version_output.get("modelName"):
                pytest.skip(f"{tops.dut_name} is vEOS device, hence test is skipped.")

            """
            TS: Running `show system environment cooling` command and verifying
            system status is ok.
            """
            output = dut["output"][tops.show_cmd]["json"]

            logging.info(
                f"On device {tops.dut_name}, output of {tops.show_cmd} command is:\n{output}\n",
            )

            self.output += f"Output of {tops.show_cmd} command is: \n{output}"
            system_cooling_status = output.get("systemStatus")
            ambient_temperature = output.get("ambientTemperature")
            tops.actual_output.update({"system_cooling_status": system_cooling_status})

            if tops.actual_output != tops.expected_output:
                tops.output_msg = (
                    "System cooling status is not ok. Ambient Temperature: "
                    f"{format(ambient_temperature,'.2f')} C'"
                )

        except (AttributeError, LookupError, EapiError) as excep:
            tops.output_msg = tops.actual_output = str(excep).split("\n", maxsplit=1)[0]
            logging.error(
                (
                    f"On device {tops.dut_name}, Error while running the testcase"
                    f" is:\n{tops.actual_output}"
                ),
            )

        tops.test_result = tops.expected_output == tops.actual_output
        tops.parse_test_steps(self.test_system_hardware_cooling_status)
        tops.generate_report(tops.dut_name, self.output)
        assert tops.expected_output == tops.actual_output
