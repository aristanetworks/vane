"""
Test class for test_catalog_client.py
"""

from unittest.mock import call
import os
import csv
import json
import datetime
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
        "tests/unittests/fixtures/test_catalog_client/no_tests_in_python_file.csv",
    ),
    (
        ["tests/unittests/fixtures/test_catalog_client/no_test_steps_in_python_file"],
        "tests/unittests/fixtures/test_catalog_client/no_test_steps_in_python_file.csv",
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
    (["tests/unittests/fixtures/test_catalog_client/non_testing_files_having_tests_in_name/"], ""),
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
    test_catalog = test_catalog_client.TestCatalogClient([TEST_DIR])

    loginfo_calls = [
        call("Creating the test catalog client object"),
    ]
    loginfo.assert_has_calls(loginfo_calls, any_order=False)

    logdebug_calls = [
        call(f"Setting the test catalog client object directories to {[TEST_DIR]}"),
    ]
    logdebug.assert_has_calls(logdebug_calls, any_order=False)
    assert sorted(test_catalog.test_dirs) == sorted([TEST_DIR])


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
    test_files = [
        "tests/unittests/fixtures/test_catalog_client/pass_dirs/api/test_api.py",
        "tests/unittests/fixtures/test_catalog_client/pass_dirs/api/test_definition.yaml",
    ]
    # Patching the parse_test_data function.
    mocker_object = mocker.patch("vane.test_catalog_client.TestCatalogClient.parse_test_data")

    test_catalog = test_catalog_client.TestCatalogClient([TEST_DIR])
    test_catalog.walk_dir()

    # Verifying expected info logs are generated.
    mocker_object.assert_called_once()
    loginfo_call = [
        call("Creating the test catalog client object"),
        call(f"Walking directory {TEST_DIR} for the test cases"),
    ]
    loginfo.assert_has_calls(loginfo_call, any_order=False)

    # Verifying expected debug logs are generated.
    logdebug_call = [
        call(f"Setting the test catalog client object directories to {[TEST_DIR]}"),
        call(f"Discovered test files: {test_files} for parsing"),
    ]
    logdebug.assert_has_calls(logdebug_call, any_order=False)


def test_walk_dir_no_test_files_collected(mocker, capsys):
    """
    Unit Test for TestCatlogClient object, method walk_dir in case of no test files in directory
    Fixture or files used:
    tests/unittests/fixtures/test_catalog_client/no_test_files_directory
    """
    no_test_dir = "tests/unittests/fixtures/test_catalog_client/no_test_files_directory"

    # Patching the parse_test_data function.
    _ = mocker.patch("vane.test_catalog_client.TestCatalogClient.parse_test_data")

    test_catalog = test_catalog_client.TestCatalogClient([no_test_dir])

    # Catching the system exit during the pytest
    with pytest.raises(SystemExit) as exitinfo:
        test_catalog.walk_dir()
    captured = capsys.readouterr()

    # Verifying that if no tests found in directory then system exit is initiated with code 0.
    assert f"No test files found in directory {[no_test_dir]}." in captured.out

    assert (
        exitinfo.value.code == 0
    ), f"Expected system exit code is '0' however it is found as {exitinfo.value.code}"


def test_parse_test_data(loginfo, mocker):
    """
    Unit Test for TestCatlogClient object, method parse_test_data
    Fixture or files used:
    tests/unittests/fixtures/test_catalog_client/pass_dirs/api/test_api.py,
    tests/unittests/fixtures/test_catalog_client/pass_dirs/api/test_definition.yaml
    """
    test_files = [
        "tests/unittests/fixtures/test_catalog_client/pass_dirs/api/test_api.py",
        "tests/unittests/fixtures/test_catalog_client/pass_dirs/api/test_definition.yaml",
    ]
    parsed_test_def_file = "tests/unittests/fixtures/test_catalog_client/parsed_test_def.json"

    # Forming the expected info logs
    loginfo_calls = [call("Creating the test catalog client object")]
    for file in test_files:
        loginfo_calls.append(
            call(f"Opening {file} file to collect details required for the test catalog.")
        )

    loginfo_calls.append(call("Collected test data required for formation of the test catalog."))

    # Patching correlate_test_data and parse_python_file functions.
    mocker_object_one = mocker.patch(
        "vane.test_catalog_client.TestCatalogClient.correlate_test_data"
    )
    mocker_object_two = mocker.patch("vane.test_catalog_client.TestCatalogClient.parse_python_file")

    test_catalog = test_catalog_client.TestCatalogClient([TEST_DIR])
    test_catalog.parse_test_data(test_files)

    mocker_object_one.assert_called_once()
    mocker_object_two.assert_called_once()
    loginfo.assert_has_calls(loginfo_calls, any_order=False)

    # Collecting the parsed test definitions file.
    with open(parsed_test_def_file, encoding="utf_8") as parsed_test_def_file:
        expected_test_def_data = json.load(parsed_test_def_file)

    assert test_catalog.test_def_data == expected_test_def_data


def test_parse_python_file():
    """
    Unit Test for TestCatlogClient object, method parse_python_file
    Fixture or files used:
    tests/unittests/fixtures/test_catalog_client/pass_dirs/api/test_api.py
    tests/unittests/fixtures/test_catalog_client/parsed_python_file_content.json
    """

    py_file = "tests/unittests/fixtures/test_catalog_client/pass_dirs/api/test_api.py"
    json_file = "tests/unittests/fixtures/test_catalog_client/parsed_python_file_content.json"

    test_catalog = test_catalog_client.TestCatalogClient([TEST_DIR])

    # Reading python file.
    with open(py_file, encoding="utf_8") as python_file:
        py_content = python_file.read()

    # Collecting the expected output.
    with open(json_file, encoding="utf_8") as json_file_data:
        expected_output = json.load(json_file_data)

    # Collecting the the parsed data.
    test_catalog.parse_python_file(py_content, py_file)
    actual_output = test_catalog.test_file_data

    assert expected_output == actual_output


def test_correlate_test_data(mocker, loginfo):
    """
    Unit Test for TestCatlogClient object, method correlate_test_data
    Fixture or files used:
    tests/unittests/fixtures/test_catalog_client/parsed_python_file_content.json
    tests/unittests/fixtures/test_catalog_client/parsed_test_def.json
    tests/unittests/fixtures/test_catalog_client/correlated_data.json
    """
    test_catalog = test_catalog_client.TestCatalogClient([TEST_DIR])

    parsed_py_file = "tests/unittests/fixtures/test_catalog_client/parsed_python_file_content.json"
    parsed_test_def_file = "tests/unittests/fixtures/test_catalog_client/parsed_test_def.json"
    final_data_file = "tests/unittests/fixtures/test_catalog_client/correlated_data.json"
    test_catalog.test_file_data = {}
    test_catalog.test_def_data = {}

    # Collecting the parsed python file.
    with open(parsed_py_file, encoding="utf_8") as parsed_python_file:
        test_catalog.test_file_data = json.load(parsed_python_file)

    # Collecting the parsed test definitions file.
    with open(parsed_test_def_file, encoding="utf_8") as parsed_test_def_file:
        test_catalog.test_def_data = json.load(parsed_test_def_file)

    # Collecting corrleated data.
    with open(final_data_file, encoding="utf_8") as final_data_file:
        final_data = json.load(final_data_file)

    write_to_csv = mocker.patch.object(test_catalog, "write_to_csv")
    test_catalog.correlate_test_data()

    loginfo_call = "Completed data correlation between test definitions and Python file."
    loginfo.assert_any_call(loginfo_call)

    write_to_csv.assert_called_once_with(final_data)


def test_get_data_rows():
    """
    Unit Test for TestCatlogClient object, method get_data_rows
    Fixture or files used:
    tests/unittests/fixtures/test_catalog_client/correlated_data.json,
    tests/unittests/fixtures/test_catalog_client/test_catalog.csv
    """
    test_catalog = test_catalog_client.TestCatalogClient([TEST_DIR])
    json_file = "tests/unittests/fixtures/test_catalog_client/correlated_data.json"
    csv_file = "tests/unittests/fixtures/test_catalog_client/test_catalog.csv"

    # Collecting the correlated data.
    with open(json_file, encoding="utf_8") as json_file_data:
        correlated_data = json.load(json_file_data)

    # Collecting the expected data rows.
    with open(csv_file, encoding="utf_8") as catalog_file:
        expected_output = list(csv.reader(catalog_file))

    expected_data_rows = expected_output[1:]
    actual_data_rows = test_catalog.get_data_rows(correlated_data)

    # Verifying actual data rows are matching with expected data rows.
    assert actual_data_rows == expected_data_rows


def test_write_to_csv(loginfo, request, mocker):
    """
    Unit Test for TestCatlogClient object, method write_to_csv
    Fixture or files used:
    tests/unittests/fixtures/test_catalog_client/correlated_data.json
    tests/unittests/fixtures/test_catalog_client/test_catalog.csv
    """
    json_file = "tests/unittests/fixtures/test_catalog_client/correlated_data.json"
    data_rows_file = "tests/unittests/fixtures/test_catalog_client/test_catalog.csv"
    test_catalog = test_catalog_client.TestCatalogClient([TEST_DIR])

    # Collecting the final correlated data.
    with open(json_file, encoding="utf_8") as json_file_data:
        data = json.load(json_file_data)

    # Collecting the data rows.
    with open(data_rows_file, encoding="utf_8", newline="") as act_file:
        actual_rows = sorted(csv.reader(act_file))

    # Patching the get_data_rows
    mocker.patch(
        "vane.test_catalog_client.TestCatalogClient.get_data_rows", return_value=actual_rows[1:]
    )

    # Patching the file timestamp.
    date_str = datetime.datetime(2024, 3, 10, 7, 43, 10, 112250)
    mock_dt = mocker.patch("vane.test_catalog_client.datetime", warps=datetime)
    mock_dt.now.return_value = date_str
    file_timestamp = date_str.strftime("%Y%m%d%H%M%S")

    # Writing test catalog in the CSV file.
    test_catalog.write_to_csv(data)
    execution_path = request.config.rootpath
    test_catalog_path = os.path.join(execution_path, "test_catalog")

    # Checking log is generated and the file exists at the specified location.
    loginfo_call = [
        call(
            f"Writing a test catalog file: test_catalog_{file_timestamp}.csv in the"
            f" {test_catalog_path}"
        )
    ]
    loginfo.assert_has_calls(loginfo_call, any_order=False)

    # Verifying test catalog file is created.
    test_catalog_file_path = os.path.join(test_catalog_path, f"test_catalog_{file_timestamp}.csv")
    assert os.path.exists(test_catalog_file_path)
    file_clean_up(f"test_catalog/test_catalog_{file_timestamp}.csv")


@pytest.mark.parametrize(
    "test_directories, expected_output_file",
    PARAMETERIZATION_DATA,
    ids=[
        "test_case_details_matched_in_test_def_and_python_file",
        "test_case_name_mismatch",
        "no_tests_in_python_file",
        "no_tests_steps_in_python_file",
        "test_suite_name_mismatch",
        "multiple_test_directories",
        "test_recursive_catalog",
        "no_tests_in_provided_directory",
    ],
)
def test_main_test_catalog_functionality(
    request, capsys, mocker, test_directories, expected_output_file
):
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
    # Patching the file timestamp.
    date_str = datetime.datetime(2024, 3, 10, 7, 43, 11, 112250)
    mock_dt = mocker.patch("vane.test_catalog_client.datetime", warps=datetime)
    mock_dt.now.return_value = date_str
    test_catalog_obj = test_catalog_client.TestCatalogClient(test_directories)
    date_str = date_str.strftime("%Y%m%d%H%M%S")

    actual_rows = "Header and data rows are not collected."
    expected_rows = "Header and data rows should be collected."

    # Forming the path of test catalog file.
    test_catalog_path = os.path.join(request.config.rootpath, "test_catalog")
    test_catalog_file_path = os.path.join(test_catalog_path, f"test_catalog_{date_str}.csv")

    # Added condition for parameterized test no_tests_in_provided_directory
    if request.node.name.split("[")[1].split("]")[0] == "no_tests_in_provided_directory":
        # Checking if systemExit exception is raised.
        with pytest.raises(SystemExit) as exitinfo:
            test_catalog_obj.write_test_catalog()

        captured = capsys.readouterr()
        assert f"No tests found in the directory {test_directories}." in captured.out
        assert (
            exitinfo.value.code == 0
        ), f"Expected system exit code is '0' however it is found as {exitinfo.value.code}"

    else:
        test_catalog_obj.write_test_catalog()
        # Checking if the file exists at the given path
        assert os.path.exists(test_catalog_file_path)

        try:
            # Collecting the CSV file for header and data rows.
            with open(expected_output_file, encoding="utf_8", newline="") as exp_file:
                expected_rows = sorted(csv.reader(exp_file))

            # Reading the generated test catalog file.
            with open(test_catalog_file_path, encoding="utf_8", newline="") as act_file:
                actual_rows = sorted(csv.reader(act_file))

            # Removing created CSV file.
            file_clean_up(test_catalog_file_path)

        except FileNotFoundError as error_msg:
            actual_rows = f"{error_msg}"

            # Removing created CSV file, if not deleted already.
            file_clean_up(test_catalog_file_path)

        assert actual_rows == expected_rows
