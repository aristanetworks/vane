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


TEST_SUITE = __file__

@pytest.mark.demo
@pytest.mark.nrfu
@pytest.mark.base_feature
@pytest.mark.users
@pytest.mark.virtual
@pytest.mark.physical
@pytest.mark.eos424
class UsersTests:
    """EOS Users Test Suite"""

    def test_if_usernames_are_configured_on_(self, dut, tests_definitions):
        """Verify username is set correctly

        Args:
          dut (dict): Encapsulates dut details including name, connection
          tests_definitions (dict): Test parameters
        """

        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)
        usernames = tops.test_parameters["usernames"]

        for username in usernames:
            tops.actual_output = username in tops.show_cmd_txt
            tops.test_result = tops.actual_output == tops.expected_output

            tops.output_msg += (
                f"On router |{tops.dut_name}|: |{username}| "
                f"username configured is "
                f"|{tops.actual_output}|, username configured "
                f"should be |{tops.expected_output}|.\n\n"
            )

            tops.actual_results.append(tops.actual_output)
            tops.expected_results.append(tops.expected_output)

        print(f"{tops.output_msg}\n{tops.comment}")

        tops.actual_output, tops.expected_output = (
            tops.actual_results,
            tops.expected_results,
        )
        tops.post_testcase()

        assert tops.actual_results == tops.expected_results
