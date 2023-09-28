# Copyright (c) 2023 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.

"""Testcases for verification of multi-agent routing functionality"""

import pytest
from pyeapi.eapilib import EapiError
from vane import tests_tools, test_case_logger
from vane.config import dut_objs, test_defs

TEST_SUITE = "nrfu_tests"
logging = test_case_logger.setup_logger(__file__)


@pytest.mark.nrfu_test
@pytest.mark.routing
class MultiAgentRoutingProtocolTests:

    """Testcases for verification of multi-agent routing functionality"""

    dut_parameters = tests_tools.parametrize_duts(TEST_SUITE, test_defs, dut_objs)
    test_duts = dut_parameters["test_multi_agent_routing_protocol"]["duts"]
    test_ids = dut_parameters["test_multi_agent_routing_protocol"]["ids"]

    @pytest.mark.parametrize("dut", test_duts, ids=test_ids)
    def test_multi_agent_routing_protocol(self, dut, tests_definitions):
        """
        TD: Test case for verification of multi-agent routing model functionality
        Args:
          dut(dict): Details related to particular DUT
          tests_definitions(dict): Test suite and test case parameters
        """

        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)
        self.output = ""
        tops.actual_output = {"multi_agent_routing_protocol": {}}
        operating_model = "Operating routing protocol model: multi-agent"
        configured_model = "Configured routing protocol model: multi-agent"

        # Forming output message if test result is pass
        tops.output_msg = (
            "Multi agent routing model protocol is configured and operational on the device."
        )

        try:
            """
            TS: Running 'show ip route summary' command and verifying multi agent routing model
            protocol is configured and operational on the device.
            """
            route_summary = dut["output"][tops.show_cmd]["text"]
            logging.info(
                f"On device {tops.dut_name}, Output of {tops.show_cmd} command"
                f" is:\n{route_summary}\n"
            )
            self.output += (
                f"On device {tops.dut_name}, Output of {tops.show_cmd} is:\n{route_summary}\n"
            )
            assert route_summary, "Routing model details are not found."

            # Verify multi-agent is configured
            tops.actual_output["multi_agent_routing_protocol"]["configured"] = (
                configured_model in route_summary
            )

            # Verify multi-agent is configured
            tops.actual_output["multi_agent_routing_protocol"]["operational"] = (
                operating_model in route_summary
            )

            # forming output message if test result is fail
            if tops.actual_output != tops.expected_output:
                tops.output_msg = ""
                if not tops.actual_output["multi_agent_routing_protocol"]["operational"]:
                    if tops.actual_output["multi_agent_routing_protocol"]["configured"]:
                        tops.output_msg += (
                            "Multi agent routing protocol is configured but it is not in the"
                            " operational state."
                        )
                    if not tops.actual_output["multi_agent_routing_protocol"]["configured"]:
                        tops.output_msg += (
                            "Multi agent routing protocol is neither configured nor in"
                            " operational state."
                        )

        except (AssertionError, AttributeError, LookupError, EapiError) as excep:
            tops.actual_output = tops.output_msg = str(excep).split("\n", maxsplit=1)[0]
            logging.error(
                f"On device {tops.dut_name}: Error while running the testcase"
                f" is:\n{tops.actual_output}"
            )

        tops.test_result = tops.expected_output == tops.actual_output
        tops.parse_test_steps(self.test_multi_agent_routing_protocol)
        tops.generate_report(tops.dut_name, self.output)
        assert tops.expected_output == tops.actual_output
