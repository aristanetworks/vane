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


class TestLLDP:
    """ Test cases for verification of lldp neighbors """

    test_data_exists = tests_tools.is_test_data_present("test_lldp_neighbors")
    test_duts, test_ids = tests_tools.get_duts_n_ids("test_lldp_neighbors")

    @pytest.mark.skipif(not test_data_exists, 
                        reason="Test not in catalog")

    @pytest.mark.parametrize("dut", test_duts, ids=test_ids)
    def test_lldp_neighbors(self, dut, tests_definitions):
        """
        TD: Test case for verification of the lldp neighbors
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
        tops.actual_output = {"lldp_information": {}}
        tops.expected_output = {"lldp_information": {}}
        self.output = ""
        shutdown_interface_details = {}
        inputs = test_params["inputs"][tops.dut_name]

        # Forming output message if the test result is passed.
        tops.output_msg = "LLDP neighbor information is correct."

        try:
            for test_input in inputs:
                neighbor = test_input["neighbors"][0]
                tops.expected_output["lldp_information"].update({neighbor["port"]: neighbor})
            logger.info(
                "On device %s, output of '%s' command is:\n%s\n",
                tops.dut_name,
                tops.show_cmd,
                command_output,
            )
            self.output += (
                f"On device {tops.dut_name}, output of {tops.show_cmd} command is:\n{command_output}"
            )

            lldp_neighbors = command_output.get("lldpNeighbors")
            assert lldp_neighbors, "LLDP neighbor information is not found in the command output."

            # Updating the actual output dictionary.
            actual_interfaces = []
            for interface in lldp_neighbors:
                port = interface["port"]
                if not port.startswith("ma"):
                    peer_device = interface.get("neighborDevice").split(".", maxsplit=1)[0]
                    actual_neighbor = { "port": port, "neighbor_device": peer_device, "neighbor_port": interface.get("neighborPort")}
                    tops.actual_output["lldp_information"].update({actual_neighbor["port"]: actual_neighbor})


            # Forming output message if the test result is failed
            if tops.actual_output != tops.expected_output:
                tops.output_msg = "LLDP neighbors are not setup correctly"

        except (AssertionError, AttributeError, LookupError, EapiError) as excep:
            tops.output_msg = tops.actual_output = str(excep).split("\n", maxsplit=1)[0]
            logger.error(
                "On device %s, Error while running the test case is:\n%s",
                tops.dut_name,
                tops.actual_output,
            )

        tops.test_result = tops.expected_output == tops.actual_output
        tops.parse_test_steps(self.test_lldp_neighbors)
        tops.generate_report(tops.dut_name, self.output)
        assert tops.expected_output == tops.actual_output
