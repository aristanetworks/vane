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

""" Tests to validate LLDP status."""

import pytest
from pyeapi.eapilib import EapiError
from vane import tests_tools, test_case_logger
from vane.config import dut_objs, test_defs


TEST_SUITE = __file__
LOG_FILE = {"parameters": {"show_log": "show_output.log"}}

dut_parameters = tests_tools.parametrize_duts(TEST_SUITE, test_defs, dut_objs)
test1_duts = dut_parameters["test_if_lldp_rx_is_enabled_on_"]["duts"]
test1_ids = dut_parameters["test_if_lldp_rx_is_enabled_on_"]["ids"]

test2_duts = dut_parameters["test_if_lldp_tx_is_enabled_on_"]["duts"]
test2_ids = dut_parameters["test_if_lldp_tx_is_enabled_on_"]["ids"]

test3_duts = dut_parameters["test_if_lldp_system_name_is_correct_on_"]["duts"]
test3_ids = dut_parameters["test_if_lldp_system_name_is_correct_on_"]["ids"]

test4_duts = dut_parameters["test_if_lldp_max_frame_size_is_correct_on_"]["duts"]
test4_ids = dut_parameters["test_if_lldp_max_frame_size_is_correct_on_"]["ids"]

test5_duts = dut_parameters["test_if_lldp_interface_id_is_correct_on_"]["duts"]
test5_ids = dut_parameters["test_if_lldp_interface_id_is_correct_on_"]["ids"]

logging = test_case_logger.setup_logger(__file__)


@pytest.mark.nrfu
@pytest.mark.l2_protocols
@pytest.mark.lldp
@pytest.mark.virtual
@pytest.mark.physical
class LldpTests:
    """LLDP Test Suite"""

    @pytest.mark.parametrize("dut", test1_duts, ids=test1_ids)
    def test_if_lldp_rx_is_enabled_on_(self, dut, tests_definitions):
        """TD: Verify LLDP receive is enabled on interesting interfaces

        Args:
            dut (dict): Encapsulates dut details including name, connection
            tests_definitions (dict): Test parameters
        """

        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)

        for interface in tops.interface_list:
            try:
                """
                TS: Collecting the output of 'show lldp' command from DUT
                """
                self.output = dut["output"][tops.show_cmd]["json"]
                interface_name = interface["interface_name"].replace(" ", "")
                assert self.output.get("lldpInterfaces").get(
                    interface_name
                ), f"Show LLDP interface: {interface_name} details are not found"
                logging.info(
                    f"On device {tops.dut_name} output of {tops.show_cmd} command is: {self.output}"
                )

                actual_output = self.output["lldpInterfaces"][interface_name]["rxEnabled"]

            except (AttributeError, LookupError, EapiError) as exp:
                actual_output = str(exp)
                logging.error(
                    f"On device {tops.dut_name}: Error while running testcase on DUT is: {str(exp)}"
                )
                tops.output_msg += (
                    f" EXCEPTION encountered on device {tops.dut_name}, while "
                    f"investigating LLDP rxEnabled: {interface_name}. Vane recorded error: {exp} "
                )

            """
            TS: Verify LLDP interface RX state on DUT
            """
            if actual_output == tops.expected_output:
                tops.output_msg += f"{tops.dut_name}'s {interface_name} LLDP RX is enabled\n"
            else:
                tops.output_msg += f"{tops.dut_name}'s {interface_name} LLDP RX is NOT enabled\n"

            tops.actual_results.append({interface_name: actual_output})
            tops.expected_results.append({interface_name: tops.expected_output})

        tops.actual_output, tops.expected_output = (
            tops.actual_results,
            tops.expected_results,
        )

        """
        TS: Creating test report based on results
        """
        tops.parse_test_steps(self.test_if_lldp_rx_is_enabled_on_)
        tops.test_result = tops.actual_output == tops.expected_output
        tops.generate_report(tops.dut_name, self.output)
        assert tops.actual_output == tops.expected_output

    @pytest.mark.parametrize("dut", test2_duts, ids=test2_ids)
    def test_if_lldp_tx_is_enabled_on_(self, dut, tests_definitions):
        """TD: Verify LLDP transmit is enabled on interesting interfaces

        Args:
            dut (dict): Encapsulates dut details including name, connection
            tests_definitions (dict): Test parameters
        """

        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)

        for interface in tops.interface_list:
            try:
                """
                TS: Collecting the output of 'show lldp' command from DUT
                """
                self.output = dut["output"][tops.show_cmd]["json"]
                interface_name = interface["interface_name"].replace(" ", "")
                assert self.output.get("lldpInterfaces").get(
                    interface_name
                ), f"Show LLDP interface: {interface_name} details are not found"
                logging.info(
                    f"On device {tops.dut_name} output of {tops.show_cmd} command is: {self.output}"
                )

                actual_output = self.output["lldpInterfaces"][interface_name]["txEnabled"]

            except (AttributeError, LookupError, EapiError) as exp:
                actual_output = str(exp)
                logging.error(
                    "On device {tops.dut_name}: Error while running testcase on DUT is: {str(exp)}"
                )
                tops.output_msg += (
                    f" EXCEPTION encountered on device {tops.dut_name}, while "
                    f"investigating LLDP txEnabled: {interface_name}. Vane recorded error: {exp} "
                )

            """
            TS: Verify LLDP interface TX state on DUT
            """
            if actual_output == tops.expected_output:
                tops.output_msg += f"{tops.dut_name}'s {interface_name} LLDP TX is enabled\n"
            else:
                tops.output_msg += f"{tops.dut_name}'s {interface_name} LLDP TX is NOT enabled\n"

            tops.actual_results.append({interface_name: actual_output})
            tops.expected_results.append({interface_name: tops.expected_output})

        tops.actual_output, tops.expected_output = (
            tops.actual_results,
            tops.expected_results,
        )

        """
        TS: Creating test report based on results
        """
        tops.parse_test_steps(self.test_if_lldp_tx_is_enabled_on_)
        tops.test_result = tops.actual_output == tops.expected_output
        tops.generate_report(tops.dut_name, self.output)
        assert tops.actual_output == tops.expected_output


@pytest.mark.nrfu
@pytest.mark.l2_protocols
@pytest.mark.lldp
@pytest.mark.virtual
@pytest.mark.physical
class LldpLocalInfoTests:
    """LLDP Local-Info Test Suite"""

    @pytest.mark.parametrize("dut", test3_duts, ids=test3_ids)
    def test_if_lldp_system_name_is_correct_on_(self, dut, tests_definitions):
        """TD: Verify show lldp local-info hostname is the system's name

        Args:
            dut (dict): Encapsulates dut details including name, connection
            tests_definitions (dict): Test parameters
        """

        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)

        try:
            """
            TS: Collecting the output of 'show lldp local-info' command from DUT
            """
            self.output = dut["output"][tops.show_cmd]["json"]
            tops.expected_output = tops.dut_name
            assert self.output.get("systemName"), "Show LLDP details are not found"
            logging.info(
                f"On device {tops.dut_name} output of {tops.show_cmd} command is: {self.output}"
            )

            tops.actual_output = self.output["systemName"]

        except (AttributeError, LookupError, EapiError) as exp:
            tops.actual_output = str(exp)
            logging.error(
                f"On device {tops.dut_name}: Error while running testcase on DUT is: {str(exp)}"
            )
            tops.output_msg += (
                f" EXCEPTION encountered on device {tops.dut_name}, while "
                f"investigating LLDP system name. Vane recorded error: {exp} "
            )

        """
        TS: Verify LLDP system name
        """
        if tops.actual_output == tops.expected_output:
            tops.test_result = True
            tops.output_msg = (
                f"{tops.dut_name}'s LLDP System Name is correct: {tops.expected_output}"
            )
        else:
            tops.test_result = False
            tops.output_msg = (
                f"{tops.dut_name}'s LLDP System Name is NOT correct: {tops.actual_output}. "
                f"LLDP System Name should be set to: {tops.expected_output}"
            )

        """
        TS: Creating test report based on results
        """
        tops.parse_test_steps(self.test_if_lldp_system_name_is_correct_on_)
        tops.generate_report(tops.dut_name, self.output)
        assert tops.actual_output == tops.expected_output

    @pytest.mark.parametrize("dut", test4_duts, ids=test4_ids)
    def test_if_lldp_max_frame_size_is_correct_on_(self, dut, tests_definitions):
        """TD: Verify show lldp local-info maxFrameSize is correct

        Args:
            dut (dict): Encapsulates dut details including name, connection
            tests_definitions (dict): Test parameters
        """

        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)

        for interface in tops.interface_list:
            try:
                """
                TS: Collecting the output of 'show lldp local-info' command from DUT
                """
                self.output = dut["output"][tops.show_cmd]["json"]
                interface_name = interface["interface_name"].replace(" ", "")
                assert self.output.get("localInterfaceInfo").get(
                    interface_name
                ), f"Show LLDP interface: {interface_name} details are not found"
                logging.info(
                    f"On device {tops.dut_name} output of {tops.show_cmd} command is: {self.output}"
                )

                actual_output = self.output["localInterfaceInfo"][interface_name]["maxFrameSize"]

            except (AttributeError, LookupError, EapiError) as exp:
                actual_output = str(exp)
                logging.error(
                    "On device {tops.dut_name}: Error while running testcase on DUT is: {str(exp)}"
                )
                tops.output_msg += (
                    f"EXCEPTION encountered on device {tops.dut_name}, while investigating"
                    f" Max frame size for {interface_name}. Vane recorded error: {exp} "
                )

            """
            TS: Verify LLDP interface max frame size on DUT
            """
            if actual_output == tops.expected_output:
                tops.output_msg += (
                    f"{tops.dut_name}'s {interface_name} Max frame size is correct: "
                    f"{actual_output}\n"
                )
            else:
                tops.output_msg += (
                    f"{tops.dut_name}'s {interface_name} Max frame size is NOT correct: "
                    f"{tops.expected_output}.  Max frame size should be {actual_output}\n"
                )

            tops.actual_results.append({interface_name: actual_output})
            tops.expected_results.append({interface_name: tops.expected_output})

        """
        TS: Creating test report based on results
        """
        tops.actual_output, tops.expected_output = (
            tops.actual_results,
            tops.expected_results,
        )

        """
        TS: Creating test report based on results
        """
        tops.parse_test_steps(self.test_if_lldp_max_frame_size_is_correct_on_)
        tops.test_result = tops.actual_output == tops.expected_output
        tops.generate_report(tops.dut_name, self.output)
        assert tops.actual_output == tops.expected_output

    @pytest.mark.parametrize("dut", test5_duts, ids=test5_ids)
    def test_if_lldp_interface_id_is_correct_on_(self, dut, tests_definitions):
        """TD: Verify show lldp local-info interfaceIdType is correct

        Args:
            dut (dict): Encapsulates dut details including name, connection
            tests_definitions (dict): Test parameters
        """

        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)

        for interface in tops.interface_list:
            try:
                """
                TS: Collecting the output of 'show lldp local-info' command from DUT
                """
                self.output = dut["output"][tops.show_cmd]["json"]
                interface_name = interface["interface_name"].replace(" ", "")
                assert self.output.get("localInterfaceInfo").get(
                    interface_name
                ), f"Show LLDP interface: {interface_name} details are not found"
                logging.info(
                    f"On device {tops.dut_name} output of {tops.show_cmd} command is: {self.output}"
                )

                actual_output = self.output["localInterfaceInfo"][interface_name]["interfaceIdType"]

            except (AttributeError, LookupError, EapiError) as exp:
                actual_output = str(exp)
                logging.error(
                    "On device {tops.dut_name}: Error while running testcase on DUT is: {str(exp)}"
                )
                tops.output_msg += (
                    f" EXCEPTION encountered on device {tops.dut_name}, while "
                    f"investigating interface ID for {interface_name}. Vane recorded error: {exp}"
                )

            """
            TS: Verify LLDP interface ID on DUT
            """
            if actual_output == tops.expected_output:
                tops.output_msg += (
                    f"{tops.dut_name}'s {interface_name} interface ID is correct: "
                    f"{actual_output}\n"
                )
            else:
                tops.output_msg += (
                    f"{tops.dut_name}'s {interface_name} interface ID is NOT correct: "
                    f"{tops.expected_output}.  Interface ID should be {actual_output}\n"
                )

            tops.actual_results.append({interface_name: actual_output})
            tops.expected_results.append({interface_name: tops.expected_output})

        tops.actual_output, tops.expected_output = (
            tops.actual_results,
            tops.expected_results,
        )

        """
        TS: Creating test report based on results
        """
        tops.parse_test_steps(self.test_if_lldp_interface_id_is_correct_on_)
        tops.test_result = tops.actual_output == tops.expected_output
        tops.generate_report(tops.dut_name, self.output)
        assert tops.actual_output == tops.expected_output
