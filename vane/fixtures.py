import pytest
import logging
from vane import tests_tools
import os
from vane.config import dut_objs, test_defs, test_duts
from jinja2 import Template
from vane.utils import get_current_fixture_testclass, get_current_fixture_testname
import datetime

def idfn(val):
    """id function for the current fixture data

    Args:
        val (dict): current value of the fixture param

    Returns:
        [string]: name of the current dut
    """
    return val['name']


@pytest.fixture(scope="session", params=dut_objs, ids=idfn)
def dut(request):
    """Parameterize each dut for a test case

    Args:
        request (dict): duts from return_duts

    Returns:
        [dict]: a single dut in duts data structure
    """

    dut = request.param
    yield dut

@pytest.fixture(scope="session")
def duts():
    """Returns all the duts under test

    Returns:
        [dict]: a list of duts
    """
    logging.info("Invoking fixture to get list of duts")
    duts_dict = {}
    for dut in dut_objs:
        duts_dict[dut['name']] = dut
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
    """ Creates checkpoint on duts and then runs setup for
        duts identified using the device name """

    for dev_name in setup_config:
        dut = duts.get(dev_name, None)

        if dut is None:
            #add logging
            continue
        setup_schema = setup_config[dev_name]["schema"]

        if setup_schema is None:
            config = setup_config[dev_name]["template"].splitlines()

        else:
            setup_template = Template(setup_config[dev_name]["template"])
            config = setup_template.render(setup_schema).splitlines()

        checkpoint_cmd = f"configure checkpoint save {checkpoint}"
        gold_config = [checkpoint_cmd]
        dut['connection'].enable(gold_config)
        dut['connection'].config(config)

def setup_via_role(duts, setup_config, checkpoint):
    """ Creates checkpoint on duts and then runs setup for
        duts identified using the device role """

    for role in setup_config:
        for _, dut in duts.items():
            if dut["role"] != role:
                #add logging
                continue
            setup_schema = setup_config[role]["schema"]
            if setup_schema is None:
                config = setup_config[role]["template"].splitlines()
            else:
                setup_template = Template(setup_config[role]["template"])
                config = setup_template.render(setup_schema).splitlines()
            checkpoint_cmd = f"configure checkpoint save {checkpoint}"
            gold_config = [checkpoint_cmd]
            dut['connection'].enable(gold_config)
            dut['connection'].config(config)


def perform_setup(duts, test, setup_config):
    """ Creates checkpoints and then runs setup on duts """

    date_obj = datetime.datetime.now()
    gold_config_date = date_obj.strftime("%y%m%d%H%M")
    checkpoint = f"{test}_{gold_config_date}"
    logging.info(f"{test} : {setup_config}")
    dev_ids = setup_config.get("key", "name")

    if dev_ids == 'name':
        setup_via_name(duts=duts, setup_config=setup_config, checkpoint=checkpoint)

    elif dev_ids == 'role':
        setup_via_role(duts=duts, setup_config=setup_config, checkpoint=checkpoint)

    return checkpoint


def teardown_via_name(duts, setup_config, checkpoint_restore_cmd, delete_checkpoint_cmd):
    """ Restores the checkpoints on duts identified by their name """

    for dev_name in setup_config:
        dut = duts.get(dev_name, None)
        if dut is None:
            continue
        restore_config = [checkpoint_restore_cmd, delete_checkpoint_cmd]
        dut['connection'].config(restore_config)
        

def teardown_via_role(duts, setup_config, checkpoint_restore_cmd, delete_checkpoint_cmd):
    """ Restores the checkpoints on duts identified by their role """

    for role in setup_config:
        for _, dut in duts.items():
            if dut['role'] != role:
                #add logging
                continue
            restore_config = [checkpoint_restore_cmd, delete_checkpoint_cmd]
            dut['connection'].config(restore_config)


def perform_teardown(duts, checkpoint, setup_config):
    """ Restore and delete checkpoint """
    if checkpoint == "":
        return

    checkpoint_restore_cmd = f"configure replace checkpoint:{checkpoint} skip-checkpoint"
    delete_checkpoint_cmd = f"delete checkpoint:{checkpoint}"
    dev_ids = setup_config.get("key", "name")

    if dev_ids == 'name':
        teardown_via_name(duts=duts, setup_config=setup_config, checkpoint_restore_cmd=checkpoint_restore_cmd, delete_checkpoint_cmd=delete_checkpoint_cmd)
    
    elif dev_ids == 'role':
        teardown_via_role(duts=duts, setup_config=setup_config, checkpoint_restore_cmd=checkpoint_restore_cmd, delete_checkpoint_cmd=delete_checkpoint_cmd)


@pytest.fixture(autouse=True, scope="class")
def setup_testsuite(request, duts):
    """ Setup the duts using the test suite(class) setup file """

    testsuit = get_current_fixture_testclass(request)
    test_suites = test_defs['test_suites']
    setup_config = []
    checkpoint = ""
    for s in test_suites:
        if s['name'] == testsuit:
            setup_config_file = s.get('test_setup', "")
            if setup_config_file != "":
                setup_config = tests_tools.setup_import_yaml(f"{s['dir_path']}/{setup_config_file}")
                checkpoint = perform_setup(duts, testsuit, setup_config)
    yield
    perform_teardown(duts, checkpoint, setup_config)

@pytest.fixture(autouse=True, scope="function")
def setup_testcase(request, duts):
    """ Setup the duts using the test case(function) setup file """

    testname = get_current_fixture_testname(request)
    test_suites = test_defs['test_suites']
    setup_config = []
    checkpoint = ""
    for s in test_suites:
        tests = s['testcases']
        for t in tests:
            if t['name'] == testname:
                setup_config_file = t.get('test_setup', "")
                if setup_config_file != "":
                    setup_config = tests_tools.setup_import_yaml(f"{s['dir_path']}/{setup_config_file}")
                    checkpoint = perform_setup(duts, testname, setup_config)

    yield
    perform_teardown(duts, checkpoint, setup_config)
