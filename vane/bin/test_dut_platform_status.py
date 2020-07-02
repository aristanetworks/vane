#!/usr/bin/python3
#
# Copyright (c) 2019, Arista Networks EOS+
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

""" Tests to validate platform status."""

from pprint import pprint
import pytest
from . import common_nrfu_infra
import os
from . import definitions

# List EOS show commands to use in test cases
EOS_SHOW_CMDS = ["show hostname",
                 "show system environment temperature",
                 "show system environment power",
                 "show system environment cooling",
                 "show logging",
                 "show processes",
                 "show hardware capacity utilization percent exceed 10",
                 "show version",
                 "show inventory"]

# PyTest from Test Engine 
if os.path.isfile(definitions.TEST_DEFINITION_FILE): 
    TEST_DEFINITION = common_nrfu_infra.import_test_definition()
    CONNECTION_LIST = common_nrfu_infra.generate_connection_list(TEST_DEFINITION)
    common_nrfu_infra.open_log_file()
    TEST_SUITE = __file__.split("/")[-1]
    DUTS = common_nrfu_infra.generate_dut_info_threaded(EOS_SHOW_CMDS, TEST_SUITE)
#Native PyTest
else:
    XLSX_WORKBOOK = common_nrfu_infra.import_spreadsheet()
    CONNECTION_LIST = common_nrfu_infra.return_connection_list(XLSX_WORKBOOK)
    common_nrfu_infra.open_log_file()
    TEST_SUITE = __file__.split("/")[-1]
    DUTS = common_nrfu_infra.return_dut_info_threaded(EOS_SHOW_CMDS, TEST_SUITE)

@pytest.mark.xpass
def test_assert_true():
    """ Prior to running any tests this test Validates that PyTest is working
        correct by verifying PyTest can assert True.
    """

    assert True

@pytest.mark.parametrize("dut", DUTS, ids=CONNECTION_LIST)
def test_show_hostname(dut):
    """ Verify hostname is set on device is correct

        Args:
          dut (dict): Encapsulates dut details including name, connection
    """

    show_cmd = "show hostname"
    eos_hostname = dut["output"][show_cmd]["json"]["hostname"]
    correct_hostname = dut['name']

    print(f"\nOn router |{dut['name']}| the configured hostname is \
|{eos_hostname}| and the correct hostname is |{correct_hostname}|")

    assert eos_hostname == correct_hostname


@pytest.mark.parametrize("dut", DUTS, ids=CONNECTION_LIST)
def test_show_system_environment_all(dut):
    """ Verify system environmentals are functional within spec

        Args:
          dut (dict): Encapsulates dut details including name, connection
    """

    test_show_system_environment_temperature(dut)
    test_show_system_environment_power(dut)
    test_show_system_environment_cooling(dut)


@pytest.mark.parametrize("dut", DUTS, ids=CONNECTION_LIST)
def test_show_system_environment_temperature(dut):
    """ Verify system temperature environmentals are functional within spec

        Args:
          dut (dict): Encapsulates dut details including name, connection
    """

    show_cmd = "show system environment temperature"
    eos_system_status = dut["output"][show_cmd]["json"]["systemStatus"]
    eos_power_supply_slots = dut["output"][show_cmd]["json\
"]["powerSupplySlots"]
    eos_temp_sensors = dut["output"][show_cmd]["json"]["tempSensors"]

    print(f"\nOn router |{dut['name']}| system temperature is \
|{eos_system_status}|")

    assert eos_system_status == 'temperatureOk'

    for powersupply in eos_power_supply_slots:
        for temp_sensors in powersupply['tempSensors']:
            print(f"Power-supply temperature sensor |{temp_sensors['name']}| \
alert state is |{temp_sensors['inAlertState']}|")

            assert temp_sensors['inAlertState'] is False

    for temp_sensor in eos_temp_sensors:
        print(f"Temperature sensor |{temp_sensor['name']}| alert state is \
|{temp_sensor['inAlertState']}|")

        assert temp_sensor['inAlertState'] is False


@pytest.mark.parametrize("dut", DUTS, ids=CONNECTION_LIST)
def test_show_system_environment_power(dut):
    """ Verify system power environmentals are functional within spec

        Args:
          dut (dict): Encapsulates dut details including name, connection
    """

    show_cmd = "show system environment power"
    eos_power_supplies = dut["output"][show_cmd]["json"]["powerSupplies"]

    print(f"\nOn router |{dut['name']}|")

    for powersupply in eos_power_supplies:
        print(f"Power Supply |{powersupply}| state is \
|{eos_power_supplies[powersupply]['state']}|")

        assert eos_power_supplies[powersupply]['state'] == 'ok'


@pytest.mark.parametrize("dut", DUTS, ids=CONNECTION_LIST)
def test_show_system_environment_cooling(dut):
    """ Verify system cooling environmentals are functional within spec

        Args:
          dut (dict): Encapsulates dut details including name, connection
    """

    show_cmd = "show system environment cooling"
    eos_system_status = dut["output"][show_cmd]["json"]["systemStatus"]

    print(f"\nOn router |{dut['name']}| system cooling status is \
|{eos_system_status}|")

    assert eos_system_status == 'coolingOk'


@pytest.mark.parametrize("dut", DUTS, ids=CONNECTION_LIST)
@pytest.mark.xfail
def test_show_module_all(dut):
    """ NO AUTOMATED TEST.  MUST TEST MANUALLY

        Args:
          dut (dict): Encapsulates dut details including name, connection
    """

    print(f"\nOn router |{dut['name']}|")
    print(f"\nNO AUTOMATED TEST.  MUST TEST MANUALLY")

    assert False


@pytest.mark.parametrize("dut", DUTS, ids=CONNECTION_LIST)
@pytest.mark.xfail
def test_show_redundancy_states(dut):
    """ NO AUTOMATED TEST.  MUST TEST MANUALLY

        Args:
          dut (dict): Encapsulates dut details including name, connection
    """

    print(f"\nOn router |{dut['name']}|")
    print(f"\nNO AUTOMATED TEST.  MUST TEST MANUALLY")

    assert False


@pytest.mark.parametrize("dut", DUTS, ids=CONNECTION_LIST)
def test_show_logging_errors(dut):
    """ Verify system environmentals are functional within spec

        Args:
          dut (dict): Encapsulates dut details including name, connection
    """

    test_show_logging_ecc_errors(dut)
    test_show_logging_server_errors(dut)
    test_show_logging_parity_errors(dut)


@pytest.mark.parametrize("dut", DUTS, ids=CONNECTION_LIST)
def test_show_logging_ecc_errors(dut):
    """ Verify log messages does not have ECC errors, servers errors, parity errors

        Args:
          dut (dict): Encapsulates dut details including name, connection
    """

    show_cmd = "show logging"
    eos_show_logging = dut["output"][show_cmd]["text"]

    print(f"\nOn router |{dut['name']}| logs:\n{eos_show_logging}")

    assert ("ECC" in eos_show_logging) is False


@pytest.mark.parametrize("dut", DUTS, ids=CONNECTION_LIST)
def test_show_logging_server_errors(dut):
    """ Verify log messages does not have ECC errors, servers errors, parity errors

        Args:
          dut (dict): Encapsulates dut details including name, connection
    """

    show_cmd = "show logging"
    eos_show_logging = dut["output"][show_cmd]["text"]

    print(f"\nOn router |{dut['name']}| logs:\n{eos_show_logging}")

    assert ("servers errors" in eos_show_logging) is False


@pytest.mark.parametrize("dut", DUTS, ids=CONNECTION_LIST)
def test_show_logging_parity_errors(dut):
    """ Verify log messages does not have ECC errors, servers errors, parity errors

        Args:
          dut (dict): Encapsulates dut details including name, connection
    """

    show_cmd = "show logging"
    eos_show_logging = dut["output"][show_cmd]["text"]

    print(f"\nOn router |{dut['name']}| logs:\n{eos_show_logging}")

    assert ("parity" in eos_show_logging) is False


@pytest.mark.parametrize("dut", DUTS, ids=CONNECTION_LIST)
def test_show_processes(dut):
    """ Verify system environmentals are functional within spec

        Args:
          dut (dict): Encapsulates dut details including name, connection
    """

    test_show_processes_1second(dut)
    test_show_processes_1minute(dut)
    test_show_processes_5minutes(dut)


@pytest.mark.parametrize("dut", DUTS, ids=CONNECTION_LIST)
def test_show_processes_1second(dut):
    """ Verify CPU is under 10%

        Args:
          dut (dict): Encapsulates dut details including name, connection
    """

    show_cmd = "show processes"
    eos_load_avg = dut["output"][show_cmd]["json"]["timeInfo"]["loadAvg"][0]

    print(f"\nOn router |{dut['name']}| 1 second CPU load average is \
|{eos_load_avg}%| and should be under |10%|")

    assert eos_load_avg < 10


@pytest.mark.parametrize("dut", DUTS, ids=CONNECTION_LIST)
def test_show_processes_1minute(dut):
    """ Verify CPU is under 10%

        Args:
          dut (dict): Encapsulates dut details including name, connection
    """

    show_cmd = "show processes"
    eos_load_avg = dut["output"][show_cmd]["json"]["timeInfo"]["loadAvg"][1]

    print(f"\nOn router |{dut['name']}| 1 minute CPU load average is \
|{eos_load_avg}%| and should be under |10%|")

    assert eos_load_avg < 10


@pytest.mark.parametrize("dut", DUTS, ids=CONNECTION_LIST)
def test_show_processes_5minutes(dut):
    """ Verify CPU is under 10%

        Args:
          dut (dict): Encapsulates dut details including name, connection
    """

    show_cmd = "show processes"
    eos_load_avg = dut["output"][show_cmd]["json"]["timeInfo"]["loadAvg"][2]

    print(f"\nOn router |{dut['name']}| 5 minutes CPU load average is \
|{eos_load_avg}%| and should be under |10%|")

    assert eos_load_avg < 10


@pytest.mark.parametrize("dut", DUTS, ids=CONNECTION_LIST)
def test_show_hardware_capacity_utilization(dut):
    """ Verify hardware capacty utilization is not exceeding 10%

        Args:
          dut (dict): Encapsulates dut details including name, connection
    """

    show_cmd = "show hardware capacity utilization percent exceed 10"
    eos_hw_tables = len(dut["output"][show_cmd]["json"]["tables"])

    print(f"\nOn router |{dut['name']}|, |{eos_hw_tables}| \
hardware capacity tables exceeds 10% utilization and there should be |0|")

    assert eos_hw_tables == 0


@pytest.mark.parametrize("dut", DUTS, ids=CONNECTION_LIST)
def test_show_memory(dut):
    """ Verify memory is not exceeding 70%

        Args:
          dut (dict): Encapsulates dut details including name, connection
    """

    show_cmd = "show version"
    eos_memory_total = dut["output"][show_cmd]["json"]['memTotal']
    eos_memory_free = dut["output"][show_cmd]["json"]['memFree']
    memory_percent = 0.00
    memory_percent = (float(eos_memory_free) / float(eos_memory_total)) * 100

    print(f"\nOn router |dut['name']| memory utilization percent is \
|{memory_percent}%| and should be under 70%")

    assert memory_percent < 70


@pytest.mark.parametrize("dut", DUTS, ids=CONNECTION_LIST)
@pytest.mark.xfail
def test_show_inventory(dut):
    """ Verify inventory is correct

        Args:
          dut (dict): Encapsulates dut details including name, connection
    """

    print(f"\nOn router |{dut['name']}|")
    print(f"\nNO AUTOMATED TEST.  MUST TEST MANUALLY")

    assert False
