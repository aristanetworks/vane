"""nrfu_client.py unit tests"""
from unittest.mock import call
import pytest
import vane
from vane import nrfu_client

# Disable redefined-outer-name for using log fixture functions
# pylint: disable=redefined-outer-name


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

# def test_setup(mocker, loginfo):
#     """Testing to see if nrfu setup functions are called correctly"""

#     mocker.patch("vane.nrfu_client.NrfuClient.get_credentials")
#     mocker.patch("vane.nrfu_client.NrfuClient.determine_if_cvp_application", return_value=False)
#     mocker_object =  mocker.patch("vane.nrfu_client.NrfuClient.not_cvp_application")
#     mocker.patch("vane.nrfu_client.NrfuClient.generate_duts_file")
#     mocker.patch("vane.nrfu_client.NrfuClient.generate_definitions_file")

#     mocker_object.assert_called_once()

def test_get_credentials():
    pass
def test_determine_if_cvp_application():
    pass
def test_cvp_application():
    pass
def test_not_cvp_application():
    pass
def test_get_duts_data():
    pass
def test_read_device_list_file():
    pass
def test_generate_duts_file():
    pass
def test_write_duts():
    pass
def test_generate_definitions_file():
    pass
def test_is_valid_text_file():
    pass






