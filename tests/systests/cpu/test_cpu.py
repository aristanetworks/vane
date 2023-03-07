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


TEST_SUITE = __file__

dut_parameters = tests_tools.parametrize_duts(TEST_SUITE, test_defs, dut_objs)
test1_duts = dut_parameters["test_1_sec_cpu_utlization_on_"]["duts"]
test1_ids = dut_parameters["test_1_sec_cpu_utlization_on_"]["ids"]
test2_duts = dut_parameters["test_1_min_cpu_utlization_on_"]["duts"]
test2_ids = dut_parameters["test_1_min_cpu_utlization_on_"]["ids"]
test3_duts = dut_parameters["test_5_min_cpu_utlization_on_"]["duts"]
test3_ids = dut_parameters["test_5_min_cpu_utlization_on_"]["ids"]


@pytest.mark.demo
@pytest.mark.nrfu
@pytest.mark.platform_status
@pytest.mark.cpu
@pytest.mark.virtual
@pytest.mark.physical
@pytest.mark.eos424
class CPUTests:
    """CPU Test Suite"""

    @pytest.mark.parametrize("dut", test1_duts, ids=test1_ids)
    def test_1_sec_cpu_utlization_on_(self, dut, tests_definitions):
        """Verify 1 second CPU % is under specificied value

        Args:
            dut (dict): Encapsulates dut details including name, connection
        """

        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)

        dut_ptr = dut["output"][tops.show_cmd]["json"]
        tops.actual_output = dut_ptr["timeInfo"]["loadAvg"][0]
        tops.test_result = tops.actual_output < tops.expected_output

        tops.output_msg = (
            f"\nOn router |{tops.dut_name}| 1 second CPU load average is "
            f"|{tops.actual_output}%| and should be under "
            f"|{tops.expected_output}%|"
        )
        print(f"{tops.output_msg}\n{tops.comment}")

        tops.post_testcase()

        assert tops.actual_output < tops.expected_output

    @pytest.mark.parametrize("dut", test2_duts, ids=test2_ids)
    def test_1_min_cpu_utlization_on_(self, dut, tests_definitions):
        """Verify 1 minute CPU % is under specificied value

        Args:
            dut (dict): Encapsulates dut details including name, connection
        """

        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)

        dut_ptr = dut["output"][tops.show_cmd]["json"]
        tops.actual_output = dut_ptr["timeInfo"]["loadAvg"][1]
        tops.test_result = tops.actual_output < tops.expected_output

        tops.output_msg = (
            f"\nOn router |{tops.dut_name}| 1 minute CPU load average is "
            f"|{tops.actual_output}%| and should be under "
            f"|{tops.expected_output}%|"
        )
        print(f"{tops.output_msg}\n{tops.comment}")

        tops.post_testcase()

        assert tops.actual_output < tops.expected_output

    @pytest.mark.parametrize("dut", test3_duts, ids=test3_ids)
    def test_5_min_cpu_utlization_on_(self, dut, tests_definitions):
        """Verify 5 minute CPU % is under specificied value

        Args:
            dut (dict): Encapsulates dut details including name, connection
        """

        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)

        dut_ptr = dut["output"][tops.show_cmd]["json"]
        tops.actual_output = dut_ptr["timeInfo"]["loadAvg"][2]
        tops.test_result = tops.actual_output < tops.expected_output

        tops.output_msg = (
            f"\nOn router |{tops.dut_name}| 5 minute CPU load average is "
            f"|{tops.actual_output}%| and should be under "
            f"|{tops.expected_output}%|"
        )
        print(f"{tops.output_msg}\n{tops.comment}")

        tops.post_testcase()

        assert tops.actual_output < tops.expected_output
