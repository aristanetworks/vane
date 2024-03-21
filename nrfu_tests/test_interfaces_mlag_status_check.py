# Copyright (c) 2024 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.

"""
Testcase for verification of MLAG functionality
"""

import pytest
from pyeapi.eapilib import EapiError
from vane import tests_tools, test_case_logger
from vane.config import dut_objs, test_defs

TEST_SUITE = "nrfu_tests"
logging = test_case_logger.setup_logger(__file__)


@pytest.mark.nrfu_test
@pytest.mark.interfaces
class MlagStatusTests:
    """
    Testcase for verification of MLAG functionality
    """

    dut_parameters = tests_tools.parametrize_duts(TEST_SUITE, test_defs, dut_objs)
    test_duts = dut_parameters["test_interfaces_mlag_status"]["duts"]
    test_ids = dut_parameters["test_interfaces_mlag_status"]["ids"]

    @pytest.mark.parametrize("dut", test_duts, ids=test_ids)
    def test_interfaces_mlag_status(self, dut, tests_definitions):
        """
        TD: Testcase for verification of MLAG functionality
        Args:
            dut(dict): details related to a particular DUT
            tests_definitions(dict): test suite and test case parameters
        """
        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)
        self.output = ""
        tops.actual_output = {"mlag_details": {}}
        tops.expected_output = {"mlag_details": {}}

        # Forming output message if test result is passed
        tops.output_msg = "MLAG is configured as active, connected and consistent on the device."

        try:
            """
            TS: Running 'show mlag' command on DUT and verifying that the MLAG is configured
            on the device.
            """
            output = dut["output"][tops.show_cmd]["json"]
            logging.info(
                f"On device {tops.dut_name}, output of {tops.show_cmd} command is: \n{output}\n",
            )
            self.output += f"\nOutput of {tops.show_cmd} command is: \n{output}"

            # Skipping, if MLAG is not configured.
            if output.get("state") == "disabled":
                tops.output_msg = (
                    f"Skipping test case on {tops.dut_name} as MLAG is not configured on device."
                )
                tests_tools.post_process_skip(tops, self.test_interfaces_mlag_status, self.output)
                pytest.skip(tops.output_msg)

            # collecting actual output.
            tops.actual_output["mlag_details"].update(
                {
                    "state": output.get("state"),
                    "negotiation_status": output.get("negStatus"),
                    "config_sanity": output.get("configSanity"),
                }
            )
            tops.expected_output["mlag_details"].update(
                {
                    "state": "active",
                    "negotiation_status": "connected",
                    "config_sanity": "consistent",
                }
            )

            # Output message formation in case of testcase fails.
            if tops.actual_output != tops.expected_output:
                tops.output_msg = "\n"
                for mlag_key, mlag_value in tops.expected_output["mlag_details"].items():
                    if mlag_value != tops.actual_output["mlag_details"].get(mlag_key):
                        tops.output_msg += (
                            f"Expected MLAG {mlag_key.replace('_', ' ')} is '{mlag_value}',"
                            " however actual found as"
                            f" '{tops.actual_output['mlag_details'].get(mlag_key)}'.\n"
                        )

        except (AssertionError, AttributeError, LookupError, EapiError) as excep:
            tops.output_msg = tops.actual_output = str(excep).split("\n", maxsplit=1)[0]
            logging.error(
                (
                    f"On device {tops.dut_name}, Error while running the testcase"
                    f" is:\n{tops.actual_output}"
                ),
            )

        tops.test_result = tops.expected_output == tops.actual_output
        tops.parse_test_steps(self.test_interfaces_mlag_status)
        tops.generate_report(tops.dut_name, self.output)
        assert tops.expected_output == tops.actual_output
