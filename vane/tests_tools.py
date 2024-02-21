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
# pylint: disable=too-many-lines

"""Utilities for using PyTest in network testing"""

import copy
import concurrent.futures
import sys
import os
import time
import inspect
import re
import pprint
import yaml


from jinja2 import Template
from icmplib import ping
from icmplib.exceptions import SocketPermissionError
from pyeapi.eapilib import EapiError, ConnectionError  # pylint: disable=W0622
from netmiko.exceptions import NetmikoAuthenticationException
from ixnetwork_restpy.assistants.statistics.statviewassistant import StatViewAssistant
from vane import config, device_interface, ixia_interface
from vane.vane_logging import logging
from vane.utils import render_cmds


DEFAULT_EOS_CONN = "eapi"


def filter_duts(duts, criteria="", dut_filter=""):
    """Filter duts based on a user provided criteria and a filter

    Args:
        duts (dict): Full global duts dictionary
        criteria (str, optional): Type of filtering required.  Valid options
        are: name, role, regex, or names. Defaults to "".
        dut_filter (str, optional): Filter for DUTs. Defaults to "".

    Returns:
        subset_duts (list(dict)), dut_names (list(str)): Filtered subset of
        global dictionary of duts and dut names
    """
    logging.info(f"Filter: {dut_filter} by criteria: {criteria}")

    subset_duts, dut_names = [], []
    if criteria == "roles":
        for role in dut_filter:
            subset_duts = subset_duts + [dut for dut in duts if role == dut["role"]]
            dut_names = dut_names + [dut["name"] for dut in duts if role == dut["role"]]
    elif criteria == "names":
        for name in dut_filter:
            subset_duts = subset_duts + [dut for dut in duts if name == dut["name"]]
            dut_names = dut_names + [dut["name"] for dut in duts if name == dut["name"]]
    elif criteria == "regex":
        subset_duts = [dut for dut in duts if re.match(dut_filter, dut["name"])]
        dut_names = [dut["name"] for dut in duts if re.match(dut_filter, dut["name"])]
    else:
        subset_duts = duts
        dut_names = [dut["name"] for dut in duts]

    return subset_duts, dut_names


def parametrize_duts(test_fname, test_defs, dut_objs):
    """Use a filter to create input variables for PyTest parametrize

    Args:
        test_fname (str): Test suite path and file name
        test_defs (dict): Dictionary with global test definitions
        dut_objs (dict): Full global dictionary duts dictionary

    Returns:
        dut_parameters (dict): Dictionary with variables PyTest parametrize for each test case.
    """
    logging.info("Discover test suite name")

    testsuite = test_fname.split("/")[-1]

    logging.info(f"Filtering test definitions by test suite name: {testsuite}")

    subset_def = [defs for defs in test_defs["test_suites"] if testsuite == defs["name"]]
    testcases = subset_def[0]["testcases"]

    logging.info("Unpack testcases by defining dut and criteria")

    dut_parameters = {}

    for testcase in testcases:
        if "name" in testcase:
            testname = testcase["name"]
            criteria = ""
            dut_filter = ""

            if "criteria" in testcase:
                criteria = testcase["criteria"]
            if "filter" in testcase:
                dut_filter = testcase["filter"]

            duts, ids = filter_duts(dut_objs, criteria, dut_filter)

            logging.debug(f"Creating dut parameters.  \nDuts: {duts} \nIds: {ids}")

            dut_parameters[testname] = {}
            dut_parameters[testname]["duts"] = duts
            dut_parameters[testname]["ids"] = ids

    return dut_parameters


def import_yaml(yaml_file):
    """Import YAML file as python data structure

    Args:
        yaml_file (str): Name of YAML file

    Returns:
        yaml_data (dict): Dictionary containing yaml data
    """
    logging.info(f"Opening {yaml_file} for read")

    try:
        yaml_data = yaml_read(yaml_file)
        if yaml_data is None:
            yaml_data = {}
        return yaml_data
    except OSError as err:
        print(f">>> {yaml_file} YAML FILE MISSING")
        logging.error(f"ERROR YAML FILE: {yaml_file} NOT " + f"FOUND. {err}")
        logging.error("EXITING TEST RUNNER")
        sys.exit(1)


def yaml_read(yaml_file):
    """Return a yaml data read from the yaml file

    Args:
        yaml_file (file): Input yaml file to be read

    Returns:
        yaml_data (dict):Yaml data read from the file
    """
    with open(yaml_file, "r", encoding="utf-8") as input_yaml:
        try:
            yaml_data = yaml.safe_load(input_yaml)
            logging.debug(f"Inputted the following yaml: {yaml_data}")
            return yaml_data
        except yaml.YAMLError as err:
            print(">>> ERROR IN YAML FILE")
            logging.error(f"ERROR IN YAML FILE: {err}")
            logging.error("EXITING TEST RUNNER")
            sys.exit(1)


def init_duts(show_cmds, test_parameters, test_duts):
    """Use PS LLD spreadsheet to find interesting duts and then execute
    inputted show commands on each dut.  Return structured data of
    dut's output data, hostname, and connection.  Using threading to
    make method more efficient.

    Args:
      show_cmds (str): list of interesting show commands
      test_parameters (dict): Abstraction of testing parameters
      test_duts (dict): Dictionary of duts

    Returns:
      duts (dict): structured data of duts output data, hostname, and
                   connection
    """
    logging.info(
        "Find DUTs and then execute inputted show commands "
        "on each dut. Return structured data of DUTs output "
        "data, hostname, and connection."
    )

    reachability, reachable_duts, unreachable_duts = check_duts_reachability(test_duts)

    try:
        continue_when_unreachable = test_parameters["parameters"]["continue_when_unreachable"]
    except KeyError:
        continue_when_unreachable = False

    if not (reachability or continue_when_unreachable):
        logging.error(
            f"Error connecting to {unreachable_duts}, not reachable via ping, hence exiting Vane"
        )
        unreachable_ips = [unreachable_dut["mgmt_ip"] for unreachable_dut in unreachable_duts]
        print(
            "\x1b[31mVane encountered an error while attempting to connect to DUT/s with ip's:\n"
            f"{unreachable_ips}\n"
            "For detailed information, please refer to the logs.\nDue to this issue, "
            "Vane is exiting. \x1b[31m"
        )
        sys.exit(1)

    reachable_duts, additional_unreachable_duts = login_duts(test_parameters, reachable_duts)
    unreachable_duts.extend(additional_unreachable_duts)
    workers = len(reachable_duts)

    logging.debug(f"Duts login info: {reachable_duts} and create {workers} workers")
    logging.debug(f"Passing the following show commands to workers: {show_cmds}")

    logging.info("Starting the execution of show commands for Vane cache")

    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        future_object = {
            executor.submit(dut_worker, dut, show_cmds, reachable_duts): dut
            for dut in reachable_duts
        }

    if future_object:
        logging.debug("Future object generated successfully")

    logging.info("Returning duts data structure")
    logging.debug(f"Return duts data structure: {reachable_duts}")
    logging.debug(f"Return unreachable duts data structure: {unreachable_duts}")

    return reachable_duts, unreachable_duts


def check_duts_reachability(test_duts):
    """Check if duts are reachable

    Args:
        test_duts (dict): Dictionary of duts

    Returns:
        reachability (boolean): result of if duts are reachable
        reachable_duts (dict): reachable duts
        unreachable_duts (dict): unreachable duts
    """

    logging.info("Checking connectivity of duts")
    reachable_duts = []
    unreachable_duts = []
    ret = False
    for dut in test_duts["duts"]:
        # check for reachability
        ip_address = dut["mgmt_ip"]
        try:
            host = ping(ip_address, count=3, interval=1, timeout=3, privileged=False)
            ret = host.is_alive
        except SocketPermissionError as e:
            logging.error(
                f"Entered the exception due to permission issues: {e}\n"
                "Trying the ping utility via os.system instead"
            )
            host = os.system(f"ping -c 1 -W 3 {ip_address} > {os.devnull}")
            ret = host == 0

        if ret:
            reachable_duts.append(dut)
        else:
            name = dut["name"]
            logging.info(f"Failed to connect to {name}")
            unreachable_duts.append(dut)

    if len(test_duts["duts"]) == len(reachable_duts):
        return True, reachable_duts, unreachable_duts

    return False, reachable_duts, unreachable_duts


def login_duts(test_parameters, duts):
    """Use eapi to connect to Arista switches for testing

    Args:
      test_parameters (dict): Abstraction of testing parameters
      test_duts (dict): Dictionary of duts

    Returns:
      reachable_duts (list): List of dictionaries with connection and name
                     of DUTs which can be reached
      unreachable_duts (list): List of dictionaries with connection and name
                     of DUTs which cannot be reached (due to bad authentication)
    """
    logging.info("Using eapi/ssh to connect to Arista switches for testing")

    reachable_duts = []
    unreachable_duts = []

    network_configs = {}
    if "network_configs" in test_parameters["parameters"]:
        if test_parameters["parameters"]["network_configs"]:
            network_configs = import_yaml(test_parameters["parameters"]["network_configs"])

    for dut in duts:
        name = dut["name"]
        login_index = len(reachable_duts)
        reachable_duts.append({})
        login_ptr = reachable_duts[login_index]

        logging.info(f"Connecting to switch: {name}")

        logging.debug(f"Connecting to switch: {name} using parameters: {dut}")

        eos_conn = test_parameters["parameters"].get("eos_conn", DEFAULT_EOS_CONN)

        if eos_conn == "eapi":
            pyeapi_conn = device_interface.PyeapiConn()
            login_ptr["eapi_conn"] = pyeapi_conn
            login_ptr["connection"] = pyeapi_conn
        elif eos_conn == "ssh":
            netmiko_conn = device_interface.NetmikoConn()
            login_ptr["ssh_conn"] = netmiko_conn
            login_ptr["connection"] = netmiko_conn
        else:
            raise ValueError(f"Invalid EOS conn type {eos_conn} specified")

        success = authenticate_and_setup_conn(dut, login_ptr["connection"])
        if not success:
            reachable_duts.pop(login_index)
            unreachable_duts.append(dut)
            continue

        login_ptr["name"] = name
        login_ptr["mgmt_ip"] = dut["mgmt_ip"]
        login_ptr["username"] = dut["username"]
        login_ptr["password"] = dut["password"]
        login_ptr["role"] = dut["role"]
        login_ptr["neighbors"] = dut["neighbors"]
        login_ptr["transport"] = dut["transport"]
        login_ptr["results_dir"] = test_parameters["parameters"]["results_dir"]
        login_ptr["report_dir"] = test_parameters["parameters"]["report_dir"]

        if name in network_configs:
            login_ptr["network_configs"] = network_configs[name]

    logging.debug(f"Returning reachable_duts: {reachable_duts}")

    return reachable_duts, unreachable_duts


def send_cmds(show_cmds, conn, encoding):
    """Send show commands to duts and recurse on failure

    Args:
        show_cmds (list): List of pre-processed commands
        conn (obj): connection
        encoding (string): encoding type of show commands: either json or text

    Returns:
        show_cmd_list (list): list of show commands
    """

    try:
        logging.debug(f"List of show commands in show_cmds with encoding {encoding}: {show_cmds}")

        if encoding == "json":
            show_cmd_list = conn.run_commands(show_cmds)
        elif encoding == "text":
            show_cmd_list = conn.run_commands(show_cmds, encoding="text")

        logging.info("Ran all show commands on dut")
        logging.debug(f"Ran all show cmds with encoding {encoding}: {show_cmds}")

    # pylint: disable-next=broad-exception-caught
    except Exception as err:
        logging.error(f"Error running all cmds: {err}")

        show_cmds = remove_cmd(err, show_cmds)

        logging.debug(f"New show_cmds: {show_cmds}")

        show_cmd_list = send_cmds(show_cmds, conn, encoding)
        show_cmd_list = show_cmd_list[0]

    logging.debug(f"Return all show cmds: {show_cmd_list}")

    return show_cmd_list, show_cmds


def remove_cmd(err, show_cmds):
    """Remove command that is not supported by pyeapi

    Args:
        err (str): Error string
        show_cmds (list): List of pre-processed commands

    Returns:
        show_cmds (list): List of post-processed commands
    """
    logging.debug(f"remove_cmd: {err}")
    logging.debug(f"remove_cmd show_cmds list: {show_cmds}")

    longest_matching_cmd = ""

    for show_cmd in show_cmds:
        if show_cmd in str(err) and longest_matching_cmd in show_cmd:
            longest_matching_cmd = show_cmd

    # longest_matching_cmd is the one in error string, lets bump it out
    if longest_matching_cmd:
        cmd_index = show_cmds.index(longest_matching_cmd)
        show_cmds.pop(cmd_index)

        logging.info(f"Removed {longest_matching_cmd} due to an error")
        logging.debug(f"Removed {longest_matching_cmd} because of {err}")

    return show_cmds


def dut_worker(dut, show_cmds, reachable_duts):
    """Execute inputted show commands on dut.  Update dut structured data
    with show output.

    Args:
      dut (dict): structured data of a dut output data, hostname, and
      show_cmds (list): List of show commands
      reachable_duts (dict): Abstraction of duts
    """
    name = dut["name"]
    conn = dut["connection"]
    dut["output"] = {}
    dut["output"]["interface_list"] = return_interfaces(name, reachable_duts)

    logging.info(f"Executing show commands on {name}")
    logging.debug(f"List of show commands {show_cmds}")

    all_cmds_json = show_cmds.copy()
    show_cmd_json_list, show_cmds_json = send_cmds(all_cmds_json, conn, "json")

    logging.debug(f"Returned from send_cmds_json {show_cmds_json}")

    all_cmds_txt = show_cmds.copy()
    show_cmd_txt_list, show_cmds_txt = send_cmds(all_cmds_txt, conn, "text")

    logging.debug(f"Returned from send_cmds_txt {show_cmds_txt}")

    for show_cmd in show_cmds:
        function_def = f'test_{("_").join(show_cmd.split())}'

        logging.debug(f"Executing show command: {show_cmd} for test {function_def}")
        logging.debug(f"Adding output of {show_cmd} to duts data structure")

        dut["output"][show_cmd] = {}

        if show_cmd in show_cmds_json:
            cmd_index = show_cmds_json.index(show_cmd)

            logging.debug(f"Found cmd: {show_cmd} at index {cmd_index} of {show_cmds_json}")
            logging.debug(
                f"length of cmds: {len(show_cmds_json)} vs length of "
                f"output {len(show_cmd_json_list)}"
            )

            show_output = show_cmd_json_list[cmd_index]
            dut["output"][show_cmd]["json"] = show_output

            logging.debug(f"Adding cmd {show_cmd} to dut and data {show_output}")
        else:
            dut["output"][show_cmd]["json"] = ""

            logging.debug(f"No json output for {show_cmd}")

        if show_cmd in show_cmds_txt:
            cmd_index = show_cmds_txt.index(show_cmd)

            logging.debug(f"Found cmd: {show_cmd} at index {cmd_index} of {show_cmds_txt}")
            logging.debug(
                f"length of cmds: {len(show_cmds_txt)} vs length of "
                f"output {len(show_cmd_txt_list)}"
            )

            show_output_txt = show_cmd_txt_list[cmd_index]["output"]
            dut["output"][show_cmd]["text"] = show_output_txt

            logging.debug(f"Adding cmd {show_cmd} to dut and data {show_output_txt}")

        else:
            dut["output"][show_cmd]["text"] = ""

            logging.debug(f"No text output for {show_cmd}")

    logging.info(f"{name} updated with show output {dut}")


def return_interfaces(hostname, reachable_duts):
    """Parse reachable_duts for interface connections and return them to test

    Args:
        hostname (str):  hostname of dut
        reachable_duts (dict): Abstraction of reachable_duts

    Returns:
      interface_list (list): list of interesting interfaces based on
                             PS LLD spreadsheet
    """
    logging.info("Parse reachable_duts for interface connections and return them to test")

    interface_list = []
    duts = reachable_duts

    for dut in duts:
        dut_name = dut["name"]

        if dut_name == hostname:
            logging.info(f"Discovering interface parameters for: {hostname}")

            neighbors = dut["neighbors"]

            for neighbor in neighbors:
                interface = {}

                logging.debug(f"Adding interface parameters: {neighbor} neighbor for: {dut_name}")

                interface["hostname"] = dut_name
                interface["interface_name"] = neighbor["port"]
                interface["z_hostname"] = neighbor["neighborDevice"]
                interface["z_interface_name"] = neighbor["neighborPort"]
                interface["media_type"] = ""
                interface_list.append(interface)

    logging.info("Returning interface list.")
    logging.debug(f"Returning interface list: {interface_list}")

    return interface_list


def get_parameters(tests_parameters, test_suite, test_case=""):
    """Return test parameters for a test case

    Args:
        test_parameters (dict): Abstraction of testing parameters
        test_suite (str): test suite of the test case

    Returns:
        case_parameters: test parameters for a test case
    """
    if not test_case:
        test_case = inspect.stack()[1][3]

        logging.info(f"Setting testcase name to {test_case}")

    logging.info("Identify test case and return parameters")

    test_suite = test_suite.split("/")[-1]

    logging.info(f"Return testcases for Test Suite: {test_suite}")

    suite_parameters = [
        param for param in tests_parameters["test_suites"] if param["name"] == test_suite
    ]

    logging.debug(f"Suite_parameters: {suite_parameters}")

    logging.info(f"Return parameters for Test Case: {test_case}")

    case_parameters = [
        param for param in suite_parameters[0]["testcases"] if param["name"] == test_case
    ]

    logging.debug(f"Case_parameters: {case_parameters[0]}")

    case_parameters[0]["test_suite"] = test_suite

    return case_parameters[0]


def verify_show_cmd(show_cmd, dut):
    """Verify if show command was successfully executed on dut

    Args:
        show_cmd (str): show command
        dut (dict): data structure of dut parameters
    """

    dut_name = dut["name"]

    logging.info(
        f"Verifying if show command {show_cmd} was successfully executed on {dut_name} dut"
    )

    if show_cmd in dut["output"]:
        logging.debug(f"Verified output for show command {show_cmd} on {dut_name}")
    else:
        logging.critical(f"Show command {show_cmd} not executed on {dut_name}")

        assert False


def verify_tacacs(dut):
    """Verify if tacacs servers are configured

    Args:
        dut (dict): data structure of dut parameters

    Returns:
        tacacs_bool (bool): boolean representing if tacacs server(s) are configured or not
    """
    dut_name = dut["name"]
    show_cmd = "show tacacs"
    tacacs_bool = True
    tacacs = dut["output"][show_cmd]["json"]["tacacsServers"]
    tacacs_servers = len(tacacs)

    logging.info(f"Verifying if tacacs server(s) are configured on {dut_name} dut")

    if tacacs_servers == 0:
        tacacs_bool = False

    logging.debug(f"{tacacs_servers} tacacs servers are configured so returning {tacacs_bool}")

    return tacacs_bool


def verify_veos(dut):
    """Verify if DUT is a VEOS instance

    Args:
        dut (dict): data structure of dut parameters

    Returns:
        veos_bool (bool): boolean representing if the dut is a VEOS instance or not.
    """
    dut_name = dut["name"]
    show_cmd = "show version"
    veos_bool = False
    veos = dut["output"][show_cmd]["json"]["modelName"]

    logging.info(f"Verifying if {dut_name} DUT is a VEOS instance. Model is {veos}")

    if "vEOS" in veos:
        veos_bool = True

        logging.debug(f"{dut_name} is a VEOS instance so returning {veos_bool}")
    else:
        logging.debug(f"{dut_name} is not a VEOS instance so returning {veos_bool}")

    return veos_bool


def return_show_cmds(test_parameters):
    """Return show commands from the test_definitions

    Args:
        test_parameters (dict): Abstraction of testing parameters

    Returns:
        show_cmds (list): show commands from the test_definitions
    """
    try:
        show_clock_flag = config.test_parameters["parameters"]["show_clock"]
    except KeyError:
        show_clock_flag = False

    show_cmds = ["show version"]

    if show_clock_flag:
        show_cmds.append("show clock")

    logging.debug(f"Discover the names of test suites from {test_parameters}")

    test_data = test_parameters["test_suites"]
    test_suites = [param["name"] for param in test_data]

    for test_suite in test_suites:
        test_index = test_suites.index(test_suite)
        test_cases = test_data[test_index]["testcases"]

        logging.info(f"Finding show commands in test suite: {test_suite}")

        for test_case in test_cases:
            show_cmd = test_case.get("show_cmd", "")
            if show_cmd:
                logging.debug(f"Found show command {show_cmd}")

                if show_cmd not in show_cmds:
                    logging.debug(f"Adding Show command {show_cmd}")

                    show_cmds.append(show_cmd)
            else:
                test_show_cmds = test_case.get("show_cmds", [])
                logging.debug(f"Found show commands {test_show_cmds}")

                for show_cmd in (
                    show_cmd for show_cmd in test_show_cmds if show_cmd not in show_cmds
                ):
                    logging.debug(f"Adding Show commands {show_cmd}")

                    show_cmds.append(show_cmd)

    logging.info(f"The following show commands are required for test cases: {show_cmds}")

    return show_cmds


def return_test_defs(test_parameters):
    """Return test_definitions from the test_parameters

    Args:
        test_parameters (dict): Abstraction of testing parameters

    Returns:
        test_defs (dict): test definitions
    """
    test_defs = {"test_suites": []}
    test_dirs = test_parameters["parameters"]["test_dirs"]
    report_dir = test_parameters["parameters"]["report_dir"]
    test_definitions_file = test_parameters["parameters"]["test_definitions"]

    for test_directory in test_dirs:
        tests_info = os.walk(test_directory)
        for dir_path, _, file_names in tests_info:
            for file_name in file_names:
                if file_name == test_definitions_file:
                    file_path = f"{dir_path}/{file_name}"
                    test_def = import_yaml(file_path)
                    for test_suite in test_def:
                        test_suite["dir_path"] = f"{dir_path}"
                        import_config(dir_path, test_suite)
                    test_defs["test_suites"] += test_def

    logging.info(f"Creating {report_dir} reports directory")
    os.makedirs(report_dir, exist_ok=True)
    export_yaml(report_dir + "/" + test_definitions_file, test_defs)

    logging.debug(f"Return the following test definitions data structure {test_defs}")

    return test_defs


def import_config(dir_path, test_suite):
    """Check for setup file.  If setup file exists import configuration for reporting

    Args:
        dir_path (str): Path to test case directory
        test_suite (dict): Test case definition parameters
    """

    for testcase in test_suite["testcases"]:
        if "test_setup" in testcase:
            setup_file = f"{dir_path}/{testcase['test_setup']}"
            logging.info(
                f"Importing setup file: {setup_file} into test case: {testcase['name']} definition"
            )

            setup_config = import_yaml(setup_file)
            logging.debug(f"Configuration setup is {setup_config}")

            dev_ids = setup_config.get("key", "name")
            logging.debug(f"Imported configuration will uses {dev_ids}")

            if dev_ids == "name":
                import_config_from_name(setup_config, testcase)
            elif dev_ids == "role":
                import_config_from_role(setup_config, testcase)


def import_config_from_name(setup_config, testcase):
    """Import configuration from a device name

    Args:
        setup_config (dict): Setup file data structure
        testcase (dict): test case defintions data structure
    """

    testcase["configuration"] = ""
    for dev_name in setup_config:
        if dev_name == "key":
            continue
        testcase["configuration"] += f"{dev_name}:\n"
        setup_schema = setup_config[dev_name]["schema"]

        if setup_schema is None:
            testcase["configuration"] += f"{setup_config[dev_name]['template']}\n"
        else:
            setup_template = Template(setup_config[dev_name]["template"])
            formatted_config = setup_template.render(setup_schema)
            testcase["configuration"] += f"{formatted_config}\n"

        logging.debug(f"Updated test case data structure with setup: {testcase['configuration']}")


def import_config_from_role(setup_config, testcase):
    """Import configuration from a device role

    Args:
        setup_config (dict): Setup file data structure
        testcase (dict): test case defintions data structure
    """

    testcase["configuration"] = ""
    for role_name in setup_config:
        if role_name != "key":
            logging.debug(f"Setting role to: {role_name}")
            dev_names = return_duts_with_role(role_name)

            for dev_name in dev_names:
                testcase["configuration"] += f"{dev_name}:\n"
                setup_schema = setup_config[role_name]["schema"]

                if setup_schema is None:
                    testcase["configuration"] += f"{setup_config[role_name]['template']}\n"
                else:
                    setup_template = Template(setup_config[role_name]["template"])
                    formatted_config = setup_template.render(setup_schema)
                    testcase["configuration"] += f"{formatted_config}\n"

                logging.debug(
                    f"Updated test case data structure with setup: {testcase['configuration']}"
                )


def return_duts_with_role(role_name):
    """Create a list of duts with a role

    Args:
        role_name (str): Role to match in duts data structure

    Returns:
        list: Hostnames of DUTs with role
    """

    dev_names = []
    for dut in config.test_duts["duts"]:
        dut_role = dut.get("role", "")
        if dut_role == role_name:
            dev_names.append(dut["name"])

    logging.debug(f"The following DUTs: {dev_names} have role: {role_name}")

    return dev_names


def export_yaml(yaml_file, yaml_data):
    """Export python data structure as a YAML file

    Args:
        yaml_file (str): Name of YAML file
        yaml_data (dict): Data to be written to yaml file
    """
    logging.info(f"Opening {yaml_file} for write")

    try:
        with open(yaml_file, "w", encoding="utf-8") as yaml_out:
            try:
                logging.debug(f"Output the following yaml: {yaml_data}")

                yaml.dump(yaml_data, yaml_out, default_flow_style=False)
            except yaml.YAMLError as err:
                print(">>> ERROR IN YAML FILE")
                logging.error(f"ERROR IN YAML FILE: {err}")
                logging.error("EXITING TEST RUNNER")
                sys.exit(1)
    except OSError as err:
        print(f">>> {yaml_file} YAML FILE MISSING")
        logging.error(f"ERROR YAML FILE: {yaml_file} NOT " + f"FOUND. {err}")
        logging.error("EXITING TEST RUNNER")
        sys.exit(1)


def export_text(text_file, text_data, dut_name):
    """Export python data structure as a TEXT file

    Args:
        text_file (str): Name of TEXT file
        text_data (dict): output of show command in python dictionary
        dut_name (str): Primary dut name
    """
    logging.info(f"Opening {text_file} for write")

    # to create the sub-directory if it does not exist
    os.makedirs(os.path.dirname(text_file), exist_ok=True)

    try:
        with open(text_file, "a", encoding="utf-8") as text_out:
            logging.debug(f"Output the following text file: {text_data}")
            divider = "================================================================"
            heading = (
                f"{divider}\nThese commands were run when PRIMARY DUT was {dut_name}\n{divider}\n\n"
            )
            text_out.write(heading)
            for key, value in text_data.items():
                text_out.write(f"{key}{value}\n")
    except OSError as err:
        print(f">>> {text_file} TEXT FILE MISSING")
        logging.error(f"ERROR TEXT FILE: {text_file} NOT FOUND. {err}")
        logging.error("EXITING TEST RUNNER")
        sys.exit(1)


def generate_duts_file(dut, file, username, password):
    """Util function to take in an individual dut and print
    its relevant data to a given file.

    Args:
        dut (dict): device structure
        file (io): file to write duts data to
        username, password (str): user credentials
    """
    dut_dict = {}
    try:
        for data in dut:
            if dut[data]["node_type"] == "veos":
                dut_dict = [
                    {
                        "mgmt_ip": dut[data]["ip_addr"],
                        "name": data,
                        "neighbors": dut[data]["neighbors"],
                        "password": password,
                        "transport": "https",
                        "username": username,
                        "role": "",
                    }
                ]
        if dut_dict:
            yaml.dump(dut_dict, file)
    except yaml.YAMLError as err:
        print(f"DUTs creation for {file} failed due to exception {err}")


def create_duts_file(topology_file, inventory_file):
    """Automatically generate a DUTs file

    Args:
        topology_file (str): Name and path of topology file
        inventory_file (str): Name and path of inventory file

    Returns:
        dict: duts data structure
    """
    dut_file = {}
    dut_properties = []
    server_properties = []
    topology_file = import_yaml(topology_file)
    inventory_file = import_yaml(inventory_file)

    try:
        if not topology_file.get("nodes", None):
            inventory_file, topology_file = topology_file, inventory_file
        for node in topology_file["nodes"]:
            name, topology_details = list(node.items())[0]
            if "cvp" in name:
                continue
            if name in inventory_file["all"]["children"]["VEOS"]["hosts"]:
                inventory_details = inventory_file["all"]["children"]["VEOS"]["hosts"][name]
                dut_properties.append(
                    {
                        "mgmt_ip": inventory_details["ansible_host"],
                        "name": name,
                        "neighbors": topology_details["neighbors"],
                        "password": inventory_details["ansible_ssh_pass"],
                        "transport": "https",
                        "username": inventory_details["ansible_user"],
                        "role": topology_details.get("role", "unknown"),
                    }
                )
            elif name in inventory_file["all"]["children"]["GENERIC"]["hosts"]:
                inventory_details = inventory_file["all"]["children"]["GENERIC"]["hosts"][name]
                server_properties.append(
                    {
                        "mgmt_ip": inventory_details["ansible_host"],
                        "name": name,
                        "neighbors": topology_details["neighbors"],
                        "password": inventory_details["ansible_ssh_pass"],
                        "transport": "https",
                        "username": inventory_details["ansible_user"],
                        "role": topology_details.get("role", "unknown"),
                    }
                )
            else:
                continue
        if dut_properties or server_properties:
            dut_file.update({"duts": dut_properties, "servers": server_properties})
            with open(config.DUTS_FILE, "w", encoding="utf-8") as yamlfile:
                yaml.dump(dut_file, yamlfile, sort_keys=False)

                return config.DUTS_FILE

    # pylint: disable-next=broad-exception-caught
    except Exception as excep:
        logging.error(f"Error occurred while creating DUTs file: {str(excep)}")
        logging.error("EXITING TEST RUNNER")
        print(">>> ERROR While creating duts file")
        sys.exit(1)

    return None


def authenticate_and_setup_conn(dut, conn_object):
    """Method to setup and authenticate setting up
    PyEapi or Netmiko connection based on conn object passed

    Args:
        dut (dict): device data
        conn_object (pyeapi/netmiko): type of connection
    """

    try:
        conn_object.set_up_conn(dut)
    except (ConnectionError, NetmikoAuthenticationException) as err:
        continue_when_unreachable = config.test_parameters["parameters"][
            "continue_when_unreachable"
        ]
        if not continue_when_unreachable:
            dut_name = dut["name"]
            print(
                "\x1b[31mExiting Vane.\n"
                f"Error running all cmds on dut {dut_name} due to failed authentication.\n{err}\n"
                "\x1b[0m"
            )
            logging.error(
                "Exiting Vane: "
                f"Error running all cmds on dut {dut_name} due to failed authentication. {err}\n"
            )
            sys.exit(1)
        else:
            return False

    return True


# pylint: disable-next=too-many-instance-attributes
class TestOps:
    """Common testcase operations and variables"""

    def __init__(self, tests_definitions, test_suite, dut):
        """Initializes TestOps Object

        Args:
            tests_definition (str): YAML representation of NRFU tests
            test_suite (str): name of test suite
            dut (dict): device under test
        """
        test_case = inspect.stack()[1][3]
        # Test cases that skip will change skip to True
        self.skip = False
        self.test_case = test_case
        self.test_parameters = self._get_parameters(tests_definitions, test_suite, self.test_case)
        self.expected_output = self.test_parameters["expected_output"]
        self.dut = dut
        self.dut_name = self.dut["name"]
        self.interface_list = self.dut["output"]["interface_list"]
        self.results_dir = self.dut["results_dir"]
        self.report_dir = self.dut["report_dir"]

        parameters = config.test_parameters

        try:
            self.show_clock_flag = parameters["parameters"]["show_clock"]
        except KeyError:
            self.show_clock_flag = False

        self.show_cmds = {self.dut_name: []}
        self._show_cmds = {self.dut_name: []}

        if self.show_clock_flag:
            self._show_cmds[self.dut_name].append("show clock")

        # add 'show version' to _show_cmds
        self._show_cmds[self.dut_name].append("show version")

        self.show_output = ""
        self.show_cmd = ""
        self.test_steps = []
        try:
            self.show_cmd = self.test_parameters["show_cmd"]
            if self.show_cmd:
                self.show_cmds[self.dut_name].append(self.show_cmd)
                self._show_cmds[self.dut_name].append(self.show_cmd)
        except KeyError:
            self.show_cmds[self.dut_name].extend(self.test_parameters["show_cmds"])
            self._show_cmds[self.dut_name].extend(self.test_parameters["show_cmds"])

        self.show_cmd_txts = {self.dut_name: []}
        self.show_cmd_txt = ""
        self._show_cmd_txts = {self.dut_name: []}

        if len(self._show_cmds[self.dut_name]) > 0 and self.dut:
            self._verify_show_cmd(self._show_cmds[self.dut_name], self.dut)
            if self.show_cmd:
                self.show_cmd_txt = self.dut["output"][self.show_cmd]["text"]
            for show_cmd in self.show_cmds[self.dut_name]:
                self.show_cmd_txts[self.dut_name].append(self.dut["output"][show_cmd]["text"])
            for show_cmd in self._show_cmds[self.dut_name]:
                self._show_cmd_txts[self.dut_name].append(self.dut["output"][show_cmd]["text"])

        self.comment = ""
        self.output_msg = ""
        self.actual_results = []
        self.expected_results = []
        self.actual_output = ""
        self.test_result = False
        self.test_id = self.test_parameters.get("test_id", None)

    def _verify_show_cmd(self, show_cmds, dut):
        """Verify if show command was successfully executed on dut

        Args:
            show_cmds (str): show command
            dut (dict): data structure of dut parameters
        """
        dut_name = dut["name"]

        logging.info(
            f"Verifying if show command {show_cmds} were successfully executed on {dut_name} dut"
        )

        for show_cmd in show_cmds:
            if show_cmd and show_cmd in dut["output"]:
                logging.debug(f"Verified output for show command {show_cmd} on {dut_name}")
            else:
                logging.critical(f"Show command {show_cmd} not executed on {dut_name}")

                assert False

    def _write_results(self):
        """Write the yaml output to a text file"""
        logging.info("Preparing to write results")

        test_suite = self.test_parameters["test_suite"]
        test_suite = test_suite.split("/")[-1]
        dut_name = self.test_parameters["dut"]
        test_case = self.test_parameters["name"]
        results_dir = self.results_dir
        yaml_file = f"{results_dir}/result-{test_case}-{dut_name}.yml"

        logging.debug(f"Creating results file named {yaml_file}")

        yaml_data = self.test_parameters
        export_yaml(yaml_file, yaml_data)

    def _write_text_results(self):
        """Write the text output of show command to a text file"""

        self._write_evidence(self._show_cmds, self._show_cmd_txts, "Verification")

    def _write_evidence(self, cmds, cmds_outputs, file_substring):
        """Write the cmds and their outputs to the file"""

        report_dir = self.report_dir
        test_id = self.test_parameters["test_id"]
        test_case = self.test_parameters["name"]

        # write evidence for cmds if any
        for dut_name, dut_cmds in cmds.items():
            text_file = (
                f"{report_dir}/TEST RESULTS/{test_id} {test_case}/"
                f"{test_id} {dut_name} {file_substring}.txt"
            )
            text_data = {}
            index = 1

            for command, text in zip(dut_cmds, cmds_outputs[dut_name]):
                text_data[str(index) + ". " + dut_name + "# " + command] = "\n\n" + text
                index += 1

            if text_data:
                export_text(text_file, text_data, self.dut_name)
            else:
                logging.debug(
                    f"No cfg command output to display for test id {test_id} test case {test_case}"
                )

    def _get_parameters(self, tests_parameters, test_suite, test_case):
        """Return test parameters for a test case

        Args:
            tests_parameters (dict): Abstraction of testing parameters
            test_suite (str): name of the test suite
            test_case (str): name of the test case

        Returns:
            case_parameters: test parameters for a test case
        """
        if not test_case:
            test_case = inspect.stack()[1][3]

            logging.info(f"Setting testcase name to {test_case}")

        logging.info("Identify test case and return parameters")

        test_suite = test_suite.split("/")[-1]

        logging.debug(f"Return testcases for Test Suite: {test_suite}")

        suite_parameters = [
            copy.deepcopy(param)
            for param in tests_parameters["test_suites"]
            if param["name"] == test_suite
        ]

        logging.debug(f"Suite_parameters: {suite_parameters}")

        logging.info(f"Returning parameters for Test Case: {test_case}")

        case_parameters = [
            copy.deepcopy(param)
            for param in suite_parameters[0]["testcases"]
            if param["name"] == test_case
        ]

        logging.debug(f"Case_parameters: {case_parameters[0]}")

        case_parameters[0]["test_suite"] = test_suite

        return case_parameters[0]

    def generate_report(self, dut_name, output):
        """Utility to generate report

        Args:
          dut_name: name of the device
        """
        logging.debug(f"Output on device {dut_name} after SSH connection is: {output}")

        self.test_parameters["comment"] = self.comment
        self.test_parameters["test_result"] = self.test_result
        self.test_parameters["output_msg"] = self.output_msg
        self.test_parameters["actual_output"] = self.actual_output
        self.test_parameters["expected_output"] = self.expected_output
        self.test_parameters["dut"] = self.dut_name
        self.test_parameters["show_cmd"] = self.show_cmd
        self.test_parameters["test_id"] = self.test_id
        self.test_parameters["show_cmd_txts"] = self._show_cmd_txts
        self.test_parameters["test_steps"] = self.test_steps
        self.test_parameters["show_cmds"] = self._show_cmds
        self.test_parameters["skip"] = self.skip

        if str(self.show_cmd_txt):
            self.test_parameters["show_cmd"] += ":\n\n" + self.show_cmd_txt

        self.test_parameters["test_id"] = self.test_id
        self.test_parameters["fail_or_skip_reason"] = ""

        if not self.test_parameters["test_result"]:
            self.test_parameters["fail_or_skip_reason"] = self.output_msg

        self._html_report()
        self._write_results()
        self._write_text_results()

    def _html_report(self):
        """Print to standard output for HTML reporting"""

        print("\nOUTPUT MESSAGES:")
        print("================")
        print(f"{self.output_msg}\n{self.comment}")

        print("\nEXPECTED OUTPUT:")
        print("================")
        pprint.pprint(self.expected_output)

        print("\n\nACTUAL OUTPUT:")
        print("==============")
        pprint.pprint(self.actual_output)

        print("\n\nSHOW OUTPUT COLLECTED IN TEST CASE:")
        print("===================================")

        for dut_name, _show_cmds in self._show_cmds.items():
            index = 1
            for command, text in zip(_show_cmds, self._show_cmd_txts[dut_name]):
                print(f"{index}. {dut_name}# {command}\n\n{text}")
                index += 1

    def verify_veos(self):
        """Verify DUT is a VEOS instance

        Returns:
            veos_bool: boolean indicating whether DUT is VEOS instance or not
        """
        show_cmd = "show version"
        veos_bool = False
        veos = self.dut["output"][show_cmd]["json"]["modelName"]

        logging.info(f"Verifying if {self.dut_name} DUT is a VEOS instance. Model is {veos}")

        if "vEOS" in veos:
            veos_bool = True

            logging.debug(f"{self.dut_name} is a VEOS instance so returning {veos_bool}")
        else:
            logging.debug(f"{self.dut_name} is not a VEOS instance so returning {veos_bool}")

        return veos_bool

    def parse_test_steps(self, func):
        """Returns a list of all the test_steps in the given function.
        Inspects functions and finds statements with TS: and organizes
        them into a list.
        Args:
            func (obj): function reference with body to inspect for test steps
        """

        # Extracting lines from the function
        comments = []
        lines, _ = inspect.getsourcelines(func)

        # converting list of strings into a single string
        content = " ".join([str(elem) for elem in lines])

        # Pattern to match to extract TS
        pattern = re.compile('(TS:.*?)(?:"""|Args:)', re.DOTALL)

        # Find all matches to pattern
        comments = pattern.findall(content)

        # Format each item in list
        comments = [x.strip() for x in comments]
        if not comments:
            comments.append("N/a no Test Steps found")

        for step in comments:
            # Add Test steps to list to be added to file
            self.test_steps.append(step.lstrip("TS:"))

        logging.info(f"These are test steps {self.test_steps}")

    def set_evidence_default(self, dut_name):
        """For initializing evidence values for neighbor duts since
        init only initializes for primary dut"""

        self._show_cmd_txts.setdefault(dut_name, [])
        self._show_cmds.setdefault(dut_name, [])
        self.show_cmd_txts.setdefault(dut_name, [])

    def get_ssh_connection(self, dut):
        """Return the ssh connection if it exists otherwise initialise
        a new ssh connection

        Args:
            dut (dict): device whose ssh connection should be returned

        Returns:
            conn (netmiko connection): ssh connection for the device"""

        if "ssh_conn" not in dut:
            netmiko_conn = device_interface.NetmikoConn()
            netmiko_conn.set_up_conn(dut)
            dut["ssh_conn"] = netmiko_conn
            dut["connection"] = netmiko_conn

        return dut["ssh_conn"]

    def get_eapi_connection(self, dut):
        """Return the eapi connection if it exists otherwise initialise
        a new eapi connection

        Args:
            dut (dict): device whose eapi connection should be returned

        Returns:
            conn (paramiko connection): eapi connection for the device"""

        if "eapi_conn" not in dut:
            pyeapi_conn = device_interface.PyeapiConn()
            pyeapi_conn.set_up_conn(dut)
            dut["eapi_conn"] = pyeapi_conn
            dut["connection"] = pyeapi_conn

        return dut["eapi_conn"]

    def get_new_conn(self, dut, conn_type, timeout):
        """get new conn returns a new connection to dut of type 'conn_type'
        with read timeout set to timeout
        Args: dut: the device to get the connection to
        conn_type: eapi or ssh
        timeout: Read time out for the connection

        Returns a new eapi or ssh connection to dut
        """
        device_data = {}
        device_data["transport"] = dut["transport"]
        device_data["mgmt_ip"] = dut["mgmt_ip"]
        device_data["username"] = dut["username"]
        device_data["password"] = dut["password"]
        device_data["enable_pwd"] = dut.get("enable_pwd", "")
        device_data["timeout"] = timeout
        device_data["name"] = dut["name"]
        if dut.get("session_log"):
            device_data["session_log"] = dut["session_log"]
        if conn_type == "eapi":
            logging.info(f"Creating new eapi connection to {dut['name']}")
            pyeapi_conn = device_interface.PyeapiConn()
            pyeapi_conn.set_up_conn(device_data)
            return pyeapi_conn

        if conn_type == "ssh":
            logging.info(f"Creating new ssh connection to {dut['name']}")
            netmiko_conn = device_interface.NetmikoConn()
            netmiko_conn.set_up_conn(device_data)
            return netmiko_conn

        raise ValueError(f"conn_type [{conn_type}] not supported")

    def run_cfg_cmds(self, cfg_cmds, dut=None, conn_type="eapi", timeout=0, new_conn=False):
        """run_cfg_cmds is a wrapper which runs the configuration cmds
        if no dut is passed then cmds are run on TestOps dut object
        if conn_type is eapi then pyeapi is used to connect to dut
        if conn_type is ssh then netmiko is used to connect to dut
        if timeout is non-zero then a new connection is created with new timeout
        if new_conn is True a new connction to dut is created

        Args: cfg_cmds: list of configuration cmds to run
        dut: device on which cfg_cmds have to run
        conn_type: connection type to dut - either pyeapi or netmiko
        timeout: read timeout for dut connection
        new_conn: whether to get a new conn to dut

        Returns: A dict object that includes the response for each command
        """

        return self._run_and_record_cmds(
            encoding="text",
            cmd_type="cfg",
            cmds=cfg_cmds,
            dut=dut,
            conn_type=conn_type,
            timeout=timeout,
            new_conn=new_conn,
        )

    def run_show_cmds(
        self,
        show_cmds,
        dut=None,
        encoding="json",
        conn_type="eapi",
        timeout=0,
        new_conn=False,
        hidden_cmd=False,
    ):
        """run_show_cmds is a wrapper which runs the 'show_cmds'
        conn_type determines how the cmds are being run
        if conn_type is eapi then pyeapi is used on specified dut
        if conn_type is ssh then netmiko connection in dut object is used
        if no dut is passed then cmds are run on TestOps dut object
        It returns the output of these 'show_cmds' in the encoding requested.
        Also it checks show_clock_flag
        to see if 'show_clock' cmd needs to be run. It stores the text output for
        'show_cmds' list in 'show_cmds_txt' list for the specific dut.
        Also 'show_cmds' list is appended to object's 'show_cmds' list.
        If timeout is non-zero then a new connection is created with new timeout
        If new_conn is set to True then new connection is created

        Args: show_cmds: list of show commands to be run
        dut: the device to run the show command on
        encoding: json or text, with json being default
        conn_type: eapi or ssh, with eapi being default
        timeout: timeout to be used for connection to DUT
        new_conn: whether or not to create a new conn to DUT

        Returns: A dict object that includes the response for each command along
        with the encoding
        """

        return self._run_and_record_cmds(
            encoding=encoding,
            cmd_type="show",
            cmds=show_cmds,
            dut=dut,
            conn_type=conn_type,
            timeout=timeout,
            new_conn=new_conn,
            hidden_cmd=hidden_cmd,
        )

    def _run_and_record_cmds(
        self,
        cmds,
        conn_type,
        timeout,
        new_conn,
        encoding="json",
        cmd_type="show",
        dut=None,
        hidden_cmd=False,
    ):
        """_run_and_record_cmds runs both config and show cmds and records the output
        of these commands
        Args:
        cmds: list of cfg/show cmds to run
        conn_type: eapi or ssh
        timeout: timeout to be used for connection to DUT, if non-zero timeout is specified
                 then a new connection is created
        new_conn: whether or not to create a new connection to DUT
        encoding: json or text, with json being default
        cmd_type: type of cmd to run - "show" or "cfg" with "show" being default
        dut: the device to run the cmds on

        Returns: A dict object that includes the response for each command
        """

        # if dut is not passed, use this object's dut
        if dut is None:
            dut = self.dut

        if timeout == 0:
            # if timeout is zero, then use existing connections
            if conn_type == "eapi":
                conn = self.get_eapi_connection(dut)
            elif conn_type == "ssh":
                conn = self.get_ssh_connection(dut)
            else:
                raise ValueError(f"conn_type [{conn_type}] not supported")
        elif timeout > 0 or new_conn:
            # if timeout is non-zero or user wants a new connection
            # get the new connection
            conn = self.get_new_conn(dut, conn_type, timeout)

        dut_name = dut["name"]

        # initializing evidence values for other duts since
        # init only initializes for primary dut

        self.set_evidence_default(dut_name)

        # first run show clock if flag is set
        if self.show_clock_flag:
            show_clock_cmds = ["show clock"]
            # run the show_clock_cmds
            try:
                show_clock_op = conn.enable(show_clock_cmds, "text")
            except BaseException as e:
                # add the show clock cmd to _show_cmds evidence list
                for cmd in show_clock_cmds:
                    self._show_cmds[dut_name].append(cmd)
                # add the exception result to _show_cmd_txts evidence output list
                self._show_cmd_txts[dut_name].append(str(e))
                raise e

            # add the show_clock_cmds to _show_cmds list
            # also add the o/p of show_clock_cmds to _show_cmd_txts list
            for result_dict in show_clock_op:
                self._show_cmds[dut_name].append(result_dict["command"])
                self._show_cmd_txts[dut_name].append(result_dict["result"]["output"])

        # then run commands
        try:
            if cmd_type == "show":
                # see if hidden cmd, cmds might be jinja2 template
                # render the cmds using dut object
                run_cmds = cmds
                if hidden_cmd:
                    run_cmds = render_cmds(dut, cmds)
                # if encoding is json run the commands, store the results
                if encoding == "json":
                    json_results = conn.enable(run_cmds)
                # also run the commands in text mode
                txt_results = conn.enable(run_cmds, encoding="text")
            else:
                # run the config cmd
                txt_results = conn.config(cmds)
        except BaseException as e:  # pylint: disable=broad-except
            logging.error(f"Following cmds {cmds} generated exception {str(e)}")
            # add the cmds to _show_cmds cmds list
            # add the exception result for all the cmds in cmds list
            for cmd in cmds:
                self._show_cmds[dut_name].append(cmd)
                if hidden_cmd:
                    self._show_cmd_txts[dut_name].append(f"{cmd} failed")
                    msg = f"{cmd} failed to run. See logs for more details"
                    raise EapiError(message=msg) from e
                if not hidden_cmd:
                    self._show_cmd_txts[dut_name].append(str(e))
                    raise e

        # add the cmds to _show_cmds list
        for cmd in cmds:
            self._show_cmds[dut_name].append(cmd)

        # also add the text o/p of cmds to _show_cmd_txts cmd output list
        if cmd_type == "cfg" and conn_type == "ssh":
            for cmd in cmds:
                self._show_cmd_txts[dut_name].append(txt_results)
        else:
            for result_dict in txt_results:
                result = result_dict.get("result", {"output": ""})
                self._show_cmd_txts[dut_name].append(result["output"])

        if cmd_type == "show" and encoding == "json":
            return json_results

        return txt_results

    def transfer_file(self, src_file, dest_file, file_system, operation, dut=None, sftp=False):
        """
        transfer_file will transfer filename to/from the the dut depending
        on the operation mentioned.

        dut: device to/from which file needs to be transferred
        src_file: full filename of src file
        dest_file: full filename of dest file
        operation: 'get' or 'put'
        sftp: whether to use sftp transport or not
        """

        if dut is None:
            dut = self.dut

        dut_name = dut["name"]

        if operation not in ("get", "put"):
            raise ValueError(f"operation [{operation}] not supported")

        new_dut = dut.copy()
        session_log = (
            f"netmiko-logs/file_transfer_{new_dut['name']}-{time.strftime('%Y%m%d-%H%M%S')}.log"
        )
        new_dut["session_log"] = session_log
        conn = self.get_new_conn(new_dut, conn_type="ssh", timeout=60)

        # first run show clock if flag is set
        if self.show_clock_flag:
            show_clock_cmds = ["show clock"]
            # run the show_clock_cmds
            try:
                show_clock_op = conn.enable(show_clock_cmds, "text")
            except BaseException as e:
                # add the show clock cmd to _show_cmds
                for cmd in show_clock_cmds:
                    self._show_cmds[dut_name].append(cmd)
                    # add the exception result to _show_cmds_txts
                    self._show_cmd_txts[dut_name].append(str(e))
                raise e

            # add the show_clock_cmds to internal cmds list
            # also add the o/p of show_clock_cmds to external cmd output list
            for result_dict in show_clock_op:
                self._show_cmds[dut_name].append(result_dict["command"])
                self._show_cmd_txts[dut_name].append(result_dict["result"]["output"])

        if sftp:
            cmd_str = "sftp"
        else:
            cmd_str = "scp"

        # form request for evidence gathering
        transfer_request = f"{cmd_str} src_file: {src_file} dest_file: {dest_file} op: {operation}"

        # transfer file
        try:
            result = conn.transfer_file(src_file, dest_file, file_system, operation, sftp)
        except BaseException as e:
            self._show_cmds[new_dut["name"]].append(transfer_request)
            self._show_cmd_txts[new_dut["name"]].append(str(e))
            raise e

        self._show_cmds[new_dut["name"]].append(transfer_request)
        # open session log and copy over the evidence
        # hide the username from the evidence collection
        with open(session_log, "r", encoding="utf-8") as file:
            self._show_cmd_txts[new_dut["name"]].append(
                file.read().replace(new_dut["username"], "XXXXX")
            )

        try:
            os.remove(session_log)
        except OSError:
            pass
        return result

    def setup_and_run_traffic(self, traffic_generator_type, configuration_file):
        """Module to call respective traffic generator based on the type of
        traffic generator being used in the test case

        Args:
            type (str): type of the traffic generator being used
            configuration_file: traffic profile file to pass to the traffic generator"""

        if traffic_generator_type == "ixia":
            self.setup_ixia(configuration_file)

    def setup_ixia(self, ixia_configuration):
        """Module to authenticate into Ixia Web Api, configure a session
        with passed in configuration file, generate traffic and return
        traffic and flow stats to validate test criteria

        Args:
            ixia_configuration (str): path of ixia config file"""

        ixia_traffic_item_stats = []
        self.traffic_item_stats = []
        ixia_flow_stats = []
        self.flow_stats = []
        ix_network = None
        session = None

        try:
            # Module 1 : Authentication: Connect to the IxNetwork API Server

            session, ix_network = ixia_interface.authenticate()

            # Module 2 : Configuration

            ix_network = ixia_interface.configure(ix_network, ixia_configuration)

            # Module 3 : Generating traffic

            ix_network = ixia_interface.generate_traffic(ix_network)

            # Get the traffic item and flow statistics

            ixia_traffic_item_stats = StatViewAssistant(ix_network, "Traffic Item Statistics")

            ixia_flow_stats = StatViewAssistant(ix_network, "Flow Statistics")

            # Generate a deep copy of traffic and flow stats to store in tops object

            index = 0
            for traffic_item_stat in ixia_traffic_item_stats.Rows:
                self.traffic_item_stats.append({})
                for column, data in zip(traffic_item_stat.Columns, traffic_item_stat.RawData[0]):
                    self.traffic_item_stats[index].update({column: data})
                index += 1

            index = 0
            for flow_stat in ixia_flow_stats.Rows:
                self.flow_stats.append({})
                for column, data in zip(flow_stat.Columns, flow_stat.RawData[0]):
                    self.flow_stats[index].update({column: data})
                index += 1

        except Exception as exception:  # pylint: disable=W0718
            logging.error(
                f"Exception: Setting up of Ixia errored out due"
                f" to the following reason: {format(exception)}"
            )

        finally:
            logging.info("Checking if there is a session to be cleared")

            if (ix_network and session) is not None:
                ixia_interface.clear_session(ix_network, session)

            else:
                logging.info("No Session to clear")


def post_process_skip(tops, steps, output=""):
    """Post processing for test case that encounters a PyTest Skip

    Args:
        tops(obj): Test case object
        steps(func): Test case
        output(str): Test case show output
    """

    tops.skip = True
    tops.parse_test_steps(steps)
    tops.generate_report(tops.dut_name, output)
