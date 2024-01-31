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

""" Tests to validate vane functionality."""

import pprint
import time
import pytest
from pyeapi.eapilib import EapiError
from vane import tests_tools, test_case_logger


TEST_SUITE = __file__
LOG_FILE = {"parameters": {"show_log": "show_output.log"}}

logging = test_case_logger.setup_logger(__file__)


@pytest.mark.vane_system_tests
class VaneTests:
    """Vane Test Suite"""

    def test_if_remove_comments_work(self, dut, tests_definitions):
        """TD: Verifies if setup comments work

        Args:
          dut (dict): Encapsulates dut details including name, connection
        """

        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)

        try:
            """
            TS: Run cmds 'show hostname' again
            """
            self.output = tops.run_show_cmds(tops.show_cmd)

            tops.actual_output = self.output[0]["result"]["hostname"]

        except (AttributeError, LookupError, EapiError) as exception:
            logging.error(
                f"On device {tops.dut_name}: Error while running testcase on DUT is: "
                f"{str(exception)}"
            )
            tops.actual_output = str(exception)
            tops.output_msg += (
                f"EXCEPTION encountered on device {tops.dut_name}, while "
                f"investigating if setup commnets can be specified. "
                f"Vane recorded error: {exception}"
            )

        """
        TS: Compare latest o/p with expected output
        """
        tops.parse_test_steps(self.test_if_remove_comments_work)
        tops.test_result = tops.actual_output == tops.expected_output
        tops.generate_report(tops.dut_name, tops.output_msg)
        assert tops.actual_output == tops.expected_output

    def test_if_ssh_json_cmds_run(self, dut, tests_definitions):
        """TD: Verifies cmds run using ssh and output is same as eapi

        Args:
          dut (dict): Encapsulates dut details including name, connection
        """

        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)

        try:
            tops.show_cmds[tops.dut_name] = ["show ntp status", "show bgp summary"]

            """
            TS: Run cmds using eapi and ssh using json encoding
            """
            eapi_output = tops.run_show_cmds(tops.show_cmds[tops.dut_name], conn_type="eapi")
            ssh_output = tops.run_show_cmds(tops.show_cmds[tops.dut_name], conn_type="ssh")

            """
            TS: Compare eapi and ssh outputs
            """
            tops.actual_output, tops.expected_output = (
                ssh_output,
                eapi_output,
            )

        except (AttributeError, LookupError, EapiError) as exception:
            logging.error(
                f"On device {tops.dut_name}: Error while running testcase on DUT is: "
                f"{str(exception)}"
            )
            tops.actual_output = str(exception)
            tops.output_msg += (
                f"EXCEPTION encountered on device {tops.dut_name}, while "
                f"investigating if ssh can be used to run cmds. Vane recorded error: {exception}"
            )

        tops.parse_test_steps(self.test_if_ssh_json_cmds_run)
        tops.test_result = tops.actual_output == tops.expected_output
        tops.generate_report(tops.dut_name, tops.output_msg)
        assert tops.actual_output == tops.expected_output

    def test_if_ssh_text_cmds_run(self, dut, tests_definitions):
        """TD: Verifies cmds run using ssh and output is same as eapi

        Args:
          dut (dict): Encapsulates dut details including name, connection
        """

        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)

        try:
            tops.show_cmds[tops.dut_name] = ["show ntp status", "show bgp summary"]

            """
            TS: Run cmds using eapi and ssh using text encoding
            """
            eapi_output = tops.run_show_cmds(
                tops.show_cmds[tops.dut_name], conn_type="eapi", encoding="text"
            )
            ssh_output = tops.run_show_cmds(
                tops.show_cmds[tops.dut_name], conn_type="ssh", encoding="text"
            )

            """
            TS: Compare eapi and ssh outputs
            """
            tops.actual_output, tops.expected_output = (
                pprint.pprint(ssh_output),
                pprint.pprint(eapi_output),
            )

        except (AttributeError, LookupError, EapiError) as exception:
            logging.error(
                f"On device {tops.dut_name}: Error while running testcase on DUT is: "
                f"{str(exception)}"
            )
            tops.actual_output = str(exception)
            tops.output_msg += (
                f"EXCEPTION encountered on device {tops.dut_name}, while "
                f"investigating if ssh can be used to run cmds. Vane recorded error: {exception}"
            )

        tops.parse_test_steps(self.test_if_ssh_text_cmds_run)
        tops.test_result = tops.actual_output == tops.expected_output
        tops.generate_report(tops.dut_name, tops.output_msg)
        assert tops.actual_output == tops.expected_output

    def test_if_ssh_can_run_show_tech_support(self, dut, tests_definitions):
        """TD: Verifies cmds run using ssh and output is same as eapi

        Args:
          dut (dict): Encapsulates dut details including name, connection
        """

        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)

        try:
            """
            TS: Run 'show tech-support' using ssh conn and text encoding
            """
            tops.show_cmds[tops.dut_name] = ["show tech-support"]

            tops.actual_output = tops.run_show_cmds(
                tops.show_cmds[tops.dut_name], conn_type="ssh", encoding="text"
            )

        except (AttributeError, LookupError, EapiError) as exception:
            logging.error(
                f"On device {tops.dut_name}: Error while running testcase on DUT is: "
                f"{str(exception)}"
            )
            tops.actual_output = str(exception)
            tops.output_msg += (
                f"EXCEPTION encountered on device {tops.dut_name}, while "
                f"investigating if ssh can be used to run cmds. Vane recorded error: {exception}"
            )

        """
        TS: Verify 'show tech-support' output should be non-empty
        """
        tops.parse_test_steps(self.test_if_ssh_can_run_show_tech_support)
        tops.test_result = tops.actual_output != ""
        tops.generate_report(tops.dut_name, tops.output_msg)
        assert tops.actual_output != ""

    def test_if_ssh_can_run_ping_cmd(self, dut, tests_definitions):
        """TD: Verifies cmds run using ssh and output is same as eapi

        Args:
          dut (dict): Encapsulates dut details including name, connection
        """

        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)

        try:
            """
            TS: Run 'ping x.x.x.x' using ssh conn and text encoding
            """
            cmd = f"ping {tops.test_parameters['input']['ping_ip']}"
            tops.show_cmds[tops.dut_name] = [cmd]

            tops.actual_output = tops.run_show_cmds(tops.show_cmds[tops.dut_name], conn_type="ssh")

        except (AttributeError, LookupError, EapiError) as exception:
            logging.error(
                f"On device {tops.dut_name}: Error while running testcase on DUT is: "
                f"{str(exception)}"
            )
            tops.actual_output = str(exception)
            tops.output_msg += (
                f"EXCEPTION encountered on device {tops.dut_name}, while "
                f"investigating if ssh can be used to run cmds. Vane recorded error: {exception}"
            )

        """
        TS: Verify ping output should be non-empty
        """
        tops.parse_test_steps(self.test_if_ssh_can_run_ping_cmd)
        tops.test_result = tops.actual_output != ""
        tops.generate_report(tops.dut_name, tops.output_msg)
        assert tops.actual_output != ""

    def test_if_ssh_run_commands_func(self, dut, tests_definitions):
        """TD: Verifies ssh connection run_commands() func

        Args:
          dut (dict): Encapsulates dut details including name, connection
        """

        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)

        try:
            tops.show_cmds[tops.dut_name] = ["show ntp status", "show bgp summary"]

            """
            TS: Run cmds using eapi and ssh run_commands
            """
            run_commands_op = dut["ssh_conn"].run_commands(tops.show_cmds[tops.dut_name])
            eapi_output = tops.run_show_cmds(tops.show_cmds[tops.dut_name], conn_type="eapi")
            eapi_op = []
            for output in eapi_output:
                eapi_op.append(output["result"])

            """
            TS: Compare eapi and ssh outputs
            """
            tops.actual_output, tops.expected_output = (run_commands_op, eapi_op)

        except (AttributeError, LookupError, EapiError) as exception:
            logging.error(
                f"On device {tops.dut_name}: Error while running testcase on DUT is: "
                f"{str(exception)}"
            )
            tops.actual_output = str(exception)
            tops.output_msg += (
                f"EXCEPTION encountered on device {tops.dut_name}, while "
                f"investigating if ssh can be used to run cmds. Vane recorded error: {exception}"
            )

        tops.parse_test_steps(self.test_if_ssh_run_commands_func)
        tops.test_result = tops.actual_output == tops.expected_output
        tops.generate_report(tops.dut_name, tops.output_msg)
        assert tops.actual_output == tops.expected_output

    def test_if_setup_fail_is_handled(self):
        """TD: Verifies if invalid cmd in setup is handled properly"""

        """ This function is never called since the setup fails"""

    def test_run_show_cmds_timeout_func(self, dut, tests_definitions):
        """TD: Verifies run_show_cmds() timeout func

        Args:
          dut (dict): Encapsulates dut details including name, connection
        """

        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)

        try:
            tops.show_cmds[tops.dut_name] = ["show ntp status", "show bgp summary"]

            """
            TS: Run cmds using eapi and ssh run_commands
            """
            ssh_output = tops.run_show_cmds(
                tops.show_cmds[tops.dut_name], conn_type="ssh", timeout=120
            )
            eapi_output = tops.run_show_cmds(
                tops.show_cmds[tops.dut_name], conn_type="eapi", timeout=120
            )
            eapi_op = []
            for output in eapi_output:
                eapi_op.append(output["result"])

            """
            TS: Compare eapi and ssh outputs
            """
            tops.actual_output, tops.expected_output = (ssh_output, eapi_output)

        except (AttributeError, LookupError, EapiError) as exception:
            logging.error(
                f"On device {tops.dut_name}: Error while running testcase on DUT is: "
                f"{str(exception)}"
            )
            tops.actual_output = str(exception)
            tops.output_msg += (
                f"EXCEPTION encountered on device {tops.dut_name}, while "
                f"investigating if ssh can be used to run cmds. Vane recorded error: {exception}"
            )

        tops.parse_test_steps(self.test_run_show_cmds_timeout_func)
        tops.test_result = tops.actual_output == tops.expected_output
        tops.generate_report(tops.dut_name, tops.output_msg)
        assert tops.actual_output == tops.expected_output

    def test_run_cfg_cmds_ssh_func(self, dut, tests_definitions):
        """TD: Verifies run_cfg_cmds() ssh functionality

        Args:
          dut (dict): Encapsulates dut details including name, connection
        """

        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)

        try:
            description = "test"
            cfg_cmds = ["interface eth16", f"description {description}"]

            """
            TS: Run cmds using ssh run_cfg_cmds
            """
            tops.run_cfg_cmds(cfg_cmds, conn_type="ssh")

            """
            TS: check if config is present
            """

            show_cmds = ["show running-config interfaces ethernet 16"]

            tops.actual_output = tops.run_show_cmds(show_cmds, encoding="text")

            tops.expected_output = f"description {description}"

            cfg_cmds = ["interface eth16", f"no description {description}"]

            tops.run_cfg_cmds(cfg_cmds, conn_type="ssh")

        except (AttributeError, LookupError, EapiError) as exception:
            logging.error(
                f"On device {tops.dut_name}: Error while running testcase on DUT is: "
                f"{str(exception)}"
            )
            tops.actual_output = str(exception)
            tops.output_msg += (
                f"EXCEPTION encountered on device {tops.dut_name}, while "
                f"investigating if ssh can be used to run cmds. Vane recorded error: {exception}"
            )

        tops.parse_test_steps(self.test_run_cfg_cmds_ssh_func)
        tops.test_result = tops.expected_output in tops.actual_output[0]["result"]["output"]
        tops.generate_report(tops.dut_name, tops.output_msg)
        assert tops.expected_output in tops.actual_output[0]["result"]["output"]

    def test_run_cfg_cmds_eapi_func(self, dut, tests_definitions):
        """TD: Verifies run_cfg_cmds() eapi functionality

        Args:
          dut (dict): Encapsulates dut details including name, connection
        """

        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)

        try:
            description = "test"
            cfg_cmds = ["interface eth16", f"description {description}"]

            """
            TS: Run cmds using eapi run_cfg_cmds
            """
            tops.run_cfg_cmds(cfg_cmds, conn_type="eapi")

            """
            TS: check if config is present
            """

            show_cmds = ["show running-config interfaces ethernet 16"]

            tops.actual_output = tops.run_show_cmds(show_cmds, encoding="text")

            tops.expected_output = f"description {description}"

            cfg_cmds = ["interface eth16", f"no description {description}"]

            tops.run_cfg_cmds(cfg_cmds, conn_type="ssh")

        except (AttributeError, LookupError, EapiError) as exception:
            logging.error(
                f"On device {tops.dut_name}: Error while running testcase on DUT is: "
                f"{str(exception)}"
            )
            tops.actual_output = str(exception)
            tops.output_msg += (
                f"EXCEPTION encountered on device {tops.dut_name}, while "
                f"investigating if eapi can be used to run cmds. Vane recorded error: {exception}"
            )

        tops.parse_test_steps(self.test_run_cfg_cmds_eapi_func)
        tops.test_result = tops.expected_output in tops.actual_output[0]["result"]["output"]
        tops.generate_report(tops.dut_name, tops.output_msg)
        assert tops.expected_output in tops.actual_output[0]["result"]["output"]

    def test_file_transfer(self, dut, tests_definitions):
        """TD: Verifies transfer_file() ssh functionality

        Args:
          dut (dict): Encapsulates dut details including name, connection
        """

        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)

        try:
            """
            TS: Transfer file named "sample.txt"
            """
            src_file = "sample_network_tests/vane_system_tests/sample.txt"
            timestr = time.strftime("%Y%m%d-%H%M%S")
            dest_file = f"sample-{timestr}.txt"

            file_system = "/mnt/flash"
            operation = "put"
            tops.expected_output = {
                "file_exists": True,
                "file_transferred": True,
                "file_verified": True,
            }
            tops.actual_output = tops.transfer_file(
                src_file=src_file, dest_file=dest_file, file_system=file_system, operation=operation
            )

        except (AttributeError, LookupError, EapiError) as exception:
            logging.error(
                f"On device {tops.dut_name}: Error while running testcase on DUT is: "
                f"{str(exception)}"
            )
            tops.actual_output = str(exception)
            tops.output_msg += (
                f"EXCEPTION encountered on device {tops.dut_name}, while "
                f"investigating file transfer over ssh functionality. Vane "
                f"recorded error: {exception}"
            )

        tops.parse_test_steps(self.test_file_transfer)
        tops.test_result = tops.expected_output == tops.actual_output
        tops.generate_report(tops.dut_name, tops.output_msg)
        assert tops.expected_output == tops.actual_output

    def test_file_transfer_using_sftp(self, dut, tests_definitions):
        """TD: Verifies transfer_file() sftp functionality

        Args:
          dut (dict): Encapsulates dut details including name, connection
        """

        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)

        try:
            """
            TS: Transfer file named "sample-sftp.txt"
            """
            src_file = "sample_network_tests/vane_system_tests/sample-sftp.txt"
            timestr = time.strftime("%Y%m%d-%H%M%S")
            dest_file = f"sample-{timestr}.txt"

            file_system = "/mnt/flash"
            operation = "put"
            tops.expected_output = {
                "file_exists": True,
                "file_transferred": True,
                "file_verified": True,
            }
            tops.actual_output = tops.transfer_file(
                src_file=src_file,
                dest_file=dest_file,
                file_system=file_system,
                operation=operation,
                sftp=True,
            )

        except (AttributeError, LookupError, EapiError) as exception:
            logging.error(
                f"On device {tops.dut_name}: Error while running testcase on DUT is: "
                f"{str(exception)}"
            )
            tops.actual_output = str(exception)
            tops.output_msg += (
                f"EXCEPTION encountered on device {tops.dut_name}, while "
                f"investigating file transfer over sftp functionality. Vane "
                f"recorded error: {exception}"
            )

        tops.parse_test_steps(self.test_file_transfer_using_sftp)
        tops.test_result = tops.expected_output == tops.actual_output
        tops.generate_report(tops.dut_name, tops.output_msg)
        assert tops.expected_output == tops.actual_output

    def test_cmd_template(self, dut, tests_definitions):
        """
        Test case to check cmd template
        """

        # Initializing the TestOps class and initializing the variables
        self.tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)
        test_params = self.tops.test_parameters
        self.tops.actual_output = {}
        self.output = ""
        test_params["input"] = {"local_interface": None, "snmp_local_interface_ip": None}
        self.tops.output_msg = (
            "SNMP traps are generated and returned no errors when snmpwalk command is executed"
            " locally on switch."
        )

        try:
            """
            TS: Running 'bash timeout <cmd wait time> snmpwalk -v <snmp_version> -a SHA -A
            <snmp_authentication_protocol_passphrase> -x AES -X <snmp_privacy_protocol_passphrase>
            -u <snmp_username> -l authPriv <snmp_local_interface_ip>
            HOST-RESOURCES-MIB::hrProcessorLoad' command and verifying SNMP traps are generated
            on device.
            """
            snmp_walk_cmd = (
                "bash timeout 5 snmpwalk -v"
                " 3 -a SHA -A {{ snmp_authentication_protocol_passphrase }}"
                " -x AES -X {{ snmp_privacy_protocol_passphrase }} -u"
                " {{ snmp_username }} -l authPriv"
                " {{ snmp_local_interface_ip }} HOST-RESOURCES-MIB::hrProcessorLoad"
            )
            dut["snmp_authentication_protocol_passphrase"] = "arista123"
            dut["snmp_privacy_protocol_passphrase"] = "arista123"
            dut["snmp_username"] = "Arista"
            dut["snmp_local_interface_ip"] = "192.168.0.9"
            output = self.tops.run_show_cmds([snmp_walk_cmd], dut=dut, hidden_cmd=True)
            snmp_output = output[0]["result"]["messages"][0].split("hrProcessorLoad\n")

            # Verifying the snmpwalk command output is not empty and updating the actual output
            # with snmp status
            snmp_output = snmp_output[0].split("\t")
            self.output += "\n\n The snmpwalk output is:\n " + str(snmp_output)
            self.tops.actual_output.update({"snmp_walk_successful": "INTEGER" in snmp_output[0]})

            # forming output message if test result is fail
            if self.tops.expected_output != self.tops.actual_output:
                self.tops.output_msg = (
                    "SNMP traps are not generated and returned invalid output when snmpwalk command"
                    " is executed locally on switch."
                )

        except (AssertionError, AttributeError, LookupError, EapiError) as excep:
            logging.error(
                "On device %s: Error while running the testcase is:\n%s",
                self.tops.dut_name,
                str(excep),
            )
            self.tops.output_msg = self.tops.actual_output = str(excep).split("\n", maxsplit=1)[0]

        self.tops.test_result = self.tops.actual_output == self.tops.expected_output
        self.tops.parse_test_steps(self.test_cmd_template)
        self.tops.generate_report(dut["name"], self.output)
        assert self.tops.expected_output == self.tops.actual_output

    def test_snmpget_to_dut(self, dut, tests_definitions):
        """
        Test case to check cmd template
        """

        # Initializing the TestOps class and initializing the variables
        self.tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)
        test_params = self.tops.test_parameters
        self.tops.actual_output = {}
        self.output = ""
        self.tops.output_msg = (
            "SNMP traps are generated and returned no errors when snmpwalk command is executed"
            " locally on switch."
        )

        try:
            """
            TS: Running 'snmpget -v <snmp_version> -a SHA -A
            <snmp_authentication_protocol_passphrase> -x AES -X <snmp_privacy_protocol_passphrase>
            -u <snmp_username> -l authPriv <snmp_local_interface_ip>
            HOST-RESOURCES-MIB::hrProcessorLoad' command and verifying SNMP traps are generated
            on device.
            """
            snmp_walk_cmd = (
                "bash timeout 5 snmpwalk -v"
                " 3 -a SHA -A {{ snmp_authentication_protocol_passphrase }}"
                " -x AES -X {{ snmp_privacy_protocol_passphrase }} -u"
                " {{ snmp_username }} -l authPriv"
                " {{ snmp_local_interface_ip }} HOST-RESOURCES-MIB::hrProcessorLoad"
            )
            dut["snmp_authentication_protocol_passphrase"] = "arista123"
            dut["snmp_privacy_protocol_passphrase"] = "arista123"
            dut["snmp_username"] = "Arista"
            dut["snmp_local_interface_ip"] = "192.168.0.9"
            oid = ".1.3.6.1.2.1.1.5.0"
            self.tops.actual_output = self.tops.run_snmpget(
                "Arista", "arista123", "arista123", oid, dut=dut
            )

            # forming output message if test result is fail
            if dut["name"] in self.tops.actual_output:
                self.tops.output_msg = (
                    "SNMP traps are not generated and returned invalid output when snmpwalk command"
                    " is executed locally on switch."
                )

        except (AssertionError, AttributeError, LookupError, EapiError) as excep:
            logging.error(
                "On device %s: Error while running the testcase is:\n%s",
                self.tops.dut_name,
                str(excep),
            )
            self.tops.output_msg = self.tops.actual_output = str(excep).split("\n", maxsplit=1)[0]

        self.tops.test_result = dut["name"] in self.tops.actual_output
        self.tops.parse_test_steps(self.test_snmpget_to_dut)
        self.tops.generate_report(dut["name"], self.output)
        assert dut["name"] in self.tops.actual_output


@pytest.mark.vane_system_tests
class TestcaseSkipTests:
    """Suite of testcases to validate PyTest skip"""

    def test_testcase_skip(self, dut, tests_definitions):
        """
        TD: Verify correct behavior when PyTest skip occurs.
        Args:
            dut(dict): details related to a particular DUT
            tests_definitions(dict): test suite and test case parameters.
        """

        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)

        """
        TS: Set skip condition to True so test case is skipped
        """
        # Skip variable simulates a test case condition that needs to be skipped
        # In a test case this condition could be testing for vEOS on a hardware test or
        # testing for tacacs configuration before a tacacs test
        # Also skip variable is only simulating condition and should not be confused with tops.skip
        skip = True
        self.output = None
        tops.output_msg = "Not skipping test case."

        try:
            """
            TS: Implement PyTest skip logic
            """
            if skip:
                tops.output_msg = f"Skipping test case on {tops.dut_name}"
                """
                TS: Use skip post processing logic
                """
                tests_tools.post_process_skip(tops, self.test_testcase_skip, self.output)
                pytest.skip(tops.output_msg)

        except (AssertionError, AttributeError, LookupError, EapiError) as excep:
            logging.error(f"On device {tops.dut_name}, Error while testing skip: {excep}")

        # Normal post processing logic that won't be used
        tops.test_result = tops.expected_output == tops.actual_output
        tops.parse_test_steps(self.test_testcase_skip)
        tops.generate_report(tops.dut_name, self.output)
        assert tops.expected_output == tops.actual_output
