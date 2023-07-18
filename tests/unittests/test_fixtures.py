"""
fixtures.py unit tests
"""

# Disable redefined-outer-name for using loginfo and logerr fixture functions
# pylint: disable=redefined-outer-name

import datetime
import logging
import sys

from unittest.mock import call
import pytest
import yaml

import vane.device_interface
import vane.fixtures


DUTS = "tests/unittests/fixtures/fixtures-test-duts-data.yaml"


@pytest.fixture
def loginfo(mocker):
    """Fixture to mock logger info calls from vane.tests_client"""
    return mocker.patch("vane.fixtures.logging.info")


@pytest.fixture
def logdebug(mocker):
    """Fixture to mock logger debug calls from vane.tests_client"""
    return mocker.patch("vane.fixtures.logging.debug")


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
                print(">>> ERROR IN YAML FILE")
                logging.error(f"ERROR IN YAML FILE: {err}")
                logging.error("EXITING TEST RUNNER")
                sys.exit(1)
    except OSError as err:
        print(f">>> {yaml_file} YAML FILE MISSING")
        logging.error(f"ERROR YAML FILE: {yaml_file} NOT FOUND. {err}")
        logging.error("EXITING TEST RUNNER")
        sys.exit(1)


def test_perform_setup_via_name(loginfo, logdebug, mocker):
    """Tests the perform_setup function using the dut names"""

    # Mock the date so we can verify the checkpoint timestamp
    test_date = datetime.datetime(2023, 6, 18, 18, 58, 20)
    mock_dt = mocker.patch("vane.fixtures.datetime", wraps=datetime)
    mock_dt.datetime.now.return_value = test_date

    # Create a string from the same date
    date_str = test_date.strftime("%y%m%d%H%M")

    # Mock the calls to the device interface
    dev_intf = mocker.patch("vane.device_interface")

    # Initialize the duts and setup_config data
    duts = read_yaml(DUTS)
    setup_config = read_yaml("tests/unittests/fixtures/fixtures-test-setup-config-names.yaml")

    # After we initialize the duts structure, create a "connection" interface object for each
    for dut in duts:
        duts[dut]["connection"] = vane.device_interface.PyeapiConn()

    # Call the perform_setup function
    test_name = "test_perform_setup_via_name"
    checkpoint = vane.fixtures.perform_setup(duts, test_name, setup_config)

    # Verify a checkpoint is returned
    checkpoint_str = f"{test_name}_{date_str}"
    assert checkpoint == checkpoint_str

    # Verify the calls to enable and config
    dev_intf_calls = [
        call.PyeapiConn().enable([f"configure checkpoint save {checkpoint_str}"]),
        call.PyeapiConn().config(
            [
                "interface Ethernet5",
                "no switchport",
                "vrf DVT-2",
                "ip address 192.168.2.1/31",
                "ip route vrf DVT-2 0.0.0.0/0 192.168.2.0",
            ]
        ),
        call.PyeapiConn().enable([f"configure checkpoint save {checkpoint_str}"]),
        call.PyeapiConn().config(
            ["interface Ethernet16", "no switchport", "ip address 192.168.2.2/31"]
        ),
        call.PyeapiConn().enable([f"configure checkpoint save {checkpoint_str}"]),
        call.PyeapiConn().config(
            [
                "interface Ethernet5",
                "no switchport",
                "vrf DVT-2",
                "ip address 192.168.2.3/31",
                "ip route vrf DVT-2 0.0.0.0/0 192.168.2.0",
            ]
        ),
        call.PyeapiConn().enable([f"configure checkpoint save {checkpoint_str}"]),
        call.PyeapiConn().config(
            ["interface Ethernet16", "no switchport", "ip address 192.168.2.4/31"]
        ),
        call.PyeapiConn().enable([f"configure checkpoint save {checkpoint_str}"]),
        call.PyeapiConn().config(
            [
                "interface Ethernet5",
                "no switchport",
                "vrf DVT-2",
                "ip address 192.168.2.5/31",
                "ip route vrf DVT-2 0.0.0.0/0 192.168.2.0",
            ]
        ),
    ]
    dev_intf.assert_has_calls(dev_intf_calls)

    # Verify info logging calls
    loginfo_calls = [
        call("Creating checkpoints and running setup on duts"),
        call(f"Checkpoint name is '{checkpoint_str}'"),
        call("Performing setup via dut names"),
        call("Sending checkpoint command and config to dut DSR01"),
        call("Sending checkpoint command and config to dut DCBBW1"),
        call("Sending checkpoint command and config to dut DCBBW2"),
        call("No dut named UNCONFIGURED-DUT found, continuing to setup next dut"),
        call("Sending checkpoint command and config to dut DCBBE1"),
        call("Sending checkpoint command and config to dut DCBBE2"),
    ]
    loginfo.assert_has_calls(loginfo_calls)

    # Verify debug logging calls
    logdebug_calls = [
        call(
            "Performing setup for test_perform_setup_via_name:\n{'DSR01': {'schema': None, "
            "'template': 'interface Ethernet5\\nno switchport\\nvrf DVT-2\\nip address "
            "192.168.2.1/31\\nip route vrf DVT-2 0.0.0.0/0 192.168.2.0\\n'}, 'DCBBW1': {'schema': "
            "None, 'template': 'interface Ethernet16\\nno switchport\\nip address "
            "192.168.2.2/31\\n'}, 'DCBBW2': {'schema': None, 'template': 'interface "
            "Ethernet5\\nno switchport\\nvrf DVT-2\\nip address 192.168.2.3/31\\nip route vrf "
            "DVT-2 0.0.0.0/0 192.168.2.0\\n'}, 'UNCONFIGURED-DUT': {'schema': None, 'template': "
            "'interface Ethernet10\\nno switchport\\nvrf DVT-2\\nip address 192.168.2.10/31\\nip "
            "route vrf DVT-2 0.0.0.0/0 192.168.2.0\\n'}, 'DCBBE1': {'schema': None, 'template': "
            "'interface Ethernet16\\nno switchport\\nip address 192.168.2.4/31\\n'}, 'DCBBE2': "
            "{'schema': None, 'template': 'interface Ethernet5\\nno switchport\\nvrf DVT-2\\nip "
            "address 192.168.2.5/31\\nip route vrf DVT-2 0.0.0.0/0 192.168.2.0\\n'}}"
        ),
        call(f"Sending checkpoint command: configure checkpoint save {checkpoint_str}"),
        call(
            "Sending config:\n['interface Ethernet5', 'no switchport', 'vrf DVT-2', 'ip address "
            "192.168.2.1/31', 'ip route vrf DVT-2 0.0.0.0/0 192.168.2.0']"
        ),
        call(f"Sending checkpoint command: configure checkpoint save {checkpoint_str}"),
        call(
            "Sending config:\n['interface Ethernet16', 'no switchport', "
            "'ip address 192.168.2.2/31']"
        ),
        call(f"Sending checkpoint command: configure checkpoint save {checkpoint_str}"),
        call(
            "Sending config:\n['interface Ethernet5', 'no switchport', 'vrf DVT-2', 'ip address "
            "192.168.2.3/31', 'ip route vrf DVT-2 0.0.0.0/0 192.168.2.0']"
        ),
        call(f"Sending checkpoint command: configure checkpoint save {checkpoint_str}"),
        call(
            "Sending config:\n['interface Ethernet16', 'no switchport', "
            "'ip address 192.168.2.4/31']"
        ),
        call(f"Sending checkpoint command: configure checkpoint save {checkpoint_str}"),
        call(
            "Sending config:\n['interface Ethernet5', 'no switchport', 'vrf DVT-2', 'ip address "
            "192.168.2.5/31', 'ip route vrf DVT-2 0.0.0.0/0 192.168.2.0']"
        ),
    ]
    logdebug.assert_has_calls(logdebug_calls)


def test_perform_setup_via_role(loginfo, logdebug, mocker):
    """Tests the perform_setup function using the dut roles"""

    # Mock the date so we can verify the checkpoint timestamp
    test_date = datetime.datetime(2023, 4, 19, 22, 58, 20)
    mock_dt = mocker.patch("vane.fixtures.datetime", wraps=datetime)
    mock_dt.datetime.now.return_value = test_date

    # Create a string from the same date
    date_str = test_date.strftime("%y%m%d%H%M")

    # Mock the calls to the device interface
    dev_intf = mocker.patch("vane.device_interface")

    # Initialize the duts and setup_config data
    duts = read_yaml(DUTS)
    setup_config = read_yaml("tests/unittests/fixtures/fixtures-test-setup-config-roles.yaml")

    # After we initialize the duts structure, create a "connection" interface object for each
    for dut in duts:
        duts[dut]["connection"] = vane.device_interface.PyeapiConn()

    # Call the perform_setup function
    test_name = "test_perform_setup_via_role"
    checkpoint = vane.fixtures.perform_setup(duts, test_name, setup_config)

    # Verify a checkpoint is returned
    checkpoint_str = f"{test_name}_{date_str}"
    assert checkpoint == checkpoint_str

    # Verify the calls to enable and config
    dev_intf_calls = [
        call.PyeapiConn().enable([f"configure checkpoint save {checkpoint_str}"]),
        call.PyeapiConn().config(
            [
                "interface Ethernet3",
                "no switchport",
                "vrf DVT-2",
                "ip address 192.168.2.4/31",
                "ip route vrf DVT-2 0.0.0.0/0 192.168.2.0",
            ]
        ),
        call.PyeapiConn().enable([f"configure checkpoint save {checkpoint_str}"]),
        call.PyeapiConn().config(
            [
                "interface Ethernet3",
                "no switchport",
                "vrf DVT-2",
                "ip address 192.168.2.4/31",
                "ip route vrf DVT-2 0.0.0.0/0 192.168.2.0",
            ]
        ),
        call.PyeapiConn().enable([f"configure checkpoint save {checkpoint_str}"]),
        call.PyeapiConn().config(
            ["interface Ethernet13", "no switchport", "ip address 192.168.2.5/31"]
        ),
        call.PyeapiConn().enable([f"configure checkpoint save {checkpoint_str}"]),
        call.PyeapiConn().config(
            ["interface Ethernet13", "no switchport", "ip address 192.168.2.5/31"]
        ),
        call.PyeapiConn().enable([f"configure checkpoint save {checkpoint_str}"]),
        call.PyeapiConn().config(
            [
                "interface Ethernet7",
                "no switchport",
                "vrf DVT-2",
                "ip address 192.168.2.6/31",
                "ip route vrf DVT-2 0.0.0.0/0 192.168.2.0",
            ]
        ),
    ]
    dev_intf.assert_has_calls(dev_intf_calls)

    # Verify info logging calls
    loginfo_calls = [
        call("Creating checkpoints and running setup on duts"),
        call(f"Checkpoint name is '{checkpoint_str}'"),
        call("Performing setup via dut roles"),
        call("Performing setup for role: key"),
        call("Performing setup for role: host1"),
        call("Sending checkpoint command and config to dut DSR01"),
        call("Sending checkpoint command and config to dut DCBBE1"),
        call("Performing setup for role: host2"),
        call("Sending checkpoint command and config to dut DCBBW1"),
        call("Sending checkpoint command and config to dut DCBBE2"),
        call("Performing setup for role: host3"),
        call("Sending checkpoint command and config to dut DCBBW2"),
    ]
    loginfo.assert_has_calls(loginfo_calls)

    # Verify debug logging calls
    logdebug_calls = [
        call(
            "Performing setup for test_perform_setup_via_role:\n{'key': 'role', 'host1': "
            "{'schema': None, 'template': 'interface Ethernet3\\nno switchport\\nvrf DVT-2\\nip "
            "address 192.168.2.4/31\\nip route vrf DVT-2 0.0.0.0/0 192.168.2.0\\n'}, 'host2': "
            "{'schema': None, 'template': 'interface Ethernet13\\nno switchport\\nip address "
            "192.168.2.5/31\\n'}, 'host3': {'schema': None, 'template': 'interface Ethernet7\\nno "
            "switchport\\nvrf DVT-2\\nip address 192.168.2.6/31\\nip route vrf DVT-2 0.0.0.0/0 "
            "192.168.2.0\\n'}}"
        ),
        call(f"Sending checkpoint command: configure checkpoint save {checkpoint_str}"),
        call(
            "Sending config:\n['interface Ethernet3', 'no switchport', 'vrf DVT-2', 'ip address "
            "192.168.2.4/31', 'ip route vrf DVT-2 0.0.0.0/0 192.168.2.0']"
        ),
        call(f"Sending checkpoint command: configure checkpoint save {checkpoint_str}"),
        call(
            "Sending config:\n['interface Ethernet3', 'no switchport', 'vrf DVT-2', 'ip address "
            "192.168.2.4/31', 'ip route vrf DVT-2 0.0.0.0/0 192.168.2.0']"
        ),
        call(f"Sending checkpoint command: configure checkpoint save {checkpoint_str}"),
        call(
            "Sending config:\n['interface Ethernet13', 'no switchport', "
            "'ip address 192.168.2.5/31']"
        ),
        call(f"Sending checkpoint command: configure checkpoint save {checkpoint_str}"),
        call(
            "Sending config:\n['interface Ethernet13', 'no switchport', "
            "'ip address 192.168.2.5/31']"
        ),
        call(f"Sending checkpoint command: configure checkpoint save {checkpoint_str}"),
        call(
            "Sending config:\n['interface Ethernet7', 'no switchport', 'vrf DVT-2', 'ip address "
            "192.168.2.6/31', 'ip route vrf DVT-2 0.0.0.0/0 192.168.2.0']"
        ),
    ]
    logdebug.assert_has_calls(logdebug_calls)


def test_perform_teardown_via_name(loginfo, logdebug, mocker):
    """Tests the perform_teardown function using the dut names"""

    # Mock the date so we can verify the checkpoint timestamp
    test_date = datetime.datetime(2023, 5, 20, 12, 58, 20)
    mock_dt = mocker.patch("vane.fixtures.datetime", wraps=datetime)
    mock_dt.datetime.now.return_value = test_date

    # Create a checkpoint string from the same date
    date_str = test_date.strftime("%y%m%d%H%M")
    test_name = "test_perform_teardown_via_name"
    checkpoint_str = f"{test_name}_{date_str}"

    # Mock the calls to the device interface
    dev_intf = mocker.patch("vane.device_interface")

    # Initialize the duts and setup_config data
    duts = read_yaml(DUTS)
    setup_config = read_yaml("tests/unittests/fixtures/fixtures-test-setup-config-names.yaml")

    # After we initialize the duts structure, create a "connection" interface object for each
    for dut in duts:
        duts[dut]["connection"] = vane.device_interface.PyeapiConn()

    # Call the perform_setup function
    vane.fixtures.perform_teardown(duts, checkpoint_str, setup_config)

    # Verify the calls
    #   Each call has a replace and delete call within it
    call_data = [
        f"configure replace checkpoint:{checkpoint_str} skip-checkpoint",
        f"delete checkpoint:{checkpoint_str}",
    ]
    # There are 5 duts, each making the same call
    dev_intf_calls = [call.PyeapiConn().config(call_data)] * 5

    dev_intf.assert_has_calls(dev_intf_calls)

    # Verify info logging calls
    loginfo_calls = [
        call(f"Performing teardown on checkpoint: {checkpoint_str}"),
        call("Performing teardown via dut names"),
        call("Restoring configuration and deleting checkpoint on dut DSR01"),
        call("Restoring configuration and deleting checkpoint on dut DCBBW1"),
        call("Restoring configuration and deleting checkpoint on dut DCBBW2"),
        call("No dut named UNCONFIGURED-DUT found, continuing to teardown next dut"),
        call("Restoring configuration and deleting checkpoint on dut DCBBE1"),
        call("Restoring configuration and deleting checkpoint on dut DCBBE2"),
    ]
    loginfo.assert_has_calls(loginfo_calls)

    # Verify debug logging calls
    #   Each dut teardown has 2 debug calls
    each_dut_teardown = [
        call(
            f"Sending checkpoint restore command: configure replace checkpoint:{checkpoint_str} "
            "skip-checkpoint"
        ),
        call(f"Sending delete checkpoint command: delete checkpoint:{checkpoint_str}"),
    ]
    #   And there are 5 duts
    logdebug_calls = each_dut_teardown * 5

    logdebug.assert_has_calls(logdebug_calls)


def test_perform_teardown_via_role(loginfo, logdebug, mocker):
    """Tests the perform_teardown function using the dut roles"""

    # Mock the date so we can verify the checkpoint timestamp
    test_date = datetime.datetime(2023, 6, 22, 22, 58, 20)
    mock_dt = mocker.patch("vane.fixtures.datetime", wraps=datetime)
    mock_dt.datetime.now.return_value = test_date

    # Create a checkpoint string from the same date
    date_str = test_date.strftime("%y%m%d%H%M")
    test_name = "test_perform_teardown_via_role"
    checkpoint_str = f"{test_name}_{date_str}"

    # Mock the calls to the device interface
    dev_intf = mocker.patch("vane.device_interface")

    # Initialize the duts and setup_config data
    duts = read_yaml(DUTS)
    setup_config = read_yaml("tests/unittests/fixtures/fixtures-test-setup-config-roles.yaml")

    # After we initialize the duts structure, create a "connection" interface object for each
    for dut in duts:
        duts[dut]["connection"] = vane.device_interface.PyeapiConn()

    # Call the perform_setup function
    vane.fixtures.perform_teardown(duts, checkpoint_str, setup_config)

    # Verify the calls
    #   Each call has a replace and delete call within it
    call_data = [
        f"configure replace checkpoint:{checkpoint_str} skip-checkpoint",
        f"delete checkpoint:{checkpoint_str}",
    ]
    # There are 5 duts, each making the same call
    dev_intf_calls = [call.PyeapiConn().config(call_data)] * 5

    dev_intf.assert_has_calls(dev_intf_calls)

    # Verify info logging calls
    loginfo_calls = [
        call(f"Performing teardown on checkpoint: {checkpoint_str}"),
        call("Performing teardown via dut roles"),
        call("Performing teardown for role: key"),
        call("Performing teardown for role: host1"),
        call("Restoring configuration and deleting checkpoint on dut DSR01"),
        call("Restoring configuration and deleting checkpoint on dut DCBBE1"),
        call("Performing teardown for role: host2"),
        call("Restoring configuration and deleting checkpoint on dut DCBBW1"),
        call("Restoring configuration and deleting checkpoint on dut DCBBE2"),
        call("Performing teardown for role: host3"),
        call("Restoring configuration and deleting checkpoint on dut DCBBW2"),
    ]
    loginfo.assert_has_calls(loginfo_calls)

    # Verify debug logging calls
    #   Each dut teardown has 2 debug calls
    each_dut_teardown = [
        call(
            f"Sending checkpoint restore command: configure replace checkpoint:{checkpoint_str} "
            "skip-checkpoint"
        ),
        call(f"Sending delete checkpoint command: delete checkpoint:{checkpoint_str}"),
    ]
    #   And there are 5 duts
    logdebug_calls = each_dut_teardown * 5

    logdebug.assert_has_calls(logdebug_calls)
