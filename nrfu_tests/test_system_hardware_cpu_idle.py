# Copyright (c) 2023 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.

"""
Testcase for verification of system hardware CPU idle time
"""

import pytest
from pyeapi.eapilib import EapiError
from vane.config import dut_objs, test_defs
from vane import tests_tools, test_case_logger

TEST_SUITE = "nrfu_tests"
logging = test_case_logger.setup_logger(__file__)


@pytest.mark.system
@pytest.mark.nrfu_test
class CpuIdleTimeTests:
    """
    Testcase for verification of system hardware CPU idle time.
    """

    dut_parameters = tests_tools.parametrize_duts(TEST_SUITE, test_defs, dut_objs)
    test_duts = dut_parameters["test_system_cpu_idle_time"]["duts"]
    test_ids = dut_parameters["test_system_cpu_idle_time"]["ids"]

    @pytest.mark.parametrize("dut", test_duts, ids=test_ids)
    def test_system_cpu_idle_time(self, dut, tests_definitions):
        """
        TD: Testcase for verification of system hardware CPU idle time.
        Args:
            dut(dict): details related to a particular DUT
            tests_definitions(dict): test suite and test case parameters.
        """
        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)
        tops.actual_output = {}
        self.output = ""

        # Forming output message if test result is passed
        tops.output_msg = "CPU idle time is within the expected range."

        try:
            """
            TS: Running `show processes top once` command and verifying CPU idle time is within
            expected range.
            """
            output = dut["output"][tops.show_cmd]["json"]
            logging.info(
                f"On device {tops.dut_name}, output of {tops.show_cmd} command is:\n{output}\n"
            )
            self.output += f"Output of {tops.show_cmd} command is:\n{output}\n"
            cpu_idle_details = output.get("cpuInfo").get("%Cpu(s)").get("idle")

            # Skipping testcase if CPU idle time is not configured on device.
            if not cpu_idle_details:
                pytest.skip(f"CPU idle time is not configured on device {tops.dut_name}.")

            # Verifying CPU idle time and updating in actual output.
            if cpu_idle_details < 25:
                cpu_idle_time_found = False
            else:
                cpu_idle_time_found = True
            tops.actual_output = {"cpu_idle_time_within_range": cpu_idle_time_found}

            # Output message formation in case of testcase fails.
            if tops.actual_output != tops.expected_output:
                tops.output_msg = (
                    "CPU idle time is not correct. Expected idle time is above "
                    "25 seconds however in actual found as "
                    f"{cpu_idle_details} seconds."
                )

        except (AttributeError, LookupError, EapiError) as excep:
            tops.output_msg = tops.actual_output = str(excep).split("\n", maxsplit=1)[0]
            logging.error(
                f"On device {tops.dut_name}, Error while running testcase is:\n{tops.actual_output}"
            )

        tops.test_result = tops.actual_output == tops.expected_output
        tops.parse_test_steps(self.test_system_cpu_idle_time)
        tops.generate_report(tops.dut_name, self.output)
        assert tops.actual_output == tops.expected_output
