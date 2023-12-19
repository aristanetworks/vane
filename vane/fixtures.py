#!/usr/bin/env python3
#
# Copyright (c) 2023, Arista Networks EOS+
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
# * Neither the name of the Arista nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

# Ignore redefined-outer-name since the dut/duts methods are defined as fixtures
# and are passed as parameters to other methods in this module
# pylint: disable=redefined-outer-name,import-error,no-name-in-module

"""
Fixture setup and teardown functions
"""

import datetime
import re
import pytest

from py.xml import html
from jinja2 import Template
from vane import tests_tools
from vane.config import dut_objs, test_defs
from vane.utils import get_current_fixture_testclass, get_current_fixture_testname, remove_comments
from vane.vane_logging import logging


def idfn(val):
    """id function for the current fixture data

    Args:
        val (dict): current value of the fixture param

    Returns:
        [string]: name of the current dut
    """

    logging.debug("Invoking idfn to get the name of the current dut")
    return val["name"]


@pytest.fixture(scope="session", params=dut_objs, ids=idfn)
def dut(request):
    """Parameterize each dut for a test case

    Args:
        request (dict): duts from return_duts

    Returns:
        [dict]: a single dut in duts data structure
    """

    logging.debug("Invoking fixture to parameterize a dut for a test case")
    dutt = request.param
    yield dutt


@pytest.fixture(scope="session")
def duts():
    """Returns all the duts under test

    Returns:
        [dict]: a list of duts
    """

    logging.debug("Invoking fixture to get list of duts")
    duts_dict = {}
    for dutt in dut_objs:
        duts_dict[dutt["name"]] = dutt

    logging.debug(f"Returning duts dictionary: {duts_dict}")
    return duts_dict


@pytest.fixture()
def tests_definitions():
    """Return test definitions to each test case

    Args:
        scope (str, optional): Defaults to 'session'.

    Yields:
        [dict]: Return test definitions to test case
    """

    logging.debug("Invoking fixture to get test definitions for each test case")
    yield test_defs


def setup_via_name(duts, setup_config, checkpoint):
    """Creates checkpoint on duts and then runs setup for
    duts identified using the device name"""

    logging.info("Performing setup via dut names")
    for dev_name in setup_config:
        dutt = duts.get(dev_name, None)

        if dutt is None:
            logging.info(f"No dut named {dev_name} found, continuing to setup next dut")
            continue

        setup_schema = remove_comments(setup_config[dev_name]["schema"])

        if setup_schema is None:
            temp_without_comments = remove_comments(setup_config[dev_name]["template"])
            config = temp_without_comments.splitlines()
        else:
            template = remove_comments(setup_config[dev_name]["template"])
            setup_template = Template(template)
            config = setup_template.render(setup_schema).splitlines()

        checkpoint_cmd = f"configure checkpoint save {checkpoint}"
        gold_config = [checkpoint_cmd]

        logging.info(f"Sending checkpoint command and config to dut {dutt['name']}")
        logging.debug(f"Sending checkpoint command: {checkpoint_cmd}")
        logging.debug(f"Sending config:\n{config}")
        try:
            dutt["connection"].enable(gold_config)
            dutt["connection"].config(config)
        except BaseException as e:
            logging.info(f"setup failed with exception {e} and mesg {str(e)}")
            logging.debug(f"reverting to checkpoint {checkpoint}")
            # something failed, call teardown
            checkpoint_restore_cmd = f"configure replace checkpoint:{checkpoint} skip-checkpoint"
            delete_checkpoint_cmd = f"delete checkpoint:{checkpoint}"
            teardown_via_name(duts, setup_config, checkpoint_restore_cmd, delete_checkpoint_cmd)
            # reraise the exception
            raise e


def setup_via_role(duts, setup_config, checkpoint):
    """Creates checkpoint on duts and then runs setup for
    duts identified using the device role"""

    logging.info("Performing setup via dut roles")
    for role in setup_config:
        logging.info(f"Performing setup for role: {role}")
        for _, dutt in duts.items():
            if dutt["role"] != role:
                continue
            setup_schema = remove_comments(setup_config[role]["schema"])

            if setup_schema is None:
                temp_without_comments = remove_comments(setup_config[role]["template"])
                config = temp_without_comments.splitlines()
            else:
                template = remove_comments(setup_config[role]["template"])
                setup_template = Template(template)
                config = setup_template.render(setup_schema).splitlines()

            checkpoint_cmd = f"configure checkpoint save {checkpoint}"
            gold_config = [checkpoint_cmd]

            logging.info(f"Sending checkpoint command and config to dut {dutt['name']}")
            logging.debug(f"Sending checkpoint command: {checkpoint_cmd}")
            logging.debug(f"Sending config:\n{config}")
            try:
                dutt["connection"].enable(gold_config)
                dutt["connection"].config(config)
            except BaseException as e:
                logging.info(f"setup failed with exception {e} and mesg {str(e)}")
                logging.debug(f"reverting to checkpoint {checkpoint}")
                # something failed, call teardown
                checkpoint_restore_cmd = (
                    f"configure replace checkpoint:{checkpoint} skip-checkpoint"
                )
                delete_checkpoint_cmd = f"delete checkpoint:{checkpoint}"
                teardown_via_role(duts, setup_config, checkpoint_restore_cmd, delete_checkpoint_cmd)
                # reraise the exception
                raise e


def perform_setup(duts, test, setup_config):
    """Creates checkpoints and then runs setup on duts"""

    logging.info("Creating checkpoints and running setup on duts")

    date_obj = datetime.datetime.now()
    gold_config_date = date_obj.strftime("%y%m%d%H%M")
    checkpoint = f"{test}_{gold_config_date}"
    logging.info(f"Checkpoint name is '{checkpoint}'")
    logging.debug(f"Performing setup for {test}:\n{setup_config}")
    dev_ids = setup_config.get("key", "name")

    if dev_ids == "name":
        setup_via_name(duts=duts, setup_config=setup_config, checkpoint=checkpoint)

    elif dev_ids == "role":
        setup_via_role(duts=duts, setup_config=setup_config, checkpoint=checkpoint)

    return checkpoint


def teardown_via_name(duts, setup_config, checkpoint_restore_cmd, delete_checkpoint_cmd):
    """Restores the checkpoints on duts identified by their name"""

    logging.info("Performing teardown via dut names")
    for dev_name in setup_config:
        dutt = duts.get(dev_name, None)
        if dutt is None:
            logging.info(f"No dut named {dev_name} found, continuing to teardown next dut")
            continue
        restore_config = [checkpoint_restore_cmd, delete_checkpoint_cmd]
        logging.info(f"Restoring configuration and deleting checkpoint on dut {dutt['name']}")
        logging.debug(f"Sending checkpoint restore command: {checkpoint_restore_cmd}")
        logging.debug(f"Sending delete checkpoint command: {delete_checkpoint_cmd}")
        dutt["connection"].config(restore_config)


def teardown_via_role(duts, setup_config, checkpoint_restore_cmd, delete_checkpoint_cmd):
    """Restores the checkpoints on duts identified by their role"""

    logging.info("Performing teardown via dut roles")
    for role in setup_config:
        logging.info(f"Performing teardown for role: {role}")
        for _, dutt in duts.items():
            if dutt["role"] != role:
                continue
            restore_config = [checkpoint_restore_cmd, delete_checkpoint_cmd]
            logging.info(f"Restoring configuration and deleting checkpoint on dut {dutt['name']}")
            logging.debug(f"Sending checkpoint restore command: {checkpoint_restore_cmd}")
            logging.debug(f"Sending delete checkpoint command: {delete_checkpoint_cmd}")
            dutt["connection"].config(restore_config)


def perform_teardown(duts, checkpoint, setup_config):
    """Restore and delete checkpoint"""
    if checkpoint == "":
        return

    logging.info(f"Performing teardown on checkpoint: {checkpoint}")
    checkpoint_restore_cmd = f"configure replace checkpoint:{checkpoint} skip-checkpoint"
    delete_checkpoint_cmd = f"delete checkpoint:{checkpoint}"
    dev_ids = setup_config.get("key", "name")

    if dev_ids == "name":
        teardown_via_name(
            duts=duts,
            setup_config=setup_config,
            checkpoint_restore_cmd=checkpoint_restore_cmd,
            delete_checkpoint_cmd=delete_checkpoint_cmd,
        )

    elif dev_ids == "role":
        teardown_via_role(
            duts=duts,
            setup_config=setup_config,
            checkpoint_restore_cmd=checkpoint_restore_cmd,
            delete_checkpoint_cmd=delete_checkpoint_cmd,
        )


@pytest.fixture(autouse=True, scope="class")
def setup_testsuite(request, duts):
    """Setup the duts using the test suite(class) setup file"""

    logging.debug("Performing test suite setup")
    testsuite = get_current_fixture_testclass(request)
    test_suites = test_defs["test_suites"]
    setup_config = []
    checkpoint = ""
    for suite in test_suites:
        if suite["name"] == testsuite:
            logging.info(f"Performing setup for test suite: {testsuite}")
            setup_config_file = suite.get("test_setup", "")
            if setup_config_file != "":
                logging.info("Applying test suite setup_config file")
                setup_config = tests_tools.import_yaml(f"{suite['dir_path']}/{setup_config_file}")
                checkpoint = perform_setup(duts, testsuite, setup_config)
                logging.debug(f"Checkpoint created: {checkpoint}")
    yield
    perform_teardown(duts, checkpoint, setup_config)


@pytest.fixture(autouse=True, scope="function")
def setup_testcase(request, duts):
    """Setup the duts using the test case(function) setup file"""

    logging.debug("Performing test suite setup")
    testname = get_current_fixture_testname(request)
    test_suites = test_defs["test_suites"]
    setup_config = []
    checkpoint = ""
    for suite in test_suites:
        tests = suite["testcases"]
        for test in tests:
            if test["name"] == testname:
                logging.info(f"Performing setup for test case: {testname}")
                setup_config_file = test.get("test_setup", "")
                if setup_config_file != "":
                    logging.info("Applying test case setup_config file")
                    setup_config = tests_tools.import_yaml(
                        f"{suite['dir_path']}/{setup_config_file}"
                    )
                    checkpoint = perform_setup(duts, testname, setup_config)
                    logging.debug(f"Checkpoint created: {checkpoint}")

    yield
    perform_teardown(duts, checkpoint, setup_config)


def find_nodeid(nodeid):
    """Return device parameter

    Args:
        nodeid (str): Device Name

    Return: Name of device

    """

    if re.match(r".*\[(.*)\]", nodeid):
        return re.match(r".*\[(.*)\]", nodeid)[1]

    return "NONE"


def read_test_id(report):
    """Returns test id for the test case being executed

    Args:
        report: pytest report
    """
    last_double_colon_index = report.nodeid.rfind("::")
    last_open_bracket_index = report.nodeid.rfind("[")
    test_case_name = report.nodeid[
        last_double_colon_index + 2 : last_open_bracket_index  # noqa: E203
    ]

    for test_suite in test_defs["test_suites"]:
        for test_case in test_suite["testcases"]:
            if test_case_name == test_case["name"]:
                if "test_id" in test_case:
                    return test_case["test_id"]
                return ""

    return ""


def pytest_html_results_table_header(cells):
    """Create custom PyTest-HTML Header Row

    Args:
        cells: Cell data
    """

    cells.insert(2, html.th("Description"))
    cells.insert(1, html.th("Test ID"))
    cells.insert(1, html.th("Device", class_="sortable string", col="device"))
    cells.pop()


def pytest_html_results_table_row(report, cells):
    """Create custom PyTest-HTML report row

    Args:
        report: pytest report
        cells: Cell data
    """

    cells.insert(2, html.td(getattr(report, "description", "")))
    cells.insert(1, html.td(getattr(report, "test_id", "")))
    cells.insert(1, html.td(find_nodeid(report.nodeid), class_="col-device"))
    cells.pop()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item):
    """Called to create a _pytest.reports.TestReport for each of the setup,
    call and teardown runtest phases of a test item.

    """

    outcome = yield
    report = outcome.get_result()

    report.test_id = read_test_id(report)

    if str(item.function.__doc__).split("Args:", maxsplit=1)[0]:
        report.description = str(item.function.__doc__).split("Args:", maxsplit=1)[0]
    elif str(item.function.__doc__):
        report.description = str(item.function.__doc__)
    else:
        report.description = "No Description"
