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
# pylint: disable=redefined-outer-name

"""
Fixture setup and teardown functions
"""

import datetime
import logging
import pytest

from jinja2 import Template
from vane import tests_tools
from vane.config import dut_objs, test_defs
from vane.utils import get_current_fixture_testclass, get_current_fixture_testname


def idfn(val):
    """id function for the current fixture data

    Args:
        val (dict): current value of the fixture param

    Returns:
        [string]: name of the current dut
    """
    return val["name"]


@pytest.fixture(scope="session", params=dut_objs, ids=idfn)
def dut(request):
    """Parameterize each dut for a test case

    Args:
        request (dict): duts from return_duts

    Returns:
        [dict]: a single dut in duts data structure
    """

    dutt = request.param
    yield dutt


@pytest.fixture(scope="session")
def duts():
    """Returns all the duts under test

    Returns:
        [dict]: a list of duts
    """
    logging.info("Invoking fixture to get list of duts")
    duts_dict = {}
    for dutt in dut_objs:
        duts_dict[dutt["name"]] = dutt
    return duts_dict


@pytest.fixture()
def tests_definitions():
    """Return test definitions to each test case

    Args:
        scope (str, optional): Defaults to 'session'.

    Yields:
        [dict]: Return test definitions to test case
    """

    yield test_defs


def setup_via_name(duts, setup_config, checkpoint):
    """Creates checkpoint on duts and then runs setup for
    duts identified using the device name"""

    for dev_name in setup_config:
        dutt = duts.get(dev_name, None)

        if dutt is None:
            # add logging
            continue
        setup_schema = setup_config[dev_name]["schema"]

        if setup_schema is None:
            config = setup_config[dev_name]["template"].splitlines()

        else:
            setup_template = Template(setup_config[dev_name]["template"])
            config = setup_template.render(setup_schema).splitlines()

        checkpoint_cmd = f"configure checkpoint save {checkpoint}"
        gold_config = [checkpoint_cmd]
        dutt["connection"].enable(gold_config)
        dutt["connection"].config(config)


def setup_via_role(duts, setup_config, checkpoint):
    """Creates checkpoint on duts and then runs setup for
    duts identified using the device role"""

    for role in setup_config:
        for _, dutt in duts.items():
            if dutt["role"] != role:
                # add logging
                continue
            setup_schema = setup_config[role]["schema"]
            if setup_schema is None:
                config = setup_config[role]["template"].splitlines()
            else:
                setup_template = Template(setup_config[role]["template"])
                config = setup_template.render(setup_schema).splitlines()
            checkpoint_cmd = f"configure checkpoint save {checkpoint}"
            gold_config = [checkpoint_cmd]
            dutt["connection"].enable(gold_config)
            dutt["connection"].config(config)


def perform_setup(duts, test, setup_config):
    """Creates checkpoints and then runs setup on duts"""

    date_obj = datetime.datetime.now()
    gold_config_date = date_obj.strftime("%y%m%d%H%M")
    checkpoint = f"{test}_{gold_config_date}"
    logging.info(f"{test} : {setup_config}")
    dev_ids = setup_config.get("key", "name")

    if dev_ids == "name":
        setup_via_name(duts=duts, setup_config=setup_config, checkpoint=checkpoint)

    elif dev_ids == "role":
        setup_via_role(duts=duts, setup_config=setup_config, checkpoint=checkpoint)

    return checkpoint


def teardown_via_name(duts, setup_config, checkpoint_restore_cmd, delete_checkpoint_cmd):
    """Restores the checkpoints on duts identified by their name"""

    for dev_name in setup_config:
        dutt = duts.get(dev_name, None)
        if dutt is None:
            continue
        restore_config = [checkpoint_restore_cmd, delete_checkpoint_cmd]
        dutt["connection"].config(restore_config)


def teardown_via_role(duts, setup_config, checkpoint_restore_cmd, delete_checkpoint_cmd):
    """Restores the checkpoints on duts identified by their role"""

    for role in setup_config:
        for _, dutt in duts.items():
            if dutt["role"] != role:
                # add logging
                continue
            restore_config = [checkpoint_restore_cmd, delete_checkpoint_cmd]
            dutt["connection"].config(restore_config)


def perform_teardown(duts, checkpoint, setup_config):
    """Restore and delete checkpoint"""
    if checkpoint == "":
        return

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

    testsuite = get_current_fixture_testclass(request)
    test_suites = test_defs["test_suites"]
    setup_config = []
    checkpoint = ""
    for suite in test_suites:
        if suite["name"] == testsuite:
            setup_config_file = suite.get("test_setup", "")
            if setup_config_file != "":
                setup_config = tests_tools.setup_import_yaml(
                    f"{suite['dir_path']}/{setup_config_file}"
                )
                checkpoint = perform_setup(duts, testsuite, setup_config)
    yield
    perform_teardown(duts, checkpoint, setup_config)


@pytest.fixture(autouse=True, scope="function")
def setup_testcase(request, duts):
    """Setup the duts using the test case(function) setup file"""

    testname = get_current_fixture_testname(request)
    test_suites = test_defs["test_suites"]
    setup_config = []
    checkpoint = ""
    for suite in test_suites:
        tests = suite["testcases"]
        for test in tests:
            if test["name"] == testname:
                setup_config_file = test.get("test_setup", "")
                if setup_config_file != "":
                    setup_config = tests_tools.setup_import_yaml(
                        f"{suite['dir_path']}/{setup_config_file}"
                    )
                    checkpoint = perform_setup(duts, testname, setup_config)

    yield
    perform_teardown(duts, checkpoint, setup_config)
