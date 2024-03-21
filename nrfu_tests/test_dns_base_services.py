# Copyright (c) 2024 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.

"""
Test case for verification of DNS base services.
"""

import pytest
from pyeapi.eapilib import EapiError
from vane import test_case_logger
from vane.config import dut_objs, test_defs
from vane import tests_tools

TEST_SUITE = "nrfu_tests"
logging = test_case_logger.setup_logger(__file__)


@pytest.mark.nrfu_test
@pytest.mark.base_services
class DnsBaseServicesTests:
    """
    Test case for verification of DNS base services.
    """

    dut_parameters = tests_tools.parametrize_duts(TEST_SUITE, test_defs, dut_objs)
    test_duts = dut_parameters["test_dns_base_services"]["duts"]
    test_ids = dut_parameters["test_dns_base_services"]["ids"]

    @pytest.mark.parametrize("dut", test_duts, ids=test_ids)
    def test_dns_base_services(self, dut, tests_definitions):
        """
        TD: Test case for verification of DNS resolution functionality.
        Args:
            dut(dict): details related to a particular device.
            tests_definitions(dict): test suite and test case parameters.
        """
        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)
        self.output = ""
        test_params = tops.test_parameters["dns_name_server_check"]
        tops.actual_output = {"name_servers": {}}
        tops.expected_output = {"name_servers": {}}

        # Forming output message if the test result is passed
        tops.output_msg = (
            "Reverse name server lookup is successful for name servers configured on the device."
        )

        try:
            """
            TS: Running `show ip name-server` command on the device and verifying the
            DNS resolution by doing a reverse lookup for the IP of the first server configured.
            """
            output = dut["output"][tops.show_cmd]["json"]
            logging.info(
                (
                    f"On device {tops.dut_name}, the output of the `{tops.show_cmd}` command"
                    f" is: \n{output}\n"
                ),
            )
            self.output += f"\n\nOutput of {tops.show_cmd} command is: \n{output}"

            # Skipping test case if name servers are not configured on the device.
            version_verification = list(test_params.values())
            if not any(version_verification):
                tops.output_msg = (
                    f"Name servers are not configured on device {tops.dut_name}, hence skipping the"
                    " test case."
                )
                tests_tools.post_process_skip(tops, self.test_dns_base_services, self.output)
                pytest.skip(tops.output_msg)

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
                        logging.info(
                            (
                                f"On device {tops.dut_name}, the output of the `{bash_cmd}` command"
                                f" is: \n{bash_cmd_output}\n"
                            ),
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

            # Forming the output message if the test case failed
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
            logging.error(
                f"On device {tops.dut_name}, Error while running the test case"
                f" is:\n{tops.actual_output}"
            )

        tops.test_result = tops.expected_output == tops.actual_output
        tops.parse_test_steps(self.test_dns_base_services)
        tops.generate_report(tops.dut_name, self.output)
        assert tops.expected_output == tops.actual_output
