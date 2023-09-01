# Copyright (c) 2022 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.

"""
Test cases for verification of configured VLAN naming
"""

import pytest
from pyeapi.eapilib import EapiError
from vane.logger import logger
from vane.config import dut_objs, test_defs
from vane import tests_tools

TEST_SUITE = "nrfu_tests"


@pytest.mark.nrfu_test
@pytest.mark.security
class VlanNameTests:
    """
    Test cases for verification of configured VLAN naming
    """

    dut_parameters = tests_tools.parametrize_duts(TEST_SUITE, test_defs, dut_objs)
    test_duts = dut_parameters["test_security_rp_l2_vlan_name"]["duts"]
    test_ids = dut_parameters["test_security_rp_l2_vlan_name"]["ids"]

    @pytest.mark.parametrize("dut", test_duts, ids=test_ids)
    def test_security_rp_l2_vlan_name(self, dut, tests_definitions):
        """
        TD: Test cases for verification of configured VLAN naming.
        Args:
            dut(dict): details related to a particular DUT
            tests_definitions(dict): test suite and test case parameters
        """
        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)
        self.output = ""
        tops.actual_output = {"vlans": {}}
        tops.expected_output = {"vlans": {}}

        # Forming output message if test result is passed
        tops.output_msg = "All configured VLANs have a name configured."

        try:
            """
            TS: Running 'show vlan' command on DUT and verifying all configured VLANs
            have a name configured.
            """
            output = dut["output"][tops.show_cmd]["json"]
            logger.info(
                "On device %s, output of %s command is: \n%s\n",
                tops.dut_name,
                tops.show_cmd,
                output,
            )
            self.output += f"\nOutput of {tops.show_cmd} command is: \n{output}"

            vlans = output.get("vlans")
            static_vlans = [vlan for vlan in vlans if not vlans[vlan].get("dynamic")]
            assert static_vlans, "Static VLANs are not found on the device."

            for vlan in static_vlans:
                modified_vlan = vlan.zfill(4)
                no_vlan_name = ""
                tops.expected_output["vlans"].update({vlan: {"configured_vlan_name": True}})
                if (
                    vlans.get(vlan).get("name") == "VLAN%s" % vlan
                    or vlans.get(vlan).get("name") == "VLAN%s" % modified_vlan
                ):
                    no_vlan_name = vlans.get(vlan).get("name")

                tops.actual_output["vlans"].update(
                    {vlan: {"configured_vlan_name": not bool(no_vlan_name)}}
                )

            # Output message formation in case of testcase fails.
            if tops.actual_output != tops.expected_output:
                tops.output_msg = ""
                no_name_configured = []
                for vlan, vlan_status in tops.expected_output.get("vlans").items():
                    for vlan_name_status in vlan_status:
                        expected_vlan_name = (
                            tops.expected_output.get("vlans").get(vlan).get(vlan_name_status)
                        )
                        actual_vlan_name = (
                            tops.actual_output.get("vlans").get(vlan).get(vlan_name_status)
                        )
                        if expected_vlan_name != actual_vlan_name:
                            no_name_configured.append(vlan)
                tops.output_msg += (
                    f"Following VLANs are no name configured: {', '.join(no_name_configured)}."
                )

        except (AssertionError, AttributeError, LookupError, EapiError) as excep:
            tops.output_msg = tops.actual_output = str(excep).split("\n", maxsplit=1)[0]
            logger.error(
                "On device %s, Error while running the testcase is:\n%s",
                tops.dut_name,
                tops.actual_output,
            )

        tops.test_result = tops.expected_output == tops.actual_output
        tops.parse_test_steps(self.test_security_rp_l2_vlan_name)
        tops.generate_report(tops.dut_name, self.output)
        assert tops.expected_output == tops.actual_output
