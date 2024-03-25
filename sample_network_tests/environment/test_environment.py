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

""" Tests to validate system environment."""

import pytest
from pyeapi.eapilib import EapiError
from vane import tests_tools, test_case_logger
from vane.config import dut_objs, test_defs

TEST_SUITE = __file__
LOG_FILE = {"parameters": {"show_log": "show_output.log"}}

dut_parameters = tests_tools.parametrize_duts(TEST_SUITE, test_defs, dut_objs)

test1_duts = dut_parameters["test_if_system_environment_temp_is_in_spec_on_"]["duts"]
test1_ids = dut_parameters["test_if_system_environment_temp_is_in_spec_on_"]["ids"]

test2_duts = dut_parameters["test_if_sensors_temp_is_in_spec_on_"]["duts"]
test2_ids = dut_parameters["test_if_sensors_temp_is_in_spec_on_"]["ids"]

test3_duts = dut_parameters["test_if_system_environment_power_are_in_spec_on_"]["duts"]
test3_ids = dut_parameters["test_if_system_environment_power_are_in_spec_on_"]["ids"]

test4_duts = dut_parameters["test_if_system_environment_cooling_is_in_spec_on_"]["duts"]
test4_ids = dut_parameters["test_if_system_environment_cooling_is_in_spec_on_"]["ids"]

test5_duts = dut_parameters["test_if_fan_status_is_in_spec_on_"]["duts"]
test5_ids = dut_parameters["test_if_fan_status_is_in_spec_on_"]["ids"]

logging = test_case_logger.setup_logger(__file__)


@pytest.mark.nrfu
@pytest.mark.platform_status
@pytest.mark.environment
@pytest.mark.physical
class EnvironmentTests:
    """Environment Test Suite"""

    @pytest.mark.parametrize("dut", test1_duts, ids=test1_ids)
    def test_if_system_environment_temp_is_in_spec_on_(self, dut, tests_definitions):
        """TD: Verify system's temperature environmental is functional within spec

        Args:
          dut (dict): Encapsulates dut details including name, connection
          tests_definitions (dict): Test parameters
        """

        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)

        if not tests_tools.verify_veos(dut):
            try:
                """
                TS: Run show command 'show system environment temperature' on dut
                """

                self.output = dut["output"][tops.show_cmd]
                assert self.output, "System environment temperature details are not collected."
                logging.info(
                    f"On device {tops.dut_name} output of {tops.show_cmd} command is: {self.output}"
                )

                tops.actual_output = self.output["json"]["systemStatus"]

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

            if tops.actual_output == tops.expected_output:
                tops.test_result = True
                tops.output_msg = (
                    f"On router {tops.dut_name} system temperature status "
                    f"is {tops.actual_output} which is correct.\n"
                )
            else:
                tops.test_result = False
                tops.output_msg = (
                    f"On router {tops.dut_name} the actual system temperature status "
                    f"is {tops.actual_output} while the expected temperature status is "
                    f"{tops.expected_output}.\n"
                )

        else:
            tops.test_result = True
            tops.actual_output = "N/A"
            tops.expected_output = "N/A"

            tops.comment = (
                tops.output_msg
            ) = (
                self.output
            ) = f"INVALID TEST: CloudEOS router {tops.dut_name} does not require cooling.\n"
            logging.info(
                f"INVALID TEST: CloudEOS router {tops.dut_name} does not require cooling.\n"
            )
        tops.parse_test_steps(self.test_if_system_environment_temp_is_in_spec_on_)
        tops.generate_report(tops.dut_name, self.output)
        assert tops.actual_output == tops.expected_output

    @pytest.mark.parametrize("dut", test2_duts, ids=test2_ids)
    def test_if_sensors_temp_is_in_spec_on_(self, dut, tests_definitions):
        """TD: Verify system's temperature sensors environmental is functional within spec

        Args:
          dut (dict): Encapsulates dut details including name, connection
          tests_definitions (dict): Test parameters
        """

        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)

        if not tests_tools.verify_veos(dut):
            try:
                """
                TS: Run show command 'show system environment temperature' on dut
                """

                self.output = dut["output"][tops.show_cmd]
                assert self.output, "System environment temperature details are not collected."
                logging.info(
                    f"On device {tops.dut_name} output of {tops.show_cmd} command is: {self.output}"
                )

                powersupplies = self.output["json"]["powerSupplySlots"]
                cards = self.output["json"]["cardSlots"]

                for sensor_array in [powersupplies, cards]:
                    for sensor_card in sensor_array:
                        temp_sensors = sensor_card["tempSensors"]
                        sensor_name = sensor_card["entPhysicalClass"]

                        for temp_sensor in temp_sensors:
                            sensor = temp_sensor["name"]
                            tops.actual_output = temp_sensor["inAlertState"]

                            if tops.actual_output == tops.expected_output:
                                tops.output_msg += (
                                    f"{sensor_name} Sensor {sensor} temperature alert status "
                                    f"is {tops.actual_output} which is correct.\n"
                                )
                            else:
                                tops.output_msg += (
                                    f"{sensor_name} Sensor {sensor} actual temperature alert "
                                    f"status is {tops.actual_output} while the expected "
                                    f"temperature alert status is {tops.expected_output}.\n"
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

            tops.comment = (
                tops.output_msg
            ) = (
                self.output
            ) = f"INVALID TEST: CloudEOS router {tops.dut_name} does not require cooling.\n"

        tops.parse_test_steps(self.test_if_sensors_temp_is_in_spec_on_)
        tops.test_result = tops.actual_output == tops.expected_output
        tops.generate_report(tops.dut_name, self.output)
        assert tops.actual_output == tops.expected_output

    @pytest.mark.parametrize("dut", test3_duts, ids=test3_ids)
    def test_if_system_environment_power_are_in_spec_on_(self, dut, tests_definitions):
        """TD: Verify system's power environmental is functional within spec
        Args:
          dut (dict): Encapsulates dut details including name, connection
          tests_definitions (dict): Test parameters
        """

        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)

        if not tests_tools.verify_veos(dut):
            try:
                """
                TS: Run show command 'show system environment power' on dut
                """
                self.output = dut["output"][tops.show_cmd]
                assert self.output, "System environment power details are not collected."
                logging.info(
                    f"On device {tops.dut_name} output of {tops.show_cmd} command is: {self.output}"
                )

                power_supplies = self.output["json"]["powerSupplies"]

                for power_supply in power_supplies:
                    tops.actual_output = power_supplies[power_supply]["state"]
                    if tops.actual_output == tops.expected_output:
                        tops.output_msg += (
                            f"Power-Supply {power_supply} state is "
                            f"{tops.actual_output} which is correct.\n"
                        )
                    else:
                        tops.output_msg += (
                            f"Power-Supply {power_supply} actual state is "
                            f"{tops.actual_output} while expected Power-Supply state is "
                            f"{tops.expected_output}.\n"
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
                f"{tops.dut_name} does not have "
                "power-supplies.\n"
            )

        tops.parse_test_steps(self.test_if_system_environment_power_are_in_spec_on_)
        tops.test_result = tops.actual_output == tops.expected_output
        tops.generate_report(tops.dut_name, self.output)
        assert tops.actual_output == tops.expected_output

    @pytest.mark.parametrize("dut", test4_duts, ids=test4_ids)
    def test_if_system_environment_cooling_is_in_spec_on_(self, dut, tests_definitions):
        """TD: Verify system's cooling environmental is functional within spec

        Args:
          dut (dict): Encapsulates dut details including name, connection
          tests_definitions (dict): Test parameters
        """

        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)

        if not tests_tools.verify_veos(dut):
            try:
                """
                TS: Run show command 'show system environment cooling' on dut
                """

                self.output = dut["output"][tops.show_cmd]
                assert self.output, "System environment cooling details are not collected."
                logging.info(
                    f"On device {tops.dut_name} output of {tops.show_cmd} command is: {self.output}"
                )

                tops.actual_output = self.output["json"]["systemStatus"]

                if tops.actual_output == tops.expected_output:
                    tops.test_result = True
                    tops.output_msg = (
                        f"On router {tops.dut_name} system cooling status "
                        f"is {tops.actual_output} which is correct.\n"
                    )
                else:
                    tops.test_result = False
                    tops.output_msg = (
                        f"On router {tops.dut_name} the actual system cooling status "
                        f"is {tops.actual_output} while the expected "
                        f"system cooling status is {tops.expected_output}.\n"
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

            tops.comment = (
                tops.output_msg
            ) = (
                self.output
            ) = f"INVALID TEST: CloudEOS router {tops.dut_name} does not require cooling.\n"

        tops.parse_test_steps(self.test_if_system_environment_cooling_is_in_spec_on_)
        tops.generate_report(tops.dut_name, self.output)
        assert tops.actual_output == tops.expected_output

    @pytest.mark.parametrize("dut", test5_duts, ids=test5_ids)
    def test_if_fan_status_is_in_spec_on_(self, dut, tests_definitions):
        """TD: Verify system's cooling environmental is functional within spec

        Args:
          dut (dict): Encapsulates dut details including name, connection
          tests_definitions (dict): Test parameters
        """

        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)

        if not tests_tools.verify_veos(dut):
            try:
                """
                TS: Run show command 'show system environment cooling' on dut
                """

                self.output = dut["output"][tops.show_cmd]["json"]
                assert self.output, "System environment cooling details are not collected."
                logging.info(
                    f"On device {tops.dut_name} output of {tops.show_cmd} command is: {self.output}"
                )

                power_supplies = self.output["powerSupplySlots"]
                fan_trays = self.output["fanTraySlots"]

                for fan_systems in [power_supplies, fan_trays]:
                    for fan_system in fan_systems:
                        fans = fan_system["fans"]

                        for fan in fans:
                            tops.actual_output = fan["status"]
                            fan_name = fan["label"]

                            if tops.actual_output == tops.expected_output:
                                tops.output_msg += (
                                    f"{fan_name} fan "
                                    f"is {tops.actual_output} which is correct.\n"
                                )

                            else:
                                tops.output_msg += (
                                    f"{fan_name} fan "
                                    f"is {tops.actual_output} while it is expected to be "
                                    f"{tops.expected_output}.\n"
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

            tops.comment = (
                tops.output_msg
            ) = (
                self.output
            ) = f"INVALID TEST: CloudEOS router {tops.dut_name} does not require fans.\n"

        tops.parse_test_steps(self.test_if_fan_status_is_in_spec_on_)
        tops.test_result = tops.actual_output == tops.expected_output
        tops.generate_report(tops.dut_name, self.output)
        assert tops.actual_output == tops.expected_output
