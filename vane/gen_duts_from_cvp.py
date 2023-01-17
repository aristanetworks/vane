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

Author: David Lewis (dlewis@arista.com)
Date: 21/10/2022

reqs: cvprac, pyeapi, yaml, ssl, urllib3

Run: python3 gen_duts_from_cvp.py
"""

from cvprac.cvp_client import CvpClient
import ssl
ssl._create_default_https_context = ssl._create_unverified_context
import urllib3
urllib3.disable_warnings()
import yaml
import pyeapi
import sys

username = '<devices username>'
password = 'devices password'
cvp_instance = '<cvp ip address>'
cvp_username = '<cvp username>'
cvp_password = '<cvp password>'

def main():
    """
    main function: 
        (1) Gets input for username and password,
        (2) Connects to CVP instance using Cvprac and sends request
        to get inventory
        (3) Iterates through device inventory, collects neighbor
        information and then generates duts file
    """

    try:
        clnt = CvpClient()
        clnt.connect(nodes=[cvp_instance], username=cvp_username, password=cvp_password) # nodes=address of cvp instance
        inventory = clnt.api.get_inventory()
    except:
        sys.exit("Can't connect to CVP instance.")
        
    # check if inventory has devices
    if inventory:
        with open('duts.yaml', 'w', encoding='utf-8') as file:
            file.write('duts: \n')
            for dut in inventory:
                neighbors = get_neighbors(host=dut["ipAddress"], username=username, password=password)
                generate_duts_file(dut=dut, file=file, username=username, password=password, neighbors=neighbors)


def get_neighbors(host, username, password):
    """
    get_neighbors function:
        (1) Connects to device using pyeapi
        (2) Executes and obtains neighbor data from dut
        (3) Returns neighbor information
    
    args:
        (1) host = hostname/address of the dut
        (2) transport = transport protocol
        (3) username = username to connect to dut
        (4) password = password to connect to dut
    """
    conn = pyeapi.connect(host=host, transport='https', username=username, password=password)
    neighbors = conn.execute(['show lldp neighbors'])
    return neighbors["result"][0]["lldpNeighbors"]


def generate_duts_file(dut, file, username, password, neighbors):
    """
    generate_duts_file function:
        (1) Creates DUT dictionary from information
        gathered from the device
        (2) Writes DUT dictionary to yaml file

    args:
        (1) dut = dut object gathered using cvprac
        (2) file = file to write the object to
        (3) username = username to write to file
        (4) password = password to write to file
        (5) neighbors = neighbor data gathered using pyeapi
    """

    dut_dict = [
        {
            'mgmt_ip' : dut["ipAddress"],
            'name' : dut["hostname"],
            'neighbors' : neighbors,
            'password' : password,
            'transport' : 'https',
            'username' : username,
            'role' : ''
        }
    ]

    yaml.dump(dut_dict, file)


if __name__ == "__main__":
    main()
