# Copyright (c) 2022 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.

"""Testcase for verification of enable password is configured."""

import pytest
from pyeapi.eapilib import EapiError
from vane.logger import logger
from vane.config import dut_objs, test_defs
from vane import tests_tools

TEST_SUITE = "nrfu_tests"


@pytest.mark.nrfu_test
@pytest.mark.security
class SecurityEnablePasswordTests:

    """
    Testcase for verification of enable password is configured.
    """

    dut_parameters = tests_tools.parametrize_duts(TEST_SUITE, test_defs, dut_objs)
    test_duts = dut_parameters["test_security_rp_enable_pw"]["duts"]
    test_ids = dut_parameters["test_security_rp_enable_pw"]["ids"]

    @pytest.mark.parametrize("dut", test_duts, ids=test_ids)
    def test_security_rp_enable_pw(self, dut, tests_definitions):
        """
        TD: Testcase for verification of enable password is configured.
        Args:
            dut(dict): details related to a particular DUT
            tests_definitions(dict): test suite and test case parameters.
        """
        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)
        tops.actual_output = {}
        self.output = ""
        enable_password_found = False

        # Forming output message if test result is passed
        tops.output_msg = "Enable password is configured on device."

        try:
            """
            TS: Running `show running-config section enable` command and verifying password is
            configured on device.
            """
            output = tops.run_show_cmds([tops.show_cmd])[0]["result"]["output"]
            logger.info(
                "On device %s, output of %s command is:\n%s\n",
                tops.dut_name,
                tops.show_cmd,
                output,
            )
            self.output += f"\nOutput of {tops.show_cmd} command is:\n{output}\n"

            if output.startswith("enable password "):
                enable_password_found = True
            tops.actual_output = {"enable_password_found": enable_password_found}

            # Forming output message if test result is fail.
            if tops.expected_output != tops.actual_output:
                if tops.expected_output.get("enable_password_found") != tops.actual_output.get(
                    "enable_password_found"
                ):
                    tops.output_msg = (
                        f"Enable password is not configured on device {tops.dut_name}."
                    )

        except (AssertionError, AttributeError, LookupError, EapiError) as excep:
            tops.output_msg = tops.actual_output = str(excep).split("\n", maxsplit=1)[0]
            logger.error(
                "On device %s, Error while running testcase is:\n%s",
                tops.dut_name,
                tops.actual_output,
            )

        tops.test_result = tops.actual_output == tops.expected_output
        tops.parse_test_steps(self.test_security_rp_enable_pw)
        tops.generate_report(tops.dut_name, self.output)
        assert tops.actual_output == tops.expected_output
