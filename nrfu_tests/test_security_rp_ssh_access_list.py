# Copyright (c) 2023 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.

"""
Test case to verify that ACL is configured for each VRF on which SSH is enabled
"""

import pytest
from pyeapi.eapilib import EapiError
from vane.logger import logger
from vane.config import dut_objs, test_defs
from vane import tests_tools

TEST_SUITE = "nrfu_tests"


@pytest.mark.nrfu_tests
@pytest.mark.security
class VrfSshAclTests:
    """
    Test case to verify that ACL is configured for each VRF on which SSH is enabled
    """

    dut_parameters = tests_tools.parametrize_duts(TEST_SUITE, test_defs, dut_objs)
    test_duts = dut_parameters["test_security_rp_ssh_access_list"]["duts"]
    test_ids = dut_parameters["test_security_rp_ssh_access_list"]["ids"]

    @pytest.mark.parametrize("dut", test_duts, ids=test_ids)
    def test_security_rp_ssh_access_list(self, dut, tests_definitions):
        """
        TD: Test case to verify that ACL is configured for each VRF on which SSH is enabled
        Args:
            dut(dict): details related to a particular DUT
            tests_definitions(dict): test suite and test case parameters.
        """

        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)
        self.output = ""
        tops.actual_output = {"vrfs": {}}
        tops.expected_output = {"vrfs": {}}
        tops.output_msg = "All VRFs that the API is active on an ACL is configured."
        show_cmds = tops.show_cmds[tops.dut_name]

        try:
            """
            TS: Running `show vrf` command on dut and collecting the list of VRFs.
            """
            vrfs = dut["output"][show_cmds[0]]["json"]
            logger.info(
                "On device %s, %s command output is:\n%s\n",
                tops.dut_name,
                show_cmds[0],
                vrfs,
            )
            self.output += f"Output of {show_cmds[0]} command is: \n{vrfs}\n"

            """
            TS: Running `show management ssh ip access-list summary` command on dut and verifying
            that VRF has SSH ACL configured.
            """
            ssh_acls = dut["output"][show_cmds[1]]["json"]
            logger.info(
                "On device %s, %s command output is:\n%s\n",
                tops.dut_name,
                show_cmds[1],
                ssh_acls,
            )
            self.output += f"Output of {show_cmds[1]} command is: \n{ssh_acls}\n"
            ssh_acls = ssh_acls["ipAclList"]["aclList"]
            assert ssh_acls, "SSH IP access-list summary details are not found."

            # Iterate over each vrf to see if SSH is enabled
            for vrf in vrfs["vrfs"]:
                ssh_status = ""
                ssh_cmd = "show management ssh"
                if vrf != "default":
                    ssh_cmd = f"show management ssh vrf {vrf}"
                try:
                    """
                    TS: Running `show management ssh` or `show management ssh vrf <vrf name>`
                    command on dut and verifying that SSH is enabled.
                    """
                    ssh_status = tops.run_show_cmds([ssh_cmd])
                    logger.info(
                        "On device %s, %s command output is:\n%s\n",
                        tops.dut_name,
                        ssh_cmd,
                        ssh_status,
                    )
                    self.output += f"Output of {ssh_cmd} command is: \n{ssh_status}\n"
                except EapiError as error:
                    if "not found under SSH" in str(error):
                        logger.info(
                            "On device %s, SSH on VRF %s is disabled.\n", tops.dut_name, vrf
                        )

                if ssh_status:
                    for line in ssh_status[0]["result"]["output"].split("\n"):
                        # Example of line it is looking for: SSHD status for Default VRF is enabled
                        if "SSHD status" in line:
                            ssh_enabled = line.split(" ")[-1]
                            if ssh_enabled == "enabled":
                                tops.expected_output["vrfs"][vrf] = {"ssh_acl_configured": True}
                                acl_found = False
                                for acl in ssh_acls:
                                    if vrf in acl["activeVrfs"]:
                                        acl_found = True
                                tops.actual_output["vrfs"][vrf] = {"ssh_acl_configured": acl_found}

            # Output message formation in case of testcase fails.
            if tops.actual_output != tops.expected_output:
                tops.output_msg = ""
                incorrect_acl_vrfs = []
                for vrf, vrf_details in tops.actual_output["vrfs"].items():
                    if not vrf_details.get("ssh_acl_configured"):
                        incorrect_acl_vrfs.append(vrf)
                if incorrect_acl_vrfs:
                    tops.output_msg += (
                        "For the following VRFs, SSH ACL is not configured on the device:"
                        f" {', '.join(incorrect_acl_vrfs)}."
                    )

        except (AssertionError, AttributeError, LookupError, EapiError) as excep:
            tops.output_msg = tops.actual_output = str(excep).split("\n", maxsplit=1)[0]
            logger.error(
                "On device %s, Error while running the testcase is:\n%s",
                tops.dut_name,
                tops.actual_output,
            )

        tops.test_result = tops.expected_output == tops.actual_output
        tops.parse_test_steps(self.test_security_rp_ssh_access_list)
        tops.generate_report(tops.dut_name, self.output)
        assert tops.expected_output == tops.actual_output
