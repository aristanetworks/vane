# Copyright (c) 2023 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.

"""
Test cases for verification of configured VLAN naming
"""

import pytest
from pyeapi.eapilib import EapiError
from vane.config import dut_objs, test_defs
from vane import tests_tools, test_case_logger

TEST_SUITE = "nrfu_tests"
logging = test_case_logger.setup_logger(__file__)


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

        # Forming output message if the test result is passed
        tops.output_msg = "All configured VLANs have a name configured."

        try:
            """
            TS: Running 'show vlan' command on DUT and verifying all configured VLANs
            have a name configured.
            """
            output = dut["output"][tops.show_cmd]["json"]
            logging.info(
                f"On device {tops.dut_name}, output of {tops.show_cmd} command is: \n{output}\n"
            )
            self.output += f"\nOutput of {tops.show_cmd} command is: \n{output}"

            vlans = output.get("vlans")
            static_vlans = [vlan for vlan in vlans if not vlans[vlan].get("dynamic")]

            for vlan in static_vlans:
                modified_vlan = vlan.zfill(4)
                no_vlan_name = ""
                tops.expected_output["vlans"].update({vlan: {"vlan_name_configured": True}})
                if vlans.get(vlan).get("name") == "VLAN%s" % modified_vlan:
                    no_vlan_name = vlans.get(vlan).get("name")

                tops.actual_output["vlans"].update(
                    {vlan: {"vlan_name_configured": not bool(no_vlan_name)}}
                )

            # Output message formation in case of test case fails.
            if tops.actual_output != tops.expected_output:
                tops.output_msg = ""
                no_name_configured = []
                for vlan, vlan_status in tops.expected_output.get("vlans").items():
                    actual_vlan_naming = (
                        tops.actual_output.get("vlans").get(vlan).get("vlan_name_configured")
                    )
                    if vlan_status["vlan_name_configured"] != actual_vlan_naming:
                        no_name_configured.append(vlan)
                tops.output_msg += (
                    f"For following VLANs name is not configured: {', '.join(no_name_configured)}."
                )

        except (AssertionError, AttributeError, LookupError, EapiError) as excep:
            tops.output_msg = tops.actual_output = str(excep).split("\n", maxsplit=1)[0]
            logging.error(
                f"On device {tops.dut_name}, Error while running the test case"
                f" is:\n{tops.actual_output}"
            )

        tops.test_result = tops.expected_output == tops.actual_output
        tops.parse_test_steps(self.test_security_rp_l2_vlan_name)
        tops.generate_report(tops.dut_name, self.output)
        assert tops.expected_output == tops.actual_output
