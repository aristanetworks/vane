# Copyright (c) 2022 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.

"""
Test cases for verification of TACACS servers details
"""

import pytest
from pyeapi.eapilib import EapiError
from vane.logger import logger
from vane.config import dut_objs, test_defs
from vane import tests_tools

TEST_SUITE = "nrfu_tests"


@pytest.mark.nrfu_test
@pytest.mark.base_services
class TacacsServersTests:
    """
    Test cases for verification of TACACS servers details
    """

    dut_parameters = tests_tools.parametrize_duts(TEST_SUITE, test_defs, dut_objs)
    test_duts = dut_parameters["test_base_services_tacacs"]["duts"]
    test_ids = dut_parameters["test_base_services_tacacs"]["ids"]

    @pytest.mark.parametrize("dut", test_duts, ids=test_ids)
    def test_base_services_tacacs(self, dut, tests_definitions):
        """
        TD: Testcase for verification of TACACS servers details.
        Args:
            dut(dict): details related to a particular DUT
            tests_definitions(dict): test suite and test case parameters.
        """
        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)
        self.output = ""
        tops.actual_output, tops.expected_output = {"tacacs_servers_info": {}}, {
            "tacacs_servers_info": {}
        }

        # Forming output message if test result is passed
        tops.output_msg = "TACACS servers have no errors, timeouts, failures or disconnects."

        try:
            """
            TS: Running `show tacacs` command on DUT and verifying TACACS servers information
            is correct.
            """
            output = dut["output"][tops.show_cmd]["json"]
            logger.info(
                "On device %s, output of %s command is: \n%s\n",
                tops.dut_name,
                tops.show_cmd,
                output,
            )
            self.output += f"\n\nOutput of {tops.show_cmd} command is: \n{output}"
            tacacs_servers = output.get('tacacsServers')

            # Skipping testcase if TACACS servers are not configured.
            if not tacacs_servers:
                pytest.skip(f"No TACACS servers are configured on {tops.dut_name}.")
            else:
                for tacacs_server in tacacs_servers:
                    tacacs_hostname = tacacs_server.get("serverInfo").get("hostname")
                    tops.expected_output["tacacs_servers_info"].update(
                        {
                            tacacs_hostname: {
                                "received_errors": 0,
                                "connection_disconnects": 0,
                                "dns_errors": 0,
                                "send_timeouts": 0,
                                "connection_timeouts": 0,
                                "connection_failures": 0,
                                "received_timeouts": 0,
                            }
                        }
                    )
                    tops.actual_output["tacacs_servers_info"].update(
                        {
                            tacacs_hostname: {
                                "received_errors": tacacs_server.get("receiveErrors"),
                                "connection_disconnects": tacacs_server.get(
                                    "connectionDisconnects"
                                ),
                                "dns_errors": tacacs_server.get("dnsErrors"),
                                "send_timeouts": tacacs_server.get("sendTimeouts"),
                                "connection_timeouts": tacacs_server.get("connectionTimeouts"),
                                "connection_failures": tacacs_server.get("connectionFailures"),
                                "received_timeouts": tacacs_server.get("receiveTimeouts"),
                            }
                        }
                    )

                # Forming output message if test result is fail.
                if tops.expected_output != tops.actual_output:
                    tops.output_msg = ""
                    for hostname, tacacs_servers_info in tops.expected_output[
                        "tacacs_servers_info"
                    ].items():
                        actual_servers_info = tops.actual_output.get("tacacs_servers_info").get(
                            hostname
                        )
                        if tacacs_servers_info != actual_servers_info:
                            tops.output_msg = f"\nFor hostname {hostname}:"
                            for (error_name, error_value), actual_value in zip(
                                tacacs_servers_info.items(), actual_servers_info.values()
                            ):
                                if error_value != actual_value:
                                    tops.output_msg += (
                                        f"\nExpected value of {error_name.replace('_', ' ') } is"
                                        f" '{error_value}' however actual found as"
                                        f" '{actual_value}'."
                                    )

        except (AssertionError, AttributeError, LookupError, EapiError) as excep:
            tops.output_msg = tops.actual_output = str(excep).split("\n", maxsplit=1)[0]
            logger.error(
                "On device %s, Error while running the testcase is:\n%s",
                tops.dut_name,
                tops.actual_output,
            )

        tops.test_result = tops.expected_output == tops.actual_output
        tops.parse_test_steps(self.test_base_services_tacacs)
        tops.generate_report(tops.dut_name, self.output)
        assert tops.expected_output == tops.actual_output
