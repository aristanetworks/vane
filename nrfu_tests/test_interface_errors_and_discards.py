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

            for interface in self.show_interfaces:
                if "Ethernet" in interface or "Management" in interface:

                    # sub-interfaces doesn't contain error information
                    if "." in interface:
                        continue

                    # Ma0 is a logical interface and doesn't contain error information
                    if "Management0" in interface:
                        continue

                    input_errors_details = (
                        self.show_interfaces.get(interface)
                        .get("interfaceCounters")
                        .get("inputErrorsDetail")
                    )
                    output_errors_details = (
                        self.show_interfaces.get(interface)
                        .get("interfaceCounters")
                        .get("outputErrorsDetail")
                    )
                    other_errors_details = self.show_interfaces.get(interface).get(
                        "interfaceCounters"
                    )

                    # Collecting actual and expected output.
                    self.tops.actual_output.update(
                        {
                            interface: {
                                "input_errors": {
                                    "runts_frames": input_errors_details.get("runtFrames"),
                                    "fcs_errors": input_errors_details.get("fcsErrors"),
                                    "alignment_errors": input_errors_details.get("alignmentErrors"),
                                    "giant_frames": input_errors_details.get("giantFrames"),
                                    "symbol_errors": input_errors_details.get("symbolErrors"),
                                },
                                "output_errors": {
                                    "deferred_transmissions": output_errors_details.get(
                                        "deferredTransmissions"
                                    ),
                                    "collisions_error": output_errors_details.get("collisions"),
                                    "late_collisions": output_errors_details.get("lateCollisions"),
                                },
                                "other_errors": {
                                    "in_discards": other_errors_details.get("inDiscards"),
                                    "total_in_errors": other_errors_details.get("totalInErrors"),
                                    "out_discards": other_errors_details.get("outDiscards"),
                                    "total_out_errors": other_errors_details.get("totalOutErrors"),
                                    "link_status_changes": other_errors_details.get(
                                        "linkStatusChanges"
                                    ),
                                },
                            }
                        }
                    )

                    input_errors_keys = (
                        self.tops.actual_output.get(interface).get("input_errors").keys()
                    )
                    output_errors_keys = (
                        self.tops.actual_output.get(interface).get("output_errors").keys()
                    )
                    other_errors_keys = (
                        self.tops.actual_output.get(interface).get("other_errors").keys()
                    )
                    self.tops.expected_output.update(
                        {
                            interface: {
                                "input_errors": dict.fromkeys(input_errors_keys, 0),
                                "output_errors": dict.fromkeys(output_errors_keys, 0),
                                "other_errors": dict.fromkeys(other_errors_keys, 0),
                            }
                        }
                    )

            # Forming output message if test result is fail.
            if self.tops.actual_output != self.tops.expected_output:
                self.tops.output_msg = "\n"
                for interface, interface_details in self.tops.expected_output.items():
                    interface_name = self.tops.actual_output.get(interface)
                    if interface_details != interface_name:
                        self.tops.output_msg += (
                            f"\nFor {interface}, following non-zero errors/discards are observed:\n"
                        )
                        for err_category, err_details in interface_details.items():
                            if err_details != interface_name.get(err_category):
                                self.tops.output_msg += (
                                    f"{(err_category.replace('_', ' ')).capitalize()}: "
                                )
                                self.err_keys = []
                                for err_key, err_values in err_details.items():
                                    if err_values != interface_name.get(err_category).get(err_key):
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
