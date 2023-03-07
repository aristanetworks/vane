#!/usr/bin/env python3
#
# Copyright (c) 2019, Arista Networks EOS+
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

import inspect
import logging
import pytest
from vane import tests_tools
from vane.fixtures import dut, tests_definitions


TEST_SUITE = __file__
LOG_FILE = {"parameters": {"show_log": "show_output.log"}}


@pytest.mark.nrfu
@pytest.mark.platform_status
@pytest.mark.environment
@pytest.mark.physical
@pytest.mark.eos424
class EnvironmentTests:
    """Environment Test Suite"""

    def test_if_system_environment_temp_is_in_spec_on_(
        self, dut, tests_definitions
    ):
        """Verify system temperature environmentals are functional within spec

        Args:
          dut (dict): Encapsulates dut details including name, connection
          tests_definitions (dict): Test parameters
        """

        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)

        if not tests_tools.verify_veos(dut):
            tops.return_show_cmd("show system environment temperature")
            tops.actual_output = tops.show_output["systemStatus"]
            tops.test_result = tops.actual_output == tops.expected_output

            tops.output_msg = (
                f"On router |{tops.dut_name}| system temperature status "
                f"is |{tops.actual_output}| and should be "
                f"|{tops.expected_output}|"
            )
        else:
            tops.test_result, tops.actual_output, tops.expected_output = (
                True,
                None,
                None,
            )

            tops.output_msg += (
                "INVALID TEST: CloudEOS router "
                f"|{tops.dut_name}| doesnt require cooling.\n"
            )

        print(f"{tops.output_msg}\n{tops.comment}")
        tops.post_testcase()
        assert tops.actual_output == tops.expected_output

    def test_if_sensors_temp_is_in_spec_on_(self, dut, tests_definitions):
        """Verify system temperature sensors environmentals are functional within spec

        Args:
          dut (dict): Encapsulates dut details including name, connection
          tests_definitions (dict): Test parameters
        """

        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)

        if not tests_tools.verify_veos(dut):
            print(f"\nOn router |{tops.dut_name}|:")

            tops.return_show_cmd("show system environment temperature")
            powersupplies = tops.show_output["powerSupplySlots"]
            cards = tops.show_output["cardSlots"]

            for sensor_array in [powersupplies, cards]:
                for sensor_card in sensor_array:
                    tempsensors = sensor_card["tempSensors"]
                    sensor_name = sensor_card["entPhysicalClass"]

                    for temp_sensor in tempsensors:
                        sensor = temp_sensor["name"]
                        tops.actual_output = temp_sensor["inAlertState"]
                        tops.test_result = (
                            tops.actual_output == tops.expected_output
                        )

                        tops.output_msg += (
                            f"{sensor_name} Sensor |{sensor}| temperature alert status "
                            f"is |{tops.actual_output}| and should be "
                            f"|{tops.expected_output}|.\n"
                        )

                        tops.actual_results.append(tops.actual_output)
                        tops.expected_results.append(tops.expected_output)

            tops.actual_output, tops.expected_output = (
                tops.actual_results,
                tops.expected_results,
            )

        else:
            tops.test_result, tops.actual_output, tops.expected_output = (
                True,
                None,
                None,
            )
            tops.actual_results, tops.expected_results = [], []

            tops.output_msg += (
                "INVALID TEST: CloudEOS router "
                f"|{tops.dut_name}| doesnt require cooling.\n"
            )

        print(f"{tops.output_msg}\n{tops.comment}")
        tops.post_testcase()
        assert tops.actual_results == tops.expected_results

    def test_if_system_environment_power_are_in_spec_on_(
        self, dut, tests_definitions
    ):
        """Verify system power environmentals are functional within spec
        Args:
          dut (dict): Encapsulates dut details including name, connection
          tests_definitions (dict): Test parameters
        """

        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)

        if not tests_tools.verify_veos(dut):
            tops.return_show_cmd("show system environment power")
            power_supplies = tops.show_output["powerSupplies"]
            print(f"\nOn router |{tops.dut_name}|")

            for powersupply in power_supplies:
                tops.actual_output = power_supplies[powersupply]["state"]
                tops.test_result = tops.actual_output == tops.expected_output

                tops.output_msg += (
                    f"Power-Supply {powersupply} state is "
                    f"|{tops.actual_output}|, should be in "
                    f"|{tops.expected_output}|.\n"
                )

                tops.actual_results.append(tops.actual_output)
                tops.expected_results.append(tops.expected_output)

        else:
            tops.test_result = True

            tops.output_msg += (
                "INVALID TEST: CloudEOS router "
                f"|{tops.dut_name}| doesnt have "
                "power-supplies.\n"
            )

        print(f"{tops.output_msg}\n{tops.comment}")

        tops.actual_output, tops.expected_output = (
            tops.actual_results,
            tops.expected_results,
        )
        tops.post_testcase()

        assert tops.actual_results == tops.expected_results

    def test_if_system_environment_cooling_is_in_spec_on_(
        self, dut, tests_definitions
    ):
        """Verify system cooling environmentals are functional within spec

        Args:
          dut (dict): Encapsulates dut details including name, connection
          tests_definitions (dict): Test parameters
        """

        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)

        if not tops.verify_veos():
            tops.actual_output = dut["output"][tops.show_cmd]["json"][
                "systemStatus"
            ]
            tops.test_result = tops.actual_output == tops.expected_output

            tops.output_msg = (
                f"On router |{tops.dut_name}| system cooling status "
                f"is |{tops.actual_output}| and should be "
                f"|{tops.expected_output}|"
            )

        else:
            tops.test_result, tops.actual_output, tops.expected_output = (
                True,
                None,
                None,
            )

            tops.output_msg += (
                "INVALID TEST: CloudEOS router "
                f"|{tops.dut_name}| doesnt require cooling.\n"
            )


        print(f"{tops.output_msg}\n{tops.comment}")
        tops.post_testcase()
        assert tops.actual_output == tops.expected_output

    def test_if_fan_status_is_in_spec_on_(self, dut, tests_definitions):
        """Verify system cooling environmentals are functional within spec

        Args:
          dut (dict): Encapsulates dut details including name, connection
          tests_definitions (dict): Test parameters
        """

        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)

        if not tops.verify_veos():
            powersupplies = dut["output"][tops.show_cmd]["json"][
                "powerSupplySlots"
            ]
            fan_trays = dut["output"][tops.show_cmd]["json"]["fanTraySlots"]

            for fan_systems in [powersupplies, fan_trays]:
                for fan_system in fan_systems:
                    fans = fan_system["fans"]

                    for fan in fans:
                        tops.actual_output = fan["status"]
                        fan_name = fan["label"]
                        tops.test_result = (
                            tops.actual_output == tops.expected_output
                        )

                        tops.output_msg += (
                            f"|{fan_name}| fan "
                            f"is |{tops.actual_output}| and should be "
                            f"|{tops.expected_output}|.\n"
                        )


                        tops.actual_results.append(tops.actual_output)
                        tops.expected_results.append(tops.expected_output)


            tops.actual_output, tops.expected_output = (
                tops.actual_results,
                tops.expected_results,
            )

        else:
            tops.test_result, tops.actual_output, tops.expected_output = (
                True,
                None,
                None,
            )
            tops.actual_results, tops.expected_results = [], []

            tops.output_msg += (
                "INVALID TEST: CloudEOS router "
                f"|{tops.dut_name}| doesnt require fans.\n"
            )


        print(f"{tops.output_msg}\n{tops.comment}")
        tops.post_testcase()
        assert tops.actual_results == tops.expected_results
