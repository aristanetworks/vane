# Copyright (c) 2023 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.

"""
Test cases for verification of NTP functionality
"""

import pytest
from pyeapi.eapilib import EapiError
from vane.config import dut_objs, test_defs
from vane import tests_tools, test_case_logger


TEST_SUITE = "new_tests"
logger = test_case_logger.setup_logger(__file__)


class TestInterfaces:
    """ Test cases for interfaces states """

    test_data_exists = tests_tools.is_test_data_present("test_interfaces_status")
    test_duts, test_ids = tests_tools.get_duts_n_ids("test_interfaces_status")

    @pytest.mark.skipif(not test_data_exists, 
                        reason="Test not in catalog")

    @pytest.mark.parametrize("dut", test_duts, ids=test_ids)
    def test_interfaces_status(self, dut, tests_definitions):
        """
        TD: Test case for verification of the interfaces states
        Args:
          dut(dict): Details related to a particular device
          tests_definitions(dict): Test suite and test case parameters
        """

        # Creating the Testops class object and initialize the variables.
        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)
        self.output = ""
        test_params = tops.test_parameters
        show_cmd = tops.show_cmd
        command_output = dut["output"][show_cmd]["json"]
        inputs = test_params["inputs"][tops.dut_name]
        interfaces = []
        for test_input in inputs:
            interface = {"name": test_input["interfaces"][0]["name"],
                         "status": test_input["interfaces"][0]["status"],}
            interfaces.append(interface)
        logger.info(
            "On device %s, output of '%s' command is:\n%s\n",
            tops.dut_name,
            show_cmd, command_output
        )
        self.output += (
            f"\n\nOn device {tops.dut_name}, output of command {show_cmd} is:"
            f" \n{command_output}"
        )

        # Forming an output message if a test result is passed.
        tops.output_msg = ("The interfaces are correctly configured.")

        try:
            """
            TS: Running `show interfaces description` command on device and verifying that ,
            interfaces are correctly configured
            """
            intf_not_configured = []
            intf_wrong_state = []
            for interface in interfaces:
                if (intf_status := command_output["interfaceDescriptions"][interface["name"]]) is None:
                    intf_not_configured.append(interface.name)
                    continue

                status = "up" if intf_status["interfaceStatus"] in {"up", "connected"} else intf_status["interfaceStatus"]
                proto = "up" if intf_status["lineProtocolStatus"] in {"up", "connected"} else intf_status["lineProtocolStatus"]

                # If line protocol status is provided, prioritize checking against both status and line protocol status
                if interface.get("line_protocol_status", None):
                    if interface["status"] != status or interface["line_protocol_status"] != proto:
                        intf_wrong_state.append(f"{interface['name']} is {status}/{proto}")
                # If line protocol status is not provided and interface status is "up", expect both status and proto to be "up"
                # If interface status is not "up", check only the interface status without considering line protocol status
                elif (interface["status"] == "up" and (status != "up" or proto != "up")) or (interface["status"] != status):
                    intf_wrong_state.append(f"{interface['name']} is {status}/{proto}")


            # Forming an output message if a test result is failed
            if intf_not_configured or intf_wrong_state:
                tops.output_msg = f"Interfaces not configured <{inft_not_configure}> interfaces not in expected state <{intf_wrong_state}>"

        except (AssertionError, AttributeError, LookupError, EapiError) as excep:
            tops.actual_output = tops.output_msg = str(excep).split("\n", maxsplit=1)[0]
            logger.error(
                "On device %s: Error occurred while running the test case is:\n%s",
                tops.dut_name,
                tops.actual_output,
            )

        tops.test_result = not intf_not_configured and not intf_wrong_state
        tops.parse_test_steps(self.test_interfaces_status)
        tops.generate_report(tops.dut_name, self.output)
        assert not intf_not_configured and not intf_wrong_state
