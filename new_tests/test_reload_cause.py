# Copyright (c) 2023 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.

"""
Test cases for verification of NTP functionality
"""

import pytest
from pyeapi.eapilib import EapiError
from vane.config import dut_objs, test_defs
from vane import tests_tools, test_case_logger


TEST_SUITE = "new_tests"
logger = test_case_logger.setup_logger(__file__)


class TestReloadCause:
    """
    Test cases for verification of NTP functionality
    """

    test_duts, test_ids = tests_tools.get_duts_n_ids("test_reload_cause")
    test_data_exists = tests_tools.is_test_data_present("test_reload_cause")

    @pytest.mark.skipif(not test_data_exists, 
                        reason="Test not in catalog")

    @pytest.mark.parametrize("dut", test_duts, ids=test_ids)
    def test_reload_cause(self, dut, tests_definitions):
        """
        TD: Test case for last reload cause of the device
        Args:
          dut(dict): Details related to a particular device
          tests_definitions(dict): Test suite and test case parameters
        """

        # Creating the Testops class object and initialize the variables.
        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)
        self.output = ""
        reload_cause_cmd = tops.show_cmds[tops.dut_name][0]

        reload_cause_cmd_output = dut["output"][reload_cause_cmd]["json"]
        # Forming an output message if a test result is passed.
        if (
            "reset_causes" not in reload_cause_cmd_output
            or len(reload_cause_cmd_output["reset_causes"]) == 0
        ):
            tops.output_msg = "Reload cause not present"

        try:
            """
            TS: Running `show reload cause` command on device and verifying that the reload cause
            is either `Reload requested by the user.` or `Reload requested after FPGA upgrade.`
            """
            logger.info(
                "On device %s, output of '%s' command is:\n%s\n",
                tops.dut_name,
                reload_cause_cmd,
                reload_cause_cmd_output,
            )
            self.output += (
                f"\n\nOn device {tops.dut_name}, output of command {reload_cause_cmd} is:"
                f" \n{reload_cause_cmd_output}"
            )

            # Updating expected output dictionary.
            tops.expected_output = [
                "Reload requested by the user.",
                "Reload requested after FPGA upgrade",
            ]

            # Updating actual output dictionary.
            reset_causes = reload_cause_cmd_output.get("resetCauses", [{}])
            tops.actual_output = reset_causes[0].get("description", "")

            tops.output_msg = f"Reload cause is `{tops.actual_output}`"

        except (AssertionError, AttributeError, LookupError, EapiError) as excep:
            tops.actual_output = tops.output_msg = str(excep).split("\n", maxsplit=1)[0]
            logger.error(
                "On device %s: Error occurred while running the test case is:\n%s",
                tops.dut_name,
                tops.actual_output,
            )

        tops.test_result = tops.actual_output in tops.expected_output
        tops.parse_test_steps(self.test_reload_cause)
        tops.generate_report(tops.dut_name, self.output)
        assert tops.actual_output in tops.expected_output
