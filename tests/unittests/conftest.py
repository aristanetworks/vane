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
        "Test 5 min cpu utilization on ",
        "Test if interface protocol status is connected on ",
        "Test if system environment cooling is in spec on ",
        "Test dut on ",
        "Test cmd on ",
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
def rc_methods():
    """Inputs report client's methods

    Returns: [list]: Names of methods"""

    return [
        "__class__",
        "__delattr__",
        "__dict__",
        "__dir__",
        "__doc__",
        "__eq__",
        "__format__",
        "__ge__",
        "__getattribute__",
        "__gt__",
        "__hash__",
        "__init__",
        "__init_subclass__",
        "__le__",
        "__lt__",
        "__module__",
        "__ne__",
        "__new__",
        "__reduce__",
        "__reduce_ex__",
        "__repr__",
        "__setattr__",
        "__sizeof__",
        "__str__",
        "__subclasshook__",
        "__weakref__",
        "_compile_custom_tc_results",
        "_compile_suite_results",
        "_compile_test_results",
        "_compile_testcase_results",
        "_compile_yaml_data",
        "_create_data_row",
        "_create_header_row",
        "_custom_tc_report",
        "_default_tc_report",
        "_document",
        "_format_tc_name",
        "_format_ts_name",
        "_major_section",
        "_parse_testcases",
        "_reconcile_results",
        "_reports_dir",
        "_required_template_fields",
        "_results_datamodel",
        "_return_summary_headers",
        "_return_tbl_value",
        "_set_default_value",
        "_summary_results",
        "_test_no",
        "_totals",
        "_write_bulleted_list",
        "_write_cell",
        "_write_config_string",
        "_write_config_term",
        "_write_custom_detail_dut_section",
        "_write_custom_paragraph",
        "_write_custom_tc_report",
        "_write_detail_dut_section",
        "_write_detail_major_section",
        "_write_detail_minor_section",
        "_write_detail_report",
        "_write_dict_string",
        "_write_dut_summary_results",
        "_write_numbered_list",
        "_write_output_name",
        "_write_suite_summary_results",
        "_write_summary_report",
        "_write_summary_results",
        "_write_test_result",
        "_write_tests_case_report",
        "_write_text",
        "_write_title_page",
        "_write_toc_page",
        "data_model",
        "write_result_doc",
    ]


@pytest.fixture
def rc_variables():
    """Inputs report client's variables

    Returns: [list]: Names of variables"""

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
