import vane.report_client as report_client
import datetime


DEFINITIONS = 'sample_network_tests/definitions.yaml'
RC = report_client.ReportClient(DEFINITIONS)

def test_assert():
    assert True


def test_object(rc_methods, rc_variables):
    """ Verify instance of TestsClient Object can be created
    """

    # Test for known methods in object
    for method in rc_methods:
        assert True == (method in dir(RC))

    # Test for known methods in variables
    for variable in rc_variables:
        assert True == (variable in dir(RC))

def test_date_creation():
    """ Verify object returns date field correctly formatted
    """

    date_obj = datetime.datetime.now()
    old_format_date = date_obj.strftime("%B %d, %Y %I:%M:%S%p")
    old_file_date = date_obj.strftime("%y%m%d%H%M")

    format_date, file_date = RC._return_date()

    assert old_file_date == file_date
    assert old_format_date == format_date

def test_formating_test_case(test_names, report_names):
    """ Verify object can format a test case name correctly
    """

    test_range = len(test_names)

    for test_index in range(test_range):
        test_name = test_names[test_index]
        report_name = report_names[test_index]

        format_name = RC._format_tc_name(test_name)

        assert format_name == report_name

def test_format_test_field(test_names, field_names):
    """ Verify object can format a test case field correctly

    Args:
        test_names (list): Names of tests
        report_names (list): Names of pass criteria
    """

    test_range = len(test_names)

    for test_index in range(test_range):
        test_name = test_names[test_index]
        field_name = field_names[test_index]

        format_name = RC._format_test_field(test_name)

        assert format_name == field_name

def test_format_test_suite_name(test_suites):
    """ Verify object can format a test suite name correcty
    """

    ts_inputs = test_suites['input']
    ts_results = test_suites['result']
    test_range = len(ts_inputs)

    for test_index in range(test_range):
        suite_name = ts_inputs[test_index]
        suite_result = ts_results[test_index]

        format_name = RC._format_ts_name(suite_name)

        assert format_name == suite_result

def test_if_keys_in_dict(duts_dict):
    """ Verify object can test if an object is in dict
    """

    duts = duts_dict['duts']
    questions = duts_dict['questions']
    answers = duts_dict['answers']
    test_range = len(questions)

    for test_index in range(test_range):

        question = questions[test_index]
        answer = answers[test_index]

        total = RC._totals(duts, question)

        assert total == answer
