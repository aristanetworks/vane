# Copyright (c) 2023 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.

"""
Test case to verify that ACL is configured for each VRF on which API is enabled.
"""

import pytest
from pyeapi.eapilib import EapiError
from vane.config import dut_objs, test_defs
from vane import tests_tools, test_case_logger

TEST_SUITE = "nrfu_tests"
logging = test_case_logger.setup_logger(__file__)


@pytest.mark.nrfu_test
@pytest.mark.security
class AclsApiAccessTests:
    """
    Test case to verify that ACL is configured for each VRF on which API is enabled.
    """

    dut_parameters = tests_tools.parametrize_duts(TEST_SUITE, test_defs, dut_objs)
    test_duts = dut_parameters["test_acls_api_vrfs_enabled"]["duts"]
    test_ids = dut_parameters["test_acls_api_vrfs_enabled"]["ids"]

    @pytest.mark.parametrize("dut", test_duts, ids=test_ids)
    def test_acls_api_vrfs_enabled(self, dut, tests_definitions):
        """
        TD: Test case to verify that ACL is configured for each VRF on which API is enabled.
        Args:
            dut(dict): details related to a particular DUT
            tests_definitions(dict): test suite and test case parameters.
        """
        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)
        tops.expected_output = {"vrfs": {}}
        tops.actual_output = {"vrfs": {}}
        self.output = ""
        show_cmds = tops.show_cmds[tops.dut_name]

        # Forming output message if the test result is passed.
        tops.output_msg = "ACL is configured on all VRFs which have API enabled."

        try:
            """
            TS: Running `show management API http-commands` command on dut
            and collecting the list of VRFs.
            """
            output_api_vrfs = dut["output"][show_cmds[0]]["json"]
            logging.info(
                f"On device {tops.dut_name}, output of {show_cmds[0]} command"
                f" is:\n{output_api_vrfs}\n"
            )
            self.output = f"Output of {show_cmds[0]} command is:\n{output_api_vrfs}\n"

            """
            TS: Running `show management API http-commands ip access-list summary` command on dut
            and verifying that all the VRFs are API ACL configured.
            """
            output_api_acls = dut["output"][show_cmds[1]]["json"]
            logging.info(
                f"On device {tops.dut_name}, output of {show_cmds[1]} command"
                f" is:\n{output_api_acls}\n"
            )
            self.output = f"Output of {show_cmds[1]} command is:\n{output_api_acls}\n"

            # Collecting VRFs and ACLs from output.
            api_vrfs = output_api_vrfs.get("vrfs")
            api_acls = output_api_acls.get("ipAclList").get("aclList")
            assert api_vrfs, "Vrfs details are not found in the output."

            assert api_acls, "ACL details for APIs are not found in the output."

            # Collecting actual and expected output.
            for vrf in api_vrfs:
                acl_found = False
                for acl in api_acls:
                    tops.expected_output["vrfs"].update({vrf: {"api_acl_configured": True}})
                    if vrf in acl["activeVrfs"]:
                        acl_found = True
                        tops.actual_output["vrfs"].update({vrf: {"api_acl_configured": True}})
                        break
                if not acl_found:
                    tops.actual_output["vrfs"].update({vrf: {"api_acl_configured": False}})

            # Forming output message if the test result is failed.
            if tops.actual_output != tops.expected_output:
                tops.output_msg = ""
                non_configured_vrfs = []
                for vrf_name, vrf_status in tops.expected_output["vrfs"].items():
                    if vrf_status != tops.actual_output["vrfs"].get(vrf_name):
                        non_configured_vrfs.append(vrf_name)
                vrf_configured_status = ", ".join(non_configured_vrfs)
                tops.output_msg += (
                    "For the following VRFs, API ACL is not configured on the device:"
                    f" {vrf_configured_status}."
                )

        except (AssertionError, AttributeError, LookupError, EapiError) as excep:
            tops.output_msg = tops.actual_output = str(excep).split("\n", maxsplit=1)[0]
            logging.error(
                f"On device {tops.dut_name}, Error while running the test case"
                f" is:\n{tops.actual_output}"
            )

        tops.test_result = tops.expected_output == tops.actual_output
        tops.parse_test_steps(self.test_acls_api_vrfs_enabled)
        tops.generate_report(tops.dut_name, self.output)
        assert tops.expected_output == tops.actual_output
