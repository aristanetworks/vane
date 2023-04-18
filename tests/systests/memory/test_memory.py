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

import pytest
from vane import tests_tools
from vane.config import dut_objs, test_defs


TEST_SUITE = "test_memory.py"

dut_parameters = tests_tools.parametrize_duts(TEST_SUITE, test_defs, dut_objs)
test1_duts = dut_parameters["test_memory_utilization_on_"]["duts"]
test1_ids = dut_parameters["test_memory_utilization_on_"]["ids"]


@pytest.mark.demo
@pytest.mark.nrfu
@pytest.mark.platform_status
@pytest.mark.memory
@pytest.mark.virtual
@pytest.mark.physical
@pytest.mark.eos424
class MemoryTests:
    """Memory Test Suite"""

    @pytest.mark.parametrize("dut", test1_duts, ids=test1_ids)
    def test_memory_utilization_on_(self, dut, tests_definitions):
        """Verify memory is not exceeding high utlization

        Args:
            dut (dict): Encapsulates dut details including name, connection
            tests_definitions (dict): Test parameters
        """

        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)

        memory_total = dut["output"][tops.show_cmd]["json"]["memTotal"]
        memory_free = dut["output"][tops.show_cmd]["json"]["memFree"]
        tops.actual_output = (float(memory_free) / float(memory_total)) * 100
        tops.test_result = tops.actual_output < tops.expected_output

        tops.output_msg = (
            f"On router |{tops.dut_name}| memory utilization percent is "
            f"|{tops.actual_output}%| and should be under "
            f"|{tops.expected_output}%|"
        )

        print(f"{tops.output_msg}\n{tops.comment}")

        tops.generate_report(tops.dut_name, tops.output_msg)

        assert tops.actual_output < tops.expected_output
