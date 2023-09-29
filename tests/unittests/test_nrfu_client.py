"""nrfu_client.py unit tests"""
from unittest.mock import call
import os
import pytest
from vane import nrfu_client
from tests.unittests.test_tests_tools import read_yaml

# Disable redefined-outer-name for using log fixture functions
# pylint: disable=redefined-outer-name,no-member


@pytest.fixture
def loginfo(mocker):
    """Fixture to mock logger calls from vane.nrfu_client"""
    return mocker.patch("vane.vane_logging.logging.info")


@pytest.fixture
def logerr(mocker):
    """Fixture to mock logger calls from vane.nrfu_client"""
    return mocker.patch("vane.vane_logging.logging.error")


@pytest.fixture
def logwarning(mocker):
    """Fixture to mock logger calls from vane.nrfu_client"""
    return mocker.patch("vane.vane_logging.logging.warning")


def test_nrfu_constructor(mocker, loginfo):
    """Test to see if setup function gets called correctly in init"""
    mocker_object = mocker.patch("vane.nrfu_client.NrfuClient.setup")

    client = nrfu_client.NrfuClient()

    assert client.definitions_file == "nrfu_tests/definitions_nrfu.yaml"
    assert client.duts_file == "nrfu_tests/duts_nrfu.yaml"
    assert client.username == ""
    assert client.password == ""

    mocker_object.assert_called_once()
    loginfo.assert_called_with("Starting the NRFU client")


def test_setup_not_cvp(mocker, capsys):
    """Testing to see if nrfu setup functions are called correctly"""

    mocker.patch("vane.nrfu_client.urllib3.disable_warnings")
    mocker.patch("vane.nrfu_client.readline.parse_and_bind")
    mocker.patch("vane.nrfu_client.NrfuClient.get_credentials")
    mocker.patch("vane.nrfu_client.NrfuClient.determine_if_cvp_application", return_value=False)
    mocker.patch("vane.nrfu_client.NrfuClient.not_cvp_application", return_value=([], "cvp"))
    mocker.patch("vane.nrfu_client.NrfuClient.generate_duts_file")
    mocker.patch("vane.nrfu_client.NrfuClient.generate_definitions_file")

    # Create an instance of the NrfuClient class
    client = nrfu_client.NrfuClient()

    # Capture the printed output
    captured = capsys.readouterr()

    # Assert that the expected content is present in the captured output
    expected_content = "Starting Execution of NRFU tests via Vane"
    assert expected_content in captured.out

    client.get_credentials.assert_called_once()
    client.determine_if_cvp_application.assert_called_once()
    client.not_cvp_application.assert_called_once()
    client.generate_duts_file.assert_called_once()
    client.generate_definitions_file.assert_called_once()


def test_setup_cvp(mocker, capsys):
    """Testing to see if nrfu setup functions are called correctly"""

    mocker.patch("vane.nrfu_client.urllib3.disable_warnings")
    mocker.patch("vane.nrfu_client.NrfuClient.get_credentials")
    mocker.patch("vane.nrfu_client.NrfuClient.determine_if_cvp_application", return_value=True)
    mocker.patch("vane.nrfu_client.NrfuClient.cvp_application", return_value=([], "noncvp"))
    mocker.patch("vane.nrfu_client.NrfuClient.generate_duts_file")
    mocker.patch("vane.nrfu_client.NrfuClient.generate_definitions_file")

    # Create an instance of the NrfuClient class
    client = nrfu_client.NrfuClient()

    # Capture the printed output
    captured = capsys.readouterr()

    # Assert that the expected content is present in the captured output
    expected_content = "Starting Execution of NRFU tests via Vane"
    assert expected_content in captured.out

    client.get_credentials.assert_called_once()
    client.determine_if_cvp_application.assert_called_once()
    client.cvp_application.assert_called_once()
    client.generate_duts_file.assert_called_once()
    client.generate_definitions_file.assert_called_once()


def test_get_credentials(mocker):
    """Testing the functionality to save username/passwords"""

    mocker.patch("vane.nrfu_client.NrfuClient.setup")
    mocker.patch("builtins.input", return_value="cvpadmin")
    mocker.patch("getpass.getpass", return_value="cvp123!")

    client = nrfu_client.NrfuClient()
    client.get_credentials()

    assert client.username == "cvpadmin"
    assert client.password == "cvp123!"


def test_determine_if_cvp_application(mocker, loginfo):
    """Testing the functionality which verifies if Vane is running
    as a CVP application"""

    mocker.patch("vane.nrfu_client.NrfuClient.setup")
    client = nrfu_client.NrfuClient()

    mocker.patch("vane.nrfu_client.os.environ.get", return_value=False)
    cvp = client.determine_if_cvp_application()

    assert not cvp

    mocker.patch("vane.nrfu_client.os.environ.get", return_value=True)
    cvp = client.determine_if_cvp_application()

    assert cvp

    loginfo_calls = [
        call("Determining if Vane is running as a CVP application"),
        call("Vane is not running as a CVP application"),
        call("Determining if Vane is running as a CVP application"),
        call("Vane is running as a CVP application"),
    ]
    loginfo.assert_has_calls(loginfo_calls, any_order=False)


def test_cvp_application(mocker, loginfo, capsys):
    """Testing the functionality which sets up cvp
    when Vane is running as CVP container"""

    mocker.patch("vane.nrfu_client.NrfuClient.setup")
    client = nrfu_client.NrfuClient()

    mocker_object = mocker.patch(
        "vane.nrfu_client.NrfuClient.get_duts_data", return_value=["hostname", "ipaddress"]
    )
    device_data, source = client.cvp_application()

    # Capture the printed output
    captured = capsys.readouterr()

    # Assert that the expected calls were made in the specified order
    expected_calls = [call("127.0.0.1")]
    assert mocker_object.call_args_list == expected_calls

    # Assert that the expected content is present in the captured output
    expected_content = "Using CVP to gather duts data"
    assert expected_content in captured.out

    assert device_data == ["hostname", "ipaddress"]
    assert source == "cvp"

    loginfo.assert_called_with("Using CVP to gather duts data")


def test_not_cvp_application_local_cvp(mocker):
    """Testing functionality of generating device data when connecting
    to CVP locally"""

    mocker.patch("vane.nrfu_client.NrfuClient.setup")
    client = nrfu_client.NrfuClient()

    mocker_object = mocker.patch("builtins.input")
    mocker_object.side_effect = [
        "yes",
        "10.255.31.187",
    ]

    expected_data = [["host1", "10.255.31.188"], ["host2", "10.255.31.189"]]
    mocker_object = mocker.patch(
        "vane.nrfu_client.NrfuClient.get_duts_data", return_value=expected_data
    )
    device_data, source = client.not_cvp_application()

    # Assert that the expected calls were made in the specified order
    expected_calls = [call("10.255.31.187")]
    assert mocker_object.call_args_list == expected_calls

    assert source == "cvp"
    assert device_data == expected_data


def test_not_cvp_application_device_file(mocker):
    """Testing functionality of generating device data when reading
    from device ip file"""

    mocker.patch("vane.nrfu_client.NrfuClient.setup")
    client = nrfu_client.NrfuClient()

    expected_data = ["10.255.31.184", "10.255.31.185", "10.255.31.186", "10.255.31.187"]
    mocker.patch("builtins.input", return_value="no")
    mocker.patch("vane.nrfu_client.prompt", return_value="tests/unittests/fixtures/device_ip_file")
    mocker_object = mocker.patch(
        "vane.nrfu_client.NrfuClient.is_valid_text_file", return_value=True
    )
    mocker_object_two = mocker.patch(
        "vane.nrfu_client.NrfuClient.read_device_list_file", return_value=expected_data
    )
    device_data, source = client.not_cvp_application()

    # Assert that the expected calls were made in the specified order
    expected_calls = [call("tests/unittests/fixtures/device_ip_file")]
    assert mocker_object.call_args_list == expected_calls
    assert mocker_object_two.call_args_list == expected_calls

    assert source == "non-cvp"
    assert device_data == expected_data


def test_not_cvp_application_invalid_choice(mocker):
    """Testing functionality which handles user choice of y/yes/n/no"""

    mocker.patch("vane.nrfu_client.NrfuClient.setup")
    client = nrfu_client.NrfuClient()

    mocker_object = mocker.patch("builtins.input")
    mocker_object.side_effect = [
        "KKK",
        "yes",
        "10.255.31.187",
    ]

    expected_data = [["host1", "10.255.31.188"], ["host2", "10.255.31.189"]]
    mocker_object_two = mocker.patch(
        "vane.nrfu_client.NrfuClient.get_duts_data", return_value=expected_data
    )
    device_data, source = client.not_cvp_application()

    assert mocker_object.call_count == 3
    # Assert that the expected calls were made in the specified order
    expected_calls = [call("10.255.31.187")]
    assert mocker_object_two.call_args_list == expected_calls

    assert source == "cvp"
    assert device_data == expected_data


def test_not_cvp_application_invalid_file(mocker):
    """Testing functionality of generating device data when reading
    from device ip file"""

    mocker.patch("vane.nrfu_client.NrfuClient.setup")
    client = nrfu_client.NrfuClient()

    expected_data = ["10.255.31.184", "10.255.31.185", "10.255.31.186", "10.255.31.187"]
    mocker.patch("builtins.input", return_value="no")
    mocker_object = mocker.patch("vane.nrfu_client.prompt")
    mocker_object.side_effect = [
        "tests/unittests/fixtures/",
        "tests/unittests/fixtures/device_ip_file",
    ]
    mocker_object_two = mocker.patch("vane.nrfu_client.NrfuClient.is_valid_text_file")
    mocker_object_two.side_effect = [
        False,
        True,
    ]
    mocker_object_three = mocker.patch(
        "vane.nrfu_client.NrfuClient.read_device_list_file", return_value=expected_data
    )
    device_data, source = client.not_cvp_application()

    # Assert that the expected calls were made in the specified order
    expected_calls = [
        call("tests/unittests/fixtures/"),
        call("tests/unittests/fixtures/device_ip_file"),
    ]
    assert mocker_object_two.call_args_list == expected_calls
    expected_calls = [call("tests/unittests/fixtures/device_ip_file")]
    assert mocker_object_three.call_args_list == expected_calls

    assert mocker_object.call_count == 2
    assert mocker_object_two.call_count == 2
    assert source == "non-cvp"
    assert device_data == expected_data


def test_get_duts_data(mocker, loginfo):
    """Testing functionality to get and process data from CVP"""
    inventory_data = [
        {
            "modelName": "DCS-7050SX3-48YC12",
            "domainName": "rtp-pslab.com",
            "hostname": "ps-rtp1-leaf1",
            "mlagEnabled": False,
            "streamingStatus": "active",
            "unAuthorized": False,
            "ipAddress": "10.88.160.164",
            "memTotal": 0,
            "memFree": 0,
            "sslConfigAvailable": False,
            "sslEnabledByCVP": False,
            "lastSyncUp": 0,
            "type": "netelement",
            "dcaKey": None,
            "containerName": "Leaf",
        },
        {
            "modelName": "CCS-720XP-48ZC2",
            "domainName": "rtp-pslab.com",
            "hostname": "ps-rtp1-host3",
            "mlagEnabled": False,
            "streamingStatus": "inactive",
            "unAuthorized": False,
            "ipAddress": "10.88.160.69",
            "memTotal": 0,
            "memFree": 0,
            "sslConfigAvailable": False,
            "sslEnabledByCVP": False,
            "lastSyncUp": 0,
            "type": "netelement",
            "dcaKey": None,
            "containerName": "Host",
        },
        {
            "modelName": "CCS-720XP-48ZC3",
            "domainName": "rtp-pslab.com",
            "hostname": "ps-rtp1-host4",
            "mlagEnabled": False,
            "streamingStatus": "active",
            "unAuthorized": False,
            "ipAddress": "10.88.160.68",
            "memTotal": 0,
            "memFree": 0,
            "sslConfigAvailable": False,
            "sslEnabledByCVP": False,
            "lastSyncUp": 0,
            "type": "netelement",
            "dcaKey": None,
            "containerName": "Undefined",
        },
        {
            "modelName": "CCS-720XP-48ZC5",
            "domainName": "rtp-pslab.com",
            "hostname": "ps-rtp1-host5",
            "mlagEnabled": False,
            "streamingStatus": "inactive",
            "unAuthorized": False,
            "ipAddress": "10.88.160.70",
            "memTotal": 0,
            "memFree": 0,
            "sslConfigAvailable": False,
            "sslEnabledByCVP": False,
            "lastSyncUp": 0,
            "type": "netelement",
            "dcaKey": None,
            "containerName": "Undefined",
        },
    ]
    mocker.patch("vane.nrfu_client.NrfuClient.setup")
    client = nrfu_client.NrfuClient()

    mocker_object_client = mocker.patch("vane.nrfu_client.CvpClient")
    mocker_object_api = mocker.patch("vane.nrfu_client.CvpApi")

    # Create a MagicMock instance to simulate the return value
    get_inventory_mock = mocker.MagicMock(return_value=inventory_data)

    # Attach the mocked get_inventory method to the cvp_api_mock
    mocker_object_api.return_value.get_inventory = get_inventory_mock

    device_data = client.get_duts_data("10.255.31.186")

    mocker_object_client.return_value.connect.assert_called_once_with(["10.255.31.186"], "", "")
    assert device_data == [["ps-rtp1-leaf1", "10.88.160.164"]]

    loginfo.assert_called_with("Connecting to CVP to gather duts data")


def test_read_device_list_file(mocker, loginfo):
    """Testing functionality which reads in list of device ip's from
    given file"""

    mocker.patch("vane.nrfu_client.NrfuClient.setup")
    client = nrfu_client.NrfuClient()

    device_list_file = "tests/unittests/fixtures/device_ip_file"
    device_data = client.read_device_list_file(device_list_file)

    expected_data = ["10.255.31.184", "10.255.31.185", "10.255.31.186", "10.255.31.187"]
    assert device_data == expected_data

    loginfo.assert_called_with("Reading in dut ip data from device list file")


def test_generate_duts_file_cvp(mocker, loginfo):
    """Testing the functionality that generates duts_nrfu file from cvp data"""

    mocker.patch("vane.nrfu_client.NrfuClient.setup")
    client = nrfu_client.NrfuClient()

    client.duts_file = "tests/unittests/fixtures/duts_nrfu.yaml"
    client.generate_duts_file(
        [
            ["ps-rtp1-leaf1", "10.88.160.154"],
            ["ps-rtp1-leaf2", "10.88.160.164"],
            ["ps-rtp1-leaf3", "10.88.160.174"],
        ],
        "cvp",
    )

    loginfo_calls = [
        call("Generating duts file for nrfu testing"),
        call("Opening tests/unittests/fixtures/duts_nrfu.yaml for write"),
    ]
    loginfo.assert_has_calls(loginfo_calls, any_order=False)

    assert read_yaml(client.duts_file) == read_yaml(
        "tests/unittests/fixtures/duts_nrfu_cvp_expected.yaml"
    )
    os.remove(client.duts_file)


def test_generate_duts_file_non_cvp(mocker, loginfo):
    """Testing the functionality that generates duts_nrfu file from non-cvp data"""

    mocker.patch("vane.nrfu_client.NrfuClient.setup")
    client = nrfu_client.NrfuClient()

    client.duts_file = "tests/unittests/fixtures/duts_nrfu.yaml"
    client.generate_duts_file(["10.88.160.154", "10.88.160.164", "10.88.160.174"], "non-cvp")

    loginfo_calls = [
        call("Generating duts file for nrfu testing"),
        call("Opening tests/unittests/fixtures/duts_nrfu.yaml for write"),
    ]
    loginfo.assert_has_calls(loginfo_calls, any_order=False)

    assert read_yaml(client.duts_file) == read_yaml(
        "tests/unittests/fixtures/duts_nrfu_non_cvp_expected.yaml"
    )
    os.remove(client.duts_file)


def test_generate_definitions_file_default(mocker, loginfo):
    """Testing functionality which generates default definitions_nrfu file"""

    mocker.patch("vane.nrfu_client.NrfuClient.setup")
    client = nrfu_client.NrfuClient()

    mocker.patch("builtins.input", return_value="no")

    client.definitions_file = "tests/unittests/fixtures/definitions_nrfu.yaml"
    client.generate_definitions_file()

    loginfo_calls = [
        call("Generating definitions file for nrfu testing"),
        call("Opening tests/unittests/fixtures/definitions_nrfu.yaml for write"),
    ]
    loginfo.assert_has_calls(loginfo_calls, any_order=False)

    assert read_yaml(client.definitions_file) == read_yaml(
        "tests/unittests/fixtures/definitions_nrfu_default_expected.yaml"
    )

    os.remove(client.definitions_file)


def test_generate_definitions_file_custom(mocker, loginfo):
    """Testing functionality which generates custom definitions_nrfu file"""

    mocker.patch("vane.nrfu_client.NrfuClient.setup")
    client = nrfu_client.NrfuClient()

    mocker.patch("builtins.input", return_value="yes")
    mocker.patch("vane.nrfu_client.prompt", return_value="sample_network_tests/memory")

    client.definitions_file = "tests/unittests/fixtures/definitions_nrfu.yaml"
    client.generate_definitions_file()

    loginfo_calls = [
        call("Generating definitions file for nrfu testing"),
        call("Opening tests/unittests/fixtures/definitions_nrfu.yaml for write"),
    ]
    loginfo.assert_has_calls(loginfo_calls, any_order=False)

    assert read_yaml(client.definitions_file) == read_yaml(
        "tests/unittests/fixtures/definitions_nrfu_custom_expected.yaml"
    )

    os.remove(client.definitions_file)


def test_generate_definitions_file_invalid_custom(mocker, loginfo):
    """Testing functionality which generates definitions_nrfu file
    with user entering invalid directories first"""

    mocker.patch("vane.nrfu_client.NrfuClient.setup")
    client = nrfu_client.NrfuClient()

    mocker.patch("builtins.input", return_value="yes")
    mocker_object = mocker.patch("vane.nrfu_client.prompt")
    mocker_object.side_effect = [
        "tests/unittests/fixtures/does_not_exist",
        "tests/unittests/fixtures/definitions_nrfu.yaml",
        "sample_network_tests/memory",
    ]

    client.definitions_file = "tests/unittests/fixtures/definitions_nrfu.yaml"
    client.generate_definitions_file()

    loginfo_calls = [
        call("Generating definitions file for nrfu testing"),
        call("Opening tests/unittests/fixtures/definitions_nrfu.yaml for write"),
    ]
    loginfo.assert_has_calls(loginfo_calls, any_order=False)

    assert mocker_object.call_count == 3
    assert read_yaml(client.definitions_file) == read_yaml(
        "tests/unittests/fixtures/definitions_nrfu_custom_expected.yaml"
    )

    os.remove(client.definitions_file)


def test_is_valid_text_file(mocker):
    """Testing the functionality which verifies the validity of a file"""

    mocker.patch("vane.nrfu_client.NrfuClient.setup")
    client = nrfu_client.NrfuClient()

    valid_file = "tests/unittests/fixtures/valid_text_file"
    validity = client.is_valid_text_file(valid_file)

    assert validity

    invalid_file = "tests/unittests"
    validity = client.is_valid_text_file(invalid_file)

    assert not validity

    non_existent = "tests/unittests/fixtures/not_exist"
    validity = client.is_valid_text_file(non_existent)

    assert not validity
