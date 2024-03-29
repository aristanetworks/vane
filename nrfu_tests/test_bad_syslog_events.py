# Copyright (c) 2024 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.

"""
Test cases for verification of bad syslog event messages
"""

import pytest
from pyeapi.eapilib import EapiError
from vane.config import dut_objs, test_defs
from vane import tests_tools, test_case_logger

TEST_SUITE = "nrfu_tests"
logging = test_case_logger.setup_logger(__file__)


@pytest.mark.nrfu_test
@pytest.mark.system
class BadSyslogEventsTests:
    """
    Test cases for verification of bad syslog event messages
    """

    dut_parameters = tests_tools.parametrize_duts(TEST_SUITE, test_defs, dut_objs)
    test_duts = dut_parameters["test_bad_syslog_events"]["duts"]
    test_ids = dut_parameters["test_bad_syslog_events"]["ids"]

    @pytest.mark.parametrize("dut", test_duts, ids=test_ids)
    def test_bad_syslog_events(self, dut, tests_definitions):
        """
        TD: Testcase for verification of bad syslog event messages.
        Args:
            dut(dict): details related to a particular DUT
            tests_definitions(dict): test suite and test case parameters.
        """
        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)
        self.output = ""
        tops.actual_output = {}
        tops.expected_output = {}
        test_params = tops.test_parameters
        days_of_logs = test_params["days_of_logs"]
        syslog_events_cmd = [["show logging"], [f"show logging last {days_of_logs} days"]]
        bad_syslog = ""

        # Forming output message if the test result is passed
        tops.output_msg = (
            "Bad syslog events(specific keywords) are not found in the collected logs."
        )

        try:
            # Collecting expected output.
            tops.expected_output.update({"bad_syslog_events_not_found": True})

            """
            TS: Running 'show logging' command on DUT and verifying that the SysLog is configured
            on the device.
            """
            syslog_output = tops.run_show_cmds(syslog_events_cmd[0], encoding="txt")
            logging.info(
                (
                    f"On device {tops.dut_name}, output of {syslog_events_cmd[0]} command"
                    f" is:\n{syslog_output}\n"
                ),
            )
            self.output += f"Output of {syslog_events_cmd[0]} command is: \n{syslog_output}"
            syslog_output_details = syslog_output[0]["result"].get("output")

            # Skipping, if SysLog is not configured.
            for detail in syslog_output_details.split("\n"):
                if "Syslog logging: disabled" in detail:
                    tops.output_msg = (
                        f"SysLog is not configured on device {tops.dut_name}, hence test skipped."
                    )
                    tests_tools.post_process_skip(tops, self.test_bad_syslog_events, self.output)
                    pytest.skip(tops.output_msg)

            """
            TS: Running `show logging last <daysOfLogs> days` command on DUT and verifying
            the keywords in syslog events that are generally considered to be bad.
            """
            output = tops.run_show_cmds(syslog_events_cmd[1], encoding="txt")
            logging.info(
                (
                    f"On device {tops.dut_name}, output of {syslog_events_cmd[1]} command"
                    f" is:\n{output}\n"
                ),
            )
            self.output += f"Output of {syslog_events_cmd[1]} command is: \n{output}"

            syslog_events = output[0]["result"].get("output")
            assert syslog_events, f"logging details for last {days_of_logs} days are not found."

            for event in syslog_events.split("\n"):
                event = event.lower()
                if (
                    "error" in event
                    or "not_available" in event
                    or "unavailable" in event
                    or "interrupt" in event
                ):
                    bad_syslog += f"{event}\n"

            # Collecting actual output.
            tops.actual_output.update({"bad_syslog_events_not_found": not bool(bad_syslog)})

            # Forming output message if the test result fails.
            if tops.actual_output != tops.expected_output:
                tops.output_msg = (
                    f"\nFollowing bad syslog events are found on the device: \n{bad_syslog}"
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
        tops.parse_test_steps(self.test_bad_syslog_events)
        tops.generate_report(tops.dut_name, self.output)
        assert tops.expected_output == tops.actual_output
