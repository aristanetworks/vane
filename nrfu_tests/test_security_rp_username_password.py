# Copyright (c) 2023 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.

"""
Test case for verification of password configuration for user accounts.
"""

import pytest
from pyeapi.eapilib import EapiError
from vane.config import dut_objs, test_defs
from vane import tests_tools, test_case_logger

TEST_SUITE = "nrfu_tests"
logging = test_case_logger.setup_logger(__file__)


@pytest.mark.nrfu_test
@pytest.mark.security
class UsernamePasswordTests:
    """
    Test case for verification of password configuration for user accounts.
    """

    dut_parameters = tests_tools.parametrize_duts(TEST_SUITE, test_defs, dut_objs)
    test_duts = dut_parameters["test_security_rp_username_password"]["duts"]
    test_ids = dut_parameters["test_security_rp_username_password"]["ids"]

    @pytest.mark.parametrize("dut", test_duts, ids=test_ids)
    def test_security_rp_username_password(self, dut, tests_definitions):
        """
        TD: Test case for verification of password configuration for user accounts.
        Args:
            dut(dict): details related to a particular DUT
            tests_definitions(dict): test suite and test case parameters.
        """
        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)
        self.output = ""
        tops.actual_output = {}
        tops.expected_output = {}

        # Forming output message if the test result is passed
        tops.output_msg = "All user accounts are configured with a password."

        try:
            """
            TS: Running `show running-config all section ^username` command on the device and
            verifying all usernames are configured with a password.
            """
            output = dut["output"][tops.show_cmd]["text"]
            logging.info(
                f"On device {tops.dut_name}, output of {tops.show_cmd} command is:\n{output}\n"
            )
            self.output += (
                f"\nOn device {tops.dut_name}, output of {tops.show_cmd} command is:\n{output}\n"
            )
            assert output, "User account details are not found in the output."

            # Collecting username and password for each user account and
            # creating expected and actual output dictionaries
            usernames = output.split("\n")
            for user in usernames:
                if user:
                    username = user.split()[1]
                    password = user.split()[-1]
                    tops.expected_output.update({username: {"password_configured": True}})
                    tops.actual_output.update({username: {"password_configured": True}})
                    if password == "nopassword":
                        tops.actual_output.update({username: {"password_configured": False}})

            # Forming output message if the test result is failed
            if tops.expected_output != tops.actual_output:
                tops.output_msg = "\n"
                password_not_configured = []

                # Collecting usernames for which password is not configured
                for username in tops.expected_output:
                    actual_username_detail = tops.actual_output.get(username, {}).get(
                        "password_configured"
                    )
                    if not actual_username_detail:
                        password_not_configured.append(username)
                if password_not_configured:
                    tops.output_msg += (
                        "Following user accounts are not configured with a"
                        f" password: {', '.join(password_not_configured)}"
                    )

        except (AssertionError, AttributeError, LookupError, EapiError) as excep:
            tops.output_msg = tops.actual_output = str(excep).split("\n", maxsplit=1)[0]
            logging.error(
                f"On device {tops.dut_name}, Error while running the test case"
                f" is:\n{tops.actual_output}"
            )

        tops.test_result = tops.expected_output == tops.actual_output
        tops.parse_test_steps(self.test_security_rp_username_password)
        tops.generate_report(tops.dut_name, self.output)
        assert tops.expected_output == tops.actual_output
