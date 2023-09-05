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
        TD: Testcase for verification of DNS base services.
        Args:
            dut(dict): details related to a particular device.
            tests_definitions(dict): test suite and test case parameters.
        """
        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)
        self.output = ""
        test_params = tops.test_parameters["dns_name_server_check"]
        tops.actual_output = {}
        tops.expected_output = {}

        # Forming output message if test result is passed
        tops.output_msg = "IPv4 and IPv6 name servers are configured on the device."

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

            # Skipping testcase if SSO protocol is not configured on the device.
            version_verification = [element for element in [test_params.values()] if bool(element)]
            if all(list(version_verification)[0]):
                pytest.skip(
                    f"Name server is not configured on {tops.dut_name}, hence skipping the"
                    " testcase."
                )

            try:
                for ip_version_verification, verification_status in test_params.items():
                    if verification_status and "ipv4" in ip_version_verification:
                        ip_version = ip_version_verification.split("_")[0]
                        vx_name_servers = output["v4NameServers"]
                    elif verification_status and "ipv6" in ip_version_verification:
                        ip_version = ip_version_verification.split("_")[0]
                        vx_name_servers = output["v6NameServers"]
                    tops.expected_output.update({f"{ip_version}_dns_request_successful": True})
                    reverse_resolution_ip = vx_name_servers[0]
                    bash_cmd = f"bash timeout 10 nslookup {reverse_resolution_ip}"
                    bash_cmd_output = tops.run_show_cmds([bash_cmd])
                    logger.info(
                        "On device %s, output of %s command is: \n%s\n",
                        tops.dut_name,
                        bash_cmd,
                        bash_cmd_output,
                    )
                    tops.actual_output.update({f"{ip_version}_dns_request_successful": True})

            except EapiError:
                tops.actual_output.update({f"{ip_version}_dns_request_successful": False})

            # Forming the output message if the testcase is failed
            if tops.actual_output != tops.expected_output:
                tops.output_msg = "\n"
                for name_server_details, dns_status in tops.actual_output.items():
                    ip_version = name_server_details.split("_")[0]
                    if not dns_status:
                        tops.output_msg += (
                            f"DNS request is not successful for {ip_version} version.\n"
                        )

        except (AttributeError, LookupError, EapiError) as excep:
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
