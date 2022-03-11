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
from vane.tests_base import TestsBase

TEST_SUITE = __file__

@pytest.mark.demo
@pytest.mark.nrfu
@pytest.mark.base_feature
@pytest.mark.ztp
@pytest.mark.virtual
@pytest.mark.physical
@pytest.mark.eos424
class ZTPTests(TestsBase):
    """Zero Touch Provisioning Test Suite"""

    def test_if_zerotouch_is_disabled_on_(self, dut, tests_definitions):
        """Verify ztp is disabled

        Args:
          dut (dict): Encapsulates dut details including name, connection
          tests_definitions (dict): Test parameters
        """

        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)
        tops.actual_output = dut["output"][tops.show_cmd]["json"]["mode"]
        tops.test_result = tops.actual_output == tops.expected_output

        tops.output_msg += (
            f"On router |{tops.dut_name}|: ZTP process is in "
            f"mode: |{tops.actual_output}| correct mode is "
            f"|{tops.expected_output}|\n"
        )
        tops.comment += (
            f"TEST is ZTP disabled on |{tops.dut_name}|.\n"
            f"GIVEN ZTP state is |{tops.expected_output}|.\n"
            f"WHEN ZTP state is |{tops.actual_output}|.\n"
            f"THEN test case result is |{tops.test_result}|.\n"
            f"OUTPUT of |{tops.show_cmd}| is :"
            f"\n\n{tops.show_cmd_txt}"
        )
        print(f"{tops.output_msg}\n{tops.comment}")

        tops.post_testcase()

        assert tops.actual_output == tops.expected_output

    def test_for_zerotouch_config_file_on_(self, dut, tests_definitions):
        """Verify zerotoucn-config file is on flash

        Args:
          dut (dict): Encapsulates dut details including name, connection
          tests_definitions (dict): Test parameters
        """

        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)
        tops.actual_output = "zerotouch-config" in tops.show_cmd_txt
        tops.test_result = tops.actual_output == tops.expected_output

        tops.output_msg += (
            f"On router |{tops.dut_name}|: ZTP configuration "
            f"file is on flash: is |{tops.actual_output}|, "
            f" correct state is |{tops.expected_output}|\n"
        )
        tops.comment += (
            "TEST is ZTP configuration file on "
            f"|{tops.dut_name}|.\n"
            "GIVEN ZTP configuration file is "
            f"|{tops.expected_output}|.\n"
            "WHEN ZTP configuration file is "
            f"|{tops.actual_output}|.\n"
            f"THEN test case result is |{tops.test_result}|.\n"
            f"OUTPUT of |{tops.show_cmd}| is :"
            f"\n\n{tops.show_cmd_txt}"
        )
        print(f"{tops.output_msg}\n{tops.comment}")

        tops.post_testcase()

        assert tops.actual_output == tops.expected_output
