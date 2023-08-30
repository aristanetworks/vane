# Copyright (c) 2022 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.

"""
Test cases for verification of system hardware free memory functionality
"""

import pytest
from pyeapi.eapilib import EapiError
from vane.logger import logger
from vane.config import dut_objs, test_defs
from vane import tests_tools

TEST_SUITE = "nrfu_tests"


@pytest.mark.nrfu_test
@pytest.mark.interfaces
class InterfaceErrorsAndDiscardsTests:
    """
    Test cases for verification of system hardware free memory functionality
    """

    dut_parameters = tests_tools.parametrize_duts(TEST_SUITE, test_defs, dut_objs)
    test_duts = dut_parameters["test_interface_errors_and_discards"]["duts"]
    test_ids = dut_parameters["test_interface_errors_and_discards"]["ids"]

    @pytest.mark.parametrize("dut", test_duts, ids=test_ids)
    def test_interface_errors_and_discards(self, dut, tests_definitions):
        """
        TD: Testcase for verification of all interfaces for errors.
        Args:
            dut(dict): details related to a particular DUT
            tests_definitions(dict): test suite and test case parameters.
        """
        self.tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)
        self.output = ""
        self.tops.actual_output = {}
        self.tops.expected_output = {}
        test_params = self.tops.test_parameters
        # error_threshold = test_params["errorThreshold"]

        # Forming output message if test result is passed
        self.tops.output_msg = "No Errors are found in all the interfaces."

        try:
            """
            TS: Running 'show interfaces' command on DUT and verifying the interfaces
            errors and discards.
            """
            self.show_interfaces = self.tops.run_show_cmds([self.tops.show_cmd])
            logger.info(
                "On device %s, output of %s command is:\n%s\n",
                self.tops.dut_name,
                self.tops.show_cmd,
                self.show_interfaces,
            )
            self.output += (
                f"\n\nOutput of {self.tops.show_cmd} command is: \n{self.show_interfaces }"
            )

            self.interfaces = self.show_interfaces[0]["result"]["interfaces"]
            assert self.interfaces, "Interfaces details are not found."

            for ethernets in self.interfaces:
                if "Ethernet" in ethernets or "Management" in ethernets:
                    # Input error detail
                    runts = self.interfaces[ethernets]["interfaceCounters"]["inputErrorsDetail"][
                        "runtFrames"
                    ]
                    fcs_errors = self.interfaces[ethernets]["interfaceCounters"][
                        "inputErrorsDetail"
                    ]["fcsErrors"]
                    alignment_errors = self.interfaces[ethernets]["interfaceCounters"][
                        "inputErrorsDetail"
                    ]["alignmentErrors"]
                    giant_frames = self.interfaces[ethernets]["interfaceCounters"][
                        "inputErrorsDetail"
                    ]["giantFrames"]
                    symbol_errors = self.interfaces[ethernets]["interfaceCounters"][
                        "inputErrorsDetail"
                    ]["symbolErrors"]

                    # Output error detail
                    deferred_transmissions = self.interfaces[ethernets]["interfaceCounters"][
                        "outputErrorsDetail"
                    ]["deferredTransmissions"]
                    collisions = self.interfaces[ethernets]["interfaceCounters"][
                        "outputErrorsDetail"
                    ]["collisions"]
                    late_collisions = self.interfaces[ethernets]["interfaceCounters"][
                        "outputErrorsDetail"
                    ]["lateCollisions"]

                    # Other Error details
                    in_discards = self.interfaces[ethernets]["interfaceCounters"]["inDiscards"]
                    total_in_errors = self.interfaces[ethernets]["interfaceCounters"][
                        "totalInErrors"
                    ]
                    out_discards = self.interfaces[ethernets]["interfaceCounters"]["outDiscards"]
                    total_out_errors = self.interfaces[ethernets]["interfaceCounters"][
                        "totalOutErrors"
                    ]
                    link_status_changes = self.interfaces[ethernets]["interfaceCounters"][
                        "linkStatusChanges"
                    ]

                    # Collecting actual and expected output.
                    self.tops.actual_output.update(
                        {
                            ethernets: {
                                "input_error_details": {
                                    "runts": runts > test_params["errorThreshold"],
                                    "fcs_errors": fcs_errors > test_params["errorThreshold"],
                                    "alignment_errors": (
                                        alignment_errors > test_params["errorThreshold"]
                                    ),
                                    "giant_frames": giant_frames > test_params["errorThreshold"],
                                    "symbol_errors": symbol_errors > test_params["errorThreshold"],
                                },
                                "output_error_details": {
                                    "deferred_transmissions": (
                                        deferred_transmissions > test_params["errorThreshold"]
                                    ),
                                    "collisions": collisions > test_params["errorThreshold"],
                                    "late_collisions": (
                                        late_collisions > test_params["errorThreshold"]
                                    ),
                                },
                                "other_error_details": {
                                    "in_discards": in_discards > test_params["errorThreshold"],
                                    "total_in_errors": (
                                        total_in_errors > test_params["errorThreshold"]
                                    ),
                                    "out_discards": out_discards > test_params["errorThreshold"],
                                    "total_out_errors": (
                                        total_out_errors > test_params["errorThreshold"]
                                    ),
                                    "link_status_changes": (
                                        link_status_changes > test_params["errorThreshold"]
                                    ),
                                },
                            }
                        }
                    )

                    self.tops.expected_output.update(
                        {
                            ethernets: {
                                "input_error_details": {
                                    "runts": False,
                                    "fcs_errors": False,
                                    "alignment_errors": False,
                                    "giant_frames": False,
                                    "symbol_errors": False,
                                },
                                "output_error_details": {
                                    "deferred_transmissions": False,
                                    "collisions": False,
                                    "late_collisions": False,
                                },
                                "other_error_details": {
                                    "in_discards": False,
                                    "total_in_errors": False,
                                    "out_discards": False,
                                    "total_out_errors": False,
                                    "link_status_changes": False,
                                },
                            }
                        }
                    )

            # Forming output message if test result is fail.
            if self.tops.actual_output != self.tops.expected_output:
                self.tops.output_msg = "\n"
                for interface, interface_details in self.tops.expected_output.items():
                    if interface_details != self.tops.actual_output.get(interface):
                        self.tops.output_msg += f"For {interface}:\n"
                        for err_category, err_details in interface_details.items():
                            if err_details != self.tops.actual_output.get(interface).get(
                                err_category
                            ):
                                self.tops.output_msg += f" in {err_category} "
                                for err_key, err_values in err_details.items():
                                    if err_values != self.tops.actual_output.get(interface).get(
                                        err_category
                                    ).get(err_key):
                                        self.tops.output_msg += f"error found for {err_key}\n\n"

        except (AssertionError, AttributeError, LookupError, EapiError) as excep:
            self.tops.output_msg = self.tops.actual_output = str(excep).split("\n", maxsplit=1)[0]
            logger.error(
                "On device %s, Error while running the testcase is:\n%s",
                self.tops.dut_name,
                self.tops.actual_output,
            )

        self.tops.test_result = self.tops.expected_output == self.tops.actual_output
        self.tops.parse_test_steps(self.test_interface_errors_and_discards)
        self.tops.generate_report(self.tops.dut_name, self.output)
        assert self.tops.expected_output == self.tops.actual_output
