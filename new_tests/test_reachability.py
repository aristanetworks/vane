# Copyright (c) 2023 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.

"""
Test cases for verification of NTP functionality
"""

import pytest
from pyeapi.eapilib import EapiError
from vane.config import dut_objs, test_defs
from vane import tests_tools, test_case_logger


TEST_SUITE = "new_tests"
logger = test_case_logger.setup_logger(__file__)


class TestReachability:
    """ Test cases for verification of reachability """

    test_data_exists = tests_tools.is_test_data_present("test_reachability")
    test_duts, test_ids = tests_tools.get_duts_n_ids("test_reachability")

    @pytest.mark.skipif(not test_data_exists, 
                        reason="Test not in catalog")

    @pytest.mark.parametrize("dut", test_duts, ids=test_ids)
    def test_reachability(self, dut, tests_definitions):
        """
        TD: Test case for verification of the network reachability to one or many destination IP(s)
        Args:
          dut(dict): Details related to a particular device
          tests_definitions(dict): Test suite and test case parameters
        """

        # Creating the Testops class object and initialize the variables.
        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)
        self.output = ""
        test_params = tops.test_parameters
        inputs = test_params["inputs"][tops.dut_name]

        # Forming an output message if a test result is passed.
        tops.output_msg = ("The reachability to all destionation is established")

        try:
            """
            TS: Running `ping vrf {vrf} {destination} source {source} repeat {repeat}` command on device and verifying that ,
            destination is reachable from the source 
            """
            tops.actual_output = []
            tops.expected_output = []
            for test_input in inputs:
                host = test_input["hosts"][0]
                dest = host["destination"]
                repeat = host["repeat"]
                src = host["source"]
                vrf = host["vrf"]
                show_cmd = f"ping vrf {vrf} ip {dest} source {src} repeat {repeat}"
                cmd_output = dut["output"][show_cmd]["text"]
                if f"{repeat} received" not in cmd_output:
                    tops.actual_output.append((src, dest))
                logger.info(
                    "On device %s, output of '%s' command is:\n%s\n",
                    tops.dut_name,
                    show_cmd, cmd_output
                )
                self.output += (
                    f"\n\nOn device {tops.dut_name}, output of command {show_cmd} is:"
                    f" \n{cmd_output}"
                )

            # Forming an output message if a test result is failed
            if tops.actual_output != tops.expected_output:
                tops.output_msg = (f"Reachability to following source-destination pair is broken: {tops.actual_output}")

        except (AssertionError, AttributeError, LookupError, EapiError) as excep:
            tops.actual_output = tops.output_msg = str(excep).split("\n", maxsplit=1)[0]
            logger.error(
                "On device %s: Error occurred while running the test case is:\n%s",
                tops.dut_name,
                tops.actual_output,
            )

        tops.test_result = tops.expected_output == tops.actual_output
        tops.parse_test_steps(self.test_reachability)
        tops.generate_report(tops.dut_name, self.output)
        assert tops.expected_output == tops.actual_output
