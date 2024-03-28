"""vane_cli.py uni tests"""
import argparse
import os
import glob
from io import StringIO
from unittest.mock import call
import pytest
import vane
from vane import vane_cli

# Disable redefined-outer-name for using log fixture functions
# pylint: disable=redefined-outer-name


@pytest.fixture
def loginfo(mocker):
    """Fixture to mock logger calls from vane.vane_cli"""
    return mocker.patch("vane.vane_logging.logging.info")


@pytest.fixture
def logerr(mocker):
    """Fixture to mock logger calls from vane.vane_cli"""
    return mocker.patch("vane.vane_logging.logging.error")


@pytest.fixture
def logwarning(mocker):
    """Fixture to mock logger calls from vane.vane_cli"""
    return mocker.patch("vane.vane_logging.logging.warning")


def test_setup_vane(loginfo, mocker):
    """Validates functionality of setup_vane method"""

    # mocking these methods since they have been tested in tests_tools tests

    mocker_object = mocker.patch("vane.tests_tools.import_yaml")
    mocker_object.side_effect = ["Duts_file", "Test_parameters"]
    mocker.patch("vane.tests_tools.return_test_defs", return_value="Test definitions")
    mocker.patch("vane.tests_tools.return_show_cmds", return_value="show_commands")
    mocker.patch("vane.tests_tools.init_duts", return_value="Dut object")

    vane_cli.setup_vane()

    # assert the vane.configs got set correctly
    assert vane.config.test_duts == "Duts_file"
    assert vane.config.test_parameters == "Test_parameters"
    assert vane.config.test_defs == "Test definitions"
    assert vane.config.dut_objs == "Dut object"

    # assert logs to ensure the method executed without errors
    loginfo_calls = [
        call("Starting Test Suite setup"),
        call("Discovering show commands from definitions"),
    ]
    loginfo.assert_has_calls(loginfo_calls, any_order=False)


def test_run_tests(loginfo, mocker):
    """Validates functionality of run_tests method"""

    # mocking these methods since they have been tested in tests_client tests
    mocker_object = mocker.patch("vane.tests_client.TestsClient")
    mocker.patch("vane.vane_cli.setup_vane")

    vane_cli.run_tests("path/to/definitions/file", "path/to/duts/file")

    mocker_object.assert_called_once_with("path/to/definitions/file", "path/to/duts/file")

    # Assert that the generate_test_definitions, setup_test_runner,
    # and test_runner method was called on the
    # returned TestClient instance

    test_client_instance = mocker_object.return_value
    test_client_instance.generate_test_definitions.assert_called_once()
    test_client_instance.setup_test_runner.assert_called_once()
    test_client_instance.test_runner.assert_called_once()

    loginfo.assert_called_with("Using class TestsClient to create vane_tests_client object")


def test_write_results(loginfo, mocker):
    """Validates functionality of write_results method"""

    # mocking these methods since they have been tested in report_client tests
    mocker_object = mocker.patch("vane.report_client.ReportClient")

    vane_cli.write_results("path/to/definitions/file")

    mocker_object.assert_called_once_with("path/to/definitions/file")

    # Assert that the write_result_doc method was called on the
    # returned ReportClient instance

    report_client_instance = mocker_object.return_value
    report_client_instance.write_result_doc.assert_called_once()

    loginfo.assert_called_with("Using class ReportClient to create vane_report_client object")


def test_show_markers(mocker):
    """Validates the functionality of show_markers method"""

    # mocking pytest.main's call to get mockers and setting our set of values
    mocker.patch("pytest.main")

    mock_stdout = mocker.Mock(spec=StringIO)
    value = (
        "@pytest.mark.filesystem: EOS File System Test Suite\n\n"
        "@pytest.mark.daemons: EOS daemons Test Suite\n\n"
        "@pytest.mark.extensions: EOS extensions Test Suite\n\n"
        "@pytest.mark.users: EOS users Test Suite\n\n"
        "@pytest.mark.tacacs: TACACS Test Suite"
    )
    mock_stdout.getvalue.return_value = value

    # Patch the 'StringIO' class to return the mock object
    mocker.patch("vane.vane_cli.StringIO", return_value=mock_stdout)

    expected_output = [
        {"marker": "filesystem", "description": "EOS File System Test Suite"},
        {"marker": "daemons", "description": "EOS daemons Test Suite"},
        {"marker": "extensions", "description": "EOS extensions Test Suite"},
        {"marker": "users", "description": "EOS users Test Suite"},
        {"marker": "tacacs", "description": "TACACS Test Suite"},
    ]
    actual_output = vane_cli.show_markers()
    assert actual_output == expected_output


def test_download_test_results(loginfo):
    """Validates if a zip archive got created and stored in the TEST RESULTS
    ARCHIVE folder"""

    dir_path = "reports/TEST RESULTS ARCHIVES"
    source_path = "reports/TEST RESULTS"
    if os.path.isdir(dir_path) and os.path.isdir(source_path):
        length = len(list(os.listdir(dir_path)))
        vane_cli.download_test_results()
        new_length = len(os.listdir(dir_path))

        # assert if a zip got created
        assert new_length == (length + 1)

        # delete the most recent zip that got created for the test
        list_of_files = glob.glob(dir_path + "/*")
        latest_file = max(list_of_files, key=os.path.getctime)
        os.remove(latest_file)

        loginfo.assert_called_with("Downloading a zip file of the TEST RESULTS folder")


def test_main_definitions_and_duts(loginfo, logwarning, mocker):
    """Tests the --definitions-file and --duts-file flag"""

    mocker.patch("vane.vane_cli.run_tests")
    mocker.patch("vane.vane_cli.write_results")
    mocker.patch("vane.vane_cli.download_test_results")

    # mocking parse cli to test --definitions-file and --duts-file flag
    mocker.patch(
        "vane.vane_cli.parse_cli",
        return_value=argparse.Namespace(
            definitions_file="definitions_sample.yaml",
            duts_file="duts_sample.yaml",
            generate_duts_file=None,
            generate_test_catalog=None,
            markers=False,
            nrfu=False,
            version=False,
        ),
    )
    vane_cli.main()

    assert vane.config.DEFINITIONS_FILE == "definitions_sample.yaml"
    assert vane.config.DUTS_FILE == "duts_sample.yaml"

    # assert info logs to ensure all the above methods executed without errors
    loginfo_calls = [
        call("Reading in input from command-line"),
        call("\n\n!VANE has completed without errors!\n\n"),
    ]
    loginfo.assert_has_calls(loginfo_calls, any_order=False)

    # assert warning logs to ensure all the above methods executed without errors
    logwarning_calls = [
        call("Changing Definitions file name to definitions_sample.yaml"),
        call("Changing DUTS file name to duts_sample.yaml"),
    ]
    logwarning.assert_has_calls(logwarning_calls, any_order=False)


def test_main_create_duts_file(loginfo, mocker):
    """Tests the --generate-duts-file flag"""

    mocker.patch("vane.tests_tools.create_duts_file")

    # mocking parse cli to test --generate-duts-file
    mocker.patch(
        "vane.vane_cli.parse_cli",
        return_value=argparse.Namespace(
            definitions_file="definitions_sample.yaml",
            duts_file="duts_sample.yaml",
            generate_duts_file=["topology.yaml", "inventory.yaml", "duts_name.yaml"],
            generate_duts_from_topo=None,
            generate_test_catalog=None,
            markers=False,
            nrfu=False,
        ),
    )
    vane_cli.main()

    # assert info logs to ensure all the above methods executed without errors
    loginfo_calls = [
        call("Reading in input from command-line"),
        call(
            "Generating DUTS File from topology: topology.yaml and "
            "inventory: inventory.yaml file.\n"
        ),
    ]
    loginfo.assert_has_calls(loginfo_calls, any_order=False)


def test_main_write_test_catalog(loginfo, mocker):
    """
    Tests the --generate-test-catalog flag
    """

    mocker.patch("vane.vane_cli.write_test_catalog")

    # mocking parse cli to test --generate-test-catalog
    mocker.patch(
        "vane.vane_cli.parse_cli",
        return_value=argparse.Namespace(
            definitions_file=None,
            duts_file=None,
            generate_duts_file=None,
            generate_test_catalog="test_directories",
            markers=False,
            test_definitions_file="test_definitions_file"
        ),
    )
    vane_cli.main()

    # assert info logs to ensure write_test_catalog method is executed without errors
    loginfo_calls = [
        call("Reading in input from command-line"),
        call("Generating test catalog for test cases within test_directories test directories\n"),
    ]
    loginfo.assert_has_calls(loginfo_calls, any_order=False)
