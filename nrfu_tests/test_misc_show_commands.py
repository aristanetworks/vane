# Copyright (c) 2023 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.

"""
Testcase for verification of miscellaneous show commands support
"""

import pytest
from pyeapi.eapilib import EapiError
from vane.config import dut_objs, test_defs
from vane import tests_tools, test_case_logger


TEST_SUITE = "nrfu_tests"
logging = test_case_logger.setup_logger(__file__)


@pytest.mark.nrfu_test
@pytest.mark.misc
class MiscShowCommandTests:
    """
    Testcase for verification of miscellaneous show commands support
    """

    dut_parameters = tests_tools.parametrize_duts(TEST_SUITE, test_defs, dut_objs)
    test_duts = dut_parameters["test_misc_show_commands"]["duts"]
    test_ids = dut_parameters["test_misc_show_commands"]["ids"]

    @pytest.mark.parametrize("dut", test_duts, ids=test_ids)
    def test_misc_show_commands(self, dut, tests_definitions):
        """
        TD: Testcase for verification of miscellaneous show commands support.
        Args:
            dut(dict): details related to a particular DUT
            tests_definitions(dict): test suite and test case parameters.
        """
        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)
        self.output, output = "", ""
        tops.actual_output, tops.expected_output = {"show_commands": {}}, {"show_commands": {}}

        # Forming output message if the test result is passed
        tops.output_msg = "Show commands are executed on device without any error."

        tops.show_cmd = [
            "show module all",
            "show logging last 1 days",
            "show interfaces description",
            "show interfaces status",
            "show interfaces | include Ethernet|Port|Vlan|Loopback|Management|MTU",
            "show lldp neighbors",
            "show spanning-tree root detail",
            "show spanning-tree blockedports",
            "show vlan",
            "show interfaces trunk",
            "show vrf",
            "show ip route vrf all summary",
        ]

        output_msg, command_failed_msg = "", ""

        try:
            """
            TS: Running show commands on the device and verifying show commands are executed
            successfully on the device.
            """
            for command in tops.show_cmd:
                try:
                    # Forming expected output as per show commands.
                    tops.expected_output["show_commands"].update(
                        {command: {"command_executed": True}}
                    )
                    output = tops.run_show_cmds([command], encoding="text")
                    logging.info(
                        f"On device {tops.dut_name}, output of {command} command is: \n{output}\n"
                    )
                    self.output += f"Output of {command} command is: \n{output}"
                    tops.actual_output["show_commands"].update(
                        {command: {"command_executed": command in output[0]["command"]}}
                    )

                except EapiError as error:
                    if "Unavailable command" in str(error):
                        output_msg += (
                            f"\nCommand '{command}' is not supported on this hardware"
                            f" platform:\n{error}\n"
                        )

                        # Do NOT Fail test case if command is not supported on hardware
                        tops.actual_output["show_commands"].update(
                            {command: {"command_executed": True}}
                        )
                    else:
                        command_failed_msg += (
                            f"\nCommand '{command}' execution on the device failed with the"
                            f" following error:\n{error}\n"
                        )

                        # Updating actual output for a particular command to false when it
                        # throws exception
                        tops.actual_output["show_commands"].update(
                            {command: {"command_executed": False}}
                        )
            if output_msg or command_failed_msg:
                tops.output_msg = output_msg + command_failed_msg

        except (AttributeError, LookupError, EapiError) as excep:
            tops.output_msg = tops.actual_output = str(excep).split("\n", maxsplit=1)[0]
            logging.error(
                (
                    f"On device {tops.dut_name}, Error while running the testcase"
                    f" is:\n{tops.actual_output}"
                ),
            )

        tops.test_result = tops.expected_output == tops.actual_output
        tops.parse_test_steps(self.test_misc_show_commands)
        tops.generate_report(tops.dut_name, self.output)
        assert tops.expected_output == tops.actual_output
