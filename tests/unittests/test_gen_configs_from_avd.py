#!/usr/bin/env python3
#
# Copyright (c) 2022, Arista Networks EOS+
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

"""Unit Tests for gen_configs_from_avd.py script"""

import argparse
import pytest
import vane
from unittest.mock import call
from vane import gen_configs_from_avd


# pylint: disable=redefined-outer-name
@pytest.fixture
def loginfo(mocker):
    """Fixture to mock logger info calls from vane.tests_tools"""
    return mocker.patch("vane.vane_logging.logging.info")


def test_main(loginfo, mocker):
    """Unit test for main()"""

    mocker_object = mocker.patch("vane.gen_configs_from_avd.parse_cli")

    # mocking parse cli to test --generate-configs-file
    mocker.patch(
        "vane.gen_duts_from_cvp.parse_cli",
        return_value=argparse.Namespace(
            generate_configs_file="path/to/dir",
        ),
    )
    gen_configs_from_avd.main()
    mocker_object.assert_called_once()

    loginfo_calls = [
        call("Set config directory to path/to/dir"),
    ]
    loginfo.assert_has_calls(loginfo_calls, any_order=False)