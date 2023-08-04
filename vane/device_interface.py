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

"""Device connection drivers - two types of drivers
   1. EAPI driver - uses pyeapi package
   2. ssh driver - uses Netmiko package
"""

import os
import json
import pyeapi
import netmiko
from netmiko.ssh_autodetect import SSHDetect
from netmiko import Netmiko
from vane.utils import make_iterable


error_responses = [
    '% This is an unconverted command\n{\n    "errors": '
    '[\n        "This is an unconverted command"\n    ]\n}',
    "% Invalid input",
]


class CommandError(Exception):
    """Base exception raised for command errors
    The CommandError instance provides a custom exception that can be used
    if the Netmiko command(s) fail.  It provides some additional information
    that can be used to understand what caused the exception.
    Args:
        error_text (string): The error text message that coincides with the
            error_code
        commands (array): The list of commands that were sent to the node
            that generated the error
    """

    def __init__(self, message, commands):
        self.error_text = message
        self.commands = commands
        # pylint: disable=super-with-arguments
        super(CommandError, self).__init__(message)

    @property
    def trace(self):
        """Returns trace by using the getter method"""
        return self.get_trace()

    def get_trace(self):
        """Returns trace

        Returns:
        trace(list): list of command and output pairs
        """
        trace = []
        index = None

        for index, out in enumerate(self.error_text):
            _entry = {"command": self.commands[index], "output": out}
            trace.append(_entry)

        if index:
            index += 1
            for cmd in self.commands[index:]:
                _entry = {"command": cmd, "output": None}
                trace.append(_entry)

        return trace


class DeviceConn:
    """Base class for connecting to Arista devices"""

    def set_up_conn(self, device_data):
        """Connect to the mentioned device"""
        pass

    def run_commands(self, cmds, encoding, send_enable, **kwargs):
        """Send commands over the device conn"""
        pass

    def get_config(self, config, params, as_string):
        """Retrieves the config from device"""
        pass

    def enable(self, commands, encoding, strict, send_enable, **kwargs):
        """Send the array of commands to the node in enable mode"""
        pass

    def config(self, commands, **kwargs):
        """Configures the node with the specified commands"""
        pass


class PyeapiConn(DeviceConn):
    """PyeapiConn connects to Arista devices using PyEAPI"""

    def connection(self):
        """returns the connection object"""
        # pylint: disable=attribute-defined-outside-init
        return self._connection

    def set_up_conn(self, device_data):
        """connects to device using pyeapi"""
        # pylint: disable=attribute-defined-outside-init
        self._connection = pyeapi.connect(
            transport=device_data["transport"],
            host=device_data["mgmt_ip"],
            username=device_data["username"],
            password=device_data["password"],
            return_node=True,
        )
        if device_data.get("enable_pwd", ""):
            self._connection.enable_authentication(device_data["enable_pwd"])

    def run_commands(self, cmds, encoding="json", send_enable=True, **kwargs):
        """wrapper around pyeapi run_commands func"""
        output = self._connection.run_commands(cmds, encoding, send_enable)
        return output

    def get_config(self, config="running-config", params=None, as_string=False):
        """wrapper around pyeapi get_config func"""
        output = self._connection.get_config(config, params, as_string)
        return output

    def enable(self, commands, encoding="json", strict=False, send_enable=True, **kwargs):
        """wrapper around pyeapi enable func"""
        output = self._connection.enable(commands, encoding, strict, send_enable, **kwargs)
        return output

    def config(self, commands, **kwargs):
        """wrapper around pyeapi config func"""
        output = self._connection.config(commands, **kwargs)
        return output


class NetmikoConn(DeviceConn):
    """NetmikoConn connects to Arista devices using ssh conn"""

    def connection(self):
        """returns the connection object"""
        return self._connection

    def set_up_conn(self, device_data):
        """sets up conn to device using _config params"""

        self.name = device_data["name"]

        default_device_type = "arista_eos"

        try:
            os.makedirs("netmiko-logs")
        except FileExistsError:
            pass

        logfile = f'netmiko-logs/netmiko-session-{device_data["name"]}.log'
        remote_device = {
            "device_type": device_data.get("device_type", default_device_type),
            "host": device_data["mgmt_ip"],
            "username": device_data["username"],
            "password": device_data["password"],
            "secret": device_data.get("enable_pwd", ""),
            "session_log": logfile,
        }
        if remote_device["device_type"] == "autodetect":
            guesser = SSHDetect(**remote_device)
            remote_device["device_type"] = guesser.autodetect()
        # pylint: disable=attribute-defined-outside-init
        self._connection = Netmiko(**remote_device)

    def get_cmds(self, cmds):
        """get_cmds: converts cmds to json cmds
        cmds can be a list of commands or just one command (str)
        """
        pipe_json = " | json"

        if isinstance(cmds, list):
            local_cmds = cmds.copy()
            for i, cmd in enumerate(cmds):
                local_cmds[i] = cmd + pipe_json
        elif isinstance(cmds, str):
            local_cmds = cmds + pipe_json

        return cmds, local_cmds

    def send_list_cmds(self, cmds, encoding="json"):
        """send_list_cmds: sends the list of commands to device conn
        and collects the output as list"""

        cmds_op = []

        for i, cmd in enumerate(cmds):
            try:
                output = self._connection.send_command(cmd)
            except netmiko.exceptions.NetmikoTimeoutException:
                # try resetting connection and see if it works
                self.set_up_conn(self.name)
                output = self._connection.send_command(cmd)

            if output not in error_responses:
                if encoding == "json":
                    output = json.loads(output)
                    cmds_op.append(output)
                elif encoding == "text":
                    # for text encoding, creating the format
                    # similar to one returned by eapi format
                    text_ob = {"output": output}
                    cmds_op.append(text_ob)
            else:
                err_msg = f"Could not execute {cmds[i]}.Got error: {output}"
                raise CommandError(err_msg, cmds)

        return cmds_op

    def send_str_cmds(self, cmds, encoding="json"):
        """send_str_cmds: sends one command to device conn"""

        cmds_op = []
        try:
            output = self._connection.send_command(cmds)
        except netmiko.exceptions.NetmikoTimeoutException:
            # try resetting connection and see if it works
            self.set_up_conn(self.name)
            output = self._connection.send_command(cmds)

        if output not in error_responses:
            if encoding == "json":
                output = json.loads(output)
                cmds_op.append(output)
            elif encoding == "text":
                text_ob = {"output": output}
                cmds_op.append(text_ob)
        else:
            err_msg = f"Could not execute {cmds} . Got error: {output}"
            raise CommandError(err_msg, cmds)

        return cmds_op

    def run_commands(self, cmds, encoding="json", send_enable=True, **kwargs):
        """This function is added to make sure both PyeapiConn and NetmikoConn
        support same functions. This will help the code to work seemlessly
        between two drivers.
        run_commands: sends a command or list of commands over the device conn
        """
        local_cmds = []

        if send_enable:
            self._connection.enable()

        if encoding == "json":
            # for json encoding, lets try to run cmds using | json
            cmds, local_cmds = self.get_cmds(cmds=cmds)
        elif encoding == "text" and isinstance(cmds, list):
            local_cmds = cmds.copy()
        else:
            # when cmds is a string and encoding is text
            local_cmds = cmds

        if isinstance(cmds, list):
            cmds_op = self.send_list_cmds(cmds=local_cmds, encoding=encoding)
        elif isinstance(cmds, str):
            cmds_op = self.send_str_cmds(cmds=local_cmds, encoding=encoding)

        return cmds_op

    def get_config(self, config="running-config", params=None, as_string=False):
        """Retrieves the config from the node.
        This method will retrieve the config from the node as
        either a string or a list object. The config to retrieve
        can be specified as either the startup-config or the running-config.
        """
        if config not in ["startup-config", "running-config"]:
            raise TypeError("invalid config name specified")
        command = f"show {config}"
        if params:
            command += f" {params}"

        result = self.run_commands(command, "text")
        if as_string:
            return str(result[0]["output"]).strip()

        return str(result[0]["output"]).split("\n")

    def enable(self, commands, encoding="json", strict=False, send_enable=True, **kwargs):
        """Sends the array of commands to the node in enable mode
        This method will send the commands to the node and
        evaluate the results. If a command fails due to an
        encoding error, then the command set will be re-issued
        individual with text encoding.
        """
        commands = make_iterable(commands)

        if "configure" in commands:
            raise TypeError("config mode commands not supported")

        results = []
        if strict:
            responses = self.run_commands(commands, encoding, send_enable, **kwargs)
            for index, response in enumerate(responses):
                results.append(
                    {
                        "command": commands[index],
                        "result": response,
                        "response": response,
                        "encoding": encoding,
                    }
                )
        else:
            for command in commands:
                try:
                    resp = self.run_commands(command, encoding, send_enable, **kwargs)
                    results.append({"command": command, "result": resp[0], "encoding": encoding})
                except CommandError:
                    # if encoding is json probably we need to run this cmd using text
                    if encoding == "json":
                        resp = self.run_commands(command, "text", send_enable, **kwargs)
                        results.append({"command": command, "result": resp[0], "encoding": "text"})
                    else:
                        raise
        return results

    def config(self, commands, **kwargs):
        """Configures the node with the specified commands.
        This method is used to send configuration commands
        to the node. It will take either a string or a list and
        prepend the necessary commands to put the session into
        config mode.
        """
        commands = make_iterable(commands)
        commands = list(commands)

        self._connection.enable()
        response = self._connection.send_config_set(commands)

        return response
