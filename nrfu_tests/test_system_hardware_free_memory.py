# Copyright (c) 2022 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.

"""
Test cases for verification of system hardware free memory functionality
"""

import pytest
from pyeapi.eapilib import EapiError
from vane.logger import logger
from vane.config import dut_objs, test_defs
from vane import tests_tools

TEST_SUITE = "nrfu_tests"


@pytest.mark.nrfu_test
@pytest.mark.system
class SystemHardwareFreeMemoryTests:
    """
    Test cases for verification of system hardware free memory functionality
    """

    dut_parameters = tests_tools.parametrize_duts(TEST_SUITE, test_defs, dut_objs)
    test_duts = dut_parameters["test_system_hardware_free_memory"]["duts"]
    test_ids = dut_parameters["test_system_hardware_free_memory"]["ids"]

    @pytest.mark.parametrize("dut", test_duts, ids=test_ids)
    def test_system_hardware_free_memory(self, dut, tests_definitions):
        """
        TD: Testcase for verification of system hardware free memory functionality.
        Args:
            dut(dict): details related to a particular DUT
            tests_definitions(dict): test suite and test case parameters
        """
        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)
        self.output = ""
        test_params = tops.test_parameters
        tops.actual_output = {}

        # Forming output message if test result is passed
        tops.output_msg = (
            "The expected memory utilization percentage of the device is less than"
            f" {test_params['verification_value']}%."
        )

        try:
            """
            TS: Running 'show version' command on DUT and verifying the free memory percentage.
            """
            output = dut["output"][tops.show_cmd]["json"]
            logger.info(
                "On device %s, output of %s command is: \n%s\n",
                tops.dut_name,
                tops.show_cmd,
                output,
            )
            self.output += f"\nOutput of {tops.show_cmd} command is: \n{output}"

            memory_total, memory_free = output["memTotal"], output["memFree"]
            memory_utilization = round(100 - int(memory_free) / int(memory_total) * 100, 2)
            actual_memory_utilization = memory_utilization > test_params["verification_value"]
            tops.actual_output.update({"memory_utilization": actual_memory_utilization})

            # Output message formation in case of testcase fails.
            if tops.actual_output != tops.expected_output:
                tops.output_msg = ""
                if not tops.actual_output["memory_utilization"]:
                    tops.output_msg += (
                        "The expected memory utilization percentage of the device is not less than"
                        f" {test_params['verification_value']}%."
                    )

        except (AttributeError, LookupError, EapiError) as excep:
            tops.output_msg = tops.actual_output = str(excep).split("\n", maxsplit=1)[0]
            logger.error(
                "On device %s, Error while running the testcase is:\n%s",
                tops.dut_name,
                tops.actual_output,
            )

        tops.test_result = tops.expected_output == tops.actual_output
        tops.parse_test_steps(self.test_system_hardware_free_memory)
        tops.generate_report(tops.dut_name, self.output)
        assert tops.expected_output == tops.actual_output
