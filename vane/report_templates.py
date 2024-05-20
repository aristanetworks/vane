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

"""Templates for reporting"""

REPORT_TEMPLATES = {
    "default": {
        "test_id": {
            "required": True,
            "format": "string",
            "output_name": "test identifier",
            "summary": True,
        },
        "name": {
            "required": True,
            "format": "string",
            "output_name": "test case name",
            "summary": True,
        },
        "description": {"required": True, "format": "string"},
        "show_cmd_txts": {
            "required": False,
            "format": "config_term",
            "default": [],
            "output_name": "dut output",
        },
        "external_command_outputs": {
            "required": False,
            "format": "nested_dict",
            "default": [],
            "output_name": "external device output",
        },
        "expected_output": {
            "required": True,
            "format": "dict_string",
            "output_name": "expected output",
        },
        "actual_output": {
            "required": True,
            "format": "dict_string",
            "output_name": "actual output",
        },
        "test_result": {
            "required": True,
            "format": "test_result",
            "output_name": "test result",
            "summary": True,
        },
        "fail_or_skip_reason": {
            "required": True,
            "format": "string",
            "default": "None",
            "output_name": "fail or skip reason",
            "summary": True,
        },
        "comment": {"required": False, "format": "string", "default": "None"},
    },
    "modern": {
        "test_id": {
            "required": True,
            "format": "string",
            "output_name": "test identifier",
            "summary": True,
        },
        "name": {
            "required": True,
            "format": "string",
            "output_name": "test case name",
            "summary": True,
        },
        "description": {"required": True, "format": "string"},
        "assumptions": {
            "required": False,
            "format": "bulleted_list",
            "default": ["No assumptions have been made"],
        },
        "dut": {
            "required": True,
            "format": "string",
            "output_name": "device under test",
            "summary": True,
        },
        "external_systems": {
            "required": False,
            "format": "bulleted_list",
            "default": ["No external systems are being used"],
            "output_name": "external systems",
        },
        "configuration": {
            "required": False,
            "format": "config_string",
            "default": ["Network configuration is unchanged"],
        },
        "test_steps": {
            "required": True,
            "format": "numbered_list",
            "output_name": "procedure",
            "summary": True,
        },
        "input": {
            "required": False,
            "format": "dict_string",
            "default": "No user defined input",
            "output_name": "input",
        },
        "show_cmd_txts": {
            "required": False,
            "format": "config_term",
            "default": [],
            "output_name": "dut output",
        },
        "external_command_outputs": {
            "required": False,
            "format": "nested_dict",
            "default": [],
            "output_name": "external device output",
        },
        "test_criteria": {
            "required": True,
            "format": "string",
            "default": "None",
            "output_name": "expected output",
        },
        "output_msg": {
            "required": True,
            "format": "string",
            "default": "None",
            "output_name": "observation",
            "summary": True,
        },
        "test_result": {
            "required": True,
            "format": "test_result",
            "default": "None",
            "output_name": "pass/fail",
            "summary": True,
        },
        "comment": {"required": False, "format": "string", "default": "None"},
    },
}
