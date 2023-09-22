"""
report_client.py unit tests
"""

# Disable protected-access for testing hidden class functions
# pylint: disable=protected-access

import datetime

from vane import report_client
from vane import utils


DEFINITIONS = "tests/unittests/fixtures/report_definitions.yaml"
RC = report_client.ReportClient(DEFINITIONS)


def test_object(rc_methods, rc_variables):
    """Verify instance of TestsClient Object can be created"""

    # Test for known methods in object
    for method in rc_methods:
        assert method in dir(RC)

    # Test for known methods in variables
    for variable in rc_variables:
        assert variable in dir(RC)


def test_date_creation():
    """Verify object returns date field correctly formatted"""

    date_obj = datetime.datetime.now()
    old_format_date = date_obj.strftime("%B %d, %Y %I:%M:%S%p")
    old_file_date = date_obj.strftime("%y%m%d%H%M")

    format_date, file_date = utils.return_date()

    assert old_file_date == file_date
    assert old_format_date == format_date


def test_formating_test_case(test_names, report_names):
    """Verify object can format a test case name correctly"""

    test_range = len(test_names)

    for test_index in range(test_range):
        test_name = test_names[test_index]
        report_name = report_names[test_index]

        format_name = RC._format_tc_name(test_name)

        assert format_name == report_name


def test_format_test_suite_name(test_suites):
    """Verify object can format a test suite name correcty"""

    ts_inputs = test_suites["input"]
    ts_results = test_suites["result"]
    test_range = len(ts_inputs)

    for test_index in range(test_range):
        suite_name = ts_inputs[test_index]
        suite_result = ts_results[test_index]

        format_name = RC._format_ts_name(suite_name)

        assert format_name == suite_result


def test_if_keys_in_dict(duts_dict):
    """Verify object can test if an object is in dict"""

    duts = duts_dict["duts"]
    questions = duts_dict["questions"]
    answers = duts_dict["answers"]
    test_range = len(questions)

    for test_index in range(test_range):
        question = questions[test_index]
        answer = answers[test_index]

        total = RC._totals(duts, question)

        assert total == answer
