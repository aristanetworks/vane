# Copyright (c) 2023 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.

"""
Testcase for verification of login banner is configured.
"""

import pytest
from pyeapi.eapilib import EapiError
from vane.logger import logger
from vane.config import dut_objs, test_defs
from vane import tests_tools

TEST_SUITE = "nrfu_tests"


@pytest.mark.nrfu_test
@pytest.mark.security
class SecurityRpLoginBannerTests:
    """
    Testcase for verification of login banner is configured.
    """

    dut_parameters = tests_tools.parametrize_duts(TEST_SUITE, test_defs, dut_objs)
    test_duts = dut_parameters["test_security_rp_login_banner"]["duts"]
    test_ids = dut_parameters["test_security_rp_login_banner"]["ids"]

    @pytest.mark.parametrize("dut", test_duts, ids=test_ids)
    def test_security_rp_login_banner(self, dut, tests_definitions):
        """
        TD: Testcase for verification of login banner is configured.
        Args:
            dut(dict): details related to a particular DUT
            tests_definitions(dict): test suite and test case parameters
        """
        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)
        self.output = ""
        tops.actual_output = {"login_banner_found": False}

        # Forming output message if test result is passed
        tops.output_msg = "Expected login banner is present on the switch."

        try:
            """
            TS: Running `show banner login` command on a DUT and verifying that the
            login banner is correct.
            """
            output = dut["output"][tops.show_cmd]["json"]
            logger.info(
                "On device %s, output of %s command is: \n%s\n",
                tops.dut_name,
                tops.show_cmd,
                output,
            )
            self.output += f"\nOutput of {tops.show_cmd} command is: \n{output}"
            login_banner = output.get("loginBanner")

            if login_banner:
                tops.actual_output = {"login_banner_found": True}

            # forming output message if test result is fail
            if tops.expected_output != tops.actual_output:
                if not tops.actual_output["login_banner_found"]:
                    tops.output_msg = f"Login banner is not configured on {tops.dut_name}"

        except (AssertionError, AttributeError, LookupError, EapiError) as excep:
            tops.output_msg = tops.actual_output = str(excep).split("\n", maxsplit=1)[0]
            logger.error(
                "On device %s, Error while running the testcase is:\n%s",
                tops.dut_name,
                tops.actual_output,
            )

        tops.test_result = tops.expected_output == tops.actual_output
        tops.parse_test_steps(self.test_security_rp_login_banner)
        tops.generate_report(tops.dut_name, self.output)
        assert tops.expected_output == tops.actual_output
