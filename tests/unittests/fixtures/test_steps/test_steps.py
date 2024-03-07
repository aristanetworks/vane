# Copyright (c) 2022 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.

"""
Testcases for verification of syslog functionality
"""


from vane.vane_logging import logging as logger

TEST_SUITE = "baseline_mgmt_tests"


class TestSyslogFunctionality:
    """
    Testcases for verification of syslog functionality
    """

    def test_syslog_functionality_on_switch(self):
        """TD: Testcase for verification of syslog logging server and
            source-interface information

        Args:
            dut(dict): fixture used to iterate over all the duts
            tests_definitions(dict): test suite and test case parameters
        """

        logger.info("This is a log")

        try:
            """
            TS: Running show logging command on dut and collecting the text output
            """

            logger.info("True")

            """
            TS: Checking logging source interface and Logging to string in output
            """

            assert True

            """
            TS: Collecting logging interface and IP address from command output
            """

            logger.info("This is a log")

            """
            TS: Collecting information of syslog logging port and vrf details from command
            output
            """
            logger.info("This is a log")

        except (AssertionError, AttributeError, LookupError) as excep:
            logger.error(excep)

        """
        TS: Comparing source-interface, port and vrf details from actual output
        with the expected output details
        """

    def test_syslog_functionality_on_server(self):
        """
        TD: Testcase for veification of syslog events on configured server

        Args:
            dut(dict): fixture used to iterate over all the duts
            tests_definitions(dict): test suite and test case parameters
        """

        """
        TS: Creating Testops class object and initializing the variable
        """
        logger.info("This is a log")

        try:
            """
            TS: Running Tcpdump on syslog server and entering in config mode
            and existing to verify logging event are captured.
            """
            assert True

        except (AttributeError, LookupError) as excep:
            logger.error(excep)

        """
        TS: Comparing the actual output and expected output. Generating docx report
        """
