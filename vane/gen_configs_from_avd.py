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

"""
Python script to generate configs.yaml from AVD structred data

reqs: yaml

Run: python3 gen_configs_from_avd.py --generate-configs-file <avd-structured-data-dir>
"""

import argparse
import os
import yaml


def create_configs_file(avd_sd_dir):
    """funciton to create configs.yaml
    Args:
      avd_sd_dir: Dir that holds AVD structured data
    """

    avd_info = os.walk(avd_sd_dir)
    config = {}
    for dir_path, _, avd_files in avd_info:
        for avd_file in avd_files:
            print(avd_file)
            if avd_file.startswith("."):
                continue
            if avd_file.endswith("debug-vars.yml"):
                file_path = f"{dir_path}/{avd_file}"
                mgmt_data = get_mgmt_data(file_path)
                device_name = avd_file.split(".")[0].replace("-debug-vars", "")
                if config.get(device_name) is None:
                    config[device_name] = {}
                config[device_name].update(mgmt_data)
            else:
                file_path = f"{dir_path}/{avd_file}"
                data = get_non_mgmt_data(file_path)
                device_name = avd_file.split(".")[0]
                if config.get(device_name) is None:
                    config[device_name] = {}
                config[device_name].update(data)

    add_lldp_neighbors_dict(config)
    with open("configs.yml", "w", encoding="utf-8") as file:
        yaml.safe_dump(config, file, sort_keys=False)


def get_non_mgmt_data(file):
    """Function to get non mgmt data from AVD SD file

    Args:
      file: full path to AVD SD file to be read
    """
    with open(file, "r", encoding="utf-8") as input_yaml:
        full_config = yaml.safe_load(input_yaml)
    data = {}
    data["router_bgp"] = full_config.get("router_bgp", {})
    data["vrfs"] = full_config.get("vrfs", {})
    data["vlans"] = full_config.get("vlans", {})
    data["vlan_interfaces"] = full_config.get("vlan_interfaces", {})
    data["port_channel_interfaces"] = full_config.get("port_channel_interfaces", {})
    data["ethernet_interfaces"] = full_config.get("ethernet_interfaces", {})
    data["mlag_configuration"] = full_config.get("mlag_configuration", {})
    data["loopback_interfaces"] = full_config.get("loopback_interfaces", {})
    data["vxlan_interfaces"] = full_config.get("vxlan_interfaces", {})
    return data


def get_mgmt_data(file):
    """Function to get mgmt data from AVD SD file

    Args:
      file: full path to AVD SD file to be read
    """
    with open(file, "r", encoding="utf-8") as input_yaml:
        full_config = yaml.safe_load(input_yaml)
    mgmt_data = {}
    mgmt_data["snmp_server"] = full_config.get("snmp_server", {})
    mgmt_data["tacacs_servers"] = full_config.get("tacacs_servers", {})
    mgmt_data["ip_tacacs_source_interfaces"] = full_config.get("ip_tacacs_source_interfaces", {})
    mgmt_data["name_server"] = full_config.get("name_server", {})
    mgmt_data["ntp"] = full_config.get("ntp", {})
    mgmt_data["mgmt_interface_vrf"] = full_config.get("mgmt_interface_vrf", {})
    mgmt_data["logging"] = full_config.get("logging", {})
    return mgmt_data


def add_lldp_neighbors_dict(config):
    """function to add lldp neighbors info to config

    Args:
      config: dict that holds all relevant AVD structured data
    """

    for _, device_info in config.items():
        device_info["lldp"] = {}
        device_info["lldp"]["neighbors"] = []
        for eth, eth_info in device_info["ethernet_interfaces"].items():
            if "peer" not in eth_info or eth_info["peer"] == "unused_ports":
                continue
            neighbor_entry = {
                "neighborDevice": eth_info["peer"],
                "neighborPort": eth_info["peer_interface"],
                "port": eth,
            }
            device_info["lldp"]["neighbors"].append(neighbor_entry)


def main():
    """main function"""

    args = parse_cli()

    if args.generate_configs_file:
        create_configs_file(args.generate_configs_file[0])


def parse_cli():
    """Parse CLI options.

    Returns:
      args (obj): An object containing the CLI arguments.
    """

    parser = argparse.ArgumentParser(
        description=("Script to generate configs.yaml for vane from AVD structured data")
    )

    parser.add_argument(
        "--generate-configs-file",
        help="Create configs.yaml for vane from AVD structured data",
        nargs=1,
        metavar=("avd_structured_data_dir"),
    )
    args = parser.parse_args()

    return args


if __name__ == "__main__":
    main()
