#!/usr/bin/env python3
#
# Copyright (c) 2022, Arista Networks EOS+
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

"""
Python script to obtain device inventory information from
CVP and generate a DUTS file for Vane

reqs: cvprac, pyeapi, yaml, urllib3

Run: python3 gen_duts_from_cvp.py
"""

import argparse
import sys
import yaml
import urllib3
import pyeapi
from cvprac.cvp_client import CvpClient
from cvprac.cvp_client_errors import (
    CvpApiError,
    CvpLoginError,
    CvpRequestError,
    CvpSessionLogOutError,
)
from requests.exceptions import HTTPError, ReadTimeout, Timeout, TooManyRedirects
from vane.vane_logging import logging


def create_duts_file_from_cvp(cvp_ip, cvp_username, cvp_password, duts_file_name, api_token=None, is_cvaas=None, dev_username=None, dev_password=None):
    """
    create_duts_file_from_cvp function:
        (1) Function to retrieve the inventory from cvp.
        (2) Also retrieves all the neighbors for each device by running lldp cmd on
        devices.
        (3) All this info is dumped in file 'duts_file_name'.
    Args:
        cvp_ip: ip address or hostname for CVP
        cvp_username: username for CVP
        cvp_password: password for CVP
        duts_file_name: name of the duts file to be written
        api_token: REST API token for CVP/CVaaS authentication
        is_cvaas: flag to specify target is CVaaS
        dev_username: username to connect to devices (required when using api_token)
        dev_password: password to connect to devices
    """

    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    try:
        clnt = CvpClient()
        if api_token:
            clnt.connect([cvp_ip], username='', password='', is_cvaas=is_cvaas, api_token=api_token)
        else:
            clnt.connect([cvp_ip], cvp_username, cvp_password)
        logging.info("Pulling the inventory from CVP")
        print(f"Pull the inventory from CVP: {cvp_ip}")
        inventory = clnt.api.get_inventory()
    except (
        CvpLoginError,
        CvpApiError,
        CvpSessionLogOutError,
        CvpRequestError,
        HTTPError,
        ReadTimeout,
        Timeout,
        TooManyRedirects,
        TypeError,
        ValueError,
    ) as err:
        msg = f"Could not get CVP inventory info: {err}"
        logging.error("Could not get CVP inventory info")
        sys.exit(msg)

    dut_file = {}
    dut_properties = []
    for dev in inventory:
        if dev["ztpMode"]:
            continue
        dev_username = dev_username or cvp_username
        dev_password = dev_password or cvp_password
        dut_properties.append(
            {
                "mgmt_ip": dev["ipAddress"],
                "name": dev["hostname"],
                "password": dev_password,
                "transport": "https",
                "username": dev_username,
                "role": "unknown",
                "neighbors": [],
            }
        )

    if dut_properties:
        dut_file.update({"duts": dut_properties})

    lldp_cmd = "show lldp neighbors | json"
    show_cmds = [lldp_cmd]
    workers = len(dut_properties)
    print(f"Run 'show lldp neighbors' on {workers} duts")
    for dut in dut_properties:
        dut_worker(dut, show_cmds)

    neighbors_matrix = {}
    for dut in dut_properties:
        try:
            neighbors = dut["output"][lldp_cmd]["result"][0]["lldpNeighbors"]
            for neighbor in neighbors:
                del neighbor["ttl"]
                fqdn = neighbor["neighborDevice"]
                neighbor["neighborDevice"] = fqdn.split(".")[0]
            neighbors_matrix[dut["name"]] = neighbors
        except KeyError:
            print(f'command "{lldp_cmd}" has not been collected from {dut["name"]}')

    for dut_property in dut_properties:
        try:
            dut_property["neighbors"] = neighbors_matrix[dut_property["name"]]
        except KeyError:
            print(f'neighbors not known for {dut_property["name"]}')
        del dut_property["output"]
        del dut_property["connection"]

    if dut_properties:
        dut_file.update({"duts": dut_properties})
        with open(duts_file_name, "w", encoding="utf-8") as yamlfile:
            yaml.dump(dut_file, yamlfile, sort_keys=False)
            logging.info(f"Yaml file {duts_file_name} created")
            print(f"Yaml file {duts_file_name} created")


def dut_worker(dut, show_cmds):
    """Execute 'show_cmds' on dut. Update dut structured data with show
    output.

    Args:
      dut(dict): structured data of a dut output data, hostname, and
      connection
      show_cmds: list of show_cmds to be run on dut. Output is added
      to dut dict itself
    """

    eos = {
        "device_type": "arista_eos",
        "ip": dut["mgmt_ip"],
        "username": dut["username"],
        "password": dut["password"],
        "secret": dut["password"],
    }

    dut["output"] = {}

    dut["connection"] = pyeapi.connect(
        host=eos["ip"], username=eos["username"], password=eos["password"]
    )

    for show_cmd in show_cmds:
        try:
            output = dut["connection"].execute(show_cmd)
            dut["output"][show_cmd] = output
        except Exception as err:
            print(f'EAPI connection to {dut["mgmt_ip"]} failed - {type(err).__name__}: {err}')

def main():
    """main function"""

    args = parse_cli()

    # original syntax (all arguments of --generate_cvp_duts_file)
    if args.generate_cvp_duts_file:
        logging.info("Generating duts file from CVP")
        create_duts_file_from_cvp(
            args.generate_cvp_duts_file[0],
            args.generate_cvp_duts_file[1],
            args.generate_cvp_duts_file[2],
            args.generate_cvp_duts_file[3],
        )
    # individual options syntax (better for token authentication)
    else:
        if args.cvp_node and args.duts_file:
            if args.username and args.password:
                create_duts_file_from_cvp(
                    args.cvp_node,
                    args.username,
                    args.password,
                    args.duts_file,
                    dev_username=args.dev_username,
                    dev_password=args.dev_password
            )
            elif args.api_token:
                if args.dev_username:
                    create_duts_file_from_cvp(
                        args.cvp_node,
                        None,
                        None,
                        args.duts_file,
                        api_token=args.api_token,
                        is_cvaas=args.is_cvaas,
                        dev_username=args.dev_username,
                        dev_password=args.dev_password
                    )
                else:
                    sys.exit('--dev-username is required for EAPI authentication when token authentication to CVP/CVaaS is used')
            else:
                sys.exit('Either --username and --password or --api-token must be specified.')
        else:
            sys.exit('IP address or hostname for CVP/CVaaS (--cvp-node) and output file (--duts-file) must be specified')


def parse_cli():
    """Parse CLI options.

    Returns:
      args (obj): An object containing the CLI arguments.
    """

    parser = argparse.ArgumentParser(
        description=(
            "Script to generate duts.yaml for vane from CVP/CVaaS and devices. Does not work for ACT env."
        )
    )

    parser.add_argument(
        '--cvp-node',
        help='IP address or hostname of CVP/CVaaS'
    )

    password_auth = parser.add_argument_group('username/password authentication', 'Authenticate to CVP with a username and password.  Does not work with CVaaS.')
    token_auth = parser.add_argument_group('API token authentication', 'Authenticate to CVP/CVaaS with a REST API token.  Required when OAuth is used (always for CVaaS).')
    dev_auth = parser.add_argument_group('Device username/password authentication', 'Authenticate to EAPI devices with a different username and password than CVP.  Required when API token auth is used.')

    password_auth.add_argument(
        '-u', '--username',
        help='Username for CVP authentication'
    )
    
    password_auth.add_argument(
        '-p', '--password',
        help='Password for CVP authentication'
    )

    token_auth.add_argument(
        '--api-token',
        help='REST API token for CVP/CVaaS authentication',
        metavar='TOKEN'
    )

    dev_auth.add_argument(
        '--dev-username',
        help='Username for EAPI device authentication'
    )
    
    dev_auth.add_argument(
        '--dev-password',
        help='Password for EAPI device authentication'
    )

    parser.add_argument(
        '--is-cvaas',
        help='enable connection to CVaaS',
        action='store_true'
    )

    parser.add_argument(
        '--duts-file',
        help='output file for duts inventory in YAML format',
        metavar='FILENAME'
    )

    parser.add_argument(
        "--generate-cvp-duts-file",
        help="Create a duts file from CVP inventory",
        nargs=4,
        metavar=("cvp_ip_address", "cvp_username", "cvp_password", "duts_file_name"),
    )
    args = parser.parse_args()

    return args


if __name__ == "__main__":
    main()
