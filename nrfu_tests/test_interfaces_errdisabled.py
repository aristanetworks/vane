# Copyright (c) 2023 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.

"""Testcases for verification of interface  status functionality"""

import pytest
from pyeapi.eapilib import EapiError
from vane import tests_tools, test_case_logger
from vane.config import dut_objs, test_defs

TEST_SUITE = "nrfu_tests"
logging = test_case_logger.setup_logger(__file__)


@pytest.mark.nrfu_test
@pytest.mark.interfaces
class InterfaceStatusTests:

    """Testcases for verification of interface  status functionality"""

    dut_parameters = tests_tools.parametrize_duts(TEST_SUITE, test_defs, dut_objs)
    test_duts = dut_parameters["test_interfaces_errdisabled_status"]["duts"]
    test_ids = dut_parameters["test_interfaces_errdisabled_status"]["ids"]

    @pytest.mark.parametrize("dut", test_duts, ids=test_ids)
    def test_interfaces_errdisabled_status(self, dut, tests_definitions):
        """
        TD: Test case for verification of interface errdisabled status
        Args:
          dut(dict): Details related to the switches
          tests_definitions(dict): Test suite and test case parameters
        """

        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)
        self.output = ""
        tops.expected_output = {"interface_state_details": {}}
        tops.actual_output = {"interface_state_details": {}}

        # Forming output message if test result is pass
        tops.output_msg = "None of the interface is in error disabled state."

        try:
            """
            TS: Running `show interfaces status errdisabled` command and verifying that the
            none of the interface is in error disabled state.
            """
            interface_details = dut["output"][tops.show_cmd]["json"]
            logging.info(
                f"On device {tops.dut_name}, Output of {tops.show_cmd} command"
                f" is:\n{interface_details}\n"
            )
            interface_statuses = interface_details.get("interfaceStatuses")
            tops.expected_output["interface_state_details"] = {
                "no_interface_in_error_disabled_state": True
            }
            tops.actual_output["interface_state_details"] = {
                "no_interface_in_error_disabled_state": not bool(interface_statuses)
            }

            # forming output message if test result is fail
            if tops.actual_output != tops.expected_output:
                tops.output_msg = "\nFollowing interfaces are in errdisabled state with causes:"
                for interface in interface_statuses:
                    causes = (
                        str(interface_statuses.get(interface, {}).get("causes"))
                        .lstrip("[")
                        .rstrip("]")
                    )
                    tops.output_msg += f"\n{interface}: {causes}."

        except (AttributeError, LookupError, EapiError) as excep:
            tops.actual_output = tops.output_msg = str(excep).split("\n", maxsplit=1)[0]
            logging.error(
                f"On device {tops.dut_name}: Error while running the testcase"
                f" is:\n{tops.actual_output}"
            )

        tops.test_result = tops.expected_output == tops.actual_output
        tops.parse_test_steps(self.test_interfaces_errdisabled_status)
        tops.generate_report(tops.dut_name, self.output)
        assert tops.expected_output == tops.actual_output
