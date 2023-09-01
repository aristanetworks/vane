# Copyright (c) 2023 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.

"""
Test cases for verification of system hardware free memory functionality
"""

import pytest
from pyeapi.eapilib import EapiError
from vane.logger import logger
from vane.config import dut_objs, test_defs
from vane import tests_tools

TEST_SUITE = "nrfu_tests"


@pytest.mark.nrfu_test
@pytest.mark.system
class BadSyslogEventsTests:
    """
    Test cases for verification of bad syslog events messages
    """

    dut_parameters = tests_tools.parametrize_duts(TEST_SUITE, test_defs, dut_objs)
    test_duts = dut_parameters["test_system_hardware_bad_syslog_event"]["duts"]
    test_ids = dut_parameters["test_system_hardware_bad_syslog_event"]["ids"]

    @pytest.mark.parametrize("dut", test_duts, ids=test_ids)
    def test_system_hardware_bad_syslog_event(self, dut, tests_definitions):
        """
        TD: Testcase for verification bad syslog events messages.
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

        # Forming output message if test result is passed
        tops.output_msg = "No bad syslog events are found."

        try:
            # Collecting expected output.
            tops.expected_output.update({"bad_syslog_events_not_found": True})

            """
            TS: Running `show logging last <daysOfLogs> days` command on DUT and verifying
            the key words in syslog events that are generally considered to be bad.
            """
            output = tops.run_show_cmds(syslog_events_cmd)
            logger.info(
                "On device %s, output of %s command is:\n%s\n",
                tops.dut_name,
                syslog_events_cmd,
                output,
            )
            self.output += f"Output of {syslog_events_cmd} command is: \n{output}"

            sys_log_events = output[0].get("result", {}).get("output")
            assert sys_log_events, f"logging details for last {days_of_logs} days are not found."

            for event in sys_log_events.split("\n"):
                if (
                    "error" in event.lower()
                    or "not_available" in event.lower()
                    or "unavailable" in event.lower()
                    or "interrupt" in event.lower()
                ):
                    bad_syslog += f"{event}\n"

            # Collecting actual output.
            tops.actual_output.update({"bad_syslog_events_not_found": len(bad_syslog) == 0})

            # Forming output message if test result is fail.
            if tops.actual_output != tops.expected_output:
                tops.output_msg = (
                    f"The following syslog events should be investigated:\n{bad_syslog}"
                )

        except (AssertionError, AttributeError, LookupError, EapiError) as excep:
            tops.output_msg = tops.actual_output = str(excep).split("\n", maxsplit=1)[0]
            logger.error(
                "On device %s, Error while running the testcase is:\n%s",
                tops.dut_name,
                tops.actual_output,
            )

        tops.test_result = tops.expected_output == tops.actual_output
        tops.parse_test_steps(self.test_system_hardware_bad_syslog_event)
        tops.generate_report(tops.dut_name, self.output)
        assert tops.expected_output == tops.actual_output
