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

""" Tests to validate the network using Ixia traffic generation."""

import pytest
from vane import tests_tools
from vane import test_case_logger
from vane.config import dut_objs, test_defs

TEST_SUITE = "test_ixia.py"
LOG_FILE = {"parameters": {"show_log": "show_output.log"}}

dut_parameters = tests_tools.parametrize_duts(TEST_SUITE, test_defs, dut_objs)
test1_duts = dut_parameters["test_basic_ixia_setup"]["duts"]
test1_ids = dut_parameters["test_basic_ixia_setup"]["ids"]

logging = test_case_logger.setup_logger(__file__)


class IxiaTests:
    """Ixia Sample Test"""

    @pytest.mark.parametrize("dut", test1_duts, ids=test1_ids)
    def test_basic_ixia_setup(self, dut, tests_definitions):
        """Verify basic Ixia setup"""

        # Create tops object
        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)

        # TODO: This config file may vary per dut basis # pylint: disable=W0511
        # Retrieve configuration file for the dut
        ixia_configuration = tops.test_parameters["configuration_file"]

        # Call to start Ixia traffic generation and collect traffic/flow stats
        # This needs to happen per dut basis since configuration file of ixia
        # might differ from one dut to another

        # API takes in configuration file and modifies tops object to store ixia stats
        # which will be used in the test case

        tops.setup_ixia(ixia_configuration)

        # Check if Ixia ran into an error to gracefully exit the test
        if not (tops.traffic_item_stats and tops.flow_stats):
            message = (
                "Skipping the test case because an error was encountered while setting up ixia"
            )
            logging.info(message)
            pytest.skip(reason=message)

        # Implement test case specific logic

        for stat in tops.traffic_item_stats:
            logging.info(f"Traffic Item Statistics:\n{format(stat)}")
            if float(stat["Loss %"]) > 0:
                loss = format(stat["Loss %"])
                logging.info(f"There was a packet loss of {loss}% in the traffic.\n")

        for flow_stat in tops.flow_stats:
            logging.info(f"Flow Statistics:\n{format(flow_stat)}\n")
            if float(flow_stat["Loss %"]) > 0:
                pair = format(flow_stat["Source/Dest Value Pair"])
                loss = format(flow_stat["Loss %"])
                logging.info(f"Endpoint pair {pair} suffered a packet loss of {loss}%\n")

        assert tops.traffic_item_stats[0]["Tx Frames"] == "1000"
        assert tops.traffic_item_stats[0]["Rx Frames"] == "1000"
        assert tops.traffic_item_stats[0]["Loss %"] == "0.000"
        assert tops.flow_stats[0]["Traffic Item"] == "Traffic Item 1"
