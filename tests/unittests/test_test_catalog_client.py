"""
Test class for test_catalog_client.py
"""

from unittest.mock import call
import os
import csv
import json
import pytest
from vane import test_catalog_client


# Global test parameters
TEST_DIR = "tests/unittests/fixtures/test_catalog_client/pass_dirs/api"
PARAMETERIZATION_DATA = [
    (
        ["tests/unittests/fixtures/test_catalog_client/pass_dirs/api"],
        "tests/unittests/fixtures/test_catalog_client/test_catalog.csv",
    ),
    (
        ["tests/unittests/fixtures/test_catalog_client/test_case_name_mismatch"],
        "tests/unittests/fixtures/test_catalog_client/test_case_name_mismatch.csv",
    ),
    (
        ["tests/unittests/fixtures/test_catalog_client/no_tests_in_python_file"],
        "tests/unittests/fixtures/test_catalog_client/no_tests_in_file.csv",
    ),
    (
        ["tests/unittests/fixtures/test_catalog_client/no_test_steps_in_python_file"],
        "tests/unittests/fixtures/test_catalog_client/no_test_steps.csv",
    ),
    (
        ["tests/unittests/fixtures/test_catalog_client/test_suite_name_mismatch"],
        "tests/unittests/fixtures/test_catalog_client/test_suite_name_mismatch.csv",
    ),
    (
        [
            "tests/unittests/fixtures/test_catalog_client/pass_dirs/api",
            "tests/unittests/fixtures/test_catalog_client/pass_dirs/extension",
        ],
        "tests/unittests/fixtures/test_catalog_client/test_catalog_multiple_directory.csv",
    ),
    (
        ["tests/unittests/fixtures/test_catalog_client/pass_dirs"],
        "tests/unittests/fixtures/test_catalog_client/test_catalog_multiple_directory.csv",
    ),
]


# pylint: disable=redefined-outer-name
@pytest.fixture
def loginfo(mocker):
    """
    Fixture to mock logger info calls from vane.test_catalog_client
    """
    return mocker.patch("vane.vane_logging.logging.info")


@pytest.fixture
def logdebug(mocker):
    """
    Fixture to mock logger debug calls from vane.test_catalog_client
    """
    return mocker.patch("vane.vane_logging.logging.debug")


def file_clean_up(file_name):
    """
    Clean up the files created in the test case.
    Args:
        file_name(str): File name to be deleted
    """
    if os.path.isfile(file_name):
        os.remove(file_name)


def test_test_catalog_client_constructor(loginfo, logdebug):
    """
    Unit Test for TestCatlogClient object, method __init__
    """
    _ = test_catalog_client.TestCatalogClient(TEST_DIR)

    loginfo_calls = [
        call("Creating the test catalog client object"),
    ]
    loginfo.assert_has_calls(loginfo_calls, any_order=False)

    logdebug_calls = [
        call(f"Setting the test catalog client object directories to {TEST_DIR}"),
    ]
    logdebug.assert_has_calls(logdebug_calls, any_order=False)


def test_write_test_catalog(loginfo, mocker):
    """
    Unit Test for TestCatlogClient object, method write_test_catalog
    """
    test_catalog = test_catalog_client.TestCatalogClient([TEST_DIR])
    mocker_object = mocker.patch("vane.test_catalog_client.TestCatalogClient.walk_dir")
    test_catalog.write_test_catalog()
    mocker_object.assert_called_once()

    loginfo_calls = [
        call("Started writing the test catalog file"),
        call("Finished writing the test catalog file"),
    ]
    loginfo.assert_has_calls(loginfo_calls, any_order=False)


def test_walk_dir(loginfo, logdebug, mocker):
    """
    Unit Test for TestCatlogClient object, method walk_dir
    Fixture or files used:
    tests/unittests/fixtures/test_catalog_client/pass_dirs/api/test_api.py,
    tests/unittests/fixtures/test_catalog_client/pass_dirs/api/test_definition.yaml
    """
    mocker_object = mocker.patch("vane.test_catalog_client.TestCatalogClient.parse_test_data")
    test_catalog = test_catalog_client.TestCatalogClient([TEST_DIR])
    test_catalog.walk_dir()
    mocker_object.assert_called_once()

    test_files = [
        "tests/unittests/fixtures/test_catalog_client/pass_dirs/api/test_api.py",
        "tests/unittests/fixtures/test_catalog_client/pass_dirs/api/test_definition.yaml",
    ]

    loginfo_call = [
        call("Creating the test catalog client object"),
        call(f"Walking directory {TEST_DIR} for the test cases"),
    ]
    loginfo.assert_has_calls(loginfo_call, any_order=False)

    logdebug_call = [
        call(f"Setting the test catalog client object directories to {[TEST_DIR]}"),
        call(f"Discovered test files: {test_files} for parsing"),
    ]
    logdebug.assert_has_calls(logdebug_call)


def test_parse_test_data(loginfo, mocker):
    """
    Unit Test for TestStepClient object, method parsed_data
    Fixture or files used:
    tests/unittests/fixtures/test_catalog_client/pass_dirs/api/test_api.py,
    tests/unittests/fixtures/test_catalog_client/pass_dirs/api/test_definition.yaml
    """
    test_files = [
        "tests/unittests/fixtures/test_catalog_client/pass_dirs/api/test_api.py",
        "tests/unittests/fixtures/test_catalog_client/pass_dirs/api/test_definition.yaml",
    ]

    loginfo_calls = [call("Creating the test catalog client object")]
    for file in test_files:
        loginfo_calls.append(
            call(f"Opening {file} file to collect details required for the test catalog.")
        )

    loginfo_calls.append(call("Collected test data required for formation of the test catalog."))
    mocker_object_one = mocker.patch(
        "vane.test_catalog_client.TestCatalogClient.correlate_test_data"
    )
    mocker_object_two = mocker.patch("vane.test_catalog_client.TestCatalogClient.parse_python_file")

    test_catalog = test_catalog_client.TestCatalogClient([TEST_DIR])
    test_catalog.parse_test_data(test_files)

    mocker_object_one.assert_called_once()
    mocker_object_two.assert_called_once()

    loginfo.assert_has_calls(loginfo_calls, any_order=False)


def test_parse_python_file():
    """
    Unit Test for TestStepClient object, method parse_python_file
    Fixture or files used:
    tests/unittests/fixtures/test_catalog_client/parsed_python_file_content.json
    """
    test_catalog = test_catalog_client.TestCatalogClient([TEST_DIR])
    test_file = "tests/unittests/fixtures/test_catalog_client/pass_dirs/api/test_api.py"
    json_file = "tests/unittests/fixtures/test_catalog_client/parsed_python_file_content.json"
    with open(test_file, encoding="utf_8") as infile:
        content = infile.read()

    with open(json_file, encoding="utf_8") as json_file_data:
        expected_output = json.load(json_file_data)

    test_catalog.parse_python_file(content, test_file)
    actual_output = test_catalog.test_file_data

    assert expected_output == actual_output


def test_correlate_test_data(mocker, loginfo):
    """
    Unit Test for TestStepClient object, method correlate_test_data
    """
    mocker_object = mocker.patch("vane.test_catalog_client.TestCatalogClient.write_to_csv")
    test_catalog = test_catalog_client.TestCatalogClient([TEST_DIR])
    test_catalog.correlate_test_data()
    mocker_object.assert_called_once()

    loginfo_call = "Completed data correlation between test definitions and Python file."
    loginfo.assert_any_call(loginfo_call)


def test_get_data_rows():
    """
    Unit Test for TestStepClient object, method get_data_rows
    Fixture or files used:: tests/unittests/fixtures/test_catalog_client/correlated_data.json,
    tests/unittests/fixtures/test_catalog_client/test_catalog.csv
    """
    test_catalog = test_catalog_client.TestCatalogClient([TEST_DIR])
    json_file = "tests/unittests/fixtures/test_catalog_client/correlated_data.json"
    csv_file = "tests/unittests/fixtures/test_catalog_client/test_catalog.csv"
    with open(json_file, encoding="utf_8") as json_file_data:
        actual_output = json.load(json_file_data)

    with open(csv_file, encoding="utf_8", newline="") as catalog_file:
        expected_output = list(csv.reader(catalog_file))

    expected_data_rows = expected_output[1:]
    actual_data_rows = test_catalog.get_data_rows(actual_output)

    assert actual_data_rows == expected_data_rows


def test_write_to_csv(loginfo, request, mocker):
    """
    Unit Test for TestStepClient object, method write_to_csv
    Fixture or files used:: tests/unittests/fixtures/test_catalog_client/correlated_data.json
    """
    json_file = "tests/unittests/fixtures/test_catalog_client/correlated_data.json"
    test_catalog = test_catalog_client.TestCatalogClient([TEST_DIR])
    with open(json_file, encoding="utf_8") as json_file_data:
        final_data = json.load(json_file_data)

    mocker.patch("vane.test_catalog_client.return_date", return_value=("not_used", "2402182049"))

    # Writing test catalog in the CSV file.
    test_catalog.write_to_csv(final_data)
    execution_path = request.config.rootpath
    test_catalog_path = os.path.join(execution_path, "test_catalog")

    # Checking log is generated and the file exists at the specified location.
    loginfo_call = [
        call(f"Writing a test catalog file: test_catalog_2402182049.csv in the {test_catalog_path}")
    ]
    loginfo.assert_has_calls(loginfo_call, any_order=False)
    test_catalog_file_path = os.path.join(test_catalog_path, "test_catalog_2402182049.csv")
    assert os.path.exists(test_catalog_file_path)
    file_clean_up("test_catalog/test_catalog_2402182049.csv")


@pytest.mark.parametrize(
    "test_directories, expected_output_file",
    PARAMETERIZATION_DATA,
    ids=[
        "test_case_details_matched_in_test_def_and_python_file",
        "test_case_name_mismatch",
        "no_tests_in_test_def",
        "no_test_steps_in_test_file",
        "test_suite_name_mismatch",
        "multiple_test_directories",
        "test_recursive_catalog",
    ],
)
def test_main_test_catalog_functionality(request, mocker, test_directories, expected_output_file):
    """
    Tests the main test catalog functionality. Verifies that the test_catalog CSV file written
    in the expected folder and the expected test catalog is present in the CSV file.
    Fixture or files used:
    tests/unittests/fixtures/test_catalog_client/pass_dirs/api,
    tests/unittests/fixtures/test_catalog_client/test_catalog.csv,
    tests/unittests/fixtures/test_catalog_client/test_case_name_mismatch,
    tests/unittests/fixtures/test_catalog_client/test_case_name_mismatch.csv,
    tests/unittests/fixtures/test_catalog_client/test_not_found_in_python_file,
    tests/unittests/fixtures/test_catalog_client/no_test_in_py_file.csv,
    tests/unittests/fixtures/test_catalog_client/ts_not_present_in_python_file,
    tests/unittests/fixtures/test_catalog_client/no_ts_py_file.csv,
    tests/unittests/fixtures/test_catalog_client/test_suite_name_mismatch,
    tests/unittests/fixtures/test_catalog_client/test_suite_name_mismatch.csv,
    tests/unittests/fixtures/test_catalog_client/pass_dirs/extension,
    tests/unittests/fixtures/test_catalog_client/test_catalog_multiple_directory.csv
    """
    # Added mocker for return date function.
    mocker.patch("vane.test_catalog_client.return_date", return_value=("not_used", "2402182049"))
    test_catalog_obj = test_catalog_client.TestCatalogClient(test_directories)

    actual_rows = "Header and data rows are not collected."
    expected_rows = "Header and data rows should be collected."

    # Collecting the path from where test execution is started.
    test_catalog_path = os.path.join(request.config.rootpath, "test_catalog")
    test_catalog_file_path = os.path.join(test_catalog_path, "test_catalog_2402182049.csv")
    test_catalog_obj.write_test_catalog()

    # Checking if the file exists at the given path
    assert os.path.exists(test_catalog_file_path)

    try:
        # Reading the CSV file for header and data rows.
        with open(expected_output_file, encoding="utf_8", newline="") as exp_file:
            expected_rows = list(csv.reader(exp_file))

        with open(test_catalog_file_path, encoding="utf_8", newline="") as act_file:
            actual_rows = list(csv.reader(act_file))

        # Removing created CSV file.
        file_clean_up(test_catalog_file_path)

    except FileNotFoundError as error_msg:
        actual_rows = f"{error_msg}"

        # Removing created CSV file, if not deleted already.
        file_clean_up(test_catalog_file_path)

    assert sorted(actual_rows) == sorted(expected_rows)
