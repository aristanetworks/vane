# Copyright (c) 2023 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.

"""
Test case for verification of system hardware-free memory utilization
"""

import pytest
from pyeapi.eapilib import EapiError
from vane.config import dut_objs, test_defs
from vane import tests_tools, test_case_logger

TEST_SUITE = "nrfu_tests"
logging = test_case_logger.setup_logger(__file__)


@pytest.mark.nrfu_test
@pytest.mark.system
class FreeMemoryTests:
    """
    Test case for verification of system hardware-free memory utilization
    """

    dut_parameters = tests_tools.parametrize_duts(TEST_SUITE, test_defs, dut_objs)
    test_duts = dut_parameters["test_system_free_memory"]["duts"]
    test_ids = dut_parameters["test_system_free_memory"]["ids"]

    @pytest.mark.parametrize("dut", test_duts, ids=test_ids)
    def test_system_free_memory(self, dut, tests_definitions):
        """
        TD: Test case for verification of system hardware-free memory utilization.
        Args:
            dut(dict): details related to a particular DUT
            tests_definitions(dict): test suite and test case parameters
        """
        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)
        self.output = ""
        tops.actual_output = {}

        try:
            """
            TS: Running 'show version' command on DUT and verifying the free memory percentage.
            """
            version_output = dut["output"]["show version"]["json"]
            logging.info(
                (
                    f"On device {tops.dut_name}, output of show version command"
                    f" is:\n{version_output}\n"
                ),
            )
            self.output += f"\nOutput of {tops.show_cmd} command is:\n{version_output}\n"

            memory_total, memory_free = version_output["memTotal"], version_output["memFree"]
            memory_utilization = round(100 - int(memory_free) / int(memory_total) * 100, 2)

            # Forming output message if the test result is passed
            tops.output_msg = (
                f"Memory utilization percentage of the device is {memory_utilization}%."
            )
            actual_memory_utilization = memory_utilization < 70
            tops.actual_output.update({"memory_utilization_under_range": actual_memory_utilization})

            # Output message formation in case of test case fails.
            if tops.actual_output != tops.expected_output:
                tops.output_msg = (
                    "Memory utilization on the device is not correct. Expected memory utilization"
                    f" is below '70%' however, in actual found as '{memory_utilization}%'."
                )

        except (AttributeError, LookupError, EapiError) as excep:
            tops.output_msg = tops.actual_output = str(excep).split("\n", maxsplit=1)[0]
            logging.error(
                (
                    f"On device {tops.dut_name}, Error while running the test case"
                    f" is:\n{tops.actual_output}"
                ),
            )

        tops.test_result = tops.expected_output == tops.actual_output
        tops.parse_test_steps(self.test_system_free_memory)
        tops.generate_report(tops.dut_name, self.output)
        assert tops.expected_output == tops.actual_output
