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


class TestNtpFunctionality:
    """
    Test cases for verification of NTP functionality
    """

    test_data_exists = tests_tools.is_test_data_present("test_ntp_functionality")

    test_duts, test_ids = tests_tools.get_duts_n_ids("test_ntp_functionality")

    @pytest.mark.skipif(not test_data_exists, 
                        reason="Test not in catalog")

    @pytest.mark.parametrize("dut", test_duts, ids=test_ids)
    def test_ntp_functionality(self, dut, tests_definitions):
        """
        TD: Test case for verification of NTP functionality.
        Args:
          dut(dict): Details related to a particular device
          tests_definitions(dict): Test suite and test case parameters
        """

        # Creating the Testops class object and initialize the variables.
        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)
        self.output = ""
        show_cmds = tops.show_cmds[tops.dut_name]
        ntp_status_command = show_cmds[0]

        # Forming an output message if a test result is passed.
        tops.output_msg = ("Primary NTA server status should be synchronized")

        try:
            """
            TS: Running `show ntp status` command on device and verifying that the primary,
            secondary, tertiary server details are correct.
            """
            ntp_status_output = dut["output"][ntp_status_command]["json"]
            logger.info(
                "On device %s, output of '%s' command is:\n%s\n",
                tops.dut_name,
                ntp_status_command,
                ntp_status_output,
            )
            self.output += (
                f"\n\nOn device {tops.dut_name}, output of command {ntp_status_command} is:"
                f" \n{ntp_status_output}"
            )

            # Verifying the actual NTP status output
            assert (
                ntp_status_output
            ), f"NTP status details are not found on the device {tops.dut_name}."

            # Updating expected output dictionary.
            tops.expected_output ={ "status": "synchronised"}

            # Updating actual output dictionary.
            tops.actual_output = { "status": ntp_status_output.get("status")}

            # Forming an output message if a test result is failed
            if tops.actual_output != tops.expected_output:
                tops.output_msg = "The device is not synchronized with the configured NTP server(s)"

        except (AssertionError, AttributeError, LookupError, EapiError) as excep:
            tops.actual_output = tops.output_msg = str(excep).split("\n", maxsplit=1)[0]
            logger.error(
                "On device %s: Error occurred while running the test case is:\n%s",
                tops.dut_name,
                tops.actual_output,
            )

        tops.test_result = tops.expected_output == tops.actual_output
        tops.parse_test_steps(self.test_ntp_functionality)
        tops.generate_report(tops.dut_name, self.output)
        assert tops.expected_output == tops.actual_output
