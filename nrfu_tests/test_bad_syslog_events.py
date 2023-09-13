# Copyright (c) 2023 Arista Networks, Inc.  All rights reserved.
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
        syslog_events_cmd = [f"show logging last {days_of_logs} days"]
        bad_syslog = ""

        # Forming output message if the test result is passed
        tops.output_msg = (
            "Bad syslog events(specific keywords) are not found in the collected logs."
        )

        try:
            # Collecting expected output.
            tops.expected_output.update({"bad_syslog_events_not_found": True})

            """
            TS: Running `show logging last <daysOfLogs> days` command on DUT and verifying
            the keywords in syslog events that are generally considered to be bad.
            """
            output = tops.run_show_cmds(syslog_events_cmd)
            logging.info(
                f"On device {tops.dut_name}, output of {syslog_events_cmd} command is:\n{output}\n",
            )
            self.output += f"Output of {syslog_events_cmd} command is: \n{output}"

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
                    f"\nFollowing bad syslog events are found on the device: \n{bad_syslog}."
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
