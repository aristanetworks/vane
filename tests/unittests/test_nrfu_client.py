"""nrfu_client.py unit tests"""
from unittest.mock import call
import pytest
from vane import nrfu_client

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

    assert client.definitions_file == ""
    assert client.duts_file == ""
    assert client.username == ""
    assert client.password == ""

    mocker_object.assert_called_once()
    loginfo.assert_called_with("Starting the NRFU client")


def test_setup_not_cvp(mocker, capsys):
    """Testing to see if nrfu setup functions are called correctly"""

    mocker.patch("vane.nrfu_client.urllib3.disable_warnings")
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
            "internalVersion": "4.28.7M",
            "systemMacAddress": "74:83:ef:78:7d:64",
            "bootupTimestamp": 0,
            "version": "4.28.7M",
            "architecture": "",
            "internalBuild": "",
            "hardwareRevision": "",
            "domainName": "rtp-pslab.com",
            "hostname": "ps-rtp1-leaf1",
            "fqdn": "ps-rtp1-leaf1.rtp-pslab.com",
            "serialNumber": "JPE18380270",
            "deviceType": "eos",
            "danzEnabled": False,
            "mlagEnabled": False,
            "streamingStatus": "active",
            "parentContainerKey": "undefined_container",
            "status": "Registered",
            "complianceCode": "0000",
            "complianceIndication": "",
            "ztpMode": False,
            "unAuthorized": False,
            "ipAddress": "10.88.160.164",
            "key": "74:83:ef:78:7d:64",
            "deviceInfo": "Registered",
            "deviceStatus": "Registered",
            "isMLAGEnabled": False,
            "isDANZEnabled": False,
            "parentContainerId": "undefined_container",
            "bootupTimeStamp": 0,
            "internalBuildId": "",
            "taskIdList": [],
            "tempAction": None,
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
            "modelName": "CCS-720XP-48ZC2",
            "internalVersion": "4.28.7M",
            "systemMacAddress": "fc:bd:67:0f:33:f5",
            "bootupTimestamp": 0,
            "version": "4.28.7M",
            "architecture": "",
            "internalBuild": "",
            "hardwareRevision": "",
            "domainName": "rtp-pslab.com",
            "hostname": "ps-rtp1-host3",
            "fqdn": "ps-rtp1-host3.rtp-pslab.com",
            "serialNumber": "JPE19161323",
            "deviceType": "eos",
            "danzEnabled": False,
            "mlagEnabled": False,
            "streamingStatus": "active",
            "parentContainerKey": "undefined_container",
            "status": "Registered",
            "complianceCode": "0000",
            "complianceIndication": "",
            "ztpMode": False,
            "unAuthorized": False,
            "ipAddress": "10.88.160.69",
            "key": "fc:bd:67:0f:33:f5",
            "deviceInfo": "Registered",
            "deviceStatus": "Registered",
            "isMLAGEnabled": False,
            "isDANZEnabled": False,
            "parentContainerId": "undefined_container",
            "bootupTimeStamp": 0,
            "internalBuildId": "",
            "taskIdList": [],
            "tempAction": None,
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


    mocker_object = mocker.patch("vane.nrfu_client.CvpClient")
    mocker.patch("vane.nrfu_client.CvpClient.connect")
    client.get_duts_data("10.255.31.186")

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


# def test_generate_duts_file():
#     pass
# def test_generate_definitions_file():
#     pass


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
