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

    mocker.patch(
        "vane.nrfu_client.NrfuClient.get_duts_data", return_value=["hostname", "ipaddress"]
    )
    device_data, source = client.cvp_application()

    # Capture the printed output
    captured = capsys.readouterr()

    # Assert that the expected content is present in the captured output
    expected_content = "Using CVP to gather duts data"
    assert expected_content in captured.out

    assert device_data == ["hostname", "ipaddress"]
    assert source == "cvp"

    loginfo.assert_called_with("Using CVP to gather duts data")

    # def test_not_cvp_application():
    #     pass
    # def test_get_duts_data():
    #     pass
    # def test_read_device_list_file():
    #     pass
    # def test_generate_duts_file():
    #     pass
    # def test_write_duts():
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
