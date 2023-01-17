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

import configparser
import pyeapi
from netmiko.ssh_autodetect import SSHDetect
from netmiko import Netmiko
import json
from vane.utils import make_iterable

error_responses = [
    '% This is an unconverted command\n{\n    "errors": [\n        "This is an unconverted command"\n    ]\n}',
    '% Invalid input',
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
        super(CommandError, self).__init__(message)

    @property
    def trace(self):
        return self.get_trace()

    def get_trace(self):
        trace = list()
        index = None

        for index, out in enumerate(self.error_text):
            _entry = {'command': self.commands[index], 'output': out}
            trace.append(_entry)

        if index:
            index += 1
            for cmd in self.commands[index:]:
                _entry = {'command': cmd, 'output': None}
                trace.append(_entry)

        return trace

class DeviceConn:
    """ Base class for connecting to Arista devices """

    def set_conn_params(self, conf_file):
        """Set the Device connection parameters"""
        pass

    def set_up_conn(self, device_name: str):
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
    """ PyeapiConn connects to Arista devices using PyEAPI """

    def connection(self):
        """ returns the connection object """
        return self._connection

    def set_conn_params(self, conf_file):
        """ sets the config using eapi conf_file """
        pyeapi.load_config(conf_file)

    def set_up_conn(self, device_name):
        """ connects to device using pyeapi """
        self._connection = pyeapi.connect_to(device_name)

    def run_commands(self, cmds, encoding='json', send_enable=True, **kwargs):
        """ wrapper around pyeapi run_commands func """
        output = self._connection.run_commands(cmds, encoding, send_enable)
        return output

    def get_config(self, config='running-config', params=None,
                   as_string=False):
        """ wrapper around pyeapi get_config func """
        output = self._connection.get_config(config, params, as_string)
        return output

    def enable(self, commands, encoding='json', strict=False,
               send_enable=True, **kwargs):
       """ wrapper around pyeapi enable func """
       output = self._connection.enable(commands, encoding, strict, send_enable, **kwargs)
       return output

    def config(self, commands, **kwargs):
       """ wrapper around pyeapi config func """
       output = self._connection.config(commands, **kwargs)
       return output

class NetmikoConn(DeviceConn):
    """ NetmikoConn connects to Arista devices using ssh conn """

    def connection(self):
        """ returns the connection object """
        return self._connection

    def set_conn_params(self, conf_file):
        """ Sets the connection params specified in conf_file """
        self._config = configparser.ConfigParser()
        self._config.read(conf_file)

    def set_up_conn(self, device_name):
        """ sets up conn to device using _config params """
        name = 'connection:{}'.format(device_name)
        if not self._config.has_section(name):
            raise AttributeError('connection profile not found')

        device_attributes = dict(self._config.items(name))

        default_device_type = 'arista_eos'
        remote_device = {
            'device_type': device_attributes.get('device_type', default_device_type),
            'host': device_attributes['host'],
            'username': device_attributes['username'],
            'password': device_attributes['password'],
            'secret': device_attributes.get('enable_mode_secret', ""),
        }
        if remote_device['device_type'] == 'autodetect':
            guesser = SSHDetect(**remote_device)
            remote_device['device_type'] = guesser.autodetect()
        self._connection = Netmiko(**remote_device)


    def get_cmds(self, cmds):
        """ get_cmds: converts cmds to json cmds
        cmds can be a list of commands or just one command (str)
        """
        pipe_json = ' | json'

        if type(cmds) is list:
            local_cmds = cmds.copy()
            for i, cmd in enumerate(local_cmds):
                local_cmds[i] = cmd + pipe_json

        elif type(cmds) is str:
            cmds = cmds + pipe_json
        return cmds, local_cmds
    
    def send_list_cmds(self, cmds, local_cmds, cmds_op, encoding='json'):
        """ send_list_cmds: sends the list of commands to device conn 
        and collects the output as list """

        for i, cmd in enumerate(local_cmds):
            output = self._connection.send_command(cmd)
            if output not in error_responses and encoding == 'json':
                output = json.loads(output)
            else:
                err_msg = ('Could not execute %s. '
                            'Got error: %s' % (cmds[i], output))
                raise CommandError(err_msg, cmds)

            if encoding == 'text':
                """ for text encoding, creating the
                format similar to one returned by
                eapi format"""
                text_ob = {"output": output}
                cmds_op.append(text_ob)
            else:
                cmds_op.append(output)

    def send_str_cmds(self, cmds, cmds_op, encoding='json'):
        """ send_str_cmds: sends one command to device conn """
        output = self._connection.send_command(cmds)

        if output not in error_responses and encoding == 'json':
            output = json.loads(output)
        else:
            err_msg = ('Could not execute %s. '
                        'Got error: %s' % (cmds, output))
            raise CommandError(err_msg, cmds)

        if encoding == 'text':
            text_ob = {"output": output}
            cmds_op.append(text_ob)
        else:
            cmds_op.append(output)
        
        return cmds_op


    def run_commands(self, cmds, encoding='json', send_enable=True, **kwargs):
        """ This function is added to make sure both PyeapiConn and NetmikoConn
        support same functions. This will help the code to work seemlessly 
        between two drivers.
        run_commands: sends a command or list of commands over the device conn 
        """
        local_cmds = []

        if send_enable:
            self._connection.enable()

        if encoding == 'json':
            """for json encoding, lets try to run cmds
            using | json"""
            cmds, local_cmds = self.get_cmds(cmds=cmds)

        elif encoding == 'text' and type(cmds) is list:
            local_cmds = cmds.copy()

        cmds_op = []
        if type(cmds) is list:
            cmds_op = self.send_list_cmds(cmds=cmds, local_cmds=local_cmds, cmds_op=cmds_op)
        elif type(cmds) is str:
            cmds_op = self.send_str_cmds(cmds=cmds, cmds_op=cmds_op)

        return cmds_op

    def get_config(self, config='running-config', params=None,
                   as_string=False):
        """ Retrieves the config from the node.
        This method will retrieve the config from the node as 
        either a string or a list object. The config to retrieve
        can be specified as either the startup-config or the running-config.
        """
        if config not in ['startup-config', 'running-config']:
            raise TypeError('invalid config name specified')
        command = 'show %s' % config
        if params:
            command += ' %s' % params

        result = self.run_commands(command, 'text')
        if as_string:
            return str(result[0]['output']).strip()

        return str(result[0]['output']).split('\n')

    def enable(self, commands, encoding='json', strict=False,
               send_enable=True, **kwargs):
        """ Sends the array of commands to the node in enable mode
            This method will send the commands to the node and 
            evaluate the results. If a command fails due to an
            encoding error, then the command set will be re-issued
            individual with text encoding.
        """
        commands = make_iterable(commands)

        if 'configure' in commands:
            raise TypeError('config mode commands not supported')

        results = list()
        if strict:
            responses = self.run_commands(
                                          commands,
                                          encoding,
                                          send_enable,
                                          **kwargs)
            for index, response in enumerate(responses):
                results.append(dict(command=commands[index],
                                    result=response,
                                    response=response,
                                    encoding=encoding))
        else:
            for command in commands:
                try:
                    resp = self.run_commands(
                            command,
                            encoding,
                            send_enable,
                            **kwargs)
                    results.append(dict(command=command,
                                        result=resp[0],
                                        encoding=encoding))
                except CommandError as exc:
                    if exc.error_code == 1003:
                        resp = self.run_commands(
                                command,
                                'text',
                                send_enable,
                                **kwargs)
                        results.append(dict(command=command,
                                            result=resp[0],
                                            encoding='text'))
                    else:
                        raise
        return results

    def config(self, commands, **kwargs):
        """ Configures the node with the specified commands.
            This method is used to send configuration commands
            to the node. It will take either a string or a list and
            prepend the necessary commands to put the session into
            config mode.
        """
        commands = make_iterable(commands)
        commands = list(commands)

        # push the configure command onto the command stack
        commands.insert(0, 'configure terminal')
        response = self.run_commands(commands, **kwargs)

        if self.autorefresh:
            self.refresh()

        # pop the configure command output off the stack
        response.pop(0)

        return response


