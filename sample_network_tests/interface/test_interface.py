#!/usr/bin/env python3
#
# Copyright (c) 2023, Arista Networks EOS+
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
# * Neither the name of the Arista nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

""" Tests to validate base feature status."""

import pytest
from pyeapi.eapilib import EapiError
from vane import tests_tools, test_case_logger
from vane.config import dut_objs, test_defs

TEST_SUITE = __file__
LOG_FILE = {"parameters": {"show_log": "show_output.log"}}

dut_parameters = tests_tools.parametrize_duts(TEST_SUITE, test_defs, dut_objs)
test1_duts = dut_parameters["test_if_intf_protocol_status_is_connected_on_"]["duts"]
test1_ids = dut_parameters["test_if_intf_protocol_status_is_connected_on_"]["ids"]

test2_duts = dut_parameters["test_if_intf_link_status_is_connected_on_"]["duts"]
test2_ids = dut_parameters["test_if_intf_link_status_is_connected_on_"]["ids"]

test3_duts = dut_parameters["test_if_intf_phy_status_connected_on_"]["duts"]
test3_ids = dut_parameters["test_if_intf_phy_status_connected_on_"]["ids"]

test4_duts = dut_parameters["test_if_intf_counters_has_input_errors_on_"]["duts"]
test4_ids = dut_parameters["test_if_intf_counters_has_input_errors_on_"]["ids"]

test5_duts = dut_parameters["test_if_intf_counters_has_output_errors_on_"]["duts"]
test5_ids = dut_parameters["test_if_intf_counters_has_output_errors_on_"]["ids"]

test6_duts = dut_parameters["test_if_intf_counters_has_frame_too_short_errors_on_"]["duts"]
test6_ids = dut_parameters["test_if_intf_counters_has_frame_too_short_errors_on_"]["ids"]

test7_duts = dut_parameters["test_if_intf_counters_has_frame_too_long_errors_on_"]["duts"]
test7_ids = dut_parameters["test_if_intf_counters_has_frame_too_long_errors_on_"]["ids"]

test8_duts = dut_parameters["test_if_intf_counters_has_fcs_errors_on_"]["duts"]
test8_ids = dut_parameters["test_if_intf_counters_has_fcs_errors_on_"]["ids"]

test9_duts = dut_parameters["test_if_intf_counters_has_alignment_errors_on_"]["duts"]
test9_ids = dut_parameters["test_if_intf_counters_has_alignment_errors_on_"]["ids"]

test10_duts = dut_parameters["test_if_intf_counters_has_symbol_errors_on_"]["duts"]
test10_ids = dut_parameters["test_if_intf_counters_has_symbol_errors_on_"]["ids"]

test11_duts = dut_parameters["test_if_interface_errors_on_"]["duts"]
test11_ids = dut_parameters["test_if_interface_errors_on_"]["ids"]

test12_duts = dut_parameters["test_interface_utilization_on_"]["duts"]
test12_ids = dut_parameters["test_interface_utilization_on_"]["ids"]

test13_duts = dut_parameters["test_if_intf_out_counters_are_discarding_on_"]["duts"]
test13_ids = dut_parameters["test_if_intf_out_counters_are_discarding_on_"]["ids"]

test14_duts = dut_parameters["test_if_intf_in_counters_are_discarding_on_"]["duts"]
test14_ids = dut_parameters["test_if_intf_in_counters_are_discarding_on_"]["ids"]

test15_duts = dut_parameters["test_if_intf_mtu_is_correct_on_"]["duts"]
test15_ids = dut_parameters["test_if_intf_mtu_is_correct_on_"]["ids"]

logging = test_case_logger.setup_logger(__file__)


@pytest.mark.demo
@pytest.mark.nrfu
@pytest.mark.interface_baseline_health
@pytest.mark.interface
class InterfaceStatusTests:
    """Interface Status Test Suite"""

    @pytest.mark.virtual
    @pytest.mark.physical
    @pytest.mark.parametrize("dut", test1_duts, ids=test1_ids)
    def test_if_intf_protocol_status_is_connected_on_(self, dut, tests_definitions):
        """TD: Verify the interfaces of interest protocol statuses are up

        Args:
            dut (dict): Encapsulates dut details including name, connection
            tests_definitions (dict): Test parameters
        """

        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)

        for interface in tops.interface_list:
            try:
                """
                TS: Run show command 'show interfaces status' on dut
                """
                interface_name = interface["interface_name"].replace(" ", "")

                self.output = dut["output"][tops.show_cmd]["json"]["interfaceStatuses"]
                assert self.output, "No Interface Details are available"
                logging.info(
                    f"On device {tops.dut_name}"
                    f" output of {tops.show_cmd} command is: {self.output}"
                )

                tops.actual_output = self.output[interface_name]["lineProtocolStatus"]

            except (
                AssertionError,
                AttributeError,
                LookupError,
                EapiError,
            ) as exception:
                logging.error(
                    f"Error occurred during the testsuite execution on dut:"
                    f" {tops.dut_name} is {str(exception)}"
                )
                tops.actual_output = str(exception)

            if tops.actual_output == tops.expected_output:
                tops.output_msg += (
                    f"On interface {interface_name}: interface link "
                    f"line protocol status is set to: {tops.actual_output}"
                    f"which is correct.\n\n"
                )
            else:
                tops.output_msg += (
                    f"On interface {interface_name}: interface link "
                    f"line protocol status is set to: {tops.actual_output}"
                    f", while the expected status is {tops.expected_output}.\n\n"
                )

            tops.actual_results.append(tops.actual_output)
            tops.expected_results.append(tops.expected_output)

        tops.actual_output, tops.expected_output = (
            tops.actual_results,
            tops.expected_results,
        )

        """
        TS: Creating test report based on results
        """
        tops.parse_test_steps(self.test_if_intf_protocol_status_is_connected_on_)
        tops.test_result = tops.actual_output == tops.expected_output
        tops.generate_report(tops.dut_name, tops.output_msg)
        assert tops.actual_output == tops.expected_output

    @pytest.mark.virtual
    @pytest.mark.physical
    @pytest.mark.parametrize("dut", test2_duts, ids=test2_ids)
    def test_if_intf_link_status_is_connected_on_(self, dut, tests_definitions):
        """TD: Verify the interfaces of interest link statuses are up

        Args:
            dut (dict): Encapsulates dut details including name, connection
            tests_definitions (dict): Test parameters
        """
        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)

        for interface in tops.interface_list:
            try:
                """
                TS: Run show command 'show interfaces status' on dut
                """
                interface_name = interface["interface_name"].replace(" ", "")

                self.output = dut["output"][tops.show_cmd]["json"]["interfaceStatuses"]
                assert self.output, "No Extensions are available"
                logging.info(
                    f"On device {tops.dut_name}"
                    f" output of {tops.show_cmd} command is: {self.output}"
                )

                tops.actual_output = self.output[interface_name]["linkStatus"]

            except (
                AssertionError,
                AttributeError,
                LookupError,
                EapiError,
            ) as exception:
                logging.error(
                    f"Error occurred during the testsuite execution on dut:"
                    f" {tops.dut_name} is {str(exception)}"
                )
                tops.actual_output = str(exception)

            if tops.actual_output == tops.expected_output:
                tops.output_msg += (
                    f"On interface {interface_name}: interface link "
                    f" status is set to: {tops.actual_output}"
                    f"which is correct.\n\n"
                )
            else:
                tops.output_msg += (
                    f"On interface {interface_name}: interface link "
                    f" status is set to: {tops.actual_output}"
                    f", while the expected status is {tops.expected_output}.\n\n"
                )

            tops.actual_results.append(tops.actual_output)
            tops.expected_results.append(tops.expected_output)

        tops.actual_output, tops.expected_output = (
            tops.actual_results,
            tops.expected_results,
        )

        """
        TS: Creating test report based on results
        """
        tops.parse_test_steps(self.test_if_intf_link_status_is_connected_on_)
        tops.test_result = tops.actual_output == tops.expected_output
        tops.generate_report(tops.dut_name, tops.output_msg)
        assert tops.actual_output == tops.expected_output


@pytest.mark.nrfu
@pytest.mark.interface_baseline_health
@pytest.mark.interface
class InterfacePhyTests:
    """Interface Status Test Suite"""

    @pytest.mark.physical
    @pytest.mark.parametrize("dut", test3_duts, ids=test3_ids)
    def test_if_intf_phy_status_connected_on_(self, dut, tests_definitions):
        """TD: Verify the interfaces of interest physical state is link up

        Args:
            dut (dict): Encapsulates dut details including name, connection
            tests_definitions (dict): Test parameters
        """

        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)

        if not tests_tools.verify_veos(dut):
            try:
                """
                TS: Run show command 'show interfaces phy detail' on dut
                """
                for interface in tops.interface_list:
                    interface_name = interface["interface_name"].replace(" ", "")

                    self.output = dut["output"][tops.show_cmd]["json"]["interfacePhyStatuses"]
                    assert self.output, "No InterfacePhysical Details are available"
                    logging.info(
                        f"On device {tops.dut_name}"
                        f" output of {tops.show_cmd} command is: {self.output}"
                    )

                    tops.actual_output = self.output[interface_name]["phyStatuses"][0]["phyState"][
                        "value"
                    ]

                    if tops.actual_output == tops.expected_output:
                        tops.output_msg += (
                            f"On interface {interface_name}: "
                            f"physical detail PHY state is set to: "
                            f"{tops.actual_output}, which is the correct state.\n\n"
                        )
                    else:
                        tops.output_msg += (
                            f"On interface {interface_name}: "
                            f"physical detail PHY state is set to: "
                            f"{tops.actual_output}, while the expected state is "
                            f"{tops.expected_output}.\n\n"
                        )
                    tops.actual_results.append(tops.actual_output)
                    tops.expected_results.append(tops.expected_output)

                tops.actual_output, tops.expected_output = (
                    tops.actual_results,
                    tops.expected_results,
                )

            except (
                AssertionError,
                AttributeError,
                LookupError,
                EapiError,
            ) as exception:
                logging.error(
                    f"Error occurred during the testsuite execution on dut: {tops.dut_name} "
                    f"is {str(exception)}"
                )
                tops.actual_output = str(exception)

        else:
            tops.test_result = True
            tops.actual_output = "N/A"
            tops.expected_output = "N/A"

            tops.comment = tops.output_msg = self.output = (
                "INVALID TEST: CloudEOS router "
                f"{tops.dut_name} does not have physical state in interface.\n"
            )

        tops.parse_test_steps(self.test_if_intf_phy_status_connected_on_)
        tops.test_result = tops.actual_output == tops.expected_output
        tops.generate_report(tops.dut_name, self.output)
        assert tops.actual_output == tops.expected_output


@pytest.mark.nrfu
@pytest.mark.interface_baseline_health
@pytest.mark.interface
class InterfaceCountersTests:
    """Interface Status Test Suite"""

    @pytest.mark.virtual
    @pytest.mark.physical
    @pytest.mark.parametrize("dut", test4_duts, ids=test4_ids)
    def test_if_intf_counters_has_input_errors_on_(self, dut, tests_definitions):
        """TD: Verify the interfaces of interest does not have input errors

        Args:
            dut (dict): Encapsulates dut details including name, connection
        """

        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)

        for interface in tops.interface_list:
            try:
                """
                TS: Run show command 'show interfaces counters errors' on dut
                """
                interface_name = interface["interface_name"].replace(" ", "")

                self.output = dut["output"][tops.show_cmd]["json"]["interfaceErrorCounters"]
                assert self.output, "No Interface Counter Errors are available"
                logging.info(
                    f"On device {tops.dut_name}"
                    f" output of {tops.show_cmd} command is: {self.output}"
                )

                tops.actual_output = self.output[interface_name]["inErrors"]
            except (
                AssertionError,
                AttributeError,
                LookupError,
                EapiError,
            ) as exception:
                logging.error(
                    f"Error occurred during the testsuite execution on dut:"
                    f" {tops.dut_name} is {str(exception)}"
                )
                tops.actual_output = str(exception)

            if tops.actual_output <= tops.expected_output:
                tops.output_msg += (
                    f"On interface {interface_name}: interface "
                    f"counter errors has {tops.actual_output} inErrors"
                    f"which is correct.\n\n"
                )
            else:
                tops.output_msg += (
                    f"On interface {interface_name}: interface "
                    f"counter errors has {tops.actual_output} inErrors"
                    f", while the expected inErrors are {tops.expected_output}.\n\n"
                )

            tops.actual_results.append(tops.actual_output)
            tops.expected_results.append(tops.expected_output)

        tops.actual_output, tops.expected_output = (
            tops.actual_results,
            tops.expected_results,
        )

        """
        TS: Creating test report based on results
        """
        tops.parse_test_steps(self.test_if_intf_counters_has_input_errors_on_)
        tops.test_result = all(x <= y for x, y in zip(tops.actual_output, tops.expected_output))
        tops.generate_report(tops.dut_name, tops.output_msg)
        assert tops.test_result

    @pytest.mark.virtual
    @pytest.mark.physical
    @pytest.mark.parametrize("dut", test5_duts, ids=test5_ids)
    def test_if_intf_counters_has_output_errors_on_(self, dut, tests_definitions):
        """TD: Verify the interfaces of interest does not have output errors

        Args:
            dut (dict): Encapsulates dut details including name, connection
        """

        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)

        for interface in tops.interface_list:
            try:
                """
                TS: Run show command 'show interfaces counters errors' on dut
                """
                interface_name = interface["interface_name"].replace(" ", "")

                self.output = dut["output"][tops.show_cmd]["json"]["interfaceErrorCounters"]
                assert self.output, "No Interface Counter Errors are available"
                logging.info(
                    f"On device {tops.dut_name}"
                    f" output of {tops.show_cmd} command is: {self.output}"
                )

                tops.actual_output = self.output[interface_name]["outErrors"]
            except (
                AssertionError,
                AttributeError,
                LookupError,
                EapiError,
            ) as exception:
                logging.error(
                    f"Error occurred during the testsuite execution on dut:"
                    f" {tops.dut_name} is {str(exception)}"
                )
                tops.actual_output = str(exception)

            if tops.actual_output <= tops.expected_output:
                tops.output_msg += (
                    f"On interface {interface_name}: interface "
                    f"counter errors has {tops.actual_output} outErrors"
                    f"which is correct.\n\n"
                )
            else:
                tops.output_msg += (
                    f"On interface {interface_name}: interface "
                    f"counter errors has {tops.actual_output} outErrors"
                    f", while the expected outErrors are {tops.expected_output}.\n\n"
                )

            tops.actual_results.append(tops.actual_output)
            tops.expected_results.append(tops.expected_output)

        tops.actual_output, tops.expected_output = (
            tops.actual_results,
            tops.expected_results,
        )

        """
        TS: Creating test report based on results
        """
        tops.parse_test_steps(self.test_if_intf_counters_has_output_errors_on_)
        tops.test_result = all(x <= y for x, y in zip(tops.actual_output, tops.expected_output))
        tops.generate_report(tops.dut_name, tops.output_msg)
        assert tops.test_result

    @pytest.mark.virtual
    @pytest.mark.physical
    @pytest.mark.parametrize("dut", test6_duts, ids=test6_ids)
    def test_if_intf_counters_has_frame_too_short_errors_on_(self, dut, tests_definitions):
        """TD: Verify the interfaces of interest have no frameTooShorts errors

        Args:
            dut (dict): Encapsulates dut details including name, connection
        """

        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)

        for interface in tops.interface_list:
            try:
                """
                TS: Run show command 'show interfaces counters errors' on dut
                """
                interface_name = interface["interface_name"].replace(" ", "")

                self.output = dut["output"][tops.show_cmd]["json"]["interfaceErrorCounters"]
                assert self.output, "No Interface Counter Errors are available"
                logging.info(
                    f"On device {tops.dut_name}"
                    f" output of {tops.show_cmd} command is: {self.output}"
                )

                tops.actual_output = self.output[interface_name]["frameTooShorts"]
            except (
                AssertionError,
                AttributeError,
                LookupError,
                EapiError,
            ) as exception:
                logging.error(
                    f"Error occurred during the testsuite execution on dut:"
                    f" {tops.dut_name} is {str(exception)}"
                )
                tops.actual_output = str(exception)

            if tops.actual_output <= tops.expected_output:
                tops.output_msg += (
                    f"On interface {interface_name}: interface "
                    f"counter errors has {tops.actual_output} "
                    "frameTooShorts, which is correct.\n\n"
                )
            else:
                tops.output_msg += (
                    f"On interface {interface_name}: interface "
                    f"counter errors has {tops.actual_output} "
                    "frameTooShorts, while the expected frameTooShorts is "
                    f"{tops.expected_output}.\n\n"
                )

            tops.actual_results.append(tops.actual_output)
            tops.expected_results.append(tops.expected_output)

        tops.actual_output, tops.expected_output = (
            tops.actual_results,
            tops.expected_results,
        )

        """
        TS: Creating test report based on results
        """
        tops.parse_test_steps(self.test_if_intf_counters_has_frame_too_short_errors_on_)
        tops.test_result = all(x <= y for x, y in zip(tops.actual_output, tops.expected_output))
        tops.generate_report(tops.dut_name, tops.output_msg)
        assert tops.test_result

    @pytest.mark.virtual
    @pytest.mark.physical
    @pytest.mark.parametrize("dut", test7_duts, ids=test7_ids)
    def test_if_intf_counters_has_frame_too_long_errors_on_(self, dut, tests_definitions):
        """TD: Verify the interfaces of interest have no frameTooLongs errors

        Args:
            dut (dict): Encapsulates dut details including name, connection
        """

        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)

        for interface in tops.interface_list:
            try:
                """
                TS: Run show command 'show interfaces counters errors' on dut
                """
                interface_name = interface["interface_name"].replace(" ", "")

                self.output = dut["output"][tops.show_cmd]["json"]["interfaceErrorCounters"]
                assert self.output, "No Interface Counter Errors are available"
                logging.info(
                    f"On device {tops.dut_name}"
                    f" output of {tops.show_cmd} command is: {self.output}"
                )

                tops.actual_output = self.output[interface_name]["frameTooLongs"]
            except (
                AssertionError,
                AttributeError,
                LookupError,
                EapiError,
            ) as exception:
                logging.error(
                    f"Error occurred during the testsuite execution on dut:"
                    f" {tops.dut_name} is {str(exception)}"
                )
                tops.actual_output = str(exception)

            if tops.actual_output <= tops.expected_output:
                tops.output_msg += (
                    f"On interface {interface_name}: interface "
                    f"counter errors has {tops.actual_output} "
                    "frameTooLongs, which is correct.\n\n"
                )
            else:
                tops.output_msg += (
                    f"On interface {interface_name}: interface "
                    f"counter errors has {tops.actual_output} "
                    "frameTooLongs, while the expected frameTooLongs is "
                    f"{tops.expected_output}.\n\n"
                )

            tops.actual_results.append(tops.actual_output)
            tops.expected_results.append(tops.expected_output)

        tops.actual_output, tops.expected_output = (
            tops.actual_results,
            tops.expected_results,
        )

        """
        TS: Creating test report based on results
        """
        tops.parse_test_steps(self.test_if_intf_counters_has_frame_too_long_errors_on_)
        tops.test_result = all(x <= y for x, y in zip(tops.actual_output, tops.expected_output))
        tops.generate_report(tops.dut_name, tops.output_msg)
        assert tops.test_result

    @pytest.mark.virtual
    @pytest.mark.physical
    @pytest.mark.parametrize("dut", test8_duts, ids=test8_ids)
    def test_if_intf_counters_has_fcs_errors_on_(self, dut, tests_definitions):
        """TD: Verify the interfaces of interest have no fcsErrors errors

        Args:
            dut (dict): Encapsulates dut details including name, connection
        """

        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)

        for interface in tops.interface_list:
            try:
                """
                TS: Run show command 'show interfaces counters errors' on dut
                """
                interface_name = interface["interface_name"].replace(" ", "")

                self.output = dut["output"][tops.show_cmd]["json"]["interfaceErrorCounters"]
                assert self.output, "No Interface Counter Errors are available"
                logging.info(
                    f"On device {tops.dut_name}"
                    f" output of {tops.show_cmd} command is: {self.output}"
                )

                tops.actual_output = self.output[interface_name]["fcsErrors"]
            except (
                AssertionError,
                AttributeError,
                LookupError,
                EapiError,
            ) as exception:
                logging.error(
                    f"Error occurred during the testsuite execution on dut:"
                    f" {tops.dut_name} is {str(exception)}"
                )
                tops.actual_output = str(exception)

            if tops.actual_output <= tops.expected_output:
                tops.output_msg += (
                    f"On interface {interface_name}: interface "
                    f"counter errors has {tops.actual_output} "
                    "fcsErrors, which is correct.\n\n"
                )
            else:
                tops.output_msg += (
                    f"On interface {interface_name}: interface "
                    f"counter errors has {tops.actual_output} "
                    "fcsErrors, while the expected fcsErrors is "
                    f"{tops.expected_output}.\n\n"
                )

            tops.actual_results.append(tops.actual_output)
            tops.expected_results.append(tops.expected_output)

        tops.actual_output, tops.expected_output = (
            tops.actual_results,
            tops.expected_results,
        )

        """
        TS: Creating test report based on results
        """
        tops.parse_test_steps(self.test_if_intf_counters_has_fcs_errors_on_)
        tops.test_result = all(x <= y for x, y in zip(tops.actual_output, tops.expected_output))
        tops.generate_report(tops.dut_name, tops.output_msg)
        assert tops.test_result

    @pytest.mark.virtual
    @pytest.mark.physical
    @pytest.mark.parametrize("dut", test9_duts, ids=test9_ids)
    def test_if_intf_counters_has_alignment_errors_on_(self, dut, tests_definitions):
        """TD: Verify the interfaces of interest have no alignmentErrors errors

        Args:
            dut (dict): Encapsulates dut details including name, connection
        """

        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)

        for interface in tops.interface_list:
            try:
                """
                TS: Run show command 'show interfaces counters errors' on dut
                """
                interface_name = interface["interface_name"].replace(" ", "")

                self.output = dut["output"][tops.show_cmd]["json"]["interfaceErrorCounters"]
                assert self.output, "No Interface Counter Errors are available"
                logging.info(
                    f"On device {tops.dut_name}"
                    f" output of {tops.show_cmd} command is: {self.output}"
                )

                tops.actual_output = self.output[interface_name]["alignmentErrors"]
            except (
                AssertionError,
                AttributeError,
                LookupError,
                EapiError,
            ) as exception:
                logging.error(
                    f"Error occurred during the testsuite execution on dut:"
                    f" {tops.dut_name} is {str(exception)}"
                )
                tops.actual_output = str(exception)

            if tops.actual_output <= tops.expected_output:
                tops.output_msg += (
                    f"On interface {interface_name}: interface "
                    f"counter errors has {tops.actual_output} "
                    "alignmentErrors, which is correct.\n\n"
                )
            else:
                tops.output_msg += (
                    f"On interface {interface_name}: interface "
                    f"counter errors has {tops.actual_output} "
                    "alignmentErrors, while the expected alignmentErrors is "
                    f"{tops.expected_output}.\n\n"
                )

            tops.actual_results.append(tops.actual_output)
            tops.expected_results.append(tops.expected_output)

        tops.actual_output, tops.expected_output = (
            tops.actual_results,
            tops.expected_results,
        )

        """
        TS: Creating test report based on results
        """
        tops.parse_test_steps(self.test_if_intf_counters_has_alignment_errors_on_)
        tops.test_result = all(x <= y for x, y in zip(tops.actual_output, tops.expected_output))
        tops.generate_report(tops.dut_name, tops.output_msg)
        assert tops.test_result

    @pytest.mark.virtual
    @pytest.mark.physical
    @pytest.mark.parametrize("dut", test10_duts, ids=test10_ids)
    def test_if_intf_counters_has_symbol_errors_on_(self, dut, tests_definitions):
        """TD: Verify the interfaces of interest have no symbolErrors errors

        Args:
            dut (dict): Encapsulates dut details including name, connection
        """

        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)

        for interface in tops.interface_list:
            try:
                """
                TS: Run show command 'show interfaces counters errors' on dut
                """
                interface_name = interface["interface_name"].replace(" ", "")

                self.output = dut["output"][tops.show_cmd]["json"]["interfaceErrorCounters"]
                assert self.output, "No Interface Counter Errors are available"
                logging.info(
                    f"On device {tops.dut_name}"
                    f" output of {tops.show_cmd} command is: {self.output}"
                )

                tops.actual_output = self.output[interface_name]["symbolErrors"]
            except (
                AssertionError,
                AttributeError,
                LookupError,
                EapiError,
            ) as exception:
                logging.error(
                    f"Error occurred during the testsuite execution on dut:"
                    f" {tops.dut_name} is {str(exception)}"
                )
                tops.actual_output = str(exception)

            if tops.actual_output <= tops.expected_output:
                tops.output_msg += (
                    f"On interface {interface_name}: interface "
                    f"counter errors has {tops.actual_output} "
                    "symbolErrors, which is correct.\n\n"
                )
            else:
                tops.output_msg += (
                    f"On interface {interface_name}: interface "
                    f"counter errors has {tops.actual_output} "
                    "symbolErrors, while the expected symbolErrors is "
                    f"{tops.expected_output}.\n\n"
                )

            tops.actual_results.append(tops.actual_output)
            tops.expected_results.append(tops.expected_output)

        tops.actual_output, tops.expected_output = (
            tops.actual_results,
            tops.expected_results,
        )

        """
        TS: Creating test report based on results
        """
        tops.parse_test_steps(self.test_if_intf_counters_has_symbol_errors_on_)
        tops.test_result = all(x <= y for x, y in zip(tops.actual_output, tops.expected_output))
        tops.generate_report(tops.dut_name, tops.output_msg)
        assert tops.test_result

    @pytest.mark.virtual
    @pytest.mark.physical
    @pytest.mark.parametrize("dut", test11_duts, ids=test11_ids)
    def test_if_interface_errors_on_(self, dut, tests_definitions):
        """TD: Verify the interfaces of interest have no L1 (Rx, Tx, FCS, Alignment) errors
        and have correct number Giant, Runt Frames.

        Args:
            dut (dict): Encapsulates dut details including name, connection
        """

        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)

        try:
            for interface in tops.interface_list:
                """
                TS: Run show command 'show interfaces' on dut
                """
                interface_name = interface["interface_name"].replace(" ", "")

                self.output = dut["output"][tops.show_cmd]["json"]["interfaces"][interface_name]
                assert self.output, "No Interface Details are available"
                logging.info(
                    f"On device {tops.dut_name}"
                    f" output of {tops.show_cmd} command is: {self.output}"
                )

                tops.actual_output = self.output["interfaceCounters"]["totalInErrors"]

                if tops.actual_output <= tops.expected_output:
                    tops.output_msg += (
                        f"On interface {interface_name}: interface "
                        f"Rx errors is {tops.actual_output}, which is correct.\n\n"
                    )
                else:
                    tops.output_msg += (
                        f"On interface {interface_name}: interface "
                        f"Rx errors is {tops.actual_output}, while the expected Rx errors is "
                        f"{tops.expected_output}.\n\n"
                    )

                tops.actual_results.append(tops.actual_output)
                tops.expected_results.append(tops.expected_output)

                tops.actual_output = self.output["interfaceCounters"]["inputErrorsDetail"][
                    "giantFrames"
                ]

                if tops.actual_output <= tops.expected_output:
                    tops.output_msg += (
                        f"On interface {interface_name}: interface "
                        f"Giant Frames is {tops.actual_output}, which is correct.\n\n"
                    )
                else:
                    tops.output_msg += (
                        f"On interface {interface_name}: interface "
                        f"Giant Frames is {tops.actual_output}, while the expected Giant Frames is "
                        f"{tops.expected_output}.\n\n"
                    )

                tops.actual_results.append(tops.actual_output)
                tops.expected_results.append(tops.expected_output)

                tops.actual_output = self.output["interfaceCounters"]["totalOutErrors"]

                if tops.actual_output <= tops.expected_output:
                    tops.output_msg += (
                        f"On interface {interface_name}: interface "
                        f"Tx Errors is {tops.actual_output}, which is correct.\n\n"
                    )
                else:
                    tops.output_msg += (
                        f"On interface {interface_name}: interface "
                        f"Tx Errors is {tops.actual_output}, while the expected Tx Errors is "
                        f"{tops.expected_output}.\n\n"
                    )

                tops.actual_results.append(tops.actual_output)
                tops.expected_results.append(tops.expected_output)

                tops.actual_output = self.output["interfaceCounters"]["inputErrorsDetail"][
                    "runtFrames"
                ]

                if tops.actual_output <= tops.expected_output:
                    tops.output_msg += (
                        f"On interface {interface_name}: interface "
                        f"Runt Frames is {tops.actual_output}, which is correct.\n\n"
                    )
                else:
                    tops.output_msg += (
                        f"On interface {interface_name}: interface "
                        f"Runt Frames is {tops.actual_output}, while the expected Runt Frames is "
                        f"{tops.expected_output}.\n\n"
                    )

                tops.actual_results.append(tops.actual_output)
                tops.expected_results.append(tops.expected_output)

                tops.actual_output = self.output["interfaceCounters"]["inputErrorsDetail"][
                    "fcsErrors"
                ]

                if tops.actual_output <= tops.expected_output:
                    tops.output_msg += (
                        f"On interface {interface_name}: interface "
                        f"FCS Errors is {tops.actual_output}, which is correct.\n\n"
                    )
                else:
                    tops.output_msg += (
                        f"On interface {interface_name}: interface "
                        f"FCS Errors is {tops.actual_output}, while the expected FCS Errors is "
                        f"{tops.expected_output}.\n\n"
                    )

                tops.actual_results.append(tops.actual_output)
                tops.expected_results.append(tops.expected_output)

                tops.actual_output = self.output["interfaceCounters"]["inputErrorsDetail"][
                    "alignmentErrors"
                ]

                if tops.actual_output <= tops.expected_output:
                    tops.output_msg += (
                        f"On interface {interface_name}: interface "
                        f"Alignment Errors is {tops.actual_output}, which is correct.\n\n"
                    )
                else:
                    tops.output_msg += (
                        f"On interface {interface_name}: interface "
                        f"Alignment Errors is {tops.actual_output}, "
                        f"while the expected Alignment Errors is "
                        f"{tops.expected_output}.\n\n"
                    )

                tops.actual_results.append(tops.actual_output)
                tops.expected_results.append(tops.expected_output)

            tops.actual_output, tops.expected_output = (
                tops.actual_results,
                tops.expected_results,
            )
        except (
            AssertionError,
            AttributeError,
            LookupError,
            EapiError,
        ) as exception:
            logging.error(
                f"Error occurred during the testsuite execution on dut:"
                f" {tops.dut_name} is {str(exception)}"
            )
            tops.actual_output = str(exception)

        """
        TS: Creating test report based on results
        """
        tops.parse_test_steps(self.test_if_interface_errors_on_)
        tops.test_result = all(x <= y for x, y in zip(tops.actual_output, tops.expected_output))
        tops.generate_report(tops.dut_name, tops.output_msg)
        assert tops.test_result

    @pytest.mark.parametrize("dut", test12_duts, ids=test12_ids)
    def test_interface_utilization_on_(self, dut, tests_definitions):
        """TD: Verify input and output bandwidth utilization of interfaces

        Args:
            dut (dict): Encapsulates dut details including name, connection
        """

        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)

        try:
            for interface in tops.interface_list:
                """
                TS: Run show command 'show interfaces' on dut
                """
                interface_name = interface["interface_name"].replace(" ", "")

                self.output = dut["output"][tops.show_cmd]["json"]["interfaces"][interface_name]
                assert self.output, "No Interface Details are available"
                logging.info(
                    f"On device {tops.dut_name}"
                    f" output of {tops.show_cmd} command is: {self.output}"
                )

                in_bps = self.output["interfaceStatistics"]["inBitsRate"]

                if tests_tools.verify_veos(dut):
                    bandwidth = 10000000000
                else:
                    bandwidth = self.output["bandwidth"]

                if in_bps == 0:
                    tops.actual_output = in_bps
                else:
                    tops.actual_output = (in_bps / bandwidth) * 100.00

                if tops.actual_output <= tops.expected_output:
                    tops.output_msg += (
                        f"On interface {interface_name}: input bandwidth "
                        f"utilization is {tops.actual_output}%, "
                        f"which is correct.\n\n"
                    )
                else:
                    tops.output_msg += (
                        f"On interface {interface_name}: input bandwidth "
                        f"utilization is {tops.actual_output}%, "
                        f"while the expected bandwidth utilization "
                        f"should be less than {tops.expected_output}%.\n\n"
                    )

                tops.actual_results.append(tops.test_result)
                tops.expected_results.append(True)

                out_bps = self.output["interfaceStatistics"]["outBitsRate"]

                if out_bps == 0:
                    tops.actual_output = out_bps
                else:
                    tops.actual_output = (out_bps / bandwidth) * 100.00

                if tops.actual_output <= tops.expected_output:
                    tops.output_msg += (
                        f"On interface {interface_name}: output bandwidth "
                        f"utilization is {tops.actual_output}%, "
                        f"which is the expected.\n\n"
                    )
                else:
                    tops.output_msg += (
                        f"On interface {interface_name}: output bandwidth "
                        f"utilization is {tops.actual_output}%, "
                        f"while bandwidth utilization "
                        f"should be less than {tops.expected_output}%.\n\n"
                    )

                tops.actual_results.append(tops.test_result)
                tops.expected_results.append(True)

            tops.actual_output, tops.expected_output = (
                tops.actual_results,
                tops.expected_results,
            )
        except (
            AssertionError,
            AttributeError,
            LookupError,
            EapiError,
        ) as exception:
            logging.error(
                f"Error occurred during the testsuite execution on dut:"
                f" {tops.dut_name} is {str(exception)}"
            )
            tops.actual_output = str(exception)

        """
        TS: Creating test report based on results
        """
        tops.parse_test_steps(self.test_interface_utilization_on_)
        tops.test_result = all(x <= y for x, y in zip(tops.actual_output, tops.expected_output))
        tops.generate_report(tops.dut_name, tops.output_msg)
        assert tops.test_result


@pytest.mark.nrfu
@pytest.mark.interface_baseline_health
@pytest.mark.interface
class InterfaceDiscardTests:
    """Interface Discard Test Suite"""

    @pytest.mark.virtual
    @pytest.mark.physical
    @pytest.mark.parametrize("dut", test13_duts, ids=test13_ids)
    def test_if_intf_out_counters_are_discarding_on_(self, dut, tests_definitions):
        """TD: Verify the interfaces of interest have no outDiscards

        Args:
            dut (dict): Encapsulates dut details including name, connection
        """

        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)

        for interface in tops.interface_list:
            try:
                """
                TS: Run show command 'show interfaces counters discards' on dut
                """
                interface_name = interface["interface_name"].replace(" ", "")

                self.output = dut["output"][tops.show_cmd]["json"]["interfaces"]
                assert self.output, "No Interface Counter Discards are available"
                logging.info(
                    f"On device {tops.dut_name}"
                    f" output of {tops.show_cmd} command is: {self.output}"
                )

                tops.actual_output = self.output[interface_name]["outDiscards"]
            except (
                AssertionError,
                AttributeError,
                LookupError,
                EapiError,
            ) as exception:
                logging.error(
                    f"Error occurred during the testsuite execution on dut:"
                    f" {tops.dut_name} is {str(exception)}"
                )
                tops.actual_output = str(exception)

            if tops.actual_output <= tops.expected_output:
                tops.output_msg += (
                    f"On interface {interface_name}: interface "
                    f"counter discards has {tops.actual_output} "
                    f"outDiscards, which is correct.\n\n"
                )
            else:
                tops.output_msg += (
                    f"On interface {interface_name}: interface "
                    f"counter discards has {tops.actual_output} "
                    f"outDiscards, while the expected outDiscards is |{tops.expected_output}|.\n\n"
                )

            tops.actual_results.append(tops.actual_output)
            tops.expected_results.append(tops.expected_output)

        tops.actual_output, tops.expected_output = (
            tops.actual_results,
            tops.expected_results,
        )

        """
        TS: Creating test report based on results
        """
        tops.parse_test_steps(self.test_if_intf_out_counters_are_discarding_on_)
        tops.test_result = all(x <= y for x, y in zip(tops.actual_output, tops.expected_output))
        tops.generate_report(tops.dut_name, tops.output_msg)
        assert tops.test_result

    @pytest.mark.virtual
    @pytest.mark.physical
    @pytest.mark.parametrize("dut", test14_duts, ids=test14_ids)
    def test_if_intf_in_counters_are_discarding_on_(self, dut, tests_definitions):
        """TD: Verify the interfaces of interest have no inDiscards

        Args:
            dut (dict): Encapsulates dut details including name, connection
        """

        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)

        for interface in tops.interface_list:
            try:
                """
                TS: Run show command 'show interfaces counters discards' on dut
                """
                interface_name = interface["interface_name"].replace(" ", "")

                self.output = dut["output"][tops.show_cmd]["json"]["interfaces"]
                assert self.output, "No Interface Counter Discards are available"
                logging.info(
                    f"On device {tops.dut_name}"
                    f" output of {tops.show_cmd} command is: {self.output}"
                )

                tops.actual_output = self.output[interface_name]["inDiscards"]
            except (
                AssertionError,
                AttributeError,
                LookupError,
                EapiError,
            ) as exception:
                logging.error(
                    f"Error occurred during the testsuite execution on dut:"
                    f" {tops.dut_name} is {str(exception)}"
                )
                tops.actual_output = str(exception)

            if tops.actual_output <= tops.expected_output:
                tops.output_msg += (
                    f"On interface {interface_name}: interface "
                    f"counter discards has {tops.actual_output} "
                    f"inDiscards, which is correct.\n\n"
                )
            else:
                tops.output_msg += (
                    f"On interface {interface_name}: interface "
                    f"counter discards has {tops.actual_output} "
                    f"inDiscards, while the expected inDiscards is {tops.expected_output}.\n\n"
                )

            tops.actual_results.append(tops.actual_output)
            tops.expected_results.append(tops.expected_output)

        tops.actual_output, tops.expected_output = (
            tops.actual_results,
            tops.expected_results,
        )

        """
        TS: Creating test report based on results
        """
        tops.parse_test_steps(self.test_if_intf_in_counters_are_discarding_on_)
        tops.test_result = all(x <= y for x, y in zip(tops.actual_output, tops.expected_output))
        tops.generate_report(tops.dut_name, tops.output_msg)
        assert tops.test_result


@pytest.mark.nrfu
@pytest.mark.interface_baseline_health
@pytest.mark.interface
class InterfaceMtuTests:
    """Interface MTU Test Suite"""

    @pytest.mark.virtual
    @pytest.mark.physical
    @pytest.mark.parametrize("dut", test15_duts, ids=test15_ids)
    def test_if_intf_mtu_is_correct_on_(self, dut, tests_definitions):
        """TD: Verify the interfaces of interest MTU

        Args:
            dut (dict): Encapsulates dut details including name, connection
        """

        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)

        for interface in tops.interface_list:
            try:
                """
                TS: Run show command 'show interfaces' on dut
                """
                interface_name = interface["interface_name"].replace(" ", "")

                self.output = dut["output"][tops.show_cmd]["json"]["interfaces"]
                assert self.output, "No Interface Details are available"
                logging.info(
                    f"On device {tops.dut_name}"
                    f" output of {tops.show_cmd} command is: {self.output}"
                )

                tops.actual_output = self.output[interface_name]["mtu"]
            except (
                AssertionError,
                AttributeError,
                LookupError,
                EapiError,
            ) as exception:
                logging.error(
                    f"Error occurred during the testsuite execution on dut:"
                    f" {tops.dut_name} is {str(exception)}"
                )
                tops.actual_output = str(exception)

            if tops.actual_output == tops.expected_output:
                tops.output_msg += (
                    f"On interface {interface_name}: interface "
                    f"MTU is {tops.actual_output}, which is correct.\n\n"
                )
            else:
                tops.output_msg += (
                    f"On interface {interface_name}: interface "
                    f"MTU is {tops.actual_output}, while the expected MTU is "
                    f"{tops.expected_output}.\n\n"
                )

            tops.actual_results.append(tops.actual_output)
            tops.expected_results.append(tops.expected_output)

        tops.actual_output, tops.expected_output = (
            tops.actual_results,
            tops.expected_results,
        )

        """
        TS: Creating test report based on results
        """
        tops.parse_test_steps(self.test_if_intf_mtu_is_correct_on_)
        tops.test_result = tops.actual_output == tops.expected_output
        tops.generate_report(tops.dut_name, tops.output_msg)
        assert tops.test_result
