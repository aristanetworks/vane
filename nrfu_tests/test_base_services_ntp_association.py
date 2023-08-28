# Copyright (c) 2023 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.

""" Test case to verify that 2 NTP clocks(a peer and a candidate) are locked on the device."""

import pytest
from pyeapi.eapilib import EapiError
from vane import tests_tools
from vane.logger import logger
from vane.config import dut_objs, test_defs

TEST_SUITE = "nrfu_tests"


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
        tops.actual_output = {
            "primary_ntp_association": "Not found",
            "secondary_ntp_association": "Not found",
        }
        # Forming output message if test result is pass
        tops.output_msg = (
            "NTP server is configured on the device. Primary and secondary NTP association is"
            " correct on the device."
        )

        try:
            """
            TS: Running `show ntp status` on device and verifying the NTP is configured.
            """
            output = dut["output"][tops.show_cmd]["json"]
            logger.info(
                "On device %s, output of %s command is:\n%s\n",
                tops.dut_name,
                tops.show_cmd,
                output,
            )
            self.output = f"Output of {tops.show_cmd} command is: \n{output}\n"

            # Skipping testcase if NTP server is not configured on DUT.
            if output.get("status") == "disabled":
                pytest.skip(f"NTP server is not configured on device {tops.dut_name}.")

            ntp_association_cmd = "show ntp associations"

            """
            TS: Running `show ntp associations` on device and verifying that the
            primary and secondary NTP association is correct on the host.
            """
            output = tops.run_show_cmds([ntp_association_cmd])
            logger.info(
                "On device %s output of %s command is:\n%s\n",
                tops.dut_name,
                ntp_association_cmd,
                output,
            )
            self.output += f"Output of {ntp_association_cmd} command is: \n{output}"
            ntp_associations = output[0]["result"].get("peers")
            assert ntp_associations, "NTP association details are not collected."

            for peer in ntp_associations:
                if ntp_associations[peer].get("condition") == "sys.peer":
                    tops.actual_output["primary_ntp_association"] = "sys.peer"
                elif ntp_associations[peer].get("condition") == "candidate":
                    tops.actual_output["secondary_ntp_association"] = "candidate"

            # Forming output message if test result is fail
            if tops.actual_output != tops.expected_output:
                tops.output_msg = ""
                not_primary_ntp_association = (
                    tops.actual_output["primary_ntp_association"]
                    != tops.expected_output["primary_ntp_association"]
                )
                not_secondary_ntp_association = (
                    tops.actual_output["secondary_ntp_association"]
                    != tops.expected_output["secondary_ntp_association"]
                )
                if not_primary_ntp_association and not_secondary_ntp_association:
                    tops.output_msg += (
                        "Primary and Secondary NTP associations are not found on the device.\n"
                    )
                elif not_primary_ntp_association:
                    tops.output_msg += "Primary NTP association is not found on the device.\n"
                elif not_secondary_ntp_association:
                    tops.output_msg += "Secondary NTP association is not found on the device."

        except (AssertionError, AttributeError, LookupError, EapiError) as excp:
            tops.actual_output = tops.output_msg = str(excp).split("\n", maxsplit=1)[0]
            logger.error(
                "On device %s: Error occurred while running testcase is:\n%s",
                tops.dut_name,
                tops.actual_output,
            )

        tops.test_result = tops.expected_output == tops.actual_output
        tops.parse_test_steps(self.test_ntp_clocks)
        tops.generate_report(tops.dut_name, self.output)
        assert tops.expected_output == tops.actual_output
