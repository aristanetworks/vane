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

""" Tests to validate memory utilization."""

import pytest
from pyeapi.eapilib import EapiError
from vane import tests_tools
from vane import test_case_logger
from vane.config import dut_objs, test_defs


TEST_SUITE = "test_memory.py"
LOG_FILE = {"parameters": {"show_log": "show_output.log"}}

dut_parameters = tests_tools.parametrize_duts(TEST_SUITE, test_defs, dut_objs)
test1_duts = dut_parameters["test_memory_utilization_on_"]["duts"]
test1_ids = dut_parameters["test_memory_utilization_on_"]["ids"]
logging = test_case_logger.setup_logger(__file__)


@pytest.mark.demo
@pytest.mark.nrfu
@pytest.mark.platform_status
@pytest.mark.memory
@pytest.mark.virtual
@pytest.mark.physical
class MemoryTests:
    """Memory Test Suite"""

    @pytest.mark.parametrize("dut", test1_duts, ids=test1_ids)
    def test_memory_utilization_on_(self, dut, tests_definitions):
        """TD: Verify memory is not exceeding high utilization

        Args:
            dut (dict): Encapsulates dut details including name, connection
            tests_definitions (dict): Test parameters
        """

        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)

        try:
            """
            TS: Run show command 'show version' on dut
            """
            self.output = dut["output"][tops.show_cmd]["json"]
            assert self.output, "Memory details are not collected."
            logging.info(
                f"On device {tops.dut_name} output of {tops.show_cmd} command is: {self.output}"
            )

            memory_total = self.output["memTotal"]
            memory_free = self.output["memFree"]
            tops.actual_output = (float(memory_free) / float(memory_total)) * 100

        except (AssertionError, AttributeError, LookupError, EapiError) as exception:
            logging.error(
                f"Error occurred during the testsuite execution on dut: "
                f"{tops.dut_name} is {str(exception)}"
            )
            tops.actual_output = str(exception)

        if tops.actual_output < tops.expected_output:
            tops.test_result = True
            tops.output_msg = (
                f"On router {tops.dut_name} memory utilization percent is "
                f"{tops.actual_output}% which is correct as it is "
                f"under {tops.expected_output}%"
            )
        else:
            tops.test_result = False
            tops.output_msg = (
                f"On router {tops.dut_name} the actual memory utilization percent is "
                f"{tops.actual_output}% while it should be under "
                f"{tops.expected_output}%"
            )

        tops.parse_test_steps(self.test_memory_utilization_on_)
        tops.generate_report(tops.dut_name, self.output)
        assert tops.actual_output < tops.expected_output
