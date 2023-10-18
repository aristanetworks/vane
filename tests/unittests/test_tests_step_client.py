"""Test class for test_step_client.py"""

from unittest.mock import call
import os
import pytest
from vane import test_step_client


# Global test parameters
TEST_DIR = "tests/unittests/fixtures/host"
TEST_FILE = ["tests/unittests/fixtures/host/test_host.py"]
TEST_STEP = [
    "September 07, 2023 06:22:55PM",
    "TD: Verify hostname set on device is correct",
    "TS: Collecting the output of 'show hostname' command from DUT",
    "TS: Verify LLDP system name",
    "TS: Creating test report based on results",
]
NO_TEST_STEPS = [
    "September 07, 2023 06:22:55PM",
    "N/a no Test Steps found",
]
# find if using github actions
IN_GITHUB_ACTIONS = os.getenv("GITHUB_ACTIONS") == "true"


# pylint: disable=redefined-outer-name
@pytest.fixture
def loginfo(mocker):
    """Fixture to mock logger info calls from vane.test_step_client"""
    return mocker.patch("vane.vane_logging.logging.info")


@pytest.fixture
def logdebug(mocker):
    """Fixture to mock logger debug calls from vane.test_step_client"""
    return mocker.patch("vane.vane_logging.logging.debug")


def file_clean_up(fname):
    """Clean up files created in a test

    Args:
        fname(str): File name to delete
    """

    if os.path.isfile(fname):
        os.remove(fname)


def test_test_step_client_constructor(loginfo, logdebug):
    "Unit Test for TestStepClient object __init__ method"

    _ = test_step_client.TestStepClient(TEST_DIR)

    loginfo_calls = [
        call("Creating Test Step Client object"),
    ]
    loginfo.assert_has_calls(loginfo_calls, any_order=False)

    logdebug_calls = [
        call(f"Set Test Step Client object directory to {TEST_DIR}"),
    ]
    logdebug.assert_has_calls(logdebug_calls, any_order=False)


def test_write_test_steps(loginfo, mocker):
    "Unit Test for TestStepClient object, write_test_steps method"

    mocker_object = mocker.patch("vane.test_step_client.TestStepClient.walk_dir")
    test_steps = test_step_client.TestStepClient(TEST_DIR)
    test_steps.write_test_steps()
    mocker_object.assert_called_once()

    loginfo_calls = [
        call("Start writing test case steps"),
        call("Ending writing test case steps"),
    ]
    loginfo.assert_has_calls(loginfo_calls, any_order=False)


def test_walk_dir(logdebug, mocker):
    "Unit Test for TestStepClient object, method walk_dir"

    mocker_object = mocker.patch("vane.test_step_client.TestStepClient.parse_file")
    test_steps = test_step_client.TestStepClient([TEST_DIR])
    test_steps.walk_dir()
    mocker_object.assert_called_once()

    # These files are unique to git actions ci environment
    # This test will fail if ran locally
    files2 = [
        "test_definition.yaml",
        "test_definition_regenerated.yaml",
        "test_host.py",
        "__init__.py",
    ]

    logdebug_calls = [
        (f"Set Test Step Client object directory to {[TEST_DIR]}"),
        (f"Walking directory {TEST_DIR} for test cases"),
        (f"Discovered files {files2} in directory {TEST_DIR}"),
        (f"Discovered test files: {TEST_FILE} for parsing"),
    ]
    for c in logdebug_calls:
        logdebug.assert_any_call(c)


def test_parse_file(loginfo, logdebug, mocker):
    "Unit Test for TestStepClient object module parse_file"

    # Set datetime to a known value
    mocker.patch(
        "vane.test_step_client.return_date",
        return_value=("September 07, 2023 06:22:55PM", "not_used"),
    )
    mocker_object_one = mocker.patch("vane.test_step_client.TestStepClient.output_json")
    mocker_object_two = mocker.patch("vane.test_step_client.TestStepClient.output_md")
    test_steps = test_step_client.TestStepClient([TEST_DIR])
    test_steps.parse_file(TEST_FILE)
    mocker_object_one.assert_called_once()
    mocker_object_two.assert_called_once()

    loginfo_calls = [
        call("Parsing files for test steps and definitions"),
    ]
    loginfo.assert_has_calls(loginfo_calls, any_order=False)

    logdebug_calls = [
        call(f"Set Test Step Client object directory to ['{TEST_DIR}']"),
        call(f"Parsing file: {TEST_FILE[0]} for test steps and definitions"),
        call(f"Create JSON and MD files for {TEST_FILE[0]} using {TEST_STEP}"),
    ]
    logdebug.assert_has_calls(logdebug_calls, any_order=False)


def test_parse_file_no_steps(loginfo, logdebug, mocker):
    "Unit Test for TestStepClient object module walk_dir."

    # Set datetime to a known value
    mocker.patch(
        "vane.test_step_client.return_date",
        return_value=("September 07, 2023 06:22:55PM", "not_used"),
    )
    mocker_object_one = mocker.patch("vane.test_step_client.TestStepClient.output_json")
    mocker_object_two = mocker.patch("vane.test_step_client.TestStepClient.output_md")

    test_steps = test_step_client.TestStepClient([TEST_DIR])
    test_steps.parse_file(["tests/unittests/fixtures/host/test_definition.yaml"])
    mocker_object_one.assert_called_once()
    mocker_object_two.assert_called_once()

    loginfo_calls = [
        call("Parsing files for test steps and definitions"),
    ]
    loginfo.assert_has_calls(loginfo_calls, any_order=False)

    logdebug_calls = [
        call(
            "Create JSON and MD files for tests/unittests/fixtures/host/test_definition.yaml"
            f" using {NO_TEST_STEPS}"
        ),
    ]
    logdebug.assert_has_calls(logdebug_calls, any_order=False)


def test_output_json():
    "Unit Test for TestStepClient object module output_json"

    with open("tests/unittests/fixtures/expected_test_host.json", encoding="utf_8") as f_name:
        expected_output = f_name.read()

    test_steps = test_step_client.TestStepClient([TEST_DIR])
    test_steps.output_json({TEST_FILE[0]: TEST_STEP})

    with open("tests/unittests/fixtures/host/test_host.json", encoding="utf_8") as j_file:
        actual_output = j_file.read()

    file_clean_up("tests/unittests/fixtures/host/test_host.json")

    assert expected_output == actual_output


def test_output_md():
    "Unit Test for TestStepClient object module output_md"

    with open("tests/unittests/fixtures/expected_test_host.md", encoding="utf_8") as f_name:
        expected_output = f_name.read()

    test_steps = test_step_client.TestStepClient([TEST_DIR])
    test_steps.output_md({TEST_FILE[0]: TEST_STEP})

    with open("tests/unittests/fixtures/host/test_host.md", encoding="utf_8") as f_name:
        actual_output = f_name.read()

    file_clean_up("tests/unittests/fixtures/host/test_host.md")

    assert expected_output == actual_output


def test_output_md_no_steps():
    "Unit Test for TestStepClient object module output_md"

    with open(
        "tests/unittests/fixtures/expected_test_host_no_steps.md", encoding="utf_8"
    ) as f_name:
        expected_output = f_name.read()

    test_steps = test_step_client.TestStepClient([TEST_DIR])
    test_steps.output_md({TEST_FILE[0]: NO_TEST_STEPS})

    with open("tests/unittests/fixtures/host/test_host.md", encoding="utf_8") as f_name:
        actual_output = f_name.read()

    file_clean_up("tests/unittests/fixtures/host/test_host.md")

    assert expected_output == actual_output


def test_output_md_multiple_tests():
    "Unit Test for TestStepClient object module output_md"

    test_dirs = ["tests/unittests/fixtures/api"]
    test_files = "tests/unittests/fixtures/api/api.py"
    test_step = [
        "September 07, 2023 06:22:55PM",
        "TD: Verify management api https server is running",
        "TS: Collecting the output of 'show management api http-commands' command from DUT",
        "TS: Check HTTPS Server running status",
        "TS: Creating test report based on results",
        "TD: Verify https server is enabled on port 443",
        "TS: Collecting the output of 'show management api http-commands' command from DUT",
        "TS: Check HTTPS Server port",
        "TS: Creating test report based on results",
        "TD: Verify management api https server is enabled",
        "TS: Collecting the output of 'show management api http-commands' command from DUT",
        "TS: Check HTTPS Server is enabled",
        "TS: Creating test report based on results",
        "TD: Verify management api http server is not running",
        "TS: Collecting the output of 'show management api http-commands' command from DUT",
        "TS: Check HTTP Server running status",
        "TS: Creating test report based on results",
        "TD: Verify management api local httpserver is not running",
        "TS: Collecting the output of 'show management api http-commands' command from DUT",
        "TS: Check Local HTTP Server running status",
        "TS: Creating test report based on results",
    ]

    with open("tests/unittests/fixtures/expected_test_api.md", encoding="utf_8") as f_name:
        expected_output = f_name.read()

    test_steps = test_step_client.TestStepClient(test_dirs)
    test_steps.output_md({test_files: test_step})

    with open("tests/unittests/fixtures/api/api.md", encoding="utf_8") as f_name:
        actual_output = f_name.read()

    file_clean_up("tests/unittests/fixtures/api/api.md")

    assert expected_output == actual_output
