"""
device_interface.py unit tests
"""
import pytest
from vane import device_interface


def test_pyeapiconn_class(mocker):
    """Tests for PyeapiConn class"""
    output = {"output"}

    class MockPyeapiConnection:
        """Mock PyeapiConn"""

        # pylint: disable=unused-argument
        def enable_authentication(self, pwd):
            """Mock enable_authentication"""
            pass

        # pylint: disable=unused-argument
        def run_commands(self, cmds, encoding, send_enable):
            """Mock run_commands"""
            return output

        # pylint: disable=unused-argument
        def get_config(self, config="running-config", params=None, as_string=False):
            """Mock get_config"""
            return output

        # pylint: disable=unused-argument
        def enable(self, commands, encoding="json", strict=False, send_enable=True, **kwargs):
            """Mock enable"""
            return output

        def config(self, commands, **kwargs):  # pylint: disable=unused-argument
            """Mock config"""
            return output

    pyeapi_connection = MockPyeapiConnection()
    mocker.patch("pyeapi.connect", return_value=pyeapi_connection)
    obj = device_interface.PyeapiConn()
    device_data = {
        "transport": "https",
        "mgmt_ip": "bogus_ip",
        "enable_pwd": "bougus",
        "username": "bogus",
        "password": "bogus",
    }
    obj.set_up_conn(device_data)
    assert pyeapi_connection == obj.connection()

    cmds = ["cmd1"]
    test_output = obj.run_commands(cmds)
    assert test_output == output

    test_output = obj.get_config()
    assert test_output == output
    test_output = obj.enable(cmds)
    assert test_output == output
    test_output = obj.config(cmds)
    assert test_output == output


def test_netmikoconn_set_up_conn(mocker):
    """Test set_up_conn for NetmikoConn class"""
    mocker.patch("os.makedirs")
    device_data = {
        "transport": "https",
        "mgmt_ip": "bogus_ip",
        "enable_pwd": "bougus",
        "name": "bogus",
        "username": "bogus",
        "password": "bogus",
    }

    netmiko_connection = "mock conn"
    mocker.patch("netmiko.Netmiko", return_value=netmiko_connection)
    obj = device_interface.NetmikoConn()
    obj.set_up_conn(device_data)

    assert netmiko_connection == obj.connection()


def test_netmikoconn_run_commands_json(mocker):
    """Test run_commands with json encoding for NetmikoConn class"""
    device_data = {
        "transport": "https",
        "mgmt_ip": "bogus_ip",
        "enable_pwd": "bougus",
        "name": "bogus",
        "username": "bogus",
        "password": "bogus",
    }

    json_output = [
        '{\n    "memTotal": 4006912,\n    "uptime": 639730.57,\n   '
        '"modelName": "vEOS",\n    "internalVersion": "4.24.2F-18436385.4242F",\n'
        '"mfgName": "",\n    "serialNumber": "",\n    "systemMacAddress": '
        '"54:15:c8:72:11:5f",\n    "bootupTimestamp": 1695907804.0,\n    '
        '"memFree": 2958704,\n    "version": "4.24.2F",\n    "configMacAddress"'
        ': "00:00:00:00:00:00",\n    "isIntlVersion": false,\n    "internalBuildId"'
        ': "03cdce3a-550e-46a8-88e5-4b27656fd2e5",\n    "hardwareRevision": "",'
        '\n    "hwMacAddress": "00:00:00:00:00:00",\n    "architecture": "i686"\n}\n',
        '{\n    "fqdn": "DC1-L2LEAF1A",\n    "hostname": "DC1-L2LEAF1A"\n}\n',
    ]

    class MockNetmikoConn:
        """Mock NetmikoConn"""

        call = 1

        def enable(self):
            """Mock enable"""
            pass

        def send_command(self, cmd):  # pylint: disable=unused-argument
            """Mock send_command"""
            if self.call == 1:
                self.call = 0
                return json_output[0]

            return json_output[1]

    netmiko_connection = MockNetmikoConn()
    mocker.patch("netmiko.Netmiko", return_value=netmiko_connection)
    obj = device_interface.NetmikoConn()
    obj.set_up_conn(device_data)
    cmds = ["show version", "show hostname"]
    test_output = obj.run_commands(cmds, encoding="json")
    result = [
        {
            "memTotal": 4006912,
            "uptime": 639730.57,
            "modelName": "vEOS",
            "internalVersion": "4.24.2F-18436385.4242F",
            "mfgName": "",
            "serialNumber": "",
            "systemMacAddress": "54:15:c8:72:11:5f",
            "bootupTimestamp": 1695907804.0,
            "memFree": 2958704,
            "version": "4.24.2F",
            "configMacAddress": "00:00:00:00:00:00",
            "isIntlVersion": False,
            "internalBuildId": "03cdce3a-550e-46a8-88e5-4b27656fd2e5",
            "hardwareRevision": "",
            "hwMacAddress": "00:00:00:00:00:00",
            "architecture": "i686",
        },
        {"fqdn": "DC1-L2LEAF1A", "hostname": "DC1-L2LEAF1A"},
    ]
    assert test_output == result


def test_netmikoconn_run_commands_text(mocker):
    """Test run_commands with text encoding for NetmikoConn class"""
    device_data = {
        "transport": "https",
        "mgmt_ip": "bogus_ip",
        "enable_pwd": "bougus",
        "name": "bogus",
        "username": "bogus",
        "password": "bogus",
    }
    text_output = [
        " vEOS\nHardware version:      \nSerial number:         \nHardware MAC address"
        ":  5415.c872.115f\nSystem MAC address:    5415.c872.115f\n\nSoftware im"
        "age version: 4.24.2F\nArchitecture:           i686\nInternal build version"
        ": 4.24.2F-18436385.4242F\nInternal build ID:      03cdce3a-550e-46a8-88e5-"
        "4b27656fd2e5\n\nUptime:                 1 weeks, 0 days, 9 hours and 44 minut"
        "es\nTotal memory:           4006912 kB\nFree memory:            2958824 kB\n\n",
        "Hostname: DC1-L2LEAF1A\nFQDN:     DC1-L2LEAF1A\n",
    ]

    class MockNetmikoConn:
        """Mock NetmikoConn"""

        call = 1

        def send_command(self, cmd):  # pylint: disable=unused-argument
            """Mock send_command"""
            if self.call == 1:
                self.call = 0
                return text_output[0]

            return text_output[1]

        def enable(self):
            """Mock enable"""
            pass

    netmiko_connection = MockNetmikoConn()
    mocker.patch("netmiko.Netmiko", return_value=netmiko_connection)
    obj = device_interface.NetmikoConn()
    obj.set_up_conn(device_data)
    cmds = ["show version", "show hostname"]
    test_output = obj.run_commands(cmds, encoding="text")
    result = [
        {
            "output": " vEOS\nHardware version:      \nSerial number"
            ":         \nHardware MAC address:  5415.c872.115f\nSystem MAC addr"
            "ess:    5415.c872.115f\n\nSoftware image version: 4.24.2F\nArchitec"
            "ture:           i686\nInternal build version: 4.24.2F-18436385.424"
            "2F\nInternal build ID:      03cdce3a-550e-46a8-88e5-4b27656fd2e5\n\nU"
            "ptime:                 1 weeks, 0 days, 9 hours and 44 minutes\nTota"
            "l memory:           4006912 kB\nFree memory:            2958824 kB\n\n"
        },
        {"output": "Hostname: DC1-L2LEAF1A\nFQDN:     DC1-L2LEAF1A\n"},
    ]
    assert test_output == result


def test_netmikoconn_run_commands_str_json(mocker):
    """Test run_commands with only one cmd for NetmikoConn class"""
    device_data = {
        "transport": "https",
        "mgmt_ip": "bogus_ip",
        "enable_pwd": "bougus",
        "name": "bogus",
        "username": "bogus",
        "password": "bogus",
    }
    json_output = [
        '{\n    "memTotal": 4006912,\n    "uptime": 639730.57,\n   '
        '"modelName": "vEOS",\n    "internalVersion": "4.24.2F-18436385.4242F",\n'
        '"mfgName": "",\n    "serialNumber": "",\n    "systemMacAddress": '
        '"54:15:c8:72:11:5f",\n    "bootupTimestamp": 1695907804.0,\n    '
        '"memFree": 2958704,\n    "version": "4.24.2F",\n    "configMacAddress"'
        ': "00:00:00:00:00:00",\n    "isIntlVersion": false,\n    "internalBuildId"'
        ': "03cdce3a-550e-46a8-88e5-4b27656fd2e5",\n    "hardwareRevision": "",'
        '\n    "hwMacAddress": "00:00:00:00:00:00",\n    "architecture": "i686"\n}\n',
        '{\n    "fqdn": "DC1-L2LEAF1A",\n    "hostname": "DC1-L2LEAF1A"\n}\n',
    ]

    class MockNetmikoConn:
        """Mock NetmikoConn"""

        call = 1

        def enable(self):
            """Mock enable"""
            pass

        def send_command(self, cmd):  # pylint: disable=unused-argument
            """Mock send_command"""
            if self.call == 1:
                self.call = 0
                return json_output[0]

            return json_output[1]

    netmiko_connection = MockNetmikoConn()
    mocker.patch("netmiko.Netmiko", return_value=netmiko_connection)
    obj = device_interface.NetmikoConn()
    obj.set_up_conn(device_data)
    cmds = "show version"
    test_output = obj.run_commands(cmds, encoding="json")
    result = [
        {
            "memTotal": 4006912,
            "uptime": 639730.57,
            "modelName": "vEOS",
            "internalVersion": "4.24.2F-18436385.4242F",
            "mfgName": "",
            "serialNumber": "",
            "systemMacAddress": "54:15:c8:72:11:5f",
            "bootupTimestamp": 1695907804.0,
            "memFree": 2958704,
            "version": "4.24.2F",
            "configMacAddress": "00:00:00:00:00:00",
            "isIntlVersion": False,
            "internalBuildId": "03cdce3a-550e-46a8-88e5-4b27656fd2e5",
            "hardwareRevision": "",
            "hwMacAddress": "00:00:00:00:00:00",
            "architecture": "i686",
        },
    ]
    assert test_output == result


def test_netmikoconn_run_commands_str_text(mocker):
    """Test run_commands with only one cmd and text encoding
    for NetmikoConn class"""
    device_data = {
        "transport": "https",
        "mgmt_ip": "bogus_ip",
        "enable_pwd": "bougus",
        "name": "bogus",
        "username": "bogus",
        "password": "bogus",
    }
    text_output = [
        " vEOS\nHardware version:      \nSerial number:         \nHardware MAC address"
        ":  5415.c872.115f\nSystem MAC address:    5415.c872.115f\n\nSoftware im"
        "age version: 4.24.2F\nArchitecture:           i686\nInternal build version"
        ": 4.24.2F-18436385.4242F\nInternal build ID:      03cdce3a-550e-46a8-88e5-"
        "4b27656fd2e5\n\nUptime:                 1 weeks, 0 days, 9 hours and 44 minut"
        "es\nTotal memory:           4006912 kB\nFree memory:            2958824 kB\n\n",
        "Hostname: DC1-L2LEAF1A\nFQDN:     DC1-L2LEAF1A\n",
    ]

    class MockNetmikoConn:
        """Mock NetmikoConn"""

        call = 1

        def send_command(self, cmd):  # pylint: disable=unused-argument
            """Mock send_command"""
            if self.call == 1:
                self.call = 0
                return text_output[0]

            return text_output[1]

        def enable(self):
            """Mock enable"""
            pass

    netmiko_connection = MockNetmikoConn()
    mocker.patch("netmiko.Netmiko", return_value=netmiko_connection)
    obj = device_interface.NetmikoConn()
    obj.set_up_conn(device_data)
    cmds = "show version"
    test_output = obj.run_commands(cmds, encoding="text")
    result = [
        {
            "output": " vEOS\nHardware version:      \nSerial number"
            ":         \nHardware MAC address:  5415.c872.115f\nSystem MAC addr"
            "ess:    5415.c872.115f\n\nSoftware image version: 4.24.2F\nArchitec"
            "ture:           i686\nInternal build version: 4.24.2F-18436385.424"
            "2F\nInternal build ID:      03cdce3a-550e-46a8-88e5-4b27656fd2e5\n\nU"
            "ptime:                 1 weeks, 0 days, 9 hours and 44 minutes\nTota"
            "l memory:           4006912 kB\nFree memory:            2958824 kB\n\n"
        },
    ]
    assert test_output == result


def test_netmikoconn_get_config(mocker):
    """Test get_config methond for NetmikoConn class"""
    device_data = {
        "transport": "https",
        "mgmt_ip": "bogus_ip",
        "enable_pwd": "bougus",
        "name": "bogus",
        "username": "bogus",
        "password": "bogus",
    }
    with open("tests/unittests/fixtures/show_running.txt", encoding="utf_8") as file:
        show_running = file.read()
    text_output = [show_running]

    class MockNetmikoConn:
        """Mock NetmikoConn"""

        def send_command(self, cmd):  # pylint: disable=unused-argument
            """Mock send_command"""
            return text_output[0]

        def enable(self):
            """Mock enable"""
            pass

    netmiko_connection = MockNetmikoConn()
    mocker.patch("netmiko.Netmiko", return_value=netmiko_connection)
    obj = device_interface.NetmikoConn()
    obj.set_up_conn(device_data)
    with pytest.raises(TypeError):
        obj.get_config(config="bogus")
    test_output = obj.get_config(params="blah")
    assert test_output[0].strip() == show_running.strip()
    test_output = obj.get_config(as_string=True)

    assert test_output.strip() == show_running.strip()


def test_netmikoconn_enable_strict(mocker):
    """Test enable with strict flag for NetmikoConn class"""
    device_data = {
        "transport": "https",
        "mgmt_ip": "bogus_ip",
        "enable_pwd": "bougus",
        "name": "bogus",
        "username": "bogus",
        "password": "bogus",
    }
    show_version_op = (
        " vEOS\nHardware version:      \nSerial number:         \nHardware MAC address"
        ":  5415.c872.115f\nSystem MAC address:    5415.c872.115f\n\nSoftware im"
        "age version: 4.24.2F\nArchitecture:           i686\nInternal build version"
        ": 4.24.2F-18436385.4242F\nInternal build ID:      03cdce3a-550e-46a8-88e5-"
        "4b27656fd2e5\n\nUptime:                 1 weeks, 0 days, 9 hours and 44 minut"
        "es\nTotal memory:           4006912 kB\nFree memory:            2958824 kB\n\n"
    )

    show_hostname_op = "Hostname: DC1-L2LEAF1A\nFQDN:     DC1-L2LEAF1A\n"
    text_output = [show_version_op, show_hostname_op]

    class MockNetmikoConn:
        """Mock NetmikoConn"""

        call = 1

        def send_command(self, cmd):  # pylint: disable=unused-argument
            """Mock send_command"""
            if self.call == 1:
                self.call = 0
                return text_output[0]

            return text_output[1]

        def enable(self):
            """Mock enable"""
            pass

    netmiko_connection = MockNetmikoConn()
    mocker.patch("netmiko.Netmiko", return_value=netmiko_connection)
    obj = device_interface.NetmikoConn()
    obj.set_up_conn(device_data)
    cmds = ["show version", "show hostname"]
    test_output = obj.enable(cmds, strict=True, encoding="text")
    result = [
        {
            "command": "show version",
            "result": {"output": show_version_op},
            "response": {"output": show_version_op},
            "encoding": "text",
        },
        {
            "command": "show hostname",
            "result": {"output": show_hostname_op},
            "response": {"output": show_hostname_op},
            "encoding": "text",
        },
    ]
    assert test_output == result


def test_netmikoconn_run_commands_json_error(mocker):
    """Test run_commands for NetmikoConn class when cmd
    is an uncoverted text-only cmd"""
    device_data = {
        "transport": "https",
        "mgmt_ip": "bogus_ip",
        "enable_pwd": "bougus",
        "name": "bogus",
        "username": "bogus",
        "password": "bogus",
    }
    error_output = """% This is an unconverted command
{
    "errors": [
        "This is an unconverted command"
    ]
}"""
    json_output = [
        '{\n    "memTotal": 4006912,\n    "uptime": 639730.57,\n   '
        '"modelName": "vEOS",\n    "internalVersion": "4.24.2F-18436385.4242F",\n'
        '"mfgName": "",\n    "serialNumber": "",\n    "systemMacAddress": '
        '"54:15:c8:72:11:5f",\n    "bootupTimestamp": 1695907804.0,\n    '
        '"memFree": 2958704,\n    "version": "4.24.2F",\n    "configMacAddress"'
        ': "00:00:00:00:00:00",\n    "isIntlVersion": false,\n    "internalBuildId"'
        ': "03cdce3a-550e-46a8-88e5-4b27656fd2e5",\n    "hardwareRevision": "",'
        '\n    "hwMacAddress": "00:00:00:00:00:00",\n    "architecture": "i686"\n}\n',
        '{\n    "fqdn": "DC1-L2LEAF1A",\n    "hostname": "DC1-L2LEAF1A"\n}\n',
    ]

    class MockNetmikoConn:
        """Mock NetmikoConn"""

        call = 1

        def enable(self):
            """mock enable"""
            pass

        def send_command(self, cmd):  # pylint: disable=unused-argument
            """mock send_command"""
            if self.call == 1:
                self.call = 0
                return error_output

            if self.call == 0:
                self.call = 2
                return json_output[0]

            return json_output[1]

    netmiko_connection = MockNetmikoConn()
    mocker.patch("netmiko.Netmiko", return_value=netmiko_connection)
    obj = device_interface.NetmikoConn()
    obj.set_up_conn(device_data)

    cmds = ["show version", "show hostname"]
    with pytest.raises(device_interface.CommandError):
        obj.run_commands(cmds, encoding="json")


def test_netmikoconn_enable_double_json_error(mocker):
    """Test enable for NetmikoConn class when cmd
    does not run in both json and text encoding"""
    device_data = {
        "transport": "https",
        "mgmt_ip": "bogus_ip",
        "enable_pwd": "bougus",
        "name": "bogus",
        "username": "bogus",
        "password": "bogus",
    }
    error_output = """% This is an unconverted command
{
    "errors": [
        "This is an unconverted command"
    ]
}"""

    class MockNetmikoConn:
        """Mock NetmikoConn"""

        def enable(self):
            """Mock enable"""
            pass

        def send_command(self, cmd):  # pylint: disable=unused-argument
            """Mock send_command"""
            return error_output

    netmiko_connection = MockNetmikoConn()
    mocker.patch("netmiko.Netmiko", return_value=netmiko_connection)
    obj = device_interface.NetmikoConn()
    obj.set_up_conn(device_data)

    cmds = ["show logging"]
    with pytest.raises(device_interface.CommandError):
        obj.enable(cmds, encoding="text")


def test_netmikoconn_enable_json_error(mocker):
    """Test enable func for NetmikoConn class with cmd
    only available in text mode"""
    device_data = {
        "transport": "https",
        "mgmt_ip": "bogus_ip",
        "enable_pwd": "bougus",
        "name": "bogus",
        "username": "bogus",
        "password": "bogus",
    }
    error_output = """% This is an unconverted command
{
    "errors": [
        "This is an unconverted command"
    ]
}"""
    json_output = [
        '{\n    "memTotal": 4006912,\n    "uptime": 639730.57,\n   '
        '"modelName": "vEOS",\n    "internalVersion": "4.24.2F-18436385.4242F",\n'
        '"mfgName": "",\n    "serialNumber": "",\n    "systemMacAddress": '
        '"54:15:c8:72:11:5f",\n    "bootupTimestamp": 1695907804.0,\n    '
        '"memFree": 2958704,\n    "version": "4.24.2F",\n    "configMacAddress"'
        ': "00:00:00:00:00:00",\n    "isIntlVersion": false,\n    "internalBuildId"'
        ': "03cdce3a-550e-46a8-88e5-4b27656fd2e5",\n    "hardwareRevision": "",'
        '\n    "hwMacAddress": "00:00:00:00:00:00",\n    "architecture": "i686"\n}\n',
    ]

    class MockNetmikoConn:
        """Mock NetmikoConn"""

        call = 1

        def enable(self):
            """Mock enable"""
            pass

        def send_command(self, cmd):  # pylint: disable=unused-argument
            """Mock send_command"""
            if self.call == 1:
                self.call = 0
                return error_output

            return json_output[0]

    netmiko_connection = MockNetmikoConn()
    mocker.patch("netmiko.Netmiko", return_value=netmiko_connection)
    obj = device_interface.NetmikoConn()
    obj.set_up_conn(device_data)

    cmds = ["show logging"]
    test_output = obj.enable(cmds, encoding="json")
    result = [
        {
            "command": "show logging",
            "result": {
                "output": '{\n    "memTotal": 4006912,\n    "uptime": 639730.57,'
                '\n   "modelName": "vEOS",\n    "internalVersion": "4.24.2'
                'F-18436385.4242F",\n"mfgName": "",\n    "serialNumber": ""'
                ',\n    "systemMacAddress": "54:15:c8:72:11:5f",\n    "bootu'
                'pTimestamp": 1695907804.0,\n    "memFree": 2958704,\n    "ver'
                'sion": "4.24.2F",\n    "configMacAddress": "00:00:00:00:00:'
                '00",\n    "isIntlVersion": false,\n    "internalBuildId": "0'
                '3cdce3a-550e-46a8-88e5-4b27656fd2e5",\n    "hardwareRevisio'
                'n": "",\n    "hwMacAddress": "00:00:00:00'
                ':00:00",\n    "architecture": "i686"\n}\n'
            },
            "encoding": "text",
        }
    ]
    assert test_output == result


def test_netmikoconn_enable_json(mocker):
    """Test enable with json encoding for NetmikoConn class"""
    device_data = {
        "transport": "https",
        "mgmt_ip": "bogus_ip",
        "enable_pwd": "bougus",
        "name": "bogus",
        "username": "bogus",
        "password": "bogus",
    }
    json_output = [
        '{\n    "memTotal": 4006912,\n    "uptime": 639730.57,\n   '
        '"modelName": "vEOS",\n    "internalVersion": "4.24.2F-18436385.4242F",\n'
        '"mfgName": "",\n    "serialNumber": "",\n    "systemMacAddress": '
        '"54:15:c8:72:11:5f",\n    "bootupTimestamp": 1695907804.0,\n    '
        '"memFree": 2958704,\n    "version": "4.24.2F",\n    "configMacAddress"'
        ': "00:00:00:00:00:00",\n    "isIntlVersion": false,\n    "internalBuildId"'
        ': "03cdce3a-550e-46a8-88e5-4b27656fd2e5",\n    "hardwareRevision": "",'
        '\n    "hwMacAddress": "00:00:00:00:00:00",\n    "architecture": "i686"\n}\n',
        '{\n    "fqdn": "DC1-L2LEAF1A",\n    "hostname": "DC1-L2LEAF1A"\n}\n',
    ]

    class MockNetmikoConn:
        """Mock NetmikoConn"""

        call = 1

        def enable(self):
            """Mock enable"""
            pass

        def send_command(self, cmd):  # pylint: disable=unused-argument
            """Mock send_command"""
            if self.call == 1:
                self.call = 0
                return json_output[0]

            return json_output[1]

    netmiko_connection = MockNetmikoConn()
    mocker.patch("netmiko.Netmiko", return_value=netmiko_connection)
    obj = device_interface.NetmikoConn()
    obj.set_up_conn(device_data)

    with pytest.raises(TypeError):
        obj.enable(["configure terminal"])
    with pytest.raises(TypeError):
        obj.enable(["conf t"])

    cmds = ["show version", "show hostname"]
    test_output = obj.enable(cmds, encoding="json")
    result = [
        {
            "command": "show version",
            "result": {
                "memTotal": 4006912,
                "uptime": 639730.57,
                "modelName": "vEOS",
                "internalVersion": "4.24.2F-18436385.4242F",
                "mfgName": "",
                "serialNumber": "",
                "systemMacAddress": "54:15:c8:72:11:5f",
                "bootupTimestamp": 1695907804.0,
                "memFree": 2958704,
                "version": "4.24.2F",
                "configMacAddress": "00:00:00:00:00:00",
                "isIntlVersion": False,
                "internalBuildId": "03cdce3a-550e-46a8-88e5-4b27656fd2e5",
                "hardwareRevision": "",
                "hwMacAddress": "00:00:00:00:00:00",
                "architecture": "i686",
            },
            "encoding": "json",
        },
        {
            "command": "show hostname",
            "result": {"fqdn": "DC1-L2LEAF1A", "hostname": "DC1-L2LEAF1A"},
            "encoding": "json",
        },
    ]
    assert test_output == result


def test_netmikoconn_config(mocker):
    """Test config func for NetmikoConn class"""
    device_data = {
        "transport": "https",
        "mgmt_ip": "bogus_ip",
        "enable_pwd": "bougus",
        "name": "bogus",
        "username": "bogus",
        "password": "bogus",
    }

    class MockNetmikoConn:
        """Mock NetmikoConn"""

        def enable(self):
            """Mock enable"""
            pass

        def send_config_set(self, cmds):  # pylint: disable=unused-argument
            """Mock send_config_set"""
            return ""

    netmiko_connection = MockNetmikoConn()
    mocker.patch("netmiko.Netmiko", return_value=netmiko_connection)
    obj = device_interface.NetmikoConn()
    obj.set_up_conn(device_data)
    cmds = ["interface ethernet1", "description test"]
    test_output = obj.config(cmds)
    result = ""
    assert test_output == result


def test_create_command_error():
    """Test CommandError exception creation"""
    result = device_interface.CommandError("test message", ["test command"])
    assert isinstance(result, device_interface.CommandError)


def test_command_error_trace():
    """Test CommandError exception get_trace method"""
    commands = ["test command", "test command", "test command"]
    output = [{}, "test output"]
    result = device_interface.CommandError(output, commands).get_trace()
    assert result is not None
