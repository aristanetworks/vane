# Copyright (c) 2024 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.

"""
Test case for the verification of redundant supervisor card.
"""

import pytest
import pyeapi.eapilib
from pyeapi.eapilib import EapiError
from vane.config import dut_objs, test_defs
from vane import tests_tools, test_case_logger

TEST_SUITE = "nrfu_tests"
logging = test_case_logger.setup_logger(__file__)


@pytest.mark.nrfu_test
@pytest.mark.base_services
class RedundantSupervisorCardTests:
    """
    Test case for the verification of redundant supervisor card.
    """

    dut_parameters = tests_tools.parametrize_duts(TEST_SUITE, test_defs, dut_objs)
    test_duts = dut_parameters["test_redundant_sso_card"]["duts"]
    test_ids = dut_parameters["test_redundant_sso_card"]["ids"]

    @pytest.mark.parametrize("dut", test_duts, ids=test_ids)
    def test_redundant_sso_card(self, dut, tests_definitions):
        """
        TD: Test case for the verification of redundant supervisor card.
        Args:
            dut(dict): details related to a particular device.
            tests_definitions(dict): test suite and test case parameters.
        """
        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)
        self.output = ""
        tops.actual_output = {"sso_protocol_details": {}}
        tops.show_cmd = "show redundancy status"

        # Forming output message if the test result is passed
        tops.output_msg = (
            "Redundancy SSO protocol is configured, operational and ready for switchover."
        )

        try:
            """
            TS: Running the 'show redundancy status' command on the device and
            verifying that the SSO protocol is configured, operational and ready for switchover.
            """
            try:
                output = tops.run_show_cmds([tops.show_cmd])
                logging.info(
                    (
                        f"On device {tops.dut_name}, the output of the `{tops.show_cmd}` command"
                        f" is: \n{output}\n"
                    ),
                )
                self.output += f"\n\nOutput of {tops.show_cmd} command is: \n{output}"
                output = output[0]["result"]

            except pyeapi.eapilib.CommandError as error:
                if "Unavailable command" in str(error):
                    tops.output_msg = (
                        f"Skipped the test case as the device {tops.dut_name}, is not a dual"
                        " supervisor device."
                    )
                    tests_tools.post_process_skip(tops, self.test_redundant_sso_card, self.output)
                    pytest.skip(tops.output_msg)

            # Skipping test case if SSO protocol is not configured on the device.
            if output["peerState"] == "notInserted":
                tops.output_msg = (
                    "Skipped the test case as peer supervisor card is not inserted on device"
                    f" {tops.dut_name}."
                )
                tests_tools.post_process_skip(tops, self.test_redundant_sso_card, self.output)
                pytest.skip(tops.output_msg)

            tops.actual_output["sso_protocol_details"].update(
                {
                    "configured_protocol": output["configuredProtocol"],
                    "operational_protocol": output["operationalProtocol"],
                    "switch_over_ready": output["switchoverReady"],
                }
            )

            # Forming the output message if the test result is failed
            if tops.expected_output != tops.actual_output:
                tops.output_msg = "\n"
                expected_details = tops.expected_output["sso_protocol_details"]
                actual_details = tops.actual_output["sso_protocol_details"]
                if expected_details["configured_protocol"] != actual_details["configured_protocol"]:
                    tops.output_msg += (
                        "Expected configured protocol is"
                        f" '{expected_details['configured_protocol']}', however in actual it is"
                        f" found as '{actual_details['configured_protocol']}'.\n"
                    )
                if (
                    expected_details["operational_protocol"]
                    != actual_details["operational_protocol"]
                ):
                    tops.output_msg += (
                        "Expected operational protocol is"
                        f" '{expected_details['operational_protocol']}', however in actual it is"
                        f" found as '{actual_details['operational_protocol']}'.\n"
                    )
                if not actual_details["switch_over_ready"]:
                    tops.output_msg += "Redundancy protocol sso is not ready for switch over.\n"

        except (AttributeError, LookupError, EapiError) as excep:
            tops.output_msg = tops.actual_output = str(excep).split("\n", maxsplit=1)[0]
            logging.error(
                f"On device {tops.dut_name}, Error while running the test case"
                f" is:\n{tops.actual_output}"
            )

        tops.test_result = tops.expected_output == tops.actual_output
        tops.parse_test_steps(self.test_redundant_sso_card)
        tops.generate_report(tops.dut_name, self.output)
        assert tops.expected_output == tops.actual_output
