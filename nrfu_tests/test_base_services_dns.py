# Copyright (c) 2023 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.

"""
Testcases for verification of DNS base services.
"""

import pytest
import pyeapi.eapilib
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

    def verify_dns(self, vx_name_servers, ip_version, ipvx_fail_if_not_configured, dut, tops):
        """
        Utility function for the verification of DNS functionality.
        Args:
            vx_name_servers(String): IP address of the name server.
            ipvx_fail_if_not_configured(boolean):
            dut(dict): details related to a particular device
            tops(dict): Testops class object
        Returns:
            dict: Actual output for verification
        """
        ip_version = ip_version.split("_")[0]
        actual_output = {}

        try:
            if ipvx_fail_if_not_configured:
                assert (
                    vx_name_servers
                ), f"For {ip_version}, name-server is not configured on device{dut['name']}.\n"

            reverse_resolution_ip = vx_name_servers[0]
            bash_cmd = f"bash timeout 10 nslookup {reverse_resolution_ip}"
            output = tops.run_show_cmds([bash_cmd])
            logger.info(
                "On device %s, output of %s command is: \n%s\n",
                tops.dut_name,
                bash_cmd,
                output,
            )
            actual_output = {"dns_request_successful": True}

        except (AssertionError, pyeapi.eapilib.CommandError):
            actual_output = {"dns_request_successful": False}

        return actual_output

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

        # Forming output message if test result is passed
        tops.output_msg = "IPv4 and IPv6 name servers are configured on the device."

        try:
            """
            TS: Running 'show ip name-server' command on the device and verifying the
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
            if not output.get("nameServerConfigs"):
                pytest.skip(
                    f"Name server is not configured on {tops.dut_name}, hence skipping the"
                    " testcase."
                )

            # Separating out v4 and v6 name servers
            v4_name_servers = output["v4NameServers"]
            v6_name_servers = output["v6NameServers"]

            tops.actual_output.update(
                {
                    "ipv4_name_server_details": self.verify_dns(
                        v4_name_servers,
                        list(test_params.keys())[0],
                        test_params["ipv4_fail_if_not_configured"],
                        dut,
                        tops,
                    )
                }
            )

            tops.actual_output.update(
                {
                    "ipv6_name_server_details": self.verify_dns(
                        v6_name_servers,
                        list(test_params.keys())[1],
                        test_params["ipv4_fail_if_not_configured"],
                        dut,
                        tops,
                    )
                }
            )

            # Forming the output message if the testcase is failed
            if tops.actual_output != tops.expected_output:
                tops.output_msg = "\n"
                for name_server, server_details in tops.actual_output.items():
                    ip_version = name_server.split("_")[0]
                    if not server_details["dns_request_successful"]:
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
