""" Unit test file for vane/gen_duts_from_cvp.py """
import json
import os
import os.path
import copy
import pytest
from vane import gen_duts_from_cvp


def test_create_duts_file_from_cvp(mocker):
    """test create_duts_file_from_cvp func success case"""
    with open("tests/unittests/fixtures/inventory.json", encoding="utf_8") as json_file:
        inventory = json.load(json_file)
    with open("tests/unittests/fixtures/lldp_neighbors.json", encoding="utf_8") as json_file:
        lldp_neighbors = json.load(json_file)
    mocker.patch("urllib3.disable_warnings")

    class MockCvpClient:
        """Mock CVP client"""

        def connect(self, cvp_ips, cvp_username, cvp_password):  # pylint: disable=unused-argument
            """Mock connect"""
            return

        def __init__(self):
            """init MockCvpClient"""
            self.api = MockCvpApi()

    class MockCvpApi:
        """Mock CVP Api"""

        def get_inventory(self):
            """get_inventory mock"""
            return inventory

    class MockPyeapiConn:
        """Mock pyeapi connection"""

        def execute(self, cmd):  # pylint: disable=unused-argument
            """Mock execute"""
            return copy.deepcopy(lldp_neighbors)

    mocker.patch("cvprac.cvp_client.CvpClient", return_value=MockCvpClient())
    mocker.patch("pyeapi.connect", return_value=MockPyeapiConn())
    gen_duts_from_cvp.create_duts_file_from_cvp(
        "blah", "blah", "blah", "unit_test_generated_duts.yaml"
    )
    assert os.path.isfile("unit_test_generated_duts.yaml")
    os.remove("unit_test_generated_duts.yaml")


def test_create_duts_file_from_cvp_exception(mocker):
    """exception test for create_duts_file_from_cvp func"""
    mocker.patch("cvprac.cvp_client.CvpClient", side_effect=ValueError("mock error"))
    with pytest.raises(SystemExit) as pytest_exit:
        gen_duts_from_cvp.create_duts_file_from_cvp(
            "blah", "blah", "blah", "unit_test_generated_duts.yaml"
        )
    assert pytest_exit.value.code == "Could not get CVP inventory info: mock error"
