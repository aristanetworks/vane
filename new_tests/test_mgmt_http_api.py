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


class TestAPIHTTPSSSL:
    """
    Test cases for verification of NTP functionality
    """

    test_duts, test_ids = tests_tools.get_duts_n_ids("test_api_https_ssl")
    test_data_exists = tests_tools.is_test_data_present("test_api_https_ssl")

    @pytest.mark.skipif(not test_data_exists, 
                        reason="Test not in catalog")

    @pytest.mark.parametrize("dut", test_duts, ids=test_ids)
    def test_api_https_ssl(self, dut, tests_definitions):
        """
        TD: Test case for last reload cause of the device
        Args:
          dut(dict): Details related to a particular device
          tests_definitions(dict): Test suite and test case parameters
        """

        # Creating the Testops class object and initialize the variables.
        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)
        self.output = ""
        mgmt_api_cmd = tops.show_cmds[tops.dut_name][0]
        input_params = tops.test_parameters["input"]
        profile = input_params["profile"]

        cmd_output = dut["output"][mgmt_api_cmd]["json"]
        # Forming an output message if a test result is passed.
        tops.output_msg = f"eAPI HTTPS server SSL profile {profile} is configured and valid"

        try:
            """
            TS: Running `show management api http-commands` command on device and verify 
            eAPI HTTPS server SSL profile is configured and valid
            """
            logger.info(
                "On device %s, output of '%s' command is:\n%s\n",
                tops.dut_name,
                mgmt_api_cmd,
                cmd_output,
            )
            self.output += (
                f"\n\nOn device {tops.dut_name}, output of command {mgmt_api_cmd} is:"
                f" \n{cmd_output}"
            )

            ssl_profile = cmd_output.get("ssl_profile", {})
            tops.expected_output = {"name": profile, "state": "valid"}
            tops.actual_output = {"name": ssl_profile.get("name", ""),  
                                                 "state": ssl_profile.get("state", "")}

            if tops.expected_output != tops.actual_output:
                tops.output_msg = f"eAPI HTTPS server SSL profile ({profile}) is misconfigured or invalid"

        except (AssertionError, AttributeError, LookupError, EapiError, KeyError) as excep:
            tops.actual_output = tops.output_msg = str(excep).split("\n", maxsplit=1)[0]
            logger.error(
                "On device %s: Error occurred while running the test case is:\n%s",
                tops.dut_name,
                tops.actual_output,
            )

        tops.test_result = tops.actual_output == tops.expected_output
        tops.parse_test_steps(self.test_api_https_ssl)
        tops.generate_report(tops.dut_name, self.output)
        assert tops.actual_output == tops.expected_output
