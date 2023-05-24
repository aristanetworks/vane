"""
tests_client.py unit tests
"""

# Disable redefined-outer-name for using loginfo and logerr fixture functions
# Disable protected-access for testing hidden class functions
# Disable import-error for missing vane imports (avoid requiring install of vane just for linting)
# pylint: disable=redefined-outer-name, protected-access, import-error

import os
import tempfile
import unittest

from unittest.mock import call

import pytest
import vane.tests_client


# Common duts file
DUTS = "tests/fixtures/duts.yaml"


@pytest.fixture
def loginfo(mocker):
    """Fixture to mock logger info calls from vane.tests_client"""
    return mocker.patch("vane.tests_client.logging.info")


@pytest.fixture
def logwarn(mocker):
    """Fixture to mock logger warning calls from vane.tests_client"""
    return mocker.patch("vane.tests_client.logging.warning")


@pytest.fixture
def logerr(mocker):
    """Fixture to mock logger error calls from vane.tests_client"""
    return mocker.patch("vane.tests_client.logging.error")


def test_constructor():
    """Verify instance of TestsClient Object can be created"""

    client = vane.tests_client.TestsClient("tests/unittests/fixtures/definitions.yaml", DUTS)

    methods = [
        "_get_markers",
        "_init_parameters",
        "_remove_result_files",
        "_remove_test_results_dir",
        "_render_eapi_cfg",
        "_set_cmdline_input",
        "_set_cmdline_no_input",
        "_set_cmdline_report",
        "_set_excel_report",
        "_set_html_report",
        "_set_json_report",
        "_set_junit",
        "_set_mark",
        "_set_processes",
        "_set_setup_show",
        "_set_stdout",
        "_set_test_cases",
        "_set_test_dirs",
        "_set_test_parameters",
        "_set_verbosity",
        "_write_file",
        "generate_test_definitions",
        "setup_test_runner",
        "test_runner",
        "write_test_def_file",
    ]
    variables = ["data_model", "duts_model"]

    # Test for known methods in object
    for method in methods:
        assert method in dir(client)

    # Test for known methods in variables
    for variable in variables:
        assert variable in dir(client)


def test_write_test_def_file(loginfo):
    """Validate creating test definitions using master definitions"""

    # Load a definitions file with generate_test_definitions set to false, to create a client
    client = vane.tests_client.TestsClient("tests/unittests/fixtures/definitions.yaml", DUTS)

    # Set the definitions information to be passed to write_test_def_file
    template_definitions = "test_definition.yaml"
    master_definitions = {}
    test_dir = "tests/unittests/fixtures"
    test_definitions = "test_definition_regenerated.yaml"  # don't overwrite the file

    # Make sure the regenerated file does not exist
    if os.path.exists(test_definitions):
        os.remove(test_definitions)

    # Write test def file
    client.write_test_def_file(template_definitions, master_definitions, test_dir, test_definitions)

    # Verify the definitions file was regenerated
    assert os.path.exists(f"{test_dir}/{test_definitions}")

    # Assert the new definition file contains the expected data (compare with known definition file)
    # pylint: disable=consider-using-with
    unittest.TestCase().assertListEqual(
        list(open(f"{test_dir}/{test_definitions}", mode="r", encoding="utf-8")),
        list(open("tests/unittests/fixtures/test_definition.yaml", mode="r", encoding="utf-8")),
    )

    # Verify logging message was called
    loginfo.assert_called_with("Regenerated test definition files")


def test_generate_test_definitions(loginfo):
    """Validate creating test definitions using master definitions"""

    # Load a definitions file with generate_test_definitions set to false
    client = vane.tests_client.TestsClient("tests/unittests/fixtures/definitions.yaml", DUTS)

    # Generate test definitions
    client.generate_test_definitions()

    # Verify logging message was called
    loginfo.assert_called_with("Attempting to regenerate test definition files")


def test_generate_test_definitions_regen(loginfo, mocker):
    """Validate creating test definitions with generate_test_definitions set to true"""

    # Mocke the file open function so we don't actually change anything
    mocker.patch("vane.tests_client.open")

    # Load a definitions file with generate_test_definitions set to true
    client = vane.tests_client.TestsClient(
        "tests/unittests/fixtures/definitions-generate.yaml", DUTS
    )

    # Generate test definitions
    client.generate_test_definitions()

    # Verify logging message was called (implying files were regenerated)
    loginfo.assert_called_with("Regenerated test definition files")


@pytest.mark.parametrize(
    # Set up iterative tests for the next test case
    # Each test passes in a separate definitions file, and a specific error message if
    # that test case fails
    "defs_file, fail_msg",
    [
        (
            # Load a definitions file with no generate_test_definitions key
            "tests/unittests/fixtures/definitions-no-generate-key.yaml",
            "tests_client.generate_test_definitions() did not handle missing key "
            "'generate_test_definitions'",
        ),
        (
            # Load a definitions file with no master_definitions key
            "tests/unittests/fixtures/definitions-no-master-def-key.yaml",
            "tests_client.generate_test_definitions() did not handle missing key "
            "'master_definitions'",
        ),
        (
            # Load a definitions file with no template_definitions key
            "tests/unittests/fixtures/definitions-no-template-def-key.yaml",
            "tests_client.generate_test_definitions() did not handle missing key "
            "'template_definitions'",
        ),
        (
            # Load a definitions file with no test_definitions key
            "tests/unittests/fixtures/definitions-no-test-def-key.yaml",
            "tests_client.generate_test_definitions() did not handle missing key "
            "'test_definitions'",
        ),
        (
            # Load a definitions file with no test_dirs key
            "tests/unittests/fixtures/definitions-no-test-dirs-key.yaml",
            "tests_client.generate_test_definitions() did not handle missing key 'test_dirs'",
        ),
    ],
)
def test_generate_test_definitions_neg(mocker, capsys, defs_file, fail_msg):
    """Validate key errors are handled by generate_test_definitions"""

    # Mock the write_test_def_file routine in case we get past the negative tests
    mocker.patch("vane.tests_client.TestsClient.write_test_def_file", return_value=None)

    # Create the client from the passed-in definitions file and common duts file
    client = vane.tests_client.TestsClient(defs_file, DUTS)

    # Call the generate test definitions method
    client.generate_test_definitions()

    # Examine the captured stdout output and verify the expected error was received, otherwise
    # report the passed-in failure message
    captured = capsys.readouterr()
    assert captured.out == "Unable to regenerate test definition files.\n", fail_msg


def test_test_runner(mocker, capsys, loginfo):
    """Validate test_runner function without generating test definitions"""

    # Load a definitions file with generate_test_definitions set to false
    client = vane.tests_client.TestsClient("tests/unittests/fixtures/definitions.yaml", DUTS)

    # Mock a valid test run
    mocker.patch("vane.tests_client.pytest.main", return_value=None)

    # Run the tests
    client.test_runner()

    captured = capsys.readouterr()
    assert (
        captured.out == "Starting test with command: pytest \n\n"
    ), "tests_client.test_runner failed when expected to pass"

    # Verify logging message was called
    loginfo.assert_called_with("Starting Test with parameters: []")


def test_test_runner_no_tests(mocker, capsys):
    """Validate test_runner with no tests collected error returned"""

    # Load a definitions file with generate_test_definitions set to false
    client = vane.tests_client.TestsClient("tests/unittests/fixtures/definitions.yaml", DUTS)

    # Mock a NO_TESTS_COLLECTED result
    mocker.patch("vane.tests_client.pytest.main", return_value=pytest.ExitCode.NO_TESTS_COLLECTED)

    # Catch the system exit during the pytest
    with pytest.raises(SystemExit) as pytest_exit:
        # Run the tests
        client.test_runner()

    captured = capsys.readouterr()
    assert (
        "No tests collected with pytest command" in captured.out
    ), "tests_client.test_runner did not fail when no tests were collected"

    # Validate the system exit was called
    assert pytest_exit.type == SystemExit
    assert pytest_exit.value.code == 1


def test_test_runner_usage_err(mocker, capsys):
    """Validate test_runner with usage error returned"""

    # Load a definitions file with generate_test_definitions set to false
    client = vane.tests_client.TestsClient("tests/unittests/fixtures/definitions.yaml", DUTS)

    # Mock a USAGE_ERROR result
    mocker.patch("vane.tests_client.pytest.main", return_value=pytest.ExitCode.USAGE_ERROR)

    # Catch the system exit during the pytest
    with pytest.raises(SystemExit) as pytest_exit:
        # Run the tests
        client.test_runner()

    captured = capsys.readouterr()
    assert (
        "Pytest usage error with parameters" in captured.out
    ), "tests_client.test_runner did not fail when usage error detected"

    # Validate the system exit was called
    assert pytest_exit.type == SystemExit
    assert pytest_exit.value.code == 1


def test__set_test_parameters(loginfo):
    """Validate _set_test_parameters with various values"""

    # pylint: disable-next=fixme
    # XXX several options all output "enable pytest output true/false" instead of
    # something descriptive of what is being set. A future issue will correct this,
    # requiring changes to the test case here to match the updated output strings.

    # Load a definitions file built for _set_test_parameters
    client = vane.tests_client.TestsClient(
        "tests/unittests/fixtures/defs_set_test_params.yaml", DUTS
    )

    # Run _set_test_parameters
    client._set_test_parameters()

    # Validate the following messages are logged in order
    loginfo_calls = [
        call("Use data-model to create test parameters"),
        call("Setting test parameters"),
        call("Initialize test parameter values"),
        call("Enable pytest output True"),
        call("Enable pytest output True"),
        call("Enable pytest output True"),
        call("Run the following tests: All"),
        call("Running All test cases."),
        call("Set HTML report name to: --html=tests/unittests/fixtures/reports/report.html"),
        call("Set --json report name to: --json=tests/unittests/fixtures/reports/report.json"),
        call("Not Setting PyTest -n"),
        call("Set PyTest -m to: demo"),
    ]
    loginfo.assert_has_calls(loginfo_calls, any_order=False)


def test__set_test_parameters_unset(loginfo, logwarn):
    """Validate _set_test_parameters that unsets parameters in functions"""

    # Load a definitions file built for _set_test_parameters with some parameters set
    # to false in the file to be unset by the functions
    client = vane.tests_client.TestsClient(
        "tests/unittests/fixtures/defs_unset_test_params.yaml", DUTS
    )

    # Run _set_test_parameters
    client._set_test_parameters()

    # Validate the following info messages are logged in order
    loginfo_calls = [
        call("Use data-model to create test parameters"),
        call("Setting test parameters"),
        call("Initialize test parameter values"),
        call("Enable pytest output True"),
        call("Run the following tests: "),
        call("Could not find test cases."),
        call("Not Setting PyTest -n"),
        call("Set PyTest -m to: demo"),
    ]
    loginfo.assert_has_calls(loginfo_calls, any_order=False)

    # Validate the following warning messages are logged in order
    logwarn_calls = [
        call("Disable pytest output False"),
        call("Disable pytest output False"),
        call("HTML report will NOT be created"),
        call("--excelreport report will NOT be created"),
        call("--json report will NOT be created"),
    ]
    logwarn.assert_has_calls(logwarn_calls, any_order=False)


def test__set_test_parameters_unset_cmd_line(loginfo, logwarn):
    """Validate _set_test_parameters that unsets parameters based on command line options"""

    # Load a definitions file built for _set_test_parameters with some parameters set
    # to false in the file to be unset by the functions, but we will override parameters
    # with command line options
    client = vane.tests_client.TestsClient(
        "tests/unittests/fixtures/defs_unset_test_params.yaml", DUTS
    )

    # Add the command line option that sets a parameter
    client.test_parameters.append("--setup-show")

    # Run _set_test_parameters
    client._set_test_parameters()

    # Validate the following info messages are logged in order
    loginfo_calls = [
        call("Use data-model to create test parameters"),
        call("Setting test parameters"),
        call("Initialize test parameter values"),
        call("Enable pytest output True"),
        call("Remove and disable pytest output False"),
        call("Run the following tests: "),
        call("Could not find test cases."),
        call("Not Setting PyTest -n"),
        call("Set PyTest -m to: demo"),
    ]
    loginfo.assert_has_calls(loginfo_calls, any_order=False)

    # Validate the following warning messages are logged in order
    logwarn_calls = [
        call("Disable pytest output False"),
        call("HTML report will NOT be created"),
        call("--excelreport report will NOT be created"),
        call("--json report will NOT be created"),
    ]
    logwarn.assert_has_calls(logwarn_calls, any_order=False)


def test__render_eapi_cfg(loginfo):
    """Validate _render_eapi_config"""

    # Load a definitions file built for _render_eapi_cfg
    # This definition file has an eapi file that is named eapi_rendered.conf
    client = vane.tests_client.TestsClient(
        "tests/unittests/fixtures/defs_render_eapi_cfg.yaml", DUTS
    )

    # Make sure the rendered eapi file does not exist
    filepath = client.data_model["parameters"]["eapi_file"]
    if os.path.exists(filepath):
        os.remove(filepath)

    # Run _render_eapi_cfg
    client._render_eapi_cfg()

    # Assert the expected file was created
    assert os.path.exists(filepath)

    # Assert the new eapi file contains the expected data (compare with known eapi file)
    # pylint: disable=consider-using-with
    unittest.TestCase().assertListEqual(
        list(open(filepath, mode="r", encoding="utf-8")),
        list(open("tests/unittests/fixtures/eapi.conf", mode="r", encoding="utf-8")),
    )

    # Validate the following messages are logged in order
    loginfo_calls = [
        call("Render .eapi.conf file for device access"),
        call("Open tests/fixtures/templates/eapi.conf.j2 Jinja2 template for reading"),
        call("Read and save contents of tests/fixtures/templates/eapi.conf.j2 Jinja2 template"),
        call(
            "Using tests/fixtures/templates/eapi.conf.j2 Jinja2 template to render "
            "tests/unittests/fixtures/eapi_rendered.conf file with parameters "
            "[{'mgmt_ip': '10.255.74.38', 'name': 'BL1', 'neighbors': [{'neighborDevice': "
            "'leaf1', 'neighborPort': 'Ethernet1', 'port': 'Ethernet1'}, {'neighborDevice': "
            "'leaf2', 'neighborPort': 'Ethernet1', 'port': 'Ethernet2'}], 'password': 'cvp123!', "
            "'transport': 'https', 'username': 'cvpadmin', 'role': 'leaf'}, {'mgmt_ip': "
            "'10.255.22.26', 'name': 'BL2', 'neighbors': [{'neighborDevice': 'leaf1', "
            "'neighborPort': 'Ethernet1', 'port': 'Ethernet1'}, {'neighborDevice': 'leaf2', "
            "'neighborPort': 'Ethernet1', 'port': 'Ethernet2'}], 'password': 'cvp123!', "
            "'transport': 'https', 'username': 'cvpadmin', 'role': 'leaf'}]"
        ),
        call(
            "Rendered tests/unittests/fixtures/eapi_rendered.conf as: [connection:BL1]\n"
            "host: 10.255.74.38\nusername: cvpadmin\n\npassword: cvp123!\n\ntransport: "
            "https\n\n[connection:BL2]\nhost: 10.255.22.26\nusername: cvpadmin\n\n"
            "password: cvp123!\n\ntransport: https\n\n"
        ),
        call("Open tests/unittests/fixtures/eapi_rendered.conf for writing"),
        call("Change permissions of tests/unittests/fixtures/eapi_rendered.conf to 777"),
    ]
    loginfo.assert_has_calls(loginfo_calls, any_order=False)


def test__render_eapi_cfg_neg(loginfo, logerr, capsys):
    """Validate failure when eapi_template does not exist"""

    # Load a definitions file built for _render_eapi_cfg
    # This definition file has an eapi file that is named eapi_rendered.conf
    client = vane.tests_client.TestsClient(
        "tests/unittests/fixtures/defs_render_eapi_cfg_no_template.yaml", DUTS
    )

    template = client.data_model["parameters"]["eapi_template"]

    # Catch the system exit during the pytest
    with pytest.raises(SystemExit) as pytest_exit:
        # Run _render_eapi_cfg
        client._render_eapi_cfg()

    captured = capsys.readouterr()
    err_msg = f"[Errno 2] No such file or directory: '{template}'"
    assert (
        f">>> ERROR READING {template}: {err_msg}" in captured.out
    ), "tests_client._render_eapi_cfg did not fail when template file could not be read"

    # Validate the system exit was called
    assert pytest_exit.type == SystemExit
    assert pytest_exit.value.code == 1

    # Validate the following messages are logged in order
    loginfo_calls = [
        call("Render .eapi.conf file for device access"),
        call("Open tests/fixtures/templates/eapi.missing.conf.j2 Jinja2 template for reading"),
    ]
    loginfo.assert_has_calls(loginfo_calls, any_order=False)

    # Validate the following messages are logged in order
    logerr_calls = [
        call(f"ERROR READING {template}: {err_msg}"),
        call("EXITING TEST RUNNER"),
    ]
    logerr.assert_has_calls(logerr_calls, any_order=False)


def test__write_file_neg(loginfo, logerr, capsys):
    """Validate failure when eapi_file path is not writable"""

    # Load a definitions file built for _render_eapi_cfg
    # This definition file has an eapi file that with a path that does not exist
    client = vane.tests_client.TestsClient(
        "tests/unittests/fixtures/defs_render_eapi_cfg_bad_path.yaml", DUTS
    )

    filepath = client.data_model["parameters"]["eapi_file"]

    # Catch the system exit during the pytest
    with pytest.raises(SystemExit) as pytest_exit:
        # Run _render_eapi_cfg
        client._render_eapi_cfg()

    captured = capsys.readouterr()
    err_msg = f"[Errno 2] No such file or directory: '{filepath}'"
    assert (
        f">>> ERROR WRITING {filepath}: {err_msg}" in captured.out
    ), "tests_client._write_file did not fail when eapi file path could not be opened"

    # Validate the system exit was called
    assert pytest_exit.type == SystemExit
    assert pytest_exit.value.code == 1

    # Validate the following messages are logged in order
    loginfo_calls = [
        call("Render .eapi.conf file for device access"),
        call("Open tests/fixtures/templates/eapi.conf.j2 Jinja2 template for reading"),
        call("Read and save contents of tests/fixtures/templates/eapi.conf.j2 Jinja2 template"),
        call(
            "Using tests/fixtures/templates/eapi.conf.j2 Jinja2 template to render "
            "tests/unittests/fixtures/invalid/path/eapi_rendered.conf file with parameters "
            "[{'mgmt_ip': '10.255.74.38', 'name': 'BL1', 'neighbors': [{'neighborDevice': "
            "'leaf1', 'neighborPort': 'Ethernet1', 'port': 'Ethernet1'}, {'neighborDevice': "
            "'leaf2', 'neighborPort': 'Ethernet1', 'port': 'Ethernet2'}], 'password': 'cvp123!', "
            "'transport': 'https', 'username': 'cvpadmin', 'role': 'leaf'}, {'mgmt_ip': "
            "'10.255.22.26', 'name': 'BL2', 'neighbors': [{'neighborDevice': 'leaf1', "
            "'neighborPort': 'Ethernet1', 'port': 'Ethernet1'}, {'neighborDevice': 'leaf2', "
            "'neighborPort': 'Ethernet1', 'port': 'Ethernet2'}], 'password': 'cvp123!', "
            "'transport': 'https', 'username': 'cvpadmin', 'role': 'leaf'}]"
        ),
        call(
            "Rendered tests/unittests/fixtures/invalid/path/eapi_rendered.conf as: "
            "[connection:BL1]\nhost: 10.255.74.38\nusername: cvpadmin\n\npassword: cvp123!\n\n"
            "transport: https\n\n[connection:BL2]\nhost: 10.255.22.26\nusername: cvpadmin\n\n"
            "password: cvp123!\n\ntransport: https\n\n"
        ),
        call("Open tests/unittests/fixtures/invalid/path/eapi_rendered.conf for writing"),
    ]
    loginfo.assert_has_calls(loginfo_calls, any_order=False)

    # Validate the following messages are logged in order
    logerr_calls = [
        call(f"ERROR WRITING {filepath}: {err_msg}"),
        call("EXITING TEST RUNNER"),
    ]
    logerr.assert_has_calls(logerr_calls, any_order=False)


def test__remove_result_files(loginfo):
    """Validate _remove_result_files removes pre-existing results files"""

    # Create a tests_client client
    client = vane.tests_client.TestsClient("tests/unittests/fixtures/definitions.yaml", DUTS)

    # Prepopulate the unittest results dir with "result-*" files
    result_dir = "tests/unittests/fixtures/reports/results"
    files = []
    for _ in range(10):
        # pylint: disable-next=consider-using-with
        tmpf = tempfile.NamedTemporaryFile(prefix="result-", dir=result_dir, delete=False)
        files.append(tmpf.name)

    # Call the function to remove the results files
    client._remove_result_files()

    # Verify the result files were deleted
    loginfo_calls = []
    for filename in files:
        loginfo_calls.append(call(f"Remove result file: {result_dir}/{os.path.basename(filename)}"))
        assert not os.path.exists(filename)

    # Verify the removal messages were logged
    loginfo.assert_has_calls(loginfo_calls, any_order=True)


# pytest.mark.filterwarnings: Ignore the warning we receive from the tempfile library
# because it can't find the files to clean them up because we deleted them manually. We
# don't tell it to not clean up the files just in case the test fails and the files do get
# left behind for some reason.
@pytest.mark.filterwarnings("ignore:Exception ignored")
def test_remove_test_results_dir(loginfo):
    """Validate _tremove_test_results_dir removes the TEST RESULTS directory"""

    # Create a tests_client client
    client = vane.tests_client.TestsClient("tests/unittests/fixtures/definitions.yaml", DUTS)

    # Make sure the reports/TEST RESULTS dir exists
    results_dir = "reports/TEST RESULTS"
    if not os.path.exists(results_dir):
        os.makedirs(results_dir)

    # Prepopulate the TEST RESULTS directory with "result-*" files
    files = []
    for _ in range(10):
        # pylint: disable-next=consider-using-with
        tmpf = tempfile.NamedTemporaryFile(prefix="result-", dir=results_dir)
        files.append(tmpf)

    # Call _remove_test_results_dir
    client._remove_test_results_dir()

    # Verify the TEST RESULTS directory was removed
    assert not os.path.exists(results_dir)

    # Verify the removal was logged
    loginfo.assert_called_with(f"Deleted {results_dir} directory successfully")
