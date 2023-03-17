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
import time
import sys
import logging
import os
import inspect
import subprocess
import re
import yaml

from vane import config, device_interface


FORMAT = "[%(asctime)s %(filename)s->%(funcName)s():%(lineno)s]%(levelname)s: %(message)s"

logging.basicConfig(
    level=logging.INFO,
    filename="vane.log",
    filemode="w",
    format=FORMAT,
)

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

    logging.info(f"Filter test definitions by test suite name: {testsuite}")

    subset_def = [defs for defs in test_defs["test_suites"] if testsuite == defs["name"]]
    testcases = subset_def[0]["testcases"]

    logging.info("unpack testcases by defining dut and criteria")

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

            logging.info(f"create dut parameters.  \nDuts: {duts} \nIds: {ids}")

            dut_parameters[testname] = {}
            dut_parameters[testname]["duts"] = duts
            dut_parameters[testname]["ids"] = ids

    return dut_parameters


def parametrize_inputs(test_fname, parameter_name, test_defs):
    """Use a filter to create input variables for PyTest parametrize

    Args:
        test_fname (str): Test suite path and file name
        parameter_name(str): Name of parameter whose values need to be picked
        test_defs (dict): Dictionary with global test definitions

    Returns:
        input_parameters (dict): Dictionary with variables PyTest parametrize for each test case.
    """
    logging.info("Discover test suite name")

    testsuite = test_fname.split("/")[-1]

    logging.info(f"Filter test definitions by test suite name: {testsuite}")

    subset_def = [defs for defs in test_defs["test_suites"] if testsuite in defs["name"]]
    testcases = subset_def[0]["testcases"]

    logging.info(
        """For each testcase in this testsuite,
            pack up the value and ids for parameter_name"""
    )

    input_parameters = {}

    for testcase in testcases:
        if "name" in testcase:
            testname = testcase["name"]
            parameter_data = []
            if parameter_name in testcase:
                parameter_data = testcase[parameter_name]
            input_parameters[testname] = {}
            input_parameters[testname]["data"] = [elem["data"] for elem in parameter_data]
            input_parameters[testname]["ids"] = [elem["id"] for elem in parameter_data]

    return input_parameters


def setup_import_yaml(yaml_file):
    """Import YAML file as python data structure
    Also remove lines starting from #

    Args:
        yaml_file (str): Name of YAML file

    Returns:
        yaml_data (dict): YAML data structure
    """
    logging.info(f"Opening {yaml_file} for read")

    temp_file = yaml_file.split(".")[0] + "_temp." + yaml_file.split(".")[1]

    try:
        # need to read the setup yaml file and filter out comments
        # here a line is copied to temp file if it does not start with #
        with open(yaml_file, "r", encoding="utf-8") as input_yaml:
            with open(temp_file, "w", encoding="utf-8") as temp_yaml:
                for line in input_yaml.readlines():
                    if not line.strip().startswith("#"):
                        temp_yaml.write(line)

        # temp file is now used to load yaml
        yaml_data = yaml_read(temp_file)
        os.remove(temp_file)
        return yaml_data

    except OSError as err:
        print(f">>> {yaml_file} YAML FILE MISSING")
        logging.error(f"ERROR YAML FILE: {yaml_file} NOT FOUND. {err}")
        logging.error("EXITING TEST RUNNER")
        sys.exit(1)


def import_yaml(yaml_file):
    """Import YAML file as python data structure

    Args:
        yaml_file (str): Name of YAML file

    Returns:
        yaml_data (dict): YAML data structure
    """
    logging.info(f"Opening {yaml_file} for read")

    try:
        yaml_data = yaml_read(yaml_file)
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
            logging.info(f"Inputted the following yaml: {yaml_data}")
            return yaml_data
        except yaml.YAMLError as err:
            print(">>> ERROR IN YAML FILE")
            logging.error(f"ERROR IN YAML FILE: {err}")
            logging.error("EXITING TEST RUNNER")
            sys.exit(1)


def return_dut_list(test_parameters):
    """Return a duts_list for specific test parameters

    Args:
        test_parameters (dict): Abstraction of testing parameters

    Returns:
        duts (list): List of DUT hostnames
    """
    logging.info("Creating a list of duts from test definitions")

    if "duts" in test_parameters:
        logging.info("Duts configured in test definitions")
        duts = [dut["name"] for dut in test_parameters["duts"]]
    else:
        print(">>> NO DUTS CONFIGURED")
        logging.error("NO DUTS CONFIGURED")
        logging.error("EXITING TEST RUNNER")
        sys.exit(1)

    logging.info(f"Returning duts: {duts}")

    return duts


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
        "Finding DUTs and then execute inputted show commands "
        "on each dut.  Return structured data of DUTs output "
        "data, hostname, and connection."
    )

    duts = login_duts(test_parameters, test_duts)
    workers = len(duts)

    logging.info(f"Duts login info: {duts} and create {workers} workers")
    logging.info(f"Passing the following show commands to workers: {show_cmds}")

    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        future_object = {
            executor.submit(dut_worker, dut, show_cmds, test_duts): dut for dut in duts
        }

    if future_object:
        logging.info("Future object generated successfully")

    logging.info(f"Return duts data structure: {duts}")

    return duts


def login_duts(test_parameters, test_duts):
    """Use eapi to connect to Arista switches for testing

    Args:
      test_parameters (dict): Abstraction of testing parameters
      test_duts (dict): Dictionary of duts

    Returns:
      logins (list): List of dictionaries with connection and name
                     of DUTs
    """
    logging.info("Using eapi to connect to Arista switches for testing")

    duts = test_duts["duts"]
    logins = []
    eapi_file = test_parameters["parameters"]["eapi_file"]

    for dut in duts:
        name = dut["name"]
        login_index = len(logins)
        logins.append({})
        login_ptr = logins[login_index]

        logging.info(f"Connecting to switch: {name} using parameters: {dut}")

        eos_conn = test_parameters["parameters"].get("eos_conn", DEFAULT_EOS_CONN)
        netmiko_conn = device_interface.NetmikoConn()
        netmiko_conn.set_conn_params(eapi_file)
        netmiko_conn.set_up_conn(name)
        login_ptr["ssh_conn"] = netmiko_conn

        if eos_conn == "eapi":
            pyeapi_conn = device_interface.PyeapiConn()
            pyeapi_conn.set_conn_params(eapi_file)
            pyeapi_conn.set_up_conn(name)
            login_ptr["connection"] = pyeapi_conn
        elif eos_conn == "ssh":
            login_ptr["connection"] = netmiko_conn
        else:
            raise ValueError(f"Invalid EOS conn type {eos_conn} specified")

        login_ptr["name"] = name
        login_ptr["mgmt_ip"] = dut["mgmt_ip"]
        login_ptr["username"] = dut["username"]
        login_ptr["role"] = dut["role"]
        login_ptr["neighbors"] = dut["neighbors"]
        login_ptr["results_dir"] = test_parameters["parameters"]["results_dir"]
        login_ptr["report_dir"] = test_parameters["parameters"]["report_dir"]
        login_ptr["eapi_file"] = eapi_file

    logging.info(f"Returning duts logins: {logins}")

    return logins


def send_cmds(show_cmds, conn, encoding):
    """Send show commands to duts and recurse on failure

    Args:
        show_cmds (list): List of pre-processed commands
        conn (obj): connection
        encoding (string): encoding type of show commands: either json or text

    Returns:
        show_cmd_list (list): list of show commands
    """
    logging.info("In send_cmds")

    try:
        logging.info(f"List of show commands in show_cmds with encoding {encoding}: {show_cmds}")

        if encoding == "json":
            show_cmd_list = conn.run_commands(show_cmds)
        elif encoding == "text":
            show_cmd_list = conn.run_commands(show_cmds, encoding="text")

        logging.info(f"ran all show cmds with encoding {encoding}: {show_cmds}")

    # pylint: disable-next=broad-exception-caught
    except Exception as err:
        logging.error(f"error running all cmds: {err}")

        show_cmds = remove_cmd(err, show_cmds)

        logging.info(f"new show_cmds: {show_cmds}")

        show_cmd_list = send_cmds(show_cmds, conn, encoding)
        show_cmd_list = show_cmd_list[0]

    logging.info(f"return all show cmds: {show_cmd_list}")

    return show_cmd_list, show_cmds


def remove_cmd(err, show_cmds):
    """Remove command that is not supported by pyeapi

    Args:
        err (str): Error string
        show_cmds (list): List of pre-processed commands

    Returns:
        show_cmds (list): List of post-processed commands
    """
    logging.info(f"remove_cmd: {err}")
    logging.info(f"remove_cmd show_cmds list: {show_cmds}")

    longest_matching_cmd = ""

    for show_cmd in show_cmds:
        if show_cmd in str(err) and longest_matching_cmd in show_cmd:
            longest_matching_cmd = show_cmd

    # longest_matching_cmd is the one in error string, lets bump it out
    if longest_matching_cmd:
        cmd_index = show_cmds.index(longest_matching_cmd)
        show_cmds.pop(cmd_index)

        logging.info(f"removed {longest_matching_cmd} because of {err}")

    return show_cmds


def dut_worker(dut, show_cmds, test_parameters):
    """Execute inputted show commands on dut.  Update dut structured data
    with show output.

    Args:
      dut (dict): structured data of a dut output data, hostname, and
      show_cmds (list): List of show commands
      test_parameters (dict): Abstraction of testing parameters
    """
    name = dut["name"]
    conn = dut["connection"]
    dut["output"] = {}
    dut["output"]["interface_list"] = return_interfaces(name, test_parameters)

    logging.info(f"Executing show commands on {name}")
    logging.info(f"List of show commands {show_cmds}")
    logging.info(f"Number of show commands {len(show_cmds)}")

    all_cmds_json = show_cmds.copy()
    show_cmd_json_list, show_cmds_json = send_cmds(all_cmds_json, conn, "json")

    logging.info(f"Returned from send_cmds_json {show_cmds_json}")

    all_cmds_txt = show_cmds.copy()
    show_cmd_txt_list, show_cmds_txt = send_cmds(all_cmds_txt, conn, "text")

    logging.info(f"Returned from send_cmds_txt {show_cmds_txt}")

    for show_cmd in show_cmds:
        function_def = f'test_{("_").join(show_cmd.split())}'

        logging.info(f"Executing show command: {show_cmd} for test {function_def}")
        logging.info(f"Adding output of {show_cmd} to duts data structure")

        dut["output"][show_cmd] = {}

        if show_cmd in show_cmds_json:
            cmd_index = show_cmds_json.index(show_cmd)

            logging.info(f"found cmd: {show_cmd} at index {cmd_index} of {show_cmds_json}")
            logging.info(
                f"length of cmds: {len(show_cmds_json)} vs length of "
                f"output {len(show_cmd_json_list)}"
            )

            show_output = show_cmd_json_list[cmd_index]
            dut["output"][show_cmd]["json"] = show_output

            logging.info(f"Adding cmd {show_cmd} to dut and data {show_output}")
        else:
            dut["output"][show_cmd]["json"] = ""

            logging.info(f"No json output for {show_cmd}")

        if show_cmd in show_cmds_txt:
            cmd_index = show_cmds_txt.index(show_cmd)
            show_output_txt = show_cmd_txt_list[cmd_index]
            dut["output"][show_cmd]["text"] = show_output_txt["output"]

            logging.warning(f"Adding text cmd {show_cmd} to dut and data {show_output_txt}")
        else:
            dut["output"][show_cmd]["text"] = ""

            logging.warning(f"No text output for {show_cmd}")

    logging.info(f"{name} updated with show output {dut}")


def return_show_cmd(show_cmd, dut, test_name, test_parameters):
    """Return model data and text output from show commands and log text output.

    Args:
      show_cmd (str): show command
      dut (dict): Dictionary containing dut name and connection
      test_name (str): test case name
      test_parameters (dict): Abstraction of testing parameters

    Returns:
      show_output (dict): json output of cli command
      show_output_text (dict): plain-text output of cli command
    """
    logging.info(
        f"Raw Input for return_show_cmd \nshow_cmd: {show_cmd}\ndut: "
        f"{dut} \ntest_name: {test_name} \ntest_parameters: "
        f"{test_parameters}"
    )

    conn = dut["connection"]
    name = dut["name"]

    logging.info(
        "Return model data and text output from show commands and "
        f"log text output for {show_cmd} with connnection {conn}"
    )

    show_output = []
    show_output_text = []
    raw_text = ""

    try:
        show_output = conn.run_commands(show_cmd, encoding="json")
    # pylint: disable-next=broad-exception-caught
    except Exception as err:
        logging.error(f"Missed on commmand {show_cmd}")
        logging.error(f"Error msg {err}")

        time.sleep(1)
        show_output_text = conn.run_commands(show_cmd, encoding="text")

        logging.error(f"new value of show_output_text  {show_output_text}")

        raw_text = show_output_text[0]["output"]

    logging.info(f"Raw text output of {show_cmd} on dut {name}: {show_output}")

    export_logs(test_name, name, raw_text, test_parameters)

    return show_output, show_output_text


def return_interfaces(hostname, test_parameters):
    """Parse test_parameters for interface connections and return them to test

    Args:
        hostname (str):  hostname of dut
        test_parameters (dict): Abstraction of testing parameters

    Returns:
      interface_list (list): list of interesting interfaces based on
                             PS LLD spreadsheet
    """
    logging.info("Parse test_parameters for interface connections and return them to test")

    interface_list = []
    duts = test_parameters["duts"]

    for dut in duts:
        dut_name = dut["name"]

        if dut_name == hostname:
            logging.info(f"Discovering interface parameters for: {hostname}")

            neighbors = dut["neighbors"]

            for neighbor in neighbors:
                interface = {}

                logging.info(f"Adding interface parameters: {neighbor} neighbor for: {dut_name}")

                interface["hostname"] = dut_name
                interface["interface_name"] = neighbor["port"]
                interface["z_hostname"] = neighbor["neighborDevice"]
                interface["z_interface_name"] = neighbor["neighborPort"]
                interface["media_type"] = ""
                interface_list.append(interface)

    logging.info(f"Returning interface list: {interface_list}")

    return interface_list


def export_logs(test_name, hostname, output, test_parameters):
    """Open log file for logging test show commands

    Args:
        test_name (str): test case name
        hostname (str):  hostname of dut
        output (str): output text of the show command
        test_parameters (dict): Abstraction of testing parameters
    """
    logging.info("Open log file for logging test show commands")

    show_log = test_parameters["parameters"]["show_log"]

    try:
        logging.info(f"Opening file {show_log} and append show output: {output}")

        with open(show_log, "w", encoding="utf-8") as log_file:
            log_file.write(f"\ntest_suite::{test_name}[{hostname}]:\n{output}")
    except OSError as error:
        print(f">>>  ERROR OPENING LOG FILE: {error}")
        logging.error(f"ERROR OPENING LOG FILE: {error}")
        logging.error("EXITING TEST RUNNER")
        sys.exit(1)


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

    logging.info(f"Suite_parameters: {suite_parameters}")

    logging.info(f"Return parameters for Test Case: {test_case}")

    case_parameters = [
        param for param in suite_parameters[0]["testcases"] if param["name"] == test_case
    ]

    logging.info(f"Case_parameters: {case_parameters[0]}")

    case_parameters[0]["test_suite"] = test_suite

    return case_parameters[0]


def verify_show_cmd(show_cmd, dut):
    """Verify if show command was successfully executed on dut

    Args:
        show_cmd (str): show command
        dut (dict): data structure of dut parameters
    """

    dut_name = dut["name"]

    logging.info(f"Verify if show command |{show_cmd}| was successfully executed on {dut_name} dut")

    if show_cmd in dut["output"]:
        logging.info(f"Verified output for show command |{show_cmd}| on {dut_name}")
    else:
        logging.critical(f"Show command |{show_cmd}| not executed on {dut_name}")

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

    logging.info(f"Verify if tacacs server(s) are configured on {dut_name} dut")

    if tacacs_servers == 0:
        tacacs_bool = False

    logging.info(f"{tacacs_servers} tacacs serverws are configured so returning {tacacs_bool}")

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

    logging.info(f"Verify if {dut_name} DUT is a VEOS instance. Model is {veos}")

    if veos == "vEOS":
        veos_bool = True

        logging.info(f"{dut_name} is a VEOS instance so returning {veos_bool}")
        logging.info(f"{dut_name} is a VEOS instance so test NOT valid")
    else:
        logging.info(f"{dut_name} is not a VEOS instance so returning {veos_bool}")

    return veos_bool


def generate_interface_list(dut_name, test_definition):
    """Test_definition is used to create a interface_list for active
    DUT interfaces and attributes

    Args:
        dut_name (str): name of the dut
        test_definition (dict):  test definition data

    Returns:
        interface_list (list): list of active DUT interfaces and attributes
    """
    dut_hostnames = [dut["name"] for dut in test_definition["duts"]]
    dut_index = dut_hostnames.index(dut_name)
    int_ptr = test_definition["duts"][dut_index]
    interface_list = int_ptr["test_criteria"][0]["criteria"]

    return interface_list


def return_show_cmds(test_parameters):
    """Return show commands from the test_definitions

    Args:
        test_parameters (dict): Abstraction of testing parameters

    Returns:
        show_cmds (list): show commands from the test_definitions
    """
    show_clock_flag = config.test_parameters["parameters"]["show_clock"]

    show_cmds = []

    if show_clock_flag:
        show_cmds = ["show version", "show clock"]

    logging.info(f"Discover the names of test suites from {test_parameters}")

    test_data = test_parameters["test_suites"]
    test_suites = [param["name"] for param in test_data]

    for test_suite in test_suites:
        test_index = test_suites.index(test_suite)
        test_cases = test_data[test_index]["testcases"]

        logging.info(f"Find show commands in test suite: {test_suite}")

        for test_case in test_cases:
            show_cmd = test_case.get("show_cmd", "")
            if show_cmd:
                logging.info(f"Found show command {show_cmd}")

                if show_cmd not in show_cmds:
                    logging.info(f"Adding Show command {show_cmd}")

                    show_cmds.append(show_cmd)
            else:
                test_show_cmds = test_case.get("show_cmds", [])
                logging.info(f"Found show commands {test_show_cmds}")

                for show_cmd in (
                    show_cmd for show_cmd in test_show_cmds if show_cmd not in show_cmds
                ):
                    logging.info(f"Adding Show commands {show_cmd}")

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
                    test_defs["test_suites"] += test_def

    export_yaml(report_dir + "/" + test_definitions_file, test_defs)

    logging.info(f"Return the following test definitions data structure {test_defs}")

    return test_defs


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
                logging.info(f"Output the following yaml: {yaml_data}")

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


def export_text(text_file, text_data):
    """Export python data structure as a TEXT file

    Args:
        text_file (str): Name of TEXT file
        text_data (dict): output of show command in python dictionary
    """
    logging.info(f"Opening {text_file} for write")

    # to create the sub-directory if it does not exist
    os.makedirs(os.path.dirname(text_file), exist_ok=True)

    try:
        with open(text_file, "w", encoding="utf-8") as text_out:
            logging.info(f"Output the following text file: {text_data}")
            for key, value in text_data.items():
                text_out.write(f"{key}{value}\n")
    except OSError as err:
        print(f">>> {text_file} TEXT FILE MISSING")
        logging.error(f"ERROR TEXT FILE: {text_file} NOT FOUND. {err}")
        logging.error("EXITING TEST RUNNER")
        sys.exit(1)


def subprocess_ping(definition_file, dut_name, loopback_ip, repeat_ping):
    """Subprocess to run the continuous ping command

    Args:
        definition_file: definitions.yaml file
        dut_name: data structure of dut parameters
        loopback_ip: loopback ip on device
        repeat_ping: number of pings to flow the traffic

    Returns:
        process: instance of the subprocess
    """
    return subprocess.Popen(
        [
            "python",
            "/".join(__file__.split("/")[:-1]) + "/test_ping.py",
            definition_file,
            dut_name,
            loopback_ip,
            repeat_ping,
        ],
        stdout=subprocess.PIPE,
        universal_newlines=True,
    )


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
        logging.error(f"Error occured while creating DUTs file: {str(excep)}")
        logging.error("EXITING TEST RUNNER")
        print(">>> ERROR While creating duts file")
        sys.exit(1)

    return None


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
        self.test_case = test_case
        self.test_parameters = self._get_parameters(tests_definitions, test_suite, self.test_case)
        self.expected_output = self.test_parameters["expected_output"]
        self.dut = dut
        self.dut_name = self.dut["name"]
        self.interface_list = self.dut["output"]["interface_list"]
        self.results_dir = self.dut["results_dir"]
        self.report_dir = self.dut["report_dir"]

        parameters = config.test_parameters
        show_clock_flag = parameters["parameters"]["show_clock"]
        self.show_cmds = []

        if show_clock_flag:
            self.show_cmds = ["show version", "show clock"]

        self.show_output = ""
        self.show_cmd = ""
        self.test_steps = []

        try:
            self.show_cmd = self.test_parameters["show_cmd"]
            if self.show_cmd:
                self.show_cmds.append(self.show_cmd)
        except KeyError:
            self.show_cmds.extend(self.test_parameters["show_cmds"])

        self.show_cmd_txts = []
        self.show_cmd_txt = ""

        if len(self.show_cmds) > 0 and self.dut:
            self._verify_show_cmd(self.show_cmds, self.dut)
            if self.show_cmd:
                self.show_cmd_txt = self.dut["output"][self.show_cmd]["text"]
            for show_cmd in self.show_cmds:
                self.show_cmd_txts.append(self.dut["output"][show_cmd]["text"])

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
            f"Verify if show command |{show_cmds}| were successfully executed on {dut_name} dut"
        )

        for show_cmd in show_cmds:
            if show_cmd and show_cmd in dut["output"]:
                logging.info(f"Verified output for show command |{show_cmd}| on {dut_name}")
            else:
                logging.critical(f"Show command |{show_cmd}| not executed on {dut_name}")

                assert False

    def post_testcase(self):
        """Do post processing for test case"""
        self.test_parameters["comment"] = self.comment
        self.test_parameters["test_result"] = self.test_result
        self.test_parameters["output_msg"] = self.output_msg
        self.test_parameters["actual_output"] = self.actual_output
        self.test_parameters["expected_output"] = self.expected_output
        self.test_parameters["dut"] = self.dut_name
        self.test_parameters["show_cmd"] = self.show_cmd
        self.test_parameters["test_id"] = self.test_id
        self.test_parameters["show_cmd_txts"] = self.show_cmd_txts
        self.test_parameters["test_steps"] = self.test_steps

        if str(self.show_cmd_txt):
            self.test_parameters["show_cmd"] += ":\n\n" + self.show_cmd_txt

        self.test_parameters["test_id"] = self.test_id
        self.test_parameters["fail_or_skip_reason"] = ""

        if not self.test_parameters["test_result"]:
            self.test_parameters["fail_or_skip_reason"] = self.output_msg

        self._write_results()
        self._write_text_results()

    def _write_results(self):
        """Write the yaml output to a text file"""
        logging.info("Preparing to write results")

        test_suite = self.test_parameters["test_suite"]
        test_suite = test_suite.split("/")[-1]
        dut_name = self.test_parameters["dut"]
        test_case = self.test_parameters["name"]
        results_dir = self.results_dir
        yaml_file = f"{results_dir}/result-{test_case}-{dut_name}.yml"

        logging.info(f"Creating results file named {yaml_file}")

        yaml_data = self.test_parameters
        export_yaml(yaml_file, yaml_data)

    def _write_text_results(self):
        """Write the text output of show command to a text file"""
        report_dir = self.report_dir
        test_id = self.test_parameters["test_id"]
        test_case = self.test_parameters["name"]
        dut_name = self.test_parameters["dut"]
        text_file = (
            f"{report_dir}/TEST RESULTS/{test_id} {test_case}/"
            f"{test_id} {dut_name} Verification.txt"
        )

        text_data = {}
        index = 1

        for command, text in zip(self.show_cmds, self.show_cmd_txts):
            text_data[str(index) + ". " + dut_name + "# " + command] = "\n\n" + text
            index += 1

        if text_data:
            logging.info(f"Preparing to write show command output to text file {text_file}")

            export_text(text_file, text_data)
        else:
            logging.info("No show command output to display")

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

        logging.info(f"Return testcases for Test Suite: {test_suite}")

        suite_parameters = [
            copy.deepcopy(param)
            for param in tests_parameters["test_suites"]
            if param["name"] == test_suite
        ]

        logging.info(f"Suite_parameters: {suite_parameters}")

        logging.info(f"Return parameters for Test Case: {test_case}")

        case_parameters = [
            copy.deepcopy(param)
            for param in suite_parameters[0]["testcases"]
            if param["name"] == test_case
        ]

        logging.info(f"Case_parameters: {case_parameters[0]}")

        case_parameters[0]["test_suite"] = test_suite

        return case_parameters[0]

    def return_show_cmd(self, show_cmd):
        """Return model data and text output from show commands and log text output.

        Args:
          show_cmd (str): show command

        Returns:
            result (bool): boolean representing if there was a successful result or not
            show_output (str): text output of running command
            show_cmd_txt (str): text output of show command
            error (str): error thrown by standard error while running command
        """
        self.show_cmd = show_cmd
        self.show_output = ""
        self.show_cmd_txt = ""
        result = True
        error = ""

        logging.info(f"Raw Input for return_show_cmd \nshow_cmd: {show_cmd}\n")

        conn = self.dut["connection"]
        name = self.dut["name"]

        logging.info(
            "Return model data and text output from show commands and "
            f"log text output for {show_cmd} with connection {conn}"
        )

        try:
            show_output_text = conn.run_commands(show_cmd, encoding="text")
            logging.info(f"Raw text output of {show_cmd} on dut {name}: {self.show_cmd_txt}")
            self.show_cmd_txt = show_output_text[0]["output"]
        # pylint: disable-next=broad-exception-caught
        except Exception as err:
            logging.info(f"Error running show command {show_cmd}: {str(err)}")
            error = str(err)
            result = False

        return result, self.show_output, self.show_cmd_txt, error

    def generate_report(self, dut_name, output):
        """Utility to generate report

        Args:
          dut_name: name of the device
        """
        logging.info(f"Output on device {dut_name} after SSH connection is: {output}")

        self.output_msg = (
            f"\nOn switch |{dut_name}| The actual output is "
            f"|{self.actual_output}%| and the expected output is "
            f"|{self.expected_output}%|"
        )
        print(f"{self.output_msg}\n{self.comment}")

        self.post_testcase()

    def verify_veos(self):
        """Verify DUT is a VEOS instance

        Returns:
            veos_bool: boolean indicating whether DUT is VEOS instance or not
        """
        show_cmd = "show version"
        veos_bool = False
        veos = self.dut["output"][show_cmd]["json"]["modelName"]

        logging.info(f"Verify if {self.dut_name} DUT is a VEOS instance. Model is {veos}")

        if veos == "vEOS":
            veos_bool = True

            logging.info(f"{self.dut_name} is a VEOS instance so returning {veos_bool}")
        else:
            logging.info(f"{self.dut_name} is not a VEOS instance so returning {veos_bool}")

        return veos_bool

    def parse_test_steps(self, func):
        """Returns a list of all the test_steps in the given function.
        Inspects functions and finds statements with TS: and organizes
        them into a list.

        Args:
            func (obj): function reference with body to inspect for test steps
        """
        source_lines, _ = inspect.getsourcelines(func)

        for line in source_lines:
            match = re.match(r"\s*TS:(.*)", line)
            if match:
                self.test_steps.append(match.group(1))

        logging.info(f"These are test steps {self.test_steps}")

    def run_show_cmds(self, show_cmds):
        """Runs show clock and show commands and appends the
        commands and their respective output to the self.show_cmds and
        self.show_cmd_txts list respectively"""

        conn = self.dut["connection"]
        show_clock_flag = config.test_parameters["parameters"]["show_clock"]
        clock_and_show_cmds = []

        if show_clock_flag:
            clock_and_show_cmds = ["show clock"]

        clock_and_show_cmds.extend(show_cmds)

        # execute the commands

        cmd_outputs, cmds = send_cmds(clock_and_show_cmds, conn, "text")

        # append the commands and the text outputs to respective variables

        self.show_cmds.extend(cmds)
        for cmd_output in cmd_outputs:
            self.show_cmd_txts.append(cmd_output["output"])
