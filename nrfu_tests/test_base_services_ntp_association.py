# Copyright (c) 2023 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.

""" Test case to verify that 2 NTP clocks(a peer and a candidate) are locked on the device."""

import pytest
from pyeapi.eapilib import EapiError
from vane import tests_tools, test_case_logger
from vane.config import dut_objs, test_defs

TEST_SUITE = "nrfu_tests"
logging = test_case_logger.setup_logger(__file__)


@pytest.mark.nrfu_test
@pytest.mark.base_services
class NtpAssociationsTests:
    """Testcases for verification of NTP association functionality"""

    dut_parameters = tests_tools.parametrize_duts(TEST_SUITE, test_defs, dut_objs)
    test_duts = dut_parameters["test_ntp_clocks"]["duts"]
    test_ids = dut_parameters["test_ntp_clocks"]["ids"]

    @pytest.mark.parametrize("dut", test_duts, ids=test_ids)
    def test_ntp_clocks(self, dut, tests_definitions):
        """
        TD: Test case to verify that 2 NTP clocks(a peer and a candidate) are locked on the device
        Args:
          dut(dict): Details related to the switches
          tests_definitions(dict): Test suite and test case parameters
        """
        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)
        self.output = ""
        test_params = tops.test_parameters
        tops.actual_output = {
            "primary_ntp_association": "Not found",
            "secondary_ntp_association": "Not found",
        }
        single_ntp_check = test_params["input"].get("single_ntp_check")
        tops.output_msg = (
            "NTP server should be configured on the device. Primary and secondary NTP association"
            " is correct on the device."
        )
        if single_ntp_check:
            tops.expected_output = {"primary_ntp_association": "sys.peer"}
            # Forming an output message if a test result is pass
            tops.output_msg = (
                "NTP server should be configured on the device. Primary NTP association is correct"
                " on the device."
            )
            test_params["test_criteria"] = (
                "NTP server should be configured on the device. Primary NTP association should be "
                "correct on the device. "
            )
            tops.actual_output = {"primary_ntp_association": "Not found"}

        try:
            """
            TS: Running `show ntp status` command on the device and verifying that
            the NTP is configured.
            """
            output = dut["output"][tops.show_cmd]["json"]
            logging.info(
                f"On device {tops.dut_name}, output of {tops.show_cmd} command is:\n{output}\n"
            )
            self.output = f"Output of {tops.show_cmd} command is: \n{output}\n"

            # Skipping testcase if NTP server is not configured on DUT.
            if output.get("status") == "disabled":
                tops.output_msg = (
                    f"Skipping test case on device {tops.dut_name} as"
                    " NTP server is not configured on device."
                )
                tests_tools.post_process_skip(tops, self.test_ntp_clocks, self.output)
                pytest.skip(tops.output_msg)

            ntp_association_cmd = "show ntp associations"

            """
            TS: Running `show ntp associations` command on the device and verifying that the
            NTP association is correct on the host.
            """
            output = tops.run_show_cmds([ntp_association_cmd])
            logging.info(
                f"On device {tops.dut_name} output of {ntp_association_cmd} command is:\n{output}\n"
            )
            self.output += f"Output of {ntp_association_cmd} command is: \n{output}"
            ntp_associations = output[0]["result"].get("peers")
            assert (
                ntp_associations
            ), f"No NTP servers found in '{ntp_association_cmd}' command output."

            for _, peer_details in ntp_associations.items():
                peer_condition = peer_details.get("condition")
                if peer_condition == "sys.peer":
                    tops.actual_output["primary_ntp_association"] = "sys.peer"
                if not single_ntp_check and peer_condition == "candidate":
                    tops.actual_output["secondary_ntp_association"] = "candidate"

            # Forming an output message if a test result is fail
            if tops.actual_output != tops.expected_output:
                tops.output_msg = ""
                actutal_primary_ntp_status = tops.actual_output.get("primary_ntp_association")
                expected_primary_ntp_status = tops.expected_output.get("primary_ntp_association")
                actual_secondary_ntp_status = tops.actual_output.get("secondary_ntp_association")
                expected_secondary_ntp_status = tops.expected_output.get(
                    "secondary_ntp_association"
                )
                no_primary_ntp = actutal_primary_ntp_status != expected_primary_ntp_status
                no_secondary_ntp = actual_secondary_ntp_status != expected_secondary_ntp_status

                if no_primary_ntp:
                    tops.output_msg += "Primary NTP association is not found on the device.\n"
                elif not single_ntp_check and no_secondary_ntp:
                    tops.output_msg += "Secondary NTP association is not found on the device."

        except (AssertionError, AttributeError, LookupError, EapiError) as excp:
            tops.actual_output = tops.output_msg = str(excp).split("\n", maxsplit=1)[0]
            logging.error(
                f"On device {tops.dut_name}: Error occurred while running testcase"
                f" is:\n{tops.actual_output}"
            )

        tops.test_result = tops.expected_output == tops.actual_output
        tops.parse_test_steps(self.test_ntp_clocks)
        tops.generate_report(tops.dut_name, self.output)
        assert tops.expected_output == tops.actual_output
