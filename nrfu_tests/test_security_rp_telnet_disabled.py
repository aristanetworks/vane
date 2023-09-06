# Copyright (c) 2023 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.

""" Test case to verify that Telnet is disabled for all the VRFs on the device """

import pytest
from pyeapi.eapilib import EapiError
from vane import tests_tools
from vane.logger import logger
from vane.config import dut_objs, test_defs

TEST_SUITE = "nrfu_tests"


@pytest.mark.nrfu_test
@pytest.mark.security
class TelnetStateTests:
    """Test case to verify that Telnet is disabled for all the VRFs on the device"""

    dut_parameters = tests_tools.parametrize_duts(TEST_SUITE, test_defs, dut_objs)
    test_duts = dut_parameters["test_telnet_is_disabled_for_all_vrfs"]["duts"]
    test_ids = dut_parameters["test_telnet_is_disabled_for_all_vrfs"]["ids"]

    @pytest.mark.parametrize("dut", test_duts, ids=test_ids)
    def test_telnet_is_disabled_for_all_vrfs(self, dut, tests_definitions):
        """
        TD: Test case to verify that Telnet is disabled for all the VRFs on the device.
        Args:
          dut(dict): Details related to the switches
          tests_definitions(dict): Test suite and test case parameters
        """
        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)
        self.output = ""
        tops.actual_output = {"vrfs": {}}
        tops.expected_output = {"vrfs": {}}

        # Forming output message if test result is pass
        tops.output_msg = "Telnet is disabled for all the VRFs on the device."

        try:
            """
            TS: Running `show vrf` on device and collecting the all the vrfs.
            """
            output = dut["output"][tops.show_cmd]["json"]
            logger.info(
                "On device %s, output of %s command is:\n%s\n",
                tops.dut_name,
                tops.show_cmd,
                output,
            )
            self.output += f"Output of {tops.show_cmd} command is: \n{output}\n"

            """
            TS: For vrf default running `show management telnet` command and for others
            `show management telnet vrf <vrf name>` command. Verifying the state of Telnet
            on each vrf.
            """
            for vrf in output.get("vrfs"):
                tops.expected_output["vrfs"].update({vrf: {"telnet_state": "disabled"}})
                telnet_cmd = "show management telnet"

                if vrf != "default":
                    telnet_cmd = f"show management telnet vrf {vrf}"
                try:
                    cmd_output = tops.run_show_cmds([telnet_cmd])
                    logger.info(
                        "On device %s, output of %s command is:\n%s\n",
                        tops.dut_name,
                        telnet_cmd,
                        cmd_output,
                    )
                    self.output += f"Output of {telnet_cmd} command is: \n{cmd_output}\n"
                    telnet_state = cmd_output[0]["result"].get("serverState")
                    tops.actual_output["vrfs"].update({vrf: {"telnet_state": telnet_state}})
                except EapiError as exception:
                    if f"VRF {vrf} not found" in str(exception):
                        tops.actual_output["vrfs"].update({vrf: {"telnet_state": "disabled"}})

            # Forming output message if test result is fail
            if tops.actual_output != tops.expected_output:
                tops.output_msg = ""
                telnet_enabled_vrfs = []

                for vrf, telnet_state in tops.expected_output["vrfs"].items():
                    vrf_data = tops.actual_output["vrfs"][vrf]
                    actual_state = vrf_data["telnet_state"]
                    if telnet_state["telnet_state"] != actual_state:
                        telnet_enabled_vrfs.append(vrf)

                if telnet_enabled_vrfs:
                    tops.output_msg += (
                        "Telnet is not disabled for following VRFs:"
                        f" {', '.join(telnet_enabled_vrfs)}\n"
                    )

        except (AttributeError, LookupError, EapiError) as excp:
            tops.actual_output = tops.output_msg = str(excp).split("\n", maxsplit=1)[0]
            logger.error(
                "On device %s: Error occurred while running testcase is:\n%s",
                tops.dut_name,
                tops.actual_output,
            )

        tops.test_result = tops.expected_output == tops.actual_output
        tops.parse_test_steps(self.test_telnet_is_disabled_for_all_vrfs)
        tops.generate_report(tops.dut_name, self.output)
        assert tops.expected_output == tops.actual_output
