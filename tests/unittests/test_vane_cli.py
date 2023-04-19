"""vane_cli.py uni tests"""
import os
from unittest.mock import call
import pytest
from vane import vane_cli


@pytest.fixture
def loginfo(mocker):
    """Fixture to mock logger calls from vane.tests_client"""
    return mocker.patch("vane.tests_client.logging.info")


@pytest.fixture
def logerr(mocker):
    """Fixture to mock logger calls from vane.tests_client"""
    return mocker.patch("vane.tests_client.logging.error")


def test_write_steps():
    """Validates the functionality of the script which writes .md and .json with test steps
    for test files. REQUIRES there to be a unittests/fixtures/test_steps/test_steps.py existing
    in this folder for test to pass"""
    assert not os.path.exists("fixtures/test_steps/test_steps.md")
    assert not os.path.exists("fixtures/test_steps/test_steps.json")
    vane_cli.write_test_steps(["fixtures/test_steps"])
    assert os.path.exists("fixtures/test_steps/test_steps.md")
    assert os.path.exists("fixtures/test_steps/test_steps.json")
    with open(
        "fixtures/test_steps/test_steps.md", "r", encoding="utf-8"
    ) as file_pointer:
        count = len(file_pointer.readlines())
        assert count == 23

    os.remove("fixtures/test_steps/test_steps.md")
    os.remove("fixtures/test_steps/test_steps.json")


def test_create_duts_from_topo():
    """Validates functionality of create_duts_from_topo method"""
    topology_file = "fixtures/test_topology.yaml"
    vane_cli.create_duts_from_topo(topology_file)
    assert os.path.isfile("fixtures/test_topology.yaml_duts.yaml")
    os.remove("fixtures/test_topology.yaml_duts.yaml")


def test_parse_cli():
    """Validates functionality of parse_cli method"""
    arguments = vane_cli.parse_cli()
    assert len(vars(arguments)) == 7
    assert arguments.definitions_file == "definitions.yaml"
    assert arguments.duts_file == "duts.yaml"
    assert arguments.environment == "test"
    assert not arguments.markers


# add functionality for checking the mocked methods return values


def test_setup_vane(loginfo, mocker):
    """Validates functionality of setup_vane method"""
    mocker.patch("vane.tests_tools.import_yaml")
    mocker.patch("vane.tests_tools.return_test_defs")
    mocker.patch("vane.tests_tools.return_show_cmds")
    mocker.patch("vane.tests_tools.init_duts")
    vane_cli.setup_vane()
    loginfo_calls = [
        call("Starting Test Suite setup"),
        call("Discovering show commands from definitions"),
    ]
    loginfo.assert_has_calls(loginfo_calls, any_order=False)


# add functionality for checking the mocked methods return values


def test_run_tests(loginfo, mocker):
    """Validates functionality of run_tests method"""
    mocker.patch("vane.tests_client.TestsClient")
    mocker.patch("vane.tests_client.TestsClient.generate_test_definitions")
    mocker.patch("vane.tests_client.TestsClient.setup_test_runner")
    mocker.patch("vane.vane_cli.setup_vane")
    mocker.patch("vane.tests_client.TestsClient.test_runner")
    vane_cli.run_tests("", "")
    loginfo.assert_called_with(
        "Using class TestsClient to create vane_tests_client object"
    )


# add functionality for checking the mocked methods return values


def test_write_results(loginfo, mocker):
    """Validates functionality of write_results method"""
    mocker.patch("vane.report_client.ReportClient")
    mocker.patch("vane.report_client.ReportClient.write_result_doc")
    vane_cli.write_results("")
    loginfo.assert_called_with(
        "Using class ReportClient to create vane_report_client object"
    )


# def test_main():
#     pass

# def test_show_markers():
#     pass

# def test_download_test_results():
#     pass
