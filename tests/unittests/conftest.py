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

""" Alter behavior of PyTest """


import pytest


@pytest.fixture
def test_names():
    """Input values for _format_tc_name test case

    Returns: [list]: Names of tests
    """

    return [
        "test_5_min_cpu_utilization_on_",
        "test_if_intf_protocol_status_is_connected_on_",
        "test_if_system_environment_cooling_is_in_spec_on_",
        "test_dut_on_",
        "test_cmd_on_",
    ]


@pytest.fixture
def report_names():
    """Pass criteria for _format_tc_name test case

    Returns: [list]: Names of pass criteria
    """

    return [
        "Test 5 min cpu utilization ",
        "Test if interface protocol status is connected ",
        "Test if system environment cooling is in spec ",
        "Test dut ",
        "Test cmd ",
    ]


@pytest.fixture
def field_names():
    """Pass criteria for _format_tc_name test case

    Returns: [list]: Names of pass criteria
    """

    return [
        "Test 5 min cpu utilization on ",
        "Test if intf protocol status is connected on ",
        "Test if system environment cooling is in spec on ",
        "Test device under test on ",
        "Test command on ",
    ]


@pytest.fixture
def test_suites():
    """Input values for _format_ts_name test case

    Returns: [list]: Names of tests
    """

    return {
        "input": [
            "test_api.py",
            "test_daemon.py",
            "test_interface.py",
            "test_tacacs.py",
            "test_environment.py",
        ],
        "result": ["Api", "Daemon", "Interface", "Tacacs", "Environment"],
    }


@pytest.fixture
def rc_methods():
    return [
        "_compile_yaml_data",
        "_reconcile_results",
        "_import_yaml",
        "write_result_doc",
        "_return_date",
        "_write_title_page",
        "_write_toc_page",
        "_write_summary_report",
        "_write_summary_results",
        "_write_dut_summary_results",
        "_write_suite_summary_results",
        "_compile_test_results",
        "_parse_testcases",
        "_totals",
        "_write_tests_case_report",
        "_write_detail_report",
        "_write_detail_major_section",
        "_write_detail_minor_section",
        "_write_detail_dut_section",
        "_add_dut_table_row",
        "_compile_suite_results",
        "_compile_testcase_results",
        "_format_ts_name",
        "_format_tc_name",
        "_format_test_field",
    ]


@pytest.fixture
def rc_variables():
    return [
        "data_model",
        "_summary_results",
        "_results_datamodel",
        "_document",
        "_major_section",
        "_test_no",
    ]


@pytest.fixture
def duts_dict():
    """represents a dut_dict"""

    return {
        "duts": {"leaf01": 3, "leaf02": 5, "leaf03": 7, "spine01": 2, "spine02": 4},
        "questions": ["leaf01", "spine01", "dci"],
        "answers": ["3", "2", "0"],
    }


@pytest.fixture
def table():
    """represents a spreadsheet table"""

    return {
        "row1": {"value1": 1, "value2": 2, "value3": 3},
        "row2": {"value1": None, "value2": 2, "value3": 3},
        "row3": {"value1": None, "value2": None, "value3": None},
    }


@pytest.fixture
def columns():
    """represents a spreadsheet column"""

    table_dimensions = {
        "start_row": 1,  # first row
        "end_row": 5,  # last row
        "start_col": 1,  # first col
        "end_col": 10,  # last col
        "header_row": 1,
        "interval": 3,
        "seed_col": 3,
        "multiplier": 2,
        "device_start": 0,
    }
    multi_cols = 2

    return {
        "table_dimensions": table_dimensions,
        "multi_cols": multi_cols,
    }


@pytest.fixture
def results_datamodel():
    return {
        "test_suites": [
            {
                "name": "baseline_mgmt_tests",
                "test_cases": [
                    {
                        "name": "test_ntp_functionality",
                        "duts": [
                            {
                                "actual_output": {
                                    "ntp_server_ip": "50.205.57.38",
                                    "ntp_status": "synchronised",
                                },
                                "comment": "",
                                "criteria": "NTP server is reachable and the NTP clock is in synchronous mode.",
                                "description": "Verification of NTP functionality",
                                "dut": "DLFW3",
                                "expected_output": {
                                    "ntp_server_ip": "23.131.64.1",
                                    "ntp_status": "synchronise",
                                },
                                "fail_or_skip_reason": "\nOn switch |DLFW3| The actual output is |{'ntp_status': 'synchronised', 'ntp_server_ip': '50.205.57.38'}%| and the expected output is |{'ntp_status': 'synchronise', 'ntp_server_ip': '23.131.64.1'}%|",
                                "name": "test_ntp_functionality",
                                "output_msg": "\nOn switch |DLFW3| The actual output is |{'ntp_status': 'synchronised', 'ntp_server_ip': '50.205.57.38'}%| and the expected output is |{'ntp_status': 'synchronise', 'ntp_server_ip': '23.131.64.1'}%|",
                                "show_cmd": "show ntp status:\n\nsynchronised to NTP server (50.205.57.38) at stratum 2\n   time correct to within 67 ms\n   polling server every 1024 s\n\n",
                                "show_cmd_txts": [
                                    "Arista vEOS-lab\nHardware version: \nSerial number: SN-DLFW3\nHardware MAC address: b4ed.8caa.7cd8\nSystem MAC address: b4ed.8caa.7cd8\n\nSoftware image version: 4.27.2F\nArchitecture: x86_64\nInternal build version: 4.27.2F-26069621.4272F\nInternal build ID: 2fd003fd-04c4-4b44-9c26-417e6ca42009\nImage format version: 1.0\nImage optimization: None\n\nUptime: 8 hours and 58 minutes\nTotal memory: 3938900 kB\nFree memory: 2203876 kB\n\n",
                                    "Tue Mar 28 17:37:15 2023\nTimezone: UTC\nClock source: NTP server (50.205.57.38)\n",
                                    "synchronised to NTP server (50.205.57.38) at stratum 2\n   time correct to within 67 ms\n   polling server every 1024 s\n\n",
                                ],
                                "show_cmds": ["show version", "show clock", "show ntp status"],
                                "test_id": "TN4.12",
                                "test_result": False,
                                "test_steps": [
                                    " Run show command ‘show ntp status’ on dut",
                                    " Verify NTP status is ‘synchronized’",
                                    " Verify NTP server has correct IP address",
                                ],
                                "test_suite": "baseline_mgmt_tests",
                            },
                        ],
                    }
                ],
            }
        ]
    }

@pytest.fixture
def test_parameters():
    return {
        "actual_output": {"ntp_server_ip": "50.205.57.38", "ntp_status": "synchronised"},
        "comment": "",
        "criteria": "NTP server is reachable and the NTP clock is in synchronous mode.",
        "description": "Verification of NTP functionality",
        "dut": "DLFW3",
        "expected_output": {"ntp_server_ip": "23.131.64.1", "ntp_status": "synchronise"},
        "fail_or_skip_reason": "\nOn switch |DLFW3| The actual output is |{'ntp_status': 'synchronised', 'ntp_server_ip': '50.205.57.38'}%| and the expected output is |{'ntp_status': 'synchronise', 'ntp_server_ip': '23.131.64.1'}%|",
        "name": "test_ntp_functionality",
        "output_msg": "\nOn switch |DLFW3| The actual output is |{'ntp_status': 'synchronised', 'ntp_server_ip': '50.205.57.38'}%| and the expected output is |{'ntp_status': 'synchronise', 'ntp_server_ip': '23.131.64.1'}%|",
        "show_cmd": "show ntp status:\n\nsynchronised to NTP server (50.205.57.38) at stratum 2\n   time correct to within 67 ms\n   polling server every 1024 s\n\n",
        "show_cmd_txts": [
            "Arista vEOS-lab\nHardware version: \nSerial number: SN-DLFW3\nHardware MAC address: b4ed.8caa.7cd8\nSystem MAC address: b4ed.8caa.7cd8\n\nSoftware image version: 4.27.2F\nArchitecture: x86_64\nInternal build version: 4.27.2F-26069621.4272F\nInternal build ID: 2fd003fd-04c4-4b44-9c26-417e6ca42009\nImage format version: 1.0\nImage optimization: None\n\nUptime: 8 hours and 58 minutes\nTotal memory: 3938900 kB\nFree memory: 2203876 kB\n\n",
            "Tue Mar 28 17:37:15 2023\nTimezone: UTC\nClock source: NTP server (50.205.57.38)\n",
            "synchronised to NTP server (50.205.57.38) at stratum 2\n   time correct to within 67 ms\n   polling server every 1024 s\n\n",
        ],
        "show_cmds": ["show version", "show clock", "show ntp status"],
        "test_id": "TN4.12",
        "test_result": False,
        "test_steps": [
            " Run show command ‘show ntp status’ on dut",
            " Verify NTP status is ‘synchronized’",
            " Verify NTP server has correct IP address",
        ],
        "test_suite": "baseline_mgmt_tests",
    }
