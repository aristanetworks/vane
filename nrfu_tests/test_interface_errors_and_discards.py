# Copyright (c) 2023 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.

"""
Test cases for verification of errors/discards on all the interfaces
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
    Test cases for verification of errors/discards on all the interfaces
    """

    dut_parameters = tests_tools.parametrize_duts(TEST_SUITE, test_defs, dut_objs)
    test_duts = dut_parameters["test_interface_errors_and_discards"]["duts"]
    test_ids = dut_parameters["test_interface_errors_and_discards"]["ids"]

    @pytest.mark.parametrize("dut", test_duts, ids=test_ids)
    def test_interface_errors_and_discards(self, dut, tests_definitions):
        """
        TD: Testcase for verification of errors/discards on all the interfaces.
        Args:
            dut(dict): details related to a particular DUT
            tests_definitions(dict): test suite and test case parameters.
        """
        self.tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)
        self.output = ""
        self.tops.actual_output = {}
        self.tops.expected_output = {}

        # Forming output message if test result is passed
        self.tops.output_msg = "Errors/discards are not found on any of the interface."

        try:
            """
            TS: Running 'show interfaces' command on DUT and verifying the interfaces
            errors and discards.
            """
            self.show_interfaces = dut["output"][self.tops.show_cmd]["json"]
            logger.info(
                "On device %s, output of %s command is:\n%s\n",
                self.tops.dut_name,
                self.tops.show_cmd,
                self.show_interfaces,
            )
            self.output += (
                f"\n\nOutput of {self.tops.show_cmd} command is: \n{self.show_interfaces }"
            )
            self.show_interfaces = self.show_interfaces["interfaces"]
            assert self.show_interfaces, "Interfaces details are not found."

            for ethernets in self.show_interfaces:
                if "Ethernet" in ethernets or "Management" in ethernets:
                    if "." in ethernets:
                        continue
                    if "Management0" in ethernets:
                        continue

                    # Collecting actual and expected output.
                    self.tops.actual_output.update(
                        {
                            ethernets: {
                                "input_errors": {
                                    "runts_frames": (
                                        self.show_interfaces.get(ethernets)
                                        .get("interfaceCounters")
                                        .get("inputErrorsDetail")
                                        .get("runtFrames")
                                    ),
                                    "fcs_errors": (
                                        self.show_interfaces.get(ethernets)
                                        .get("interfaceCounters")
                                        .get("inputErrorsDetail")
                                        .get("fcsErrors")
                                    ),
                                    "alignment_errors": (
                                        self.show_interfaces.get(ethernets)
                                        .get("interfaceCounters")
                                        .get("inputErrorsDetail")
                                        .get("alignmentErrors")
                                    ),
                                    "giant_frames": (
                                        self.show_interfaces.get(ethernets)
                                        .get("interfaceCounters")
                                        .get("inputErrorsDetail")
                                        .get("giantFrames")
                                    ),
                                    "symbol_errors": (
                                        self.show_interfaces.get(ethernets)
                                        .get("interfaceCounters")
                                        .get("inputErrorsDetail")
                                        .get("symbolErrors")
                                    ),
                                },
                                "output_errors": {
                                    "deferred_transmissions": (
                                        self.show_interfaces.get(ethernets)
                                        .get("interfaceCounters")
                                        .get("outputErrorsDetail")
                                        .get("deferredTransmissions")
                                    ),
                                    "collisions_error": (
                                        self.show_interfaces.get(ethernets)
                                        .get("interfaceCounters")
                                        .get("outputErrorsDetail")
                                        .get("collisions")
                                    ),
                                    "late_collisions": (
                                        self.show_interfaces.get(ethernets)
                                        .get("interfaceCounters")
                                        .get("outputErrorsDetail")
                                        .get("lateCollisions")
                                    ),
                                },
                                "other_errors": {
                                    "in_discards": (
                                        self.show_interfaces.get(ethernets)
                                        .get("interfaceCounters")
                                        .get("inDiscards")
                                    ),
                                    "total_in_errors": (
                                        self.show_interfaces.get(ethernets)
                                        .get("interfaceCounters")
                                        .get("totalInErrors")
                                    ),
                                    "out_discards": (
                                        self.show_interfaces.get(ethernets)
                                        .get("interfaceCounters")
                                        .get("outDiscards")
                                    ),
                                    "total_out_errors": (
                                        self.show_interfaces.get(ethernets)
                                        .get("interfaceCounters")
                                        .get("totalOutErrors")
                                    ),
                                    "link_status_changes": (
                                        self.show_interfaces.get(ethernets)
                                        .get("interfaceCounters")
                                        .get("linkStatusChanges")
                                    ),
                                },
                            }
                        }
                    )

                    self.tops.expected_output.update(
                        {
                            ethernets: {
                                "input_errors": {
                                    "runts_frames": 0,
                                    "fcs_errors": 0,
                                    "alignment_errors": 0,
                                    "giant_frames": 0,
                                    "symbol_errors": 0,
                                },
                                "output_errors": {
                                    "deferred_transmissions": 0,
                                    "collisions_error": 0,
                                    "late_collisions": 0,
                                },
                                "other_errors": {
                                    "in_discards": 0,
                                    "total_in_errors": 0,
                                    "out_discards": 0,
                                    "total_out_errors": 0,
                                    "link_status_changes": 0,
                                },
                            }
                        }
                    )

            # Forming output message if test result is fail.
            if self.tops.actual_output != self.tops.expected_output:
                self.tops.output_msg = "\n"
                for interface, interface_details in self.tops.expected_output.items():
                    if interface_details != self.tops.actual_output.get(interface):
                        self.tops.output_msg += (
                            f"\nFor {interface} following errors/discards are observed:\n"
                        )
                        for err_category, err_details in interface_details.items():
                            if err_details != self.tops.actual_output.get(interface).get(
                                err_category
                            ):
                                self.tops.output_msg += (
                                    f"{(err_category.replace('_', ' ')).capitalize()}: "
                                )
                                self.err_keys = []
                                for err_key, err_values in err_details.items():
                                    if err_values != self.tops.actual_output.get(interface).get(
                                        err_category
                                    ).get(err_key):
                                        self.err_keys.append(err_key.replace("_", " "))
                                self.tops.output_msg += f"{', '.join(self.err_keys)}\n"

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
