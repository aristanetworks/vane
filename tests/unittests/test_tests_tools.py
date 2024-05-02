"""Test class for tests_tools.py"""
import os
import shutil
import sys
from unittest.mock import call, MagicMock
from icmplib.exceptions import SocketPermissionError
from pyeapi.eapilib import ConnectionError  # pylint: disable=W0622
from netmiko.exceptions import NetmikoAuthenticationException
import pytest
import yaml
import pyeapi.eapilib
import vane
from tests.unittests.fixtures.test_steps import test_steps
from vane import tests_tools


# TEST UTILITY FUNCTIONS

# Disable redefined-outer-name for using log fixture functions
# Disable protected-access for testing hidden class functions
# Disable too-many-lines and too-many-function-args since some test functions
# need to be long and passed a certain number of arguments
# pylint: disable=redefined-outer-name, protected-access, too-many-lines, too-many-function-args


@pytest.fixture
def loginfo(mocker):
    """Fixture to mock logger info calls from vane.tests_tools"""
    return mocker.patch("vane.vane_logging.logging.info")


@pytest.fixture
def logerr(mocker):
    """Fixture to mock logger error  calls from vane.tests_tools"""
    return mocker.patch("vane.vane_logging.logging.error")


@pytest.fixture
def logdebug(mocker):
    """Fixture to mock logger debug calls from vane.tests_tools"""
    return mocker.patch("vane.vane_logging.logging.debug")


@pytest.fixture
def logcritical(mocker):
    """Fixture to mock logger critical calls from vane.tests_tools"""
    return mocker.patch("vane.vane_logging.logging.critical")


def read_yaml(yaml_file):
    """Import YAML file as python data structure

    Args:
        yaml_file (str): Name of YAML file

    Returns:
        yaml_data (dict): YAML data structure
    """

    try:
        with open(yaml_file, "r", encoding="utf-8") as input_yaml:
            try:
                yaml_data = yaml.safe_load(input_yaml)
                return yaml_data
            except yaml.YAMLError as err:
                print(f">>> ERROR IN YAML FILE: {err}\n EXITING TEST RUNNER")
                sys.exit(1)
    except OSError as err:
        print(f">>> {yaml_file} YAML FILE MISSING. {err}\n EXITING TEST RUNNER.")
        sys.exit(1)


# NON TEST-OPS METHODS


def test_filter_duts(loginfo):
    """Validates the method which filters duts according to criteria and dut filter by
    passing different combinations of those inputs"""
    duts = [
        {"role": "Role1", "name": "Test Dut 1"},
        {"role": "Role2", "name": "Test Dut 2"},
    ]

    # check when no criteria or filter is set
    output_duts, output_names = tests_tools.filter_duts(duts, "", "")
    assert len(output_duts) == 2
    assert len(output_names) == 2
    loginfo.assert_called_with("Filter:  by criteria: ")

    # check when criteria is set but filter is not
    output_duts, output_names = tests_tools.filter_duts(duts, "roles", "")
    assert len(output_duts) == 0
    assert len(output_names) == 0
    loginfo.assert_called_with("Filter:  by criteria: roles")

    # check when criteria is not set but filter is set
    output_duts, output_names = tests_tools.filter_duts(duts, "", "Role1")
    assert len(output_duts) == 2
    assert len(output_names) == 2
    loginfo.assert_called_with("Filter: Role1 by criteria: ")

    # check when criteria and filter both are set
    # Criteria: Roles
    # One filter value
    output_duts, output_names = tests_tools.filter_duts(duts, "roles", ["Role1"])
    assert len(output_duts) == 1
    assert len(output_names) == 1

    # Two filter values
    output_duts, output_names = tests_tools.filter_duts(duts, "roles", ["Role1", "Role2"])
    assert len(output_duts) == 2
    assert len(output_names) == 2

    # Criteria: Names
    # One filter value
    output_duts, output_names = tests_tools.filter_duts(duts, "names", ["Test Dut 1"])
    assert len(output_duts) == 1
    assert len(output_names) == 1

    # Two filter values
    output_duts, output_names = tests_tools.filter_duts(duts, "names", ["Test Dut 1", "Test Dut 2"])
    assert len(output_duts) == 2
    assert len(output_names) == 2

    # Criteria: Regex
    # Regex match
    output_duts, output_names = tests_tools.filter_duts(duts, "regex", "Te")
    assert len(output_duts) == 2
    assert len(output_names) == 2
    loginfo.assert_called_with("Filter: Te by criteria: regex")

    # Regex mismatch
    output_duts, output_names = tests_tools.filter_duts(duts, "regex", "R")
    assert len(output_duts) == 0
    assert len(output_names) == 0
    loginfo.assert_called_with("Filter: R by criteria: regex")


def test_parametrize_duts(loginfo, logdebug):
    """Validates the parametrize_duts method"""
    # defining parameters to pass to method under test
    test_fname = "vane-tests-bofa/tests/nrfu_tests/baseline_mgmt_tests"
    test_defs = {
        "test_suites": [
            {
                "name": "baseline_mgmt_tests",
                "testcases": [
                    {"name": "test_local_user_access"},
                    {"name": "test_tacacs_functionality", "criteria": "names", "filter": ["DLFW3"]},
                ],
            }
        ]
    }
    duts = [
        {"role": "Role1", "name": "DLFW3"},
        {"role": "Role2", "name": "Test Dut 2"},
    ]
    actual_dut_parameters = tests_tools.parametrize_duts(test_fname, test_defs, duts)
    loginfo_calls = [
        call("Discover test suite name"),
        call("Filtering test definitions by test suite name: baseline_mgmt_tests"),
        call("Unpack testcases by defining dut and criteria"),
        call("Filter:  by criteria: "),
        call("Filter: ['DLFW3'] by criteria: names"),
    ]
    loginfo.assert_has_calls(loginfo_calls, any_order=False)

    logdebug_calls = [
        call(
            "Creating dut parameters.  \nDuts: [{'role': 'Role1', 'name': 'DLFW3'}, "
            "{'role': 'Role2', 'name': 'Test Dut 2'}] \nIds: ['DLFW3', 'Test Dut 2']"
        ),
        call(
            "Creating dut parameters.  \nDuts: [{'role': 'Role1', 'name': 'DLFW3'}]"
            " \nIds: ['DLFW3']"
        ),
    ]
    logdebug.assert_has_calls(logdebug_calls, any_order=False)

    # defining expected output
    expected_dut_parameters = {}
    expected_dut_parameters["test_local_user_access"] = {}
    expected_dut_parameters["test_local_user_access"]["duts"] = duts
    expected_dut_parameters["test_local_user_access"]["ids"] = [duts[0]["name"], duts[1]["name"]]
    expected_dut_parameters["test_tacacs_functionality"] = {}
    expected_dut_parameters["test_tacacs_functionality"]["duts"] = [duts[0]]
    expected_dut_parameters["test_tacacs_functionality"]["ids"] = [duts[0]["name"]]

    assert expected_dut_parameters == actual_dut_parameters


@pytest.mark.parametrize(
    "input_file_data, expected_yaml",
    [
        ("", {}),
        ("a: 1", {"a": 1}),
    ],
)
def test_yaml_read_valid_yaml(mocker, input_file_data, expected_yaml):
    """Validates read yaml method"""
    mocked_file_data = mocker.mock_open(read_data=input_file_data)
    mocker.patch("builtins.open", mocked_file_data)
    actual_yaml = tests_tools.import_yaml("yaml_file")
    assert expected_yaml == actual_yaml


def test_yaml_read_invalid_yaml(mocker, logerr):
    """Validates yaml read method with invalid yaml"""
    mocked_file_data = mocker.mock_open(read_data="a: a: b:")
    mocker.patch("builtins.open", mocked_file_data)
    sys_exit_mocked = mocker.patch("sys.exit")
    tests_tools.import_yaml("yaml_file")
    sys_exit_mocked.assert_called_with(1)
    logerr.assert_called_with("EXITING TEST RUNNER")


def test_import_yaml_success(mocker):
    """Validates import yaml method"""
    mocked_file_data = mocker.mock_open(read_data="a: 1\nb: 2\n")
    mocker.patch("builtins.open", mocked_file_data)
    expected_yaml = {"a": 1, "b": 2}
    actual_yaml = tests_tools.import_yaml("yaml_file")
    assert expected_yaml == actual_yaml


def test_import_yaml_non_existing_file(mocker, logerr):
    """Validates import yaml method with non-existing file"""
    sys_exit_mocked = mocker.patch("sys.exit")
    tests_tools.import_yaml("tests/unittests/fixtures/non_existing_file.yaml")
    sys_exit_mocked.assert_called_with(1)
    logerr.assert_called_with("EXITING TEST RUNNER")


def test_init_duts_reachable(loginfo, logdebug, mocker):
    """Validates the functionality of init_duts
    FIXTURE NEEDED: fixture_definitions.yaml, fixture_duts.yaml"""
    show_cmds = ["show version", "show clock"]
    test_parameters = read_yaml("tests/unittests/fixtures/fixture_definitions.yaml")
    test_duts = read_yaml("tests/unittests/fixtures/fixture_duts.yaml")

    mocker.patch("vane.tests_tools.login_duts", return_value=([test_duts["duts"][0]], []))
    mocker.patch("vane.tests_tools.dut_worker")
    mocker.patch(
        "vane.tests_tools.check_duts_reachability", return_value=(True, [test_duts["duts"][0]], [])
    )

    reachable_duts, unreachable_duts = tests_tools.init_duts(show_cmds, test_parameters, test_duts)

    assert reachable_duts == [test_duts["duts"][0]]
    assert not unreachable_duts

    loginfo_calls = [
        call(
            "Find DUTs and then execute inputted show commands "
            "on each dut. Return structured data of DUTs output "
            "data, hostname, and connection."
        ),
        call("Starting the execution of show commands for Vane cache"),
        call("Returning duts data structure"),
    ]
    loginfo.assert_has_calls(loginfo_calls, any_order=False)

    logdebug_calls = [
        call(f"Duts login info: {reachable_duts} and create 1 workers"),
        call("Passing the following show commands to workers: ['show version', 'show clock']"),
        call("Future object generated successfully"),
        call(f"Return duts data structure: {reachable_duts}"),
        call(f"Return unreachable duts data structure: {unreachable_duts}"),
    ]
    logdebug.assert_has_calls(logdebug_calls, any_order=False)


def test_init_duts_unreachable_and_not_continue(loginfo, logdebug, logerr, mocker):
    """Validates the functionality of init_duts
    FIXTURE NEEDED: fixture_definitions.yaml, fixture_duts.yaml"""
    show_cmds = ["show version", "show clock"]
    test_parameters = read_yaml("tests/unittests/fixtures/fixture_definitions.yaml")
    test_duts = read_yaml("tests/unittests/fixtures/fixture_duts.yaml")

    mocker.patch("vane.tests_tools.login_duts", return_value=([test_duts["duts"][0]], []))
    mocker.patch("vane.tests_tools.dut_worker")
    mocker.patch(
        "vane.tests_tools.check_duts_reachability",
        return_value=(False, [test_duts["duts"][0]], [test_duts["duts"][1]]),
    )
    sys_exit_mocked = mocker.patch("sys.exit")
    reachable_duts, unreachable_duts = tests_tools.init_duts(show_cmds, test_parameters, test_duts)

    assert reachable_duts == [test_duts["duts"][0]]
    assert unreachable_duts == [test_duts["duts"][1]]

    loginfo_calls = [
        call(
            "Find DUTs and then execute inputted show commands "
            "on each dut. Return structured data of DUTs output "
            "data, hostname, and connection."
        ),
        call("Starting the execution of show commands for Vane cache"),
        call("Returning duts data structure"),
    ]
    loginfo.assert_has_calls(loginfo_calls, any_order=False)

    logdebug_calls = [
        call(f"Duts login info: {reachable_duts} and create 1 workers"),
        call("Passing the following show commands to workers: ['show version', 'show clock']"),
        call("Future object generated successfully"),
        call(f"Return duts data structure: {reachable_duts}"),
        call(f"Return unreachable duts data structure: {unreachable_duts}"),
    ]
    logdebug.assert_has_calls(logdebug_calls, any_order=False)

    sys_exit_mocked.assert_called_with(1)
    logerr.assert_called_with(
        f"Error connecting to {unreachable_duts}, not reachable via ping, hence exiting Vane"
    )


def test_login_duts_eapi(loginfo, logdebug, mocker):
    """Validates the functionality of login_duts
    FIXTURE NEEDED: fixture_definitions.yaml, fixture_duts.yaml"""

    test_parameters = read_yaml("tests/unittests/fixtures/fixture_definitions.yaml")
    test_duts = read_yaml("tests/unittests/fixtures/fixture_duts.yaml")
    duts = test_duts["duts"]

    # mocking method calls in login_duts

    mocker.patch(
        "vane.tests_tools.import_yaml",
        return_value={"DSR01": "network_configs", "DCBBW1": "network_configs"},
    )

    mocker_object = mocker.patch("vane.device_interface.PyeapiConn")
    pyeapi_instance = mocker_object.return_value

    mocker_authentication_object = mocker.patch("vane.tests_tools.authenticate_and_setup_conn")
    mocker_authentication_object.side_effect = [True, True]

    reachable_duts, _ = tests_tools.login_duts(test_parameters, duts)

    # assert values when pyeapi connection

    for index in range(0, 2):
        dut_info = reachable_duts[index]
        assert dut_info["eapi_conn"] == pyeapi_instance
        assert dut_info["connection"] == pyeapi_instance
        assert dut_info["name"] == test_duts["duts"][index]["name"]
        assert dut_info["mgmt_ip"] == test_duts["duts"][index]["mgmt_ip"]
        assert dut_info["username"] == test_duts["duts"][index]["username"]
        assert dut_info["role"] == test_duts["duts"][index]["role"]
        assert dut_info["neighbors"] == test_duts["duts"][index]["neighbors"]
        assert dut_info["results_dir"] == test_parameters["parameters"]["results_dir"]
        assert dut_info["report_dir"] == test_parameters["parameters"]["report_dir"]
        assert dut_info["network_configs"] == "network_configs"

    # assert logs

    loginfo_calls = [
        call("Using eapi/ssh to connect to Arista switches for testing"),
        call("Connecting to switch: DSR01"),
        call("Connecting to switch: DCBBW1"),
        call(f"Returning reachable_duts: {reachable_duts}"),
    ]

    loginfo.assert_has_calls(loginfo_calls, any_order=False)

    logdebug_calls = [
        call(f"Connecting to switch: DSR01 using parameters: {duts[0]}"),
        call(f"Connecting to switch: DCBBW1 using parameters: {duts[1]}"),
    ]

    logdebug.assert_has_calls(logdebug_calls, any_order=False)

    # assert values when neither pyeapi nor ssh connection

    test_parameters["parameters"]["eos_conn"] = "invalid_connection_type"

    try:
        reachable_duts, _ = tests_tools.login_duts(test_parameters, duts)
    except ValueError as exception:
        assert str(exception) == "Invalid EOS conn type invalid_connection_type specified"


def test_login_duts_no_neighbor_no_role_info(mocker):
    """Validates the functionality of login_duts when neighbors and
    role info is missing"""
    test_parameters = read_yaml("tests/unittests/fixtures/fixture_definitions.yaml")
    test_duts = read_yaml("tests/unittests/fixtures/fixture_duts_no_neighbors_no_role.yaml")
    duts = test_duts["duts"]
    test_parameters["parameters"]["eos_conn"] = "ssh"

    mocker.patch(
        "vane.tests_tools.import_yaml",
        return_value={"DSR01": "network_configs", "DCBBW1": "network_configs"},
    )

    mocker.patch("vane.device_interface.NetmikoConn")

    mocker.patch("vane.tests_tools.authenticate_and_setup_conn", return_value=True)

    reachable_duts, _ = tests_tools.login_duts(test_parameters, duts)
    dut_info = reachable_duts[0]

    # assert value when no neighbors and no role is present in duts file

    assert dut_info["neighbors"] == ""
    assert dut_info["role"] == ""


def test_login_duts_ssh(loginfo, logdebug, mocker):
    """Validates the functionality of login_duts
    FIXTURE NEEDED: fixture_definitions.yaml, fixture_duts.yaml"""

    test_parameters = read_yaml("tests/unittests/fixtures/fixture_definitions.yaml")
    test_duts = read_yaml("tests/unittests/fixtures/fixture_duts.yaml")
    duts = test_duts["duts"]
    test_parameters["parameters"]["eos_conn"] = "ssh"

    # mocking method calls in login_duts

    mocker.patch(
        "vane.tests_tools.import_yaml",
        return_value={"DSR01": "network_configs", "DCBBW1": "network_configs"},
    )

    mocker_object = mocker.patch("vane.device_interface.NetmikoConn")
    netmiko_instance = mocker_object.return_value

    mocker_authentication_object = mocker.patch("vane.tests_tools.authenticate_and_setup_conn")
    mocker_authentication_object.side_effect = [True, False]

    reachable_duts, unreachable_duts = tests_tools.login_duts(test_parameters, duts)

    # assert values when netmiko connection

    dut_info = reachable_duts[0]
    assert dut_info["ssh_conn"] == netmiko_instance
    assert dut_info["connection"] == netmiko_instance
    assert dut_info["name"] == test_duts["duts"][0]["name"]
    assert dut_info["mgmt_ip"] == test_duts["duts"][0]["mgmt_ip"]
    assert dut_info["username"] == test_duts["duts"][0]["username"]
    assert dut_info["role"] == test_duts["duts"][0]["role"]
    assert dut_info["neighbors"] == test_duts["duts"][0]["neighbors"]
    assert dut_info["results_dir"] == test_parameters["parameters"]["results_dir"]
    assert dut_info["report_dir"] == test_parameters["parameters"]["report_dir"]
    assert dut_info["network_configs"] == "network_configs"

    assert len(reachable_duts) == 1
    assert unreachable_duts[0] == duts[1]
    # assert logs

    loginfo_calls = [
        call("Using eapi/ssh to connect to Arista switches for testing"),
        call("Connecting to switch: DSR01"),
        call("Connecting to switch: DCBBW1"),
        call(f"Returning reachable_duts: {reachable_duts}"),
    ]

    loginfo.assert_has_calls(loginfo_calls, any_order=False)

    logdebug_calls = [
        call(f"Connecting to switch: DSR01 using parameters: {duts[0]}"),
        call(f"Connecting to switch: DCBBW1 using parameters: {duts[1]}"),
    ]

    logdebug.assert_has_calls(logdebug_calls, any_order=False)


def test_check_duts_reachability_when_unreachable(mocker, loginfo):
    """Validates the functionality of check_duts_reachability method
    when a dut is unreachable"""

    mocker_object1 = MagicMock()
    mocker_object2 = MagicMock()

    mocker_object = mocker.patch("vane.tests_tools.ping")
    mocker_object.side_effect = [mocker_object1, mocker_object2]

    mocker_object1.is_alive = True
    mocker_object2.is_alive = False

    test_duts = {
        "duts": [
            {
                "mgmt_ip": "10.255.70.132",
                "name": "DCBBW1",
                "password": "cvp123!",
                "transport": "https",
                "username": "cvpadmin",
                "role": "unknown",
            },
            {
                "mgmt_ip": "10.255.70.133",
                "name": "DCBBW2",
                "password": "cvp123!",
                "transport": "https",
                "username": "cvpadmin",
                "role": "unknown",
            },
        ]
    }

    reachability, reachable_duts, unreachable_duts = tests_tools.check_duts_reachability(test_duts)
    assert not reachability
    assert reachable_duts[0] == test_duts["duts"][0]
    assert unreachable_duts[0] == test_duts["duts"][1]
    loginfo_calls = [call("Checking connectivity of duts"), call("Failed to connect to DCBBW2")]

    loginfo.assert_has_calls(loginfo_calls, any_order=False)


def test_authenticate_and_setup_conn_netmiko_valid(mocker, loginfo):
    """Validate the functionality of authenticate_and_setup_conn
    method when valid netmiko connection is setup"""

    mocker_object = mocker.patch("vane.device_interface.NetmikoConn")
    netmiko_instance = mocker_object.return_value

    test_duts = read_yaml("tests/unittests/fixtures/fixture_duts.yaml")
    dut = test_duts["duts"][0]

    success = tests_tools.authenticate_and_setup_conn(dut, netmiko_instance)

    # assert called to NetmikoConn were made correctly
    assert netmiko_instance.set_up_conn.call_count == 1

    name = dut["name"]
    loginfo.assert_called_with(f"Authentication to dut {name} is successful")

    assert success


def test_authenticate_and_setup_conn_netmiko_invalid(mocker, logerr, capsys):
    """Validate the functionality of authenticate_and_setup_conn
    method when netmiko connection with invalid credentials is tried
    and Vane should exit out immediately"""

    mocker_object = mocker.patch("vane.device_interface.NetmikoConn")
    netmiko_instance = mocker_object.return_value
    sys_exit_mocked = mocker.patch("sys.exit")

    # Create a MagicMock for the set_up_conn method
    mocked_set_up_conn = mocker.patch.object(netmiko_instance, "set_up_conn")

    # Configure the MagicMock to raise an exception when called
    mocked_set_up_conn.side_effect = NetmikoAuthenticationException("Incorrect credentials")

    test_duts = read_yaml("tests/unittests/fixtures/fixture_duts.yaml")
    dut = test_duts["duts"][0]

    vane.config.test_parameters = {"parameters": {"continue_when_unreachable": False}}

    tests_tools.authenticate_and_setup_conn(dut, netmiko_instance)

    # assert calls NetmikoConn were made correctly

    assert netmiko_instance.set_up_conn.call_count == 1

    name = dut["name"]
    logerr.assert_called_with(
        f"Exiting Vane: Error running all cmds on dut {name} due to failed authentication."
        " Incorrect credentials\n"
    )

    captured_output = capsys.readouterr()

    output = (
        "\x1b[31mExiting Vane.\n"
        f"Error running all cmds on dut {name} due to failed authentication."
        "\nIncorrect credentials\n"
        "\x1b[0m"
    )

    # Assert that the expected prints occurred
    assert output in captured_output.out

    sys_exit_mocked.assert_called_with(1)


def test_authenticate_and_setup_conn_pyeapi_valid(mocker, loginfo):
    """Validate the functionality of authenticate_and_setup_conn
    method when pyeapi connection with invalid credentials is tried"""

    mocker_object = mocker.patch("vane.device_interface.PyeapiConn")
    pyeapi_instance = mocker_object.return_value

    test_duts = read_yaml("tests/unittests/fixtures/fixture_duts.yaml")
    dut = test_duts["duts"][0]

    success = tests_tools.authenticate_and_setup_conn(dut, pyeapi_instance)

    # assert calls PyeapiConn were made correctly

    assert pyeapi_instance.set_up_conn.call_count == 1

    name = dut["name"]
    loginfo.assert_called_with(f"Authentication to dut {name} is successful")

    assert success


def test_authenticate_and_setup_conn_pyeapi_invalid(mocker, loginfo):
    """Validate the functionality of authenticate_and_setup_conn
    method when pyeapi connection with invalid credentials is tried
    and Vane should still continue"""

    mocker_object = mocker.patch("vane.device_interface.PyeapiConn")
    pyeapi_instance = mocker_object.return_value

    # Create a MagicMock for the set_up_conn method
    mocked_set_up_conn = mocker.patch.object(pyeapi_instance, "set_up_conn")

    # Configure the MagicMock to raise an exception when called
    mocked_set_up_conn.side_effect = ConnectionError("pyeapi", "Incorrect Credentials")

    test_duts = read_yaml("tests/unittests/fixtures/fixture_duts.yaml")
    dut = test_duts["duts"][0]

    vane.config.test_parameters = {"parameters": {"continue_when_unreachable": True}}

    success = tests_tools.authenticate_and_setup_conn(dut, pyeapi_instance)

    # assert calls NetmikoConn were made correctly

    assert pyeapi_instance.set_up_conn.call_count == 1

    name = dut["name"]
    loginfo.assert_called_with(f"Authentication to dut {name} failed")

    assert not success


def test_check_duts_reachability_when_reachable(mocker, loginfo):
    """Validates the functionality of check_duts_reachability method
    when dut is reachable"""

    mocker_object = mocker.patch("vane.tests_tools.ping")
    host = mocker_object.return_value
    host.is_alive = True
    test_duts = {
        "duts": [
            {
                "mgmt_ip": "10.255.70.133",
                "name": "DCBBW1",
                "password": "cvp123!",
                "transport": "https",
                "username": "cvpadmin",
                "role": "unknown",
            }
        ]
    }

    reachability, reachable_duts, unreachable_duts = tests_tools.check_duts_reachability(test_duts)
    assert reachability
    assert reachable_duts[0] == test_duts["duts"][0]
    assert not unreachable_duts

    loginfo_calls = [
        call("Checking connectivity of duts"),
    ]

    loginfo.assert_has_calls(loginfo_calls, any_order=False)


def test_check_duts_reachability_when_exception(mocker, loginfo, logerr):
    """Validates the functionality of check_duts_reachability method
    when an exception is raised but dut is reachable"""

    mocker_object = mocker.patch("vane.tests_tools.ping")
    mocker.patch("os.system", return_value=0)
    mocker_object.side_effect = [
        SocketPermissionError("Windows subsystem cannot execute this package")
    ]
    test_duts = {
        "duts": [
            {
                "mgmt_ip": "10.255.70.133",
                "name": "DCBBW1",
                "password": "cvp123!",
                "transport": "https",
                "username": "cvpadmin",
                "role": "unknown",
            }
        ]
    }

    reachability, reachable_duts, unreachable_duts = tests_tools.check_duts_reachability(test_duts)
    assert reachability
    assert reachable_duts[0] == test_duts["duts"][0]
    assert not unreachable_duts

    loginfo_calls = [
        call("Checking connectivity of duts"),
    ]

    loginfo.assert_has_calls(loginfo_calls, any_order=False)
    logerr.assert_called_with(
        "Entered the exception due to permission issues: "
        "Root privileges are required to create the socket\n"
        "Trying the ping utility via os.system instead"
    )


def test_send_cmds_json(loginfo, logdebug, mocker):
    """Validates the functionality of send_cmds method"""

    # mocking call to run commands method on connection object

    mocker.patch("vane.device_interface.PyeapiConn.run_commands", return_value="output_in_json")

    show_cmds = ["show version"]
    show_cmds_output, show_cmd_list_output = tests_tools.send_cmds(
        show_cmds, vane.device_interface.PyeapiConn, "json"
    )

    # asserting return values when encoding is json

    assert show_cmds_output == "output_in_json"
    assert show_cmd_list_output == show_cmds
    loginfo.assert_called_with("Ran all show commands on dut to gather json data")
    logdebug_calls = [
        call("List of show commands in show_cmds with encoding json: ['show version']"),
        call("Ran all show cmds with encoding json: ['show version']"),
        call("Return all show cmds: output_in_json"),
    ]
    logdebug.assert_has_calls(logdebug_calls, any_order=False)


def test_send_cmds_text(loginfo, logdebug, mocker):
    """Validates the functionality of send_cmds method"""

    # mocking call to run commands method on connection object

    mocker.patch("vane.device_interface.PyeapiConn.run_commands", return_value="output_in_text")

    show_cmds = ["show version"]
    show_cmds_output, show_cmd_list_output = tests_tools.send_cmds(
        show_cmds, vane.device_interface.PyeapiConn, "text"
    )

    # asserting return values when encoding is text

    assert show_cmds_output == "output_in_text"
    assert show_cmd_list_output == show_cmds
    loginfo.assert_called_with("Ran all show commands on dut to gather text data")
    logdebug_calls = [
        call("List of show commands in show_cmds with encoding text: ['show version']"),
        call("Ran all show cmds with encoding text: ['show version']"),
        call("Return all show cmds: output_in_text"),
    ]
    logdebug.assert_has_calls(logdebug_calls, any_order=False)


def test_send_cmds_exception(logdebug, logerr, mocker):
    """Validates the functionality of send_cmds method"""

    # mocking call to run commands method on connection object

    mocker_object = mocker.patch("vane.device_interface.PyeapiConn.run_commands")
    mocker_object.side_effect = [
        Exception("show version is erring"),
        "",
    ]

    show_cmds = ["show version"]
    show_cmds_output, show_cmd_list_output = tests_tools.send_cmds(
        show_cmds, vane.device_interface.PyeapiConn, "text"
    )

    # asserting when run_commands raises an exception
    assert show_cmds_output == ""
    assert show_cmd_list_output == []
    logdebug_calls = [
        call("New show_cmds: []"),
    ]
    logdebug.assert_has_calls(logdebug_calls, any_order=False)

    logerr.assert_called_with("Error running all cmds: show version is erring")


error = ["show lldp neighbors has an error in it", "show lldp neighbors status has an error in it"]
show_cmds = [
    ["show version", "show clock", "show lldp neighbors", "show lldp neighbors status"],
    ["show version", "show clock", "show lldp neighbors", "show lldp neighbors status"],
]
expected_output = [
    ["show version", "show clock", "show lldp neighbors status"],
    ["show version", "show clock", "show lldp neighbors"],
]


@pytest.mark.parametrize(
    "error, show_cmds, expected_output",
    [(error[0], show_cmds[0], expected_output[0]), (error[1], show_cmds[1], expected_output[1])],
)
def test_remove_cmd(error, show_cmds, expected_output):
    """Validates functionality of remove_cmd method"""

    actual_output = tests_tools.remove_cmd(error, show_cmds)
    assert expected_output == actual_output


def test_dut_worker(logdebug, mocker):
    """Validates functionality of dut_worker method
    FIXTURE NEEDED: fixture_duts.yaml"""
    dut = {
        "connection": "vane.device_interface.PyeapiConn",
        "name": "DSR01",
        "mgmt_ip": "10.255.50.212",
        "username": "cvpadmin",
        "role": "unknown",
        "neighbors": [
            {"neighborDevice": "DCBBW1", "neighborPort": "Ethernet1", "port": "Ethernet1"},
            {"neighborDevice": "DCBBW2", "neighborPort": "Ethernet1", "port": "Ethernet2"},
            {"neighborDevice": "DCBBE1", "neighborPort": "Ethernet1", "port": "Ethernet3"},
            {"neighborDevice": "DCBBE2", "neighborPort": "Ethernet1", "port": "Ethernet4"},
        ],
        "results_dir": "reports/results",
        "report_dir": "reports",
        "eapi_file": "tests/unittests/fixtures/eapi.conf",
    }
    show_cmds = ["show version", "show clock"]
    test_duts = read_yaml("tests/unittests/fixtures/fixture_duts.yaml")

    # mocking methods called in dut_worker

    mocker_object = mocker.patch("vane.tests_tools.send_cmds")
    mocker_object.side_effect = [
        [["version_output_json"], ["show version"]],
        [[{"output": "clock_output_text"}], ["show clock"]],
    ]
    mocker.patch("vane.tests_tools.return_interfaces", return_value=[])

    tests_tools.dut_worker(dut, show_cmds, test_duts)

    # assert values

    assert dut["output"]["interface_list"] == []
    assert dut["output"]["show version"]["json"] == "version_output_json"
    assert dut["output"]["show clock"]["json"] == ""
    assert dut["output"]["show version"]["text"] == ""
    assert dut["output"]["show clock"]["text"] == "clock_output_text"

    logdebug_calls = [
        call("List of show commands ['show version', 'show clock']"),
        call("Returned from send_cmds_json ['show version']"),
        call("Returned from send_cmds_txt ['show clock']"),
        call("Executing show command: show version for test test_show_version"),
        call("Adding output of show version to duts data structure"),
        call("Found cmd: show version at index 0 of ['show version']"),
        call("length of cmds: 1 vs length of output 1"),
        call("Adding cmd show version to dut and data version_output_json"),
        call("No text output for show version"),
        call("Executing show command: show clock for test test_show_clock"),
        call("Adding output of show clock to duts data structure"),
        call("No json output for show clock"),
        call("Found cmd: show clock at index 0 of ['show clock']"),
        call("length of cmds: 1 vs length of output 1"),
        call("Adding cmd show clock to dut and data clock_output_text"),
    ]
    logdebug.assert_has_calls(logdebug_calls, any_order=False)


def test_return_interfaces(loginfo, logdebug):
    """Validates if interfaces are being read properly from test parameters
    FIXTURE NEEDED: fixture_duts.yaml and fixture_duts_no_neighbors.yaml"""
    test_duts = read_yaml("tests/unittests/fixtures/fixture_duts.yaml")
    duts = test_duts["duts"]
    actual_output = tests_tools.return_interfaces("DSR01", duts)
    expected_output = [
        {
            "hostname": "DSR01",
            "interface_name": "Ethernet1",
            "z_hostname": "DCBBW1",
            "z_interface_name": "Ethernet1",
            "media_type": "",
        },
        {
            "hostname": "DSR01",
            "interface_name": "Ethernet2",
            "z_hostname": "DCBBW2",
            "z_interface_name": "Ethernet1",
            "media_type": "",
        },
        {
            "hostname": "DSR01",
            "interface_name": "Ethernet3",
            "z_hostname": "DCBBE1",
            "z_interface_name": "Ethernet1",
            "media_type": "",
        },
        {
            "hostname": "DSR01",
            "interface_name": "Ethernet4",
            "z_hostname": "DCBBE2",
            "z_interface_name": "Ethernet1",
            "media_type": "",
        },
    ]
    assert actual_output == expected_output
    loginfo_calls = [
        call("Parse reachable_duts for interface connections and return them to test"),
        call("Discovering interface parameters for: DSR01"),
        call("Returning interface list."),
    ]
    loginfo.assert_has_calls(loginfo_calls, any_order=False)
    logdebug_calls = [
        call(
            "Adding interface parameters:"
            " {'neighborDevice': 'DCBBW1', 'neighborPort': 'Ethernet1', 'port': 'Ethernet1'}"
            " neighbor for: DSR01"
        ),
        call(
            "Adding interface parameters:"
            " {'neighborDevice': 'DCBBW2', 'neighborPort': 'Ethernet1', 'port': 'Ethernet2'}"
            " neighbor for: DSR01"
        ),
        call(
            "Adding interface parameters:"
            " {'neighborDevice': 'DCBBE1', 'neighborPort': 'Ethernet1', 'port': 'Ethernet3'}"
            " neighbor for: DSR01"
        ),
        call(
            "Adding interface parameters:"
            " {'neighborDevice': 'DCBBE2', 'neighborPort': 'Ethernet1', 'port': 'Ethernet4'}"
            " neighbor for: DSR01"
        ),
        call(
            "Returning interface list:"
            " [{'hostname': 'DSR01', 'interface_name': 'Ethernet1',"
            " 'z_hostname': 'DCBBW1', 'z_interface_name': 'Ethernet1', 'media_type': ''},"
            " {'hostname': 'DSR01', 'interface_name': 'Ethernet2',"
            " 'z_hostname': 'DCBBW2', 'z_interface_name': 'Ethernet1', 'media_type': ''},"
            " {'hostname': 'DSR01', 'interface_name': 'Ethernet3',"
            " 'z_hostname': 'DCBBE1', 'z_interface_name': 'Ethernet1', 'media_type': ''},"
            " {'hostname': 'DSR01', 'interface_name': 'Ethernet4',"
            " 'z_hostname': 'DCBBE2', 'z_interface_name': 'Ethernet1', 'media_type': ''}]"
        ),
    ]
    logdebug.assert_has_calls(logdebug_calls, any_order=False)

    # Test to validate return_interfaces when neighbors field is not present in duts.yaml
    test_duts = read_yaml("tests/unittests/fixtures/fixture_duts_no_neighbors_no_role.yaml")
    duts = test_duts["duts"]
    actual_output = tests_tools.return_interfaces("DSR01", duts)
    expected_output = []
    assert actual_output == expected_output


def test_get_parameters(loginfo, logdebug):
    """Validates getting test case details from test parameters, suites and name
    FIXTURES NEEDED: fixture_test_parameters.yaml"""
    tests_parameters = read_yaml("tests/unittests/fixtures/fixture_test_parameters.yaml")
    test_suite = "sample_network_tests/aaa/test_aaa.py"
    test_case = "test_if_exec_authorization_methods_set_on_"

    expected_output = {
        "name": "test_if_exec_authorization_methods_set_on_",
        "description": "Verify AAA exec authorization are method-lists set correct",
        "exec_auth": ["none"],
        "show_cmd": "show aaa methods all",
        "expected_output": None,
        "comment": None,
        "result": True,
        "test_suite": "test_aaa.py",
    }

    actual_output = tests_tools.get_parameters(tests_parameters, test_suite, test_case)
    assert expected_output == actual_output

    loginfo_calls = [
        call("Identify test case and return parameters"),
        call("Return testcases for Test Suite: test_aaa.py"),
        call("Return parameters for Test Case: test_if_exec_authorization_methods_set_on_"),
    ]
    loginfo.assert_has_calls(loginfo_calls, any_order=False)

    logdebug_calls = [
        call(
            "Suite_parameters:"
            " [{'name': 'test_aaa.py',"
            " 'testcases': [{'name': 'test_if_authentication_counters_are_incrementing_on_',"
            " 'description': 'Verify AAA counters are working correctly',"
            " 'show_cmds': ['show lldp neighbors', 'show aaa counters'], 'expected_output': None,"
            " 'comment': None, 'result': True},"
            " {'name': 'test_if_aaa_session_logging_is_working_on_',"
            " 'description': 'Verify AAA session logging is working by"
            " identifying eapi connection',"
            " 'show_cmd': 'show users detail', 'expected_output': 'commandApi',"
            " 'comment': None, 'result': True},"
            " {'name': 'test_if_commands_authorization_methods_set_on_',"
            " 'description': 'Verify AAA command authorization are method-lists set correct',"
            " 'cmd_auth': ['none'], 'show_cmd': 'show aaa methods all', 'expected_output': None,"
            " 'comment': None, 'result': True},"
            " {'name': 'test_if_exec_authorization_methods_set_on_',"
            " 'description': 'Verify AAA exec authorization are method-lists set correct',"
            " 'exec_auth': ['none'], 'show_cmd': 'show aaa methods all', 'expected_output': None,"
            " 'comment': None, 'result': True}], 'dir_path': 'sample_network_tests/aaa'}]"
        ),
        call(
            "Case_parameters: {'name': 'test_if_exec_authorization_methods_set_on_',"
            " 'description': 'Verify AAA exec authorization are method-lists set correct',"
            " 'exec_auth': ['none'], 'show_cmd': 'show aaa methods all', 'expected_output': None,"
            " 'comment': None, 'result': True}"
        ),
    ]
    logdebug.assert_has_calls(logdebug_calls, any_order=False)


def test_verify_show_cmd_pass(loginfo, logdebug):
    """Validates verification of show commands being executed on given dut"""
    dut = {"output": {"show clock": ""}, "name": "Test Dut"}
    show_cmd = "show clock"
    tests_tools.verify_show_cmd(show_cmd, dut)
    loginfo.assert_called_with(
        "Verifying if show command show clock was successfully executed on Test Dut dut"
    )
    logdebug.assert_called_with("Verified output for show command show clock on Test Dut")


def test_verify_show_cmd_fail(logcritical):
    """Validates verification of show commands being executed on given dut"""
    dut = {"output": {"show clock": ""}, "name": "Test Dut"}
    show_cmd = "show lldp neighbors"

    # handling the assert False raised in the verify_show_cmd method
    # when show_cmd is not executed on the dut

    with pytest.raises(AssertionError):
        tests_tools.verify_show_cmd(show_cmd, dut)
    logcritical.assert_called_with("Show command show lldp neighbors not executed on Test Dut")


def test_verify_tacacs_exists(loginfo, logdebug):
    """Validates verification of tacacs servers on duts"""
    dut = {
        "output": {
            "show tacacs": {"json": {"tacacsServers": [{"One": "value1"}, {"Two": "value2"}]}}
        },
        "name": "Test Dut",
    }
    actual_output = tests_tools.verify_tacacs(dut)
    assert actual_output
    loginfo.assert_called_with("Verifying if tacacs server(s) are configured on Test Dut dut")
    logdebug.assert_called_with("2 tacacs servers are configured so returning True")


def test_verify_tacacs_not_exist(loginfo):
    """Validates verification of tacacs servers on duts"""
    dut = {"output": {"show tacacs": {"json": {"tacacsServers": []}}}, "name": "Test Dut"}
    actual_output = tests_tools.verify_tacacs(dut)
    assert not actual_output
    loginfo.assert_called_with("Verifying if tacacs server(s) are configured on Test Dut dut")


def test_verify_veos_pass(loginfo, logdebug):
    """Validates verification of dut instances' model"""
    dut = {"output": {"show version": {"json": {"modelName": "vEOS-Lab"}}}, "name": "Test Dut"}
    actual_output = tests_tools.verify_veos(dut)
    loginfo.assert_called_with("Verifying if Test Dut DUT is a VEOS instance. Model is vEOS-Lab")
    logdebug.assert_called_with("Test Dut is a VEOS instance so returning True")
    assert actual_output


def test_verify_veos_fail(loginfo, logdebug):
    """Validates verification of dut instances' model"""
    dut = {"output": {"show version": {"json": {"modelName": "cEOS"}}}, "name": "Test Dut"}
    actual_output = tests_tools.verify_veos(dut)
    loginfo.assert_called_with("Verifying if Test Dut DUT is a VEOS instance. Model is cEOS")
    logdebug.assert_called_with("Test Dut is not a VEOS instance so returning False")
    assert not actual_output


def test_return_show_cmds(loginfo, logdebug):
    """Validates if correct show commands get returned given test suites
    FIXTURES NEEDED: fixture_test_parameters.yaml"""
    test_parameters = read_yaml("tests/unittests/fixtures/fixture_test_parameters.yaml")
    expected_output = [
        "show version",
        "show lldp neighbors",
        "show aaa counters",
        "show users detail",
        "show aaa methods all",
    ]
    actual_output = tests_tools.return_show_cmds(test_parameters)
    assert expected_output == actual_output
    loginfo_calls = [
        call("Finding show commands in test suite: test_aaa.py"),
        call(
            "The following show commands are required for test cases: "
            "['show version', 'show lldp neighbors', 'show aaa counters', "
            "'show users detail', 'show aaa methods all']"
        ),
    ]
    loginfo.assert_has_calls(loginfo_calls, any_order=False)

    logdebug_calls = [
        call(
            "Discover the names of test suites from"
            " {'test_suites':"
            " [{'name': 'test_aaa.py',"
            " 'testcases': [{'name': 'test_if_authentication_counters_are_incrementing_on_',"
            " 'description': 'Verify AAA counters are working correctly',"
            " 'show_cmds': ['show lldp neighbors', 'show aaa counters'], 'expected_output': None,"
            " 'comment': None, 'result': True},"
            " {'name': 'test_if_aaa_session_logging_is_working_on_',"
            " 'description': 'Verify AAA session logging is working by"
            " identifying eapi connection',"
            " 'show_cmd': 'show users detail', 'expected_output': 'commandApi',"
            " 'comment': None, 'result': True},"
            " {'name': 'test_if_commands_authorization_methods_set_on_',"
            " 'description': 'Verify AAA command authorization are method-lists set correct',"
            " 'cmd_auth': ['none'], 'show_cmd': 'show aaa methods all', 'expected_output': None,"
            " 'comment': None, 'result': True},"
            " {'name': 'test_if_exec_authorization_methods_set_on_',"
            " 'description': 'Verify AAA exec authorization are method-lists set correct',"
            " 'exec_auth': ['none'], 'show_cmd': 'show aaa methods all', 'expected_output': None,"
            " 'comment': None, 'result': True}], 'dir_path': 'sample_network_tests/aaa'}]}"
        ),
        call("Found show commands ['show lldp neighbors', 'show aaa counters']"),
        call("Adding Show commands show lldp neighbors"),
        call("Adding Show commands show aaa counters"),
        call("Found show command show users detail"),
        call("Adding Show command show users detail"),
        call("Found show command show aaa methods all"),
        call("Adding Show command show aaa methods all"),
        call("Found show command show aaa methods all"),
    ]
    logdebug.assert_has_calls(logdebug_calls, any_order=False)


def test_return_test_defs(logdebug):
    """Validates if test definitions are being generated correctly
    Creates a temporary reports/test_definition and deletes it before exiting
    FIXTURE NEEDED: fixture_tacacs_test_def.yaml"""
    expected_yaml = {
        "parameters": {
            "report_dir": "reports",
            "test_cases": "test_tacacs.py",
            "test_dirs": ["tests/unittests/fixtures/fixture_tacacs"],
            "test_definitions": "test_definition.yaml",
        }
    }
    os.makedirs(os.path.dirname("reports/test_definition.yaml"), exist_ok=True)
    actual_output = tests_tools.return_test_defs(expected_yaml)
    expected_output = read_yaml("tests/unittests/fixtures/fixture_tacacs_test_def.yaml")
    assert (
        actual_output["test_suites"][0]["testcases"]
        == expected_output["test_suites"][0]["testcases"]
    )
    assert actual_output["test_suites"][0]["name"] == expected_output["test_suites"][0]["name"]
    assert actual_output == expected_output

    logdebug.assert_called_with(
        "Return the following test definitions data structure "
        "{'test_suites': [{'name': 'test_tacacs.py', "
        "'testcases': [{'name': 'test_if_tacacs_is_sending_messages_on_', "
        "'description': 'Verify tacacs messages are sending correctly', 'show_cmd': 'show tacacs', "
        "'expected_output': None, 'report_style': 'modern', "
        "'test_criteria': 'Verify tacacs messages are sending correctly', "
        "'criteria': 'names', 'filter': ['DSR01', 'DCBBW1'], 'comment': None, 'result': True}, "
        "{'name': 'test_if_tacacs_is_receiving_messages_on_', "
        "'description': 'Verify tacacs messages are received correctly', "
        "'show_cmd': 'show tacacs', "
        "'expected_output': None, 'report_style': 'modern', "
        "'test_criteria': 'Verify tacacs messages are received correctly', "
        "'criteria': 'names', 'filter': ['DSR01', 'DCBBW1'], 'comment': None, 'result': True}], "
        "'dir_path': 'tests/unittests/fixtures/fixture_tacacs'}]}"
    )
    shutil.rmtree("reports", ignore_errors=True)


def test_export_yaml():
    """Validates exporting of data into a yaml file"""
    yaml_file = "export_file.yaml"
    yaml_data = {
        "parameters": {
            "report_dir": "reports",
            "test_cases": "test_tacacs.py",
            "test_dirs": ["../systests/tacacs"],
            "test_definitions": "test_definition.yaml",
        }
    }
    assert not os.path.isfile(yaml_file)
    tests_tools.export_yaml(yaml_file, yaml_data)

    # check if yaml file got created
    assert os.path.isfile(yaml_file)

    # check if yaml file got written to correctly
    with open(yaml_file, "r", encoding="utf-8") as input_yaml:
        assert yaml_data == yaml.safe_load(input_yaml)
    os.remove(yaml_file)


def test_export_text():
    """Validates exporting of data to text file"""
    text_file = "text/export_file.txt"
    text_data = {
        "report_dir": "reports",
        "test_cases": "test_tacacs.py",
        "test_dirs": ["../sample_network_tests/tacacs"],
        "test_definitions": "test_definition.yaml",
    }

    divider = "================================================================"
    heading = f"{divider}\nThese commands were run when PRIMARY DUT was DUT1\n{divider}\n\n"
    expected_data = heading
    for key, value in text_data.items():
        expected_data += str(key) + str(value) + "\n"

    assert not os.path.exists(text_file)
    tests_tools.export_text(text_file, text_data, "DUT1")

    # check if text file got created
    assert os.path.exists(text_file)

    # # check if text file got written to correctly
    with open("text/export_file.txt", "r", encoding="utf-8") as file:
        contents = file.read()
        assert contents == expected_data

    shutil.rmtree("text", ignore_errors=True)


def test_create_duts_file():
    """Validates generation of duts file from topology and inventory file
    FIXTURES NEEDED: fixture_topology.yaml, fixture_inventory.yaml"""
    topology_data = "tests/unittests/fixtures/fixture_topology.yaml"
    inventory_data = "tests/unittests/fixtures/fixture_inventory.yaml"
    duts_file_name = "duts_file_name.yaml"

    expected_data = {
        "duts": [
            {
                "mgmt_ip": "10.255.99.253",
                "name": "DCBBW1",
                "neighbors": [
                    {"neighborDevice": "DSR01", "neighborPort": "Ethernet1", "port": "Ethernet1"}
                ],
                "password": "cvp123!",
                "transport": "https",
                "username": "cvpadmin",
                "role": "unknown",
            }
        ],
    }

    tests_tools.create_duts_file(topology_data, inventory_data, duts_file_name)
    assert os.path.isfile(duts_file_name)
    with open(duts_file_name, "r", encoding="utf-8") as input_yaml:
        assert expected_data == yaml.safe_load(input_yaml)
    os.remove(duts_file_name)


# TEST-OPS METHODS

# global variables

TEST_DEFINITION = read_yaml("tests/unittests/fixtures/fixture_test_definitions.yaml")
TEST_SUITE = "test_memory.py"
DUT = read_yaml("tests/unittests/fixtures/fixture_detail_duts.yaml")
OUTPUT = (
    "Arista vEOS-lab\nHardware version: \nSerial number: SN-DCBBW1\n"
    "Hardware MAC address: a486.49d7.e2d9\nSystem MAC address: a486.49d7.e2d9\n\n"
    "Software image version: 4.27.2F\nArchitecture: x86_64\n"
    "Internal build version: 4.27.2F-26069621.4272F\n"
    "Internal build ID: 2fd003fd-04c4-4b44-9c26-417e6ca42009\nImage format version: 1.0\n"
    "Image optimization: None\n\nUptime: 3 days, 4 hours and 56 minutes\n"
    "Total memory: 3938900 kB\nFree memory: 2755560 kB\n\n"
)


# utility method for creating tops object


def create_test_ops_instance(mocker):
    """Utility function to create tops object needed for testing TestOps methods"""

    # creating test ops object and mocking inspect_stack call
    mocker.patch("inspect.stack", return_value=["", ["", "", "", "test_memory_utilization_on_"]])

    tops = tests_tools.TestOps(TEST_DEFINITION, TEST_SUITE, DUT)

    return tops


def test_test_ops_constructor(mocker):
    "Validates that TestOPs object gets initialized correctly"

    # mocking the call to _verify_show_cmd and _get_parameters in init()

    mocker.patch(
        "vane.tests_tools.TestOps._get_parameters",
        return_value=read_yaml("tests/unittests/fixtures/fixture_testops_test_parameters.yaml"),
    )
    mocker.patch("vane.tests_tools.TestOps._verify_show_cmd", return_value=True)
    tops = create_test_ops_instance(mocker)

    # assert all the object values are set correctly

    assert tops.test_case == "test_memory_utilization_on_"
    assert tops.test_parameters == read_yaml(
        "tests/unittests/fixtures/fixture_testops_test_parameters.yaml"
    )
    assert tops.expected_output == 80
    assert tops.dut == read_yaml("tests/unittests/fixtures/fixture_detail_duts.yaml")
    assert tops.dut_name == "DCBBW1"
    assert tops.interface_list == [
        {
            "hostname": "DCBBW1",
            "interface_name": "Ethernet1",
            "media_type": "",
            "z_hostname": "DSR01",
            "z_interface_name": "Ethernet1",
        },
        {
            "hostname": "DCBBW1",
            "interface_name": "Ethernet3",
            "media_type": "",
            "z_hostname": "BLFW1",
            "z_interface_name": "Ethernet1",
        },
        {
            "hostname": "DCBBW1",
            "interface_name": "Ethernet4",
            "media_type": "",
            "z_hostname": "BLFW2",
            "z_interface_name": "Ethernet1",
        },
    ]
    assert tops.results_dir == "reports/results"
    assert tops.report_dir == "reports"

    assert tops.show_cmds == {"DCBBW1": ["show version"]}
    assert tops._show_cmds == {"DCBBW1": ["show version", "show version"]}
    assert tops.show_cmd == "show version"

    assert tops.show_cmd_txts == {"DCBBW1": [OUTPUT]}
    assert tops._show_cmd_txts == {"DCBBW1": [OUTPUT, OUTPUT]}

    assert tops.show_cmd_txt == OUTPUT

    assert tops.show_output == ""
    assert not tops.test_steps

    assert tops.comment == ""
    assert tops.output_msg == ""
    assert not tops.actual_results
    assert not tops.expected_results
    assert tops.actual_output == ""
    assert not tops.test_result
    assert tops.test_id == tops.test_parameters.get("test_id", None)


def test_test_ops_verify_show_cmd_pass(loginfo, logdebug, mocker):
    """Validates verification of show commands being executed on given dut"""

    # mocking the call to _get_parameters in init()

    mocker.patch(
        "vane.tests_tools.TestOps._get_parameters",
        return_value=read_yaml("tests/unittests/fixtures/fixture_testops_test_parameters.yaml"),
    )
    tops = create_test_ops_instance(mocker)

    # handling the true case

    show_cmds = ["show version"]
    tops._verify_show_cmd(show_cmds, DUT)
    loginfo.assert_called_with(
        "Verifying if show command ['show version'] were successfully executed on DCBBW1 dut"
    )
    logdebug.assert_called_with("Verified output for show command show version on DCBBW1")


def test_test_ops_verify_show_cmd_fail(logcritical, mocker):
    """Validates verification of show commands being executed on given dut"""

    # mocking the call to _get_parameters in init()

    mocker.patch(
        "vane.tests_tools.TestOps._get_parameters",
        return_value=read_yaml("tests/unittests/fixtures/fixture_testops_test_parameters.yaml"),
    )
    tops = create_test_ops_instance(mocker)

    # handling the false case

    show_cmd = ["show lldp neighbors"]

    # handling the assert False raised in the verify_show_cmd method
    # when show_cmd is not executed on the dut

    with pytest.raises(AssertionError):
        tops._verify_show_cmd(show_cmd, DUT)
    logcritical.assert_called_with("Show command show lldp neighbors not executed on DCBBW1")


def test_test_ops_write_results(loginfo, logdebug, mocker):
    "Validates functionality of write_results method"

    # mocking the call to _verify_show_cmd and _get_parameters in init()

    mocker.patch(
        "vane.tests_tools.TestOps._get_parameters",
        return_value=read_yaml("tests/unittests/fixtures/fixture_testops_test_parameters.yaml"),
    )
    mocker.patch("vane.tests_tools.TestOps._verify_show_cmd", return_value=True)

    # mocking call to export_yaml

    mocker_object = mocker.patch("vane.tests_tools.export_yaml")

    tops = create_test_ops_instance(mocker)
    tops._write_results()

    # assert the logs

    loginfo.assert_called_with("Preparing to write results")
    logdebug.assert_called_with(
        "Creating results file named reports/results/result-test_memory_utilization_on_-DSR01.yml"
    )

    # assert export_yaml got called with correctly processed arguments

    test_params = read_yaml("tests/unittests/fixtures/fixture_testops_test_parameters.yaml")
    mocker_object.assert_called_once_with(
        "reports/results/result-test_memory_utilization_on_-DSR01.yml", test_params
    )


def test_test_ops_write_text_results(mocker):
    "Validates functionality of write_text_results method"

    # mocking the call to _verify_show_cmd and _get_parameters in init()

    mocker.patch(
        "vane.tests_tools.TestOps._get_parameters",
        return_value=read_yaml("tests/unittests/fixtures/fixture_testops_test_parameters.yaml"),
    )
    mocker.patch("vane.tests_tools.TestOps._verify_show_cmd", return_value=True)

    # mocking call to export_yaml

    mocker_object = mocker.patch("vane.tests_tools.export_text")

    tops = create_test_ops_instance(mocker)
    tops._write_text_results()

    # assert export_text got called with correctly processed arguments

    text_file = "reports/TEST RESULTS/1 test_memory_utilization_on_/1 DCBBW1 Verification.txt"
    text_data = {
        "1. DCBBW1# show version": "\n\n" + OUTPUT,
        "2. DCBBW1# show version": "\n\n" + OUTPUT,
    }
    dut_name = "DCBBW1"
    mocker_object.assert_called_once_with(text_file, text_data, dut_name)


def test_test_ops_get_parameters(loginfo, logdebug, mocker):
    """Validates getting test case details from test parameters, suites and name"""

    # mocking the call to _verify_show_cmd in init()

    mocker.patch("vane.tests_tools.TestOps._verify_show_cmd", return_value=True)
    tops = create_test_ops_instance(mocker)

    expected_output = {
        "name": "test_memory_utilization_on_",
        "description": "Verify memory is not exceeding high utilization",
        "show_cmd": "show version",
        "expected_output": 80,
        "report_style": "modern",
        "test_criteria": "Verify memory is not exceeding high utilization",
        "criteria": "names",
        "filter": ["DSR01", "DCBBW1"],
        "comment": None,
        "result": True,
        "test_suite": "test_memory.py",
    }

    actual_output = tops._get_parameters(TEST_DEFINITION, TEST_SUITE, "test_memory_utilization_on_")
    assert expected_output == actual_output

    loginfo_calls = [
        call("Identify test case and return parameters"),
        call("Returning parameters for Test Case: test_memory_utilization_on_"),
    ]
    loginfo.assert_has_calls(loginfo_calls, any_order=False)

    logdebug_calls = [
        call("Return testcases for Test Suite: test_memory.py"),
        call(
            "Suite_parameters: [{'name': 'test_memory.py', 'testcases': "
            "[{'name': 'test_memory_utilization_on_', "
            "'description': 'Verify memory is not exceeding high utilization', "
            "'show_cmd': 'show version', 'expected_output': 80, 'report_style': 'modern', "
            "'test_criteria': 'Verify memory is not exceeding high utilization', "
            "'criteria': 'names', 'filter': ['DSR01', 'DCBBW1'], 'comment': None, "
            "'result': True}]}]"
        ),
        call(
            "Case_parameters: {'name': 'test_memory_utilization_on_', "
            "'description': 'Verify memory is not exceeding high utilization', "
            "'show_cmd': 'show version', 'expected_output': 80, 'report_style': 'modern', "
            "'test_criteria': 'Verify memory is not exceeding high utilization', "
            "'criteria': 'names', 'filter': ['DSR01', 'DCBBW1'], 'comment': None, "
            "'result': True}"
        ),
    ]
    logdebug.assert_has_calls(logdebug_calls, any_order=False)


def test_test_ops_generate_report(logdebug, mocker):
    """Validates functionality of generate_report method"""
    mocker.patch(
        "vane.tests_tools.TestOps._get_parameters",
        return_value=read_yaml("tests/unittests/fixtures/fixture_testops_test_parameters.yaml"),
    )
    mocker.patch("vane.tests_tools.TestOps._verify_show_cmd", return_value=True)
    mocker_object_one = mocker.patch("vane.tests_tools.TestOps._html_report")
    mocker_object_two = mocker.patch("vane.tests_tools.TestOps._write_results")
    mocker_object_three = mocker.patch("vane.tests_tools.TestOps._write_text_results")
    tops = create_test_ops_instance(mocker)

    expected_output = {
        "comment": "",
        "criteria": "names",
        "description": "Verify memory is not exceeding high utilization",
        "expected_output": 80,
        "filter": ["DSR01", "DCBBW1"],
        "name": "test_memory_utilization_on_",
        "report_style": "modern",
        "result": True,
        "show_cmd": "show version:\n\n" + OUTPUT,
        "test_criteria": "Verify memory is not exceeding high utilization",
        "test_suite": "test_memory.py",
        "dut": "DCBBW1",
        "test_result": False,
        "output_msg": "",
        "actual_output": "",
        "skip": False,
        "test_id": 1,
        "show_cmd_txts": {
            "DCBBW1": [
                OUTPUT,
                OUTPUT,
            ]
        },
        "test_steps": [],
        "show_cmds": {"DCBBW1": ["show version", "show version"]},
        "fail_or_skip_reason": "",
    }

    tops.generate_report("DCBBW1", "Output")

    # assert method calls and values

    assert tops.test_parameters == expected_output

    mocker_object_one.assert_called_once()
    mocker_object_two.assert_called_once()
    mocker_object_three.assert_called_once()

    logdebug.assert_called_with("Output on device DCBBW1 after SSH connection is: Output")


def test_test_ops_html_report(mocker, capsys):
    """Validates html_report functionality"""

    mocker.patch(
        "vane.tests_tools.TestOps._get_parameters",
        return_value=read_yaml("tests/unittests/fixtures/fixture_testops_test_parameters.yaml"),
    )
    mocker.patch("vane.tests_tools.TestOps._verify_show_cmd", return_value=True)
    tops = create_test_ops_instance(mocker)

    tops._html_report()

    # Capture the standard output
    captured_output = capsys.readouterr()

    show_output = (
        f"SHOW OUTPUT COLLECTED IN TEST CASE:\n===================================\n"
        f"1. DCBBW1# show version\n\n{OUTPUT}\n2. DCBBW1# show version\n\n{OUTPUT}"
    )

    # Assert that the expected prints occurred
    assert "OUTPUT MESSAGES:" in captured_output.out
    assert "\nEXPECTED OUTPUT:\n================\n80\n" in captured_output.out
    assert "ACTUAL OUTPUT:" in captured_output.out

    assert show_output in captured_output.out


def test_test_ops_parse_test_steps(loginfo, mocker):
    """Validates verification of the parse_test_steps method
    FIXTURE NEEDED: tests/unittests/fixtures/test_steps/test_steps.py"""

    # mocking the call to _verify_show_cmd and _get_parameters in init()

    mocker.patch(
        "vane.tests_tools.TestOps._get_parameters",
        return_value=read_yaml("tests/unittests/fixtures/fixture_testops_test_parameters.yaml"),
    )
    mocker.patch("vane.tests_tools.TestOps._verify_show_cmd", return_value=True)
    tops = create_test_ops_instance(mocker)
    tops.parse_test_steps(test_steps.TestSyslogFunctionality.test_syslog_functionality_on_server)

    # assert the test steps log call
    loginfo.assert_called_with(
        "These are test steps [' Creating Testops class object and initializing the variable ', '"
        " Running Tcpdump on syslog server and entering in config mode and existing to verify"
        " logging event are captured. ', ' Comparing the actual output and expected output."
        " Generating docx report ']"
    )


def test_test_ops_run_show_cmds_json(mocker):
    """Validates the functionality of run_show_cmds method"""
    mocker.patch(
        "vane.tests_tools.TestOps._get_parameters",
        return_value=read_yaml("tests/unittests/fixtures/fixture_testops_test_parameters.yaml"),
    )
    mocker.patch("vane.tests_tools.TestOps._verify_show_cmd", return_value=True)

    mocker_object = mocker.patch("vane.device_interface.PyeapiConn.enable")
    mocker_object.side_effect = [
        [
            {
                "command": "show clock",
                "result": {
                    "output": "Thu Jun  1 14:03:59 2023\nTimezone: UTC\nClock source: local\n"
                },
                "encoding": "text",
            }
        ],
        [
            {
                "command": "show interfaces status",
                "result": {"output": {"interfaceStatuses": "Management1"}},
                "encoding": "json",
            }
        ],
        [
            {
                "command": "show interfaces status",
                "result": {"output": "TEXT_INTERFACE_STATUS_result"},
                "encoding": "text",
            },
        ],
    ]

    tops = create_test_ops_instance(mocker)

    show_cmds = ["show interfaces status"]
    dut = {"connection": vane.device_interface.PyeapiConn, "name": "neighbor"}
    dut["eapi_conn"] = dut["connection"]
    tops.show_clock_flag = True
    tops.show_cmds = show_cmds
    actual_output = tops.run_show_cmds(show_cmds, dut, "json")

    # assert return values
    assert actual_output == [
        {
            "command": "show interfaces status",
            "result": {"output": {"interfaceStatuses": "Management1"}},
            "encoding": "json",
        }
    ]
    assert tops.show_cmds == show_cmds
    assert tops._show_cmds == {
        "DCBBW1": ["show version", "show version"],
        "neighbor": ["show clock", "show interfaces status"],
    }

    assert tops._show_cmd_txts == {
        "DCBBW1": [OUTPUT, OUTPUT],
        "neighbor": [
            "Thu Jun  1 14:03:59 2023\nTimezone: UTC\nClock source: local\n",
            "TEXT_INTERFACE_STATUS_result",
        ],
    }


def test_test_ops_run_show_cmds_text(mocker):
    """Validates the functionality of run_show_cmds method"""
    mocker.patch(
        "vane.tests_tools.TestOps._get_parameters",
        return_value=read_yaml("tests/unittests/fixtures/fixture_testops_test_parameters.yaml"),
    )
    mocker.patch("vane.tests_tools.TestOps._verify_show_cmd", return_value=True)

    mocker_object = mocker.patch("vane.device_interface.PyeapiConn.enable")
    mocker_object.side_effect = [
        [
            {
                "command": "show lldp neighbors",
                "result": {"output": "TEXT_result"},
                "encoding": "text",
            },
            {
                "command": "show interfaces status",
                "result": {"output": "TEXT_result"},
                "encoding": "text",
            },
        ],
    ]

    tops = create_test_ops_instance(mocker)

    dut = {"connection": vane.device_interface.PyeapiConn, "name": "neighbor"}
    dut["eapi_conn"] = dut["connection"]
    tops.show_clock_flag = False
    tops.show_cmds = ["show lldp neighbors", "show interfaces status"]

    actual_output = tops.run_show_cmds(tops.show_cmds, dut, "text")

    # assert return values
    assert actual_output == [
        {"command": "show lldp neighbors", "result": {"output": "TEXT_result"}, "encoding": "text"},
        {
            "command": "show interfaces status",
            "result": {"output": "TEXT_result"},
            "encoding": "text",
        },
    ]
    assert tops.show_cmds == ["show lldp neighbors", "show interfaces status"]
    assert tops._show_cmds == {
        "DCBBW1": ["show version", "show version"],
        "neighbor": ["show lldp neighbors", "show interfaces status"],
    }

    assert tops._show_cmd_txts == {
        "DCBBW1": [
            OUTPUT,
            OUTPUT,
        ],
        "neighbor": ["TEXT_result", "TEXT_result"],
    }


def test_test_ops_run_show_cmds_json_exception_fail(mocker):
    """Validates the functionality of run_show_cmds method"""
    mocker.patch(
        "vane.tests_tools.TestOps._get_parameters",
        return_value=read_yaml("tests/unittests/fixtures/fixture_testops_test_parameters.yaml"),
    )
    mocker.patch("vane.tests_tools.TestOps._verify_show_cmd", return_value=True)

    mocker_object = mocker.patch("vane.device_interface.PyeapiConn.enable")
    mocker_object.side_effect = [pyeapi.eapilib.CommandError(1000, "Invalid command")]

    tops = create_test_ops_instance(mocker)

    show_cmds = ["show interfaces status"]
    dut = {"connection": vane.device_interface.PyeapiConn, "name": "neighbor"}
    dut["eapi_conn"] = dut["connection"]

    with pytest.raises(pyeapi.eapilib.CommandError):
        tops.run_show_cmds(show_cmds, dut, "json")

    # verify that _show_cmds still got updated with commands that failed
    assert tops._show_cmds["neighbor"] == ["show interfaces status"]

    assert tops._show_cmd_txts["neighbor"] == ["Error [1000]: Invalid command [None]"]


def test_test_ops_run_show_cmds_text_exception_fail(mocker):
    """Validates the functionality of run_show_cmds method"""
    mocker.patch(
        "vane.tests_tools.TestOps._get_parameters",
        return_value=read_yaml("tests/unittests/fixtures/fixture_testops_test_parameters.yaml"),
    )
    mocker.patch("vane.tests_tools.TestOps._verify_show_cmd", return_value=True)

    mocker_object = mocker.patch("vane.device_interface.PyeapiConn.enable")
    mocker_object.side_effect = [pyeapi.eapilib.CommandError(1000, "Invalid command")]

    tops = create_test_ops_instance(mocker)

    dut = {"connection": vane.device_interface.PyeapiConn, "name": "neighbor"}
    dut["eapi_conn"] = dut["connection"]

    show_cmds = ["show interfaces status"]

    with pytest.raises(pyeapi.eapilib.CommandError):
        tops.run_show_cmds(show_cmds, dut, "text")

    # verify that _show_cmds still got updated with commands that failed
    assert tops._show_cmds["neighbor"] == ["show interfaces status"]

    assert tops._show_cmd_txts["neighbor"] == ["Error [1000]: Invalid command [None]"]


def test_test_ops_run_cfg_cmds_pyeapi(mocker):
    """Validates the functionality of run_show_cmds method"""
    mocker.patch(
        "vane.tests_tools.TestOps._get_parameters",
        return_value=read_yaml("tests/unittests/fixtures/fixture_testops_test_parameters.yaml"),
    )
    mocker.patch("vane.tests_tools.TestOps._verify_show_cmd", return_value=True)

    mocker_object = mocker.patch("vane.device_interface.PyeapiConn.enable")
    mocker_object.side_effect = [
        [
            {
                "command": "show clock",
                "result": {
                    "output": "Thu Jun  1 14:03:59 2023\nTimezone: UTC\nClock source: local\n"
                },
                "encoding": "text",
            }
        ],
    ]

    mocker_object = mocker.patch("vane.device_interface.PyeapiConn.config")
    mocker_object.side_effect = [
        [{}, {}],
    ]

    tops = create_test_ops_instance(mocker)

    dut = {"connection": vane.device_interface.PyeapiConn, "name": "neighbor"}
    dut["eapi_conn"] = dut["connection"]
    tops.show_clock_flag = True
    cfg_cmds = ["interface eth16", "description unittest"]

    actual_output = tops.run_cfg_cmds(cfg_cmds, dut)

    # assert return values
    assert actual_output == [
        {},
        {},
    ]
    assert tops._show_cmds == {
        "DCBBW1": ["show version", "show version"],
        "neighbor": ["show clock", "interface eth16", "description unittest"],
    }

    assert tops._show_cmd_txts == {
        "DCBBW1": [OUTPUT, OUTPUT],
        "neighbor": ["Thu Jun  1 14:03:59 2023\nTimezone: UTC\nClock source: local\n", "", ""],
    }


def test_test_ops_run_cfg_cmds_ssh(mocker):
    """Validates the functionality of run_show_cmds method"""
    mocker.patch(
        "vane.tests_tools.TestOps._get_parameters",
        return_value=read_yaml("tests/unittests/fixtures/fixture_testops_test_parameters.yaml"),
    )
    mocker.patch("vane.tests_tools.TestOps._verify_show_cmd", return_value=True)

    mocker_object = mocker.patch("vane.device_interface.NetmikoConn.enable")
    mocker_object.side_effect = [
        [
            {
                "command": "show clock",
                "result": {
                    "output": "Thu Jun  1 14:03:59 2023\nTimezone: UTC\nClock source: local\n"
                },
                "encoding": "text",
            }
        ],
    ]

    mocker_object = mocker.patch("vane.device_interface.NetmikoConn.config")
    config_return_value = (
        "configure terminal\nneighbor(config)#"
        "interface eth16\nneighbor(config-if-Et16)#"
        "description unittest\nneighbor(config-if-Et16)#end\nneighbor#"
    )
    mocker_object.side_effect = [config_return_value]

    tops = create_test_ops_instance(mocker)

    dut = {"connection": vane.device_interface.NetmikoConn, "name": "neighbor"}
    dut["ssh_conn"] = dut["connection"]
    tops.show_clock_flag = True
    cfg_cmds = ["interface eth16", "description unittest"]

    actual_output = tops.run_cfg_cmds(cfg_cmds, dut, conn_type="ssh")

    # assert return values
    assert actual_output == config_return_value

    assert tops._show_cmds == {
        "DCBBW1": ["show version", "show version"],
        "neighbor": ["show clock", "interface eth16", "description unittest"],
    }

    assert tops._show_cmd_txts == {
        "DCBBW1": [OUTPUT, OUTPUT],
        "neighbor": [
            "Thu Jun  1 14:03:59 2023\nTimezone: UTC\nClock source: local\n",
            config_return_value,
            config_return_value,
        ],
    }


def test_test_ops_transfer_file(mocker):
    """Validates the functionality of transfer_file method"""
    mocker.patch("vane.tests_tools.TestOps._verify_show_cmd", return_value=True)

    mocker.patch(
        "vane.device_interface.NetmikoConn.set_up_conn",
        return_value=vane.device_interface.NetmikoConn,
    )
    mocker_object = mocker.patch("vane.device_interface.NetmikoConn.enable")
    mocker_object.side_effect = [
        [
            {
                "command": "show clock",
                "result": {
                    "output": "Thu Jun  1 14:03:59 2023\nTimezone: UTC\nClock source: local\n"
                },
                "encoding": "text",
            }
        ],
    ]

    transfer_file_return = {
        "file_exists": True,
        "file_transferred": True,
        "file_verified": True,
    }
    mocker.patch(
        "vane.device_interface.NetmikoConn.transfer_file", return_value=transfer_file_return
    )

    tops = create_test_ops_instance(mocker)
    file_tranfer_log = (
        "Last login: Wed Aug 16 20:51:31 2023 from 10.8.0.14\n\n\nDSR01#\nDSR01"
        "#terminal width 511\nWidth set to 511 columns.\nDSR01#terminal length 0"
        "\nPagination disabled.\nDSR01#\nDSR01#\nDSR01#bash\n\nArista Networks "
        "EOS shell\n\n[XXXXX@DSR01 ~]$ /bin/ls /mnt/flash/sample-20230816-145133"
        ".txt 2> /dev/null\n[XXXXX@DSR01 ~]$ exit\nlogout\nDSR01#bash\n\nArista "
        "Networks EOS shell\n\n[XXXXX@DSR01 ~]$ /bin/df -k /mnt/flash\nFilesystem     "
        "1K-blocks    Used Available Use% Mounted on\n/dev/nvme0n1p1   "
        "8124856 1146708   6961764  15% /mnt/flash\n[XXXXX@DSR01 ~]$ exit\nlogout"
        "\nDSR01#\nDSR01#verify /md5 file:/mnt/flash/sample-20230816-145133.txt\nverify "
        "/md5 (file:/mnt/flash/sample-20230816-145133.txt) = 3c5fd98f35b7e6b24a07c"
        "f3fc3220352\nDSR01#"
    )

    mocked_file_data = mocker.mock_open(read_data=file_tranfer_log)
    mocker.patch("builtins.open", mocked_file_data)
    mocker.patch("os.remove")

    dut = {
        "connection": vane.device_interface.NetmikoConn,
        "name": "neighbor",
        "transport": "https",
        "mgmt_ip": "1.1.1.1",
        "username": "user1",
        "password": "pass1",
    }
    tops.dut = dut
    tops._show_cmds["neighbor"] = []
    tops._show_cmd_txts["neighbor"] = []
    tops.show_clock_flag = True

    actual_output = tops.transfer_file(
        src_file="sample.txt",
        dest_file="sample-20230816-145133.txt",
        file_system="/mnt/flash",
        operation="get",
        sftp=True,
    )

    # assert return values
    assert actual_output == {
        "file_exists": True,
        "file_transferred": True,
        "file_verified": True,
    }
    assert tops._show_cmds == {
        "DCBBW1": ["show version", "show version"],
        "neighbor": [
            "show clock",
            "sftp src_file: sample.txt dest_file: sample-20230816-145133.txt op: get",
        ],
    }

    assert tops._show_cmd_txts == {
        "DCBBW1": [OUTPUT, OUTPUT],
        "neighbor": [
            "Thu Jun  1 14:03:59 2023\nTimezone: UTC\nClock source: local\n",
            file_tranfer_log,
        ],
    }


def test_test_ops_get_ssh_connection(mocker):
    """Validates the functionality of get_ssh_connection method"""

    mocker_object = mocker.patch("vane.device_interface.NetmikoConn")
    netmiko_instance = mocker_object.return_value

    dut = {"name": "DSR01"}
    tops = create_test_ops_instance(mocker)

    conn = tops.get_ssh_connection(dut)

    # assert call to NetmikoConn was made correctly

    assert netmiko_instance.set_up_conn.call_count == 1

    assert conn == netmiko_instance
    assert dut["ssh_conn"] == dut["connection"] == netmiko_instance

    # assert when a value already exists, it is returned as is and
    # new connection is not created

    dut["ssh_conn"] = "I have a predefined value"
    conn = tops.get_ssh_connection(dut)
    assert conn == dut["ssh_conn"] == "I have a predefined value"


def test_test_ops_get_eapi_connection(mocker):
    """Validates the functionality of get_eapi_connection method"""
    mocker_object = mocker.patch("vane.device_interface.PyeapiConn")
    pyeapi_instance = mocker_object.return_value

    dut = {"name": "DSR01"}
    tops = create_test_ops_instance(mocker)

    conn = tops.get_eapi_connection(dut)

    # assert call to PyeapiConn was made correctly

    assert pyeapi_instance.set_up_conn.call_count == 1

    assert conn == pyeapi_instance
    assert dut["eapi_conn"] == dut["connection"] == pyeapi_instance

    # assert when a value already exists, it is returned as is and
    # new connection is not created

    dut["eapi_conn"] = "I have a predefined value"
    conn = tops.get_eapi_connection(dut)
    assert conn == dut["eapi_conn"] == "I have a predefined value"
