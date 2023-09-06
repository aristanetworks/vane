# Copyright (c) 2023 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.

"""
Testcases for verification of DNS base services.
"""

import pytest
from pyeapi.eapilib import EapiError
from vane.logger import logger
from vane.config import dut_objs, test_defs
from vane import tests_tools

TEST_SUITE = "nrfu_tests"


@pytest.mark.nrfu_test
@pytest.mark.base_services
class DnsBaseServicesTests:
    """
    Testcases for verification of DNS base services.
    """

    dut_parameters = tests_tools.parametrize_duts(TEST_SUITE, test_defs, dut_objs)
    test_duts = dut_parameters["test_dns_base_services"]["duts"]
    test_ids = dut_parameters["test_dns_base_services"]["ids"]

    @pytest.mark.parametrize("dut", test_duts, ids=test_ids)
    def test_dns_base_services(self, dut, tests_definitions):
        """
        TD: Testcase for verification of DNS resolution functionality.
        Args:
            dut(dict): details related to a particular device.
            tests_definitions(dict): test suite and test case parameters.
        """
        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)
        self.output = ""
        test_params = tops.test_parameters["dns_name_server_check"]
        tops.actual_output = {"name_servers": {}}
        tops.expected_output = {"name_servers": {}}

        # Forming output message if test result is passed
        tops.output_msg = (
            "Reverse name server lookup is successful for name servers configured on the device."
        )

        try:
            """
            TS: Running `show ip name-server` command on the device and verifying the
            DNS resolution by doing a reverse lookup for the IP of the first server configured.
            """
            output = dut["output"][tops.show_cmd]["json"]
            logger.info(
                "On device %s, output of %s command is: \n%s\n",
                tops.dut_name,
                tops.show_cmd,
                output,
            )
            self.output += f"\n\nOutput of {tops.show_cmd} command is: \n{output}"

            # Skipping testcase if name servers are not configured on the device.
            version_verification = list(test_params.values())
            if not any(version_verification):
                pytest.skip(
                    f"Name servers are not configured on {tops.dut_name}, hence skipping the"
                    " testcase."
                )

            try:
                for ip_version_verification, verification_status in test_params.items():
                    if verification_status:
                        ip_version = ip_version_verification.split("_")[0]
                        tops.actual_output["name_servers"].update({ip_version: {}})
                        tops.expected_output["name_servers"].update({ip_version: {}})
                        if "ipv4" in ip_version_verification:
                            vx_name_servers = output.get("v4NameServers")
                        else:
                            vx_name_servers = output.get("v6NameServers")
                        assert (
                            vx_name_servers
                        ), f"Name server details are not found for {ip_version}.\n"

                        reverse_resolution_ip = vx_name_servers[0]
                        tops.expected_output["name_servers"].update(
                            {
                                ip_version: {
                                    reverse_resolution_ip: {"reverse_nslookup_successful": True}
                                }
                            }
                        )

                        bash_cmd = f"bash timeout 10 nslookup {reverse_resolution_ip}"
                        bash_cmd_output = tops.run_show_cmds([bash_cmd])
                        logger.info(
                            "On device %s, output of %s command is: \n%s\n",
                            tops.dut_name,
                            bash_cmd,
                            bash_cmd_output,
                        )
                        tops.actual_output["name_servers"].update(
                            {
                                ip_version: {
                                    reverse_resolution_ip: {"reverse_nslookup_successful": True}
                                }
                            }
                        )

            except EapiError:
                tops.actual_output["name_servers"].update(
                    {ip_version: {reverse_resolution_ip: {"reverse_nslookup_successful": False}}}
                )

            # Forming the output message if the testcase is failed
            if tops.actual_output != tops.expected_output:
                tops.output_msg = "\n"
                for version_status in tops.actual_output["name_servers"].values():
                    for ip_address, dns_status in version_status.items():
                        if not dns_status["reverse_nslookup_successful"]:
                            tops.output_msg += (
                                "Reverse name server lookup is failed for name server"
                                f" {ip_address}.\n"
                            )

        except (AssertionError, AttributeError, LookupError, EapiError) as excep:
            tops.output_msg = tops.actual_output = str(excep).split("\n", maxsplit=1)[0]
            logger.error(
                "On device %s, Error while running the testcase is:\n%s",
                tops.dut_name,
                tops.actual_output,
            )

        tops.test_result = tops.expected_output == tops.actual_output
        tops.parse_test_steps(self.test_dns_base_services)
        tops.generate_report(tops.dut_name, self.output)
        assert tops.expected_output == tops.actual_output
