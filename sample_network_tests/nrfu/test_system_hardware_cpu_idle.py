# Copyright (c) 2023 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.

"""Testcase for verification of cpu idle time."""

import pytest
from pyeapi.eapilib import EapiError
from vane.logger import logger
from vane.config import dut_objs, test_defs
from vane import tests_tools

TEST_SUITE = "sample_network_tests"


@pytest.mark.system
@pytest.mark.nrfu_test
class SystemHardwareCpuIdleTests:
    """
    Testcase for verification of cpu idle time.
    """

    dut_parameters = tests_tools.parametrize_duts(TEST_SUITE, test_defs, dut_objs)
    test_duts = dut_parameters["test_system_hardware_cpu_idle"]["duts"]
    test_ids = dut_parameters["test_system_hardware_cpu_idle"]["ids"]

    @pytest.mark.parametrize("dut", test_duts, ids=test_ids)
    def test_system_hardware_cpu_idle(self, dut, tests_definitions):
        """
        TD: Testcase for verification of cpu idle time.
        Args:
            dut(dict): details related to a particular DUT
            tests_definitions(dict): test suite and test case parameters.
        """
        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)
        tops.actual_output = {}
        self.output = ""

        # Forming output message if test result is passed
        tops.output_msg = "Cpu idle time is configured on device."

        try:
            """
            TS: Running `show processes top once` command and verifying cpu idle time is
            configured on device.
            """
            output = tops.run_show_cmds([tops.show_cmd])
            logger.info(
                "On device %s, output of %s command is:\n%s\n",
                tops.dut_name,
                tops.show_cmd,
                output,
            )
            self.output += f"Output of {tops.show_cmd} command is:\n{output}\n"
            cpu_idle_details = output[0].get("result").get("cpuInfo").get("%Cpu(s)").get("idle")

            # Skipping testcase if Cpu idle time is not configured on device.
            if not cpu_idle_details:
                pytest.skip(f"Cpu idle time is not configured on device {tops.dut_name}.")
            else:
                cpu_idle_time_found = "Cpu idle time is low" if cpu_idle_details < 25 else True
                tops.actual_output = {"cpu_idle_time_found": cpu_idle_time_found}

            # Output message formation in case of testcase fails.
            if tops.actual_output != tops.expected_output:
                if tops.actual_output.get("cpu_idle_time_found") == "Cpu idle time is low":
                    tops.output_msg = (
                        f"{tops.actual_output.get('cpu_idle_time_found')}: {cpu_idle_details} on"
                        f" device {tops.dut_name}."
                    )

        except (AssertionError, AttributeError, LookupError, EapiError) as excep:
            tops.output_msg = tops.actual_output = str(excep).split("\n", maxsplit=1)[0]
            logger.error(
                "On device %s, Error while running testcase is:\n%s",
                tops.dut_name,
                tops.actual_output,
            )

        tops.test_result = tops.actual_output == tops.expected_output
        tops.parse_test_steps(self.test_system_hardware_cpu_idle)
        tops.generate_report(tops.dut_name, self.output)
        assert tops.actual_output == tops.expected_output
