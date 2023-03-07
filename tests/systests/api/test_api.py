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
LOG_FILE = {"parameters": {"show_log": "show_output.log"}}

@pytest.mark.demo
@pytest.mark.nrfu
@pytest.mark.base_feature
@pytest.mark.api
@pytest.mark.virtual
@pytest.mark.physical
@pytest.mark.eos424
class APITests:
    """API Test Suite"""

    def test_if_management_https_api_server_is_running_on_(
        self, dut, tests_definitions
    ):
        """Verify management api https server is running
        Args:
         dut (dict): Encapsulates dut details including name, connection
         tests_definitions (dict): Test parameters
        """

        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)
        ptr = dut["output"][tops.show_cmd]["json"]
        tops.actual_output = ptr["httpsServer"]["running"]
        tops.test_result = tops.actual_output == tops.expected_output

        tops.output_msg += (
            f"\nOn router |{tops.dut_name}| HTTPS Server is "
            f"running state: |{tops.actual_output}|, should be "
            f"in state |{tops.expected_output}|"
        )
        print(f"{tops.output_msg}\n{tops.comment}")

        tops.post_testcase()

        assert tops.expected_output == tops.actual_output

    def test_if_management_https_api_server_port_is_correct_on_(
        self, dut, tests_definitions
    ):
        """Verify https server is enabled on port 443
        Args:
         dut (dict): Encapsulates dut details including name, connection
         tests_definitions (dict): Test parameters
        """

        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)
        ptr = dut["output"][tops.show_cmd]["json"]
        tops.actual_output = ptr["httpsServer"]["port"]
        tops.test_result = tops.actual_output == tops.expected_output

        tops.output_msg += (
            f"\nOn router |{tops.dut_name}| HTTPS Server is "
            f"running on port: |{tops.actual_output}|, should be "
            f"port |{tops.expected_output}|"
        )
        print(f"{tops.output_msg}\n{tops.comment}")

        tops.post_testcase()

        assert tops.expected_output == tops.actual_output

    def test_if_management_https_api_server_is_enabled_on_(
        self, dut, tests_definitions
    ):
        """Verify management api https server is enabled
        Args:
         dut (dict): Encapsulates dut details including name, connection
         tests_definitions (dict): Test parameters
        """

        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)
        tops.actual_output = dut["output"][tops.show_cmd]["json"]["enabled"]
        tops.test_result = tops.actual_output == tops.expected_output

        tops.output_msg += (
            f"\nOn router |{tops.dut_name}| API is "
            f"enabled state: |{tops.actual_output}|, should be "
            f"in state |{tops.expected_output}|"
        )
        print(f"{tops.output_msg}\n{tops.comment}")

        tops.post_testcase()

        assert tops.expected_output == tops.actual_output

    def test_if_management_http_api_server_is_running_on_(
        self, dut, tests_definitions
    ):
        """Verify management api http server is not running
        Args:
         dut (dict): Encapsulates dut details including name, connection
         tests_definitions (dict): Test parameters
        """

        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)
        ptr = dut["output"][tops.show_cmd]["json"]
        tops.actual_output = ptr["httpServer"]["running"]
        tops.test_result = tops.actual_output == tops.expected_output

        tops.output_msg += (
            f"\nOn router |{tops.dut_name}| HTTP Server is "
            f"running state: |{tops.actual_output}|, should be "
            f"in state |{tops.expected_output}|"
        )
        print(f"{tops.output_msg}\n{tops.comment}")

        tops.post_testcase()

        assert tops.expected_output == tops.actual_output

    def test_if_management_local_http_api_server_is_running_on_(
        self, dut, tests_definitions
    ):
        """Verify management api local httpserver is not running
        Args:
         dut (dict): Encapsulates dut details including name, connection
         tests_definitions (dict): Test parameters
        """

        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)
        ptr = dut["output"][tops.show_cmd]["json"]
        tops.actual_output = ptr["localHttpServer"]["running"]
        tops.test_result = tops.actual_output == tops.expected_output

        tops.output_msg += (
            f"\nOn router |{tops.dut_name}| HTTP Server is "
            f"running state: |{tops.actual_output}|, should be "
            f"in state |{tops.expected_output}|"
        )
        print(f"{tops.output_msg}\n{tops.comment}")

        tops.post_testcase()

        assert tops.expected_output == tops.actual_output
