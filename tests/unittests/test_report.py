"""
report_client.py unit tests
"""

# Disable protected-access for testing hidden class functions
# pylint: disable=protected-access

from vane import report_client


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


def test_formatting_test_case(test_names, report_names):
    """Verify object can format a test case name correctly"""

    test_range = len(test_names)

    for test_index in range(test_range):
        test_name = test_names[test_index]
        report_name = report_names[test_index]

        format_name = RC._format_tc_name(test_name)

        assert format_name == report_name


def test_format_test_suite_name():
    """Verify object can format a test suite name correctly"""

    test_suites = {
        "input": [
            "test_api.py",
            "test_daemon.py",
            "test_interface.py",
            "test_tacacs.py",
            "test_environment.py",
        ],
        "result": ["test_api", "test_daemon", "test_interface", "test_tacacs", "test_environment"],
    }

    ts_inputs = test_suites["input"]
    ts_results = test_suites["result"]
    test_range = len(ts_inputs)

    for test_index in range(test_range):
        suite_name = ts_inputs[test_index]
        suite_result = ts_results[test_index]

        format_name = RC._format_ts_name(suite_name)

        assert format_name == suite_result

    # Testing when no "_" in test suite name
    format_name = RC._format_ts_name("TestMemory.py")
    assert format_name == "TestMemory"


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
