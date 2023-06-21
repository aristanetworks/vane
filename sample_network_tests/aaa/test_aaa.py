#!/usr/bin/env python3
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

""" Tests to validate base feature status."""

import inspect
import logging
import pytest
from vane import tests_tools


TEST_SUITE = __file__
LOG_FILE = {"parameters": {"show_log": "show_output.log"}}


@pytest.mark.nrfu
@pytest.mark.base_feature
@pytest.mark.aaa
class AAATests:
    """AAA Test Suite"""

    @pytest.mark.skip(reason="No AAA setup on DUTs")
    def test_if_authentication_counters_are_incrementing_on_(
        self, return_global_data, dut, tests_definitions
    ):
        """Verify AAA counters are working correctly

        Args:
          dut (dict): Encapsulates dut details including name, connection
          tests_definitions (dict): Test parameters
        """

        test_case = inspect.currentframe().f_code.co_name
        test_parameters = tests_tools.get_parameters(
            tests_definitions, TEST_SUITE, test_case
        )

        expected_output = test_parameters["expected_output"]
        dut_name = dut["name"]

        show_cmd = test_parameters["show_cmd"]
        tests_tools.verify_show_cmd(show_cmd, dut)
        show_cmd_txt = dut["output"][show_cmd]["text"]

        logging.info(
            f"TEST is |{dut_name}| authentication counters " "incrementing"
        )

        ptr = dut["output"][show_cmd]["json"]
        auth_allowed_1 = ptr["authorizationAllowed"]
        logging.info(
            f"GIVEN {auth_allowed_1} authentication counters at " "time 1"
        )

        show_output, _ = tests_tools.return_show_cmd(
            show_cmd, dut, test_case, LOG_FILE
        )
        auth_allowed_2 = show_output[0]["result"]["authorizationAllowed"]
        logging.info(
            f"WHEN {auth_allowed_2} authentication counters at " "time 2"
        )

        actual_output = f"Authroization Allowed Message Time 1: \
                        {auth_allowed_1} \nAuthorization Allowed Message \
                        Time 2: {auth_allowed_2}"

        if auth_allowed_1 < auth_allowed_2:
            print(
                f"\nOn router |{dut_name}| AAA authorization allowed "
                f"messages2: |{auth_allowed_2}| increments from AAA "
                f"authorization allowed message1: |{auth_allowed_1}|"
            )
            logging.info("THEN test case result is |True|")
        else:
            print(
                f"\nOn router |{dut_name}| AAA authorization allowed "
                f"messages2: |{auth_allowed_2}| doesn't increments from AAA "
                f"authorization allowed message1: |{auth_allowed_1}|"
            )
            logging.info("THEN test case result is |False|")

        logging.info(f"OUTPUT of |{show_cmd}| is :\n\n{show_cmd_txt}")
        assert auth_allowed_1 < auth_allowed_2

    def test_if_aaa_session_logging_is_working_on_(
        self, dut, tests_definitions
    ):
        """Verify AAA session logging is working by identifying eapi connection

        Args:
          dut (dict): Encapsulates dut details including name, connection
          tests_definitions (dict): Test parameters
        """

        test_case = inspect.currentframe().f_code.co_name
        test_parameters = tests_tools.get_parameters(
            tests_definitions, TEST_SUITE, test_case
        )

        expected_output = test_parameters["expected_output"]
        dut_name = dut["name"]

        show_cmd = test_parameters["show_cmd"]
        tests_tools.verify_show_cmd(show_cmd, dut)
        show_cmd_txt = dut["output"][show_cmd]["text"]

        logging.info(
            f"TEST is |{dut_name}| AAA session logging is working by "
            "identifying eapi connection"
        )

        actual_output = dut["output"][show_cmd]["json"]["nonInteractives"]
        aaa_flag = False

        for non_interactive in actual_output:
            service = actual_output[non_interactive]["service"]
            logging.info(f"GIVEN {expected_output} is nonInteractive sessions")
            logging.info(f"WHEN {service} is nonInteractive sessions")

            if service == "commandApi":
                print(
                    f"\nOn router |{dut_name}| identified eAPi AAA session: "
                    f"|{service}|"
                )
                aaa_flag = True

        if not aaa_flag:
            print(
                f"\nOn router |{dut_name}| did NOT identified eAPi AAA "
                f"session: |{service}|"
            )

        for non_interactive in actual_output:
            service = actual_output[non_interactive]["service"]

            test_result = service == expected_output
            logging.info(f"THEN test case result is |{test_result}|")
            logging.info(f"OUTPUT of |{show_cmd}| is :\n\n{show_cmd_txt}")

            assert service == expected_output

    @pytest.mark.authorization
    def test_if_commands_authorization_methods_set_on_(
        self, dut, tests_definitions
    ):
        """Verify AAA command authorization are method-lists set correct

        Args:
          dut (dict): Encapsulates dut details including name, connection
          tests_definitions (dict): Test parameters
        """

        test_case = inspect.currentframe().f_code.co_name
        test_parameters = tests_tools.get_parameters(
            tests_definitions, TEST_SUITE, test_case
        )

        expected_output = test_parameters["expected_output"]
        dut_name = dut["name"]
        cmd_auth = test_parameters["cmd_auth"]
        expected_output = cmd_auth

        show_cmd = test_parameters["show_cmd"]
        tests_tools.verify_show_cmd(show_cmd, dut)
        show_cmd_txt = dut["output"][show_cmd]["text"]

        logging.info(
            "TEST is command authorization methods list set correct "
            f"on |{dut_name}| "
        )
        logging.info(f"GIVEN command authorization method list: |{cmd_auth}|")

        ptr = dut["output"][show_cmd]["json"]["authorization"]
        actual_output = ptr["commandsAuthzMethods"]["privilege0-15"]["methods"]
        logging.info(
            f"WHEN EOS command authorization method list is set "
            f"to |{actual_output}|"
        )

        test_result = actual_output == expected_output
        logging.info(f"THEN test case result is |{test_result}|")
        logging.info(f"OUTPUT of |{show_cmd}| is :\n\n{show_cmd_txt}")

        print(
            f"\nOn router |{dut_name}| AAA authorization methods for f"
            f"commands: |{actual_output}|"
        )

        assert actual_output == expected_output

    @pytest.mark.authorization
    def test_if_exec_authorization_methods_set_on_(
        self, dut, tests_definitions
    ):
        """Verify AAA exec authorization are method-lists set correct

        Args:
          dut (dict): Encapsulates dut details including name, connection
          tests_definitions (dict): Test parameters
        """

        test_case = inspect.currentframe().f_code.co_name
        test_parameters = tests_tools.get_parameters(
            tests_definitions, TEST_SUITE, test_case
        )

        expected_output = test_parameters["expected_output"]
        dut_name = dut["name"]
        exec_auth = test_parameters["exec_auth"]
        expected_output = exec_auth

        show_cmd = test_parameters["show_cmd"]
        tests_tools.verify_show_cmd(show_cmd, dut)
        show_cmd_txt = dut["output"][show_cmd]["text"]

        logging.info(
            "TEST is exec authorization methods list set correct "
            f"on |{dut_name}| "
        )
        logging.info(f"GIVEN exec authorization method list: |{exec_auth}|")

        ptr = dut["output"][show_cmd]["json"]["authorization"]
        actual_output = ptr["execAuthzMethods"]["exec"]["methods"]
        logging.info(
            "WHEN EOS exec authorization method list is set to "
            f"|{actual_output}|"
        )

        test_result = actual_output == expected_output
        logging.info(f"THEN test case result is |{test_result}|")
        logging.info(f"OUTPUT of |{show_cmd}| is :\n\n{show_cmd_txt}")

        print(
            f"\nOn router |{dut_name}| AAA authorization methods for exec: "
            f"|{actual_output}|"
        )

        assert actual_output == expected_output

    @pytest.mark.authentication
    def test_if_default_login_authentication_methods_set_on_(
        self, dut, tests_definitions
    ):
        """Verify AAA default login authentication are method-lists set correct

        Args:
          dut (dict): Encapsulates dut details including name, connection
          tests_definitions (dict): Test parameters
        """

        test_case = inspect.currentframe().f_code.co_name
        test_parameters = tests_tools.get_parameters(
            tests_definitions, TEST_SUITE, test_case
        )

        expected_output = test_parameters["expected_output"]
        dut_name = dut["name"]
        login_auth = test_parameters["login_auth"]
        expected_output = login_auth

        show_cmd = test_parameters["show_cmd"]
        tests_tools.verify_show_cmd(show_cmd, dut)
        show_cmd_txt = dut["output"][show_cmd]["text"]

        logging.info(
            f"TEST is default login authentication methods list set "
            f"correct on |{dut_name}| "
        )
        logging.info(f"GIVEN login authentication method list: |{login_auth}|")

        ptr = dut["output"][show_cmd]["json"]["authentication"]
        actual_output = ptr["loginAuthenMethods"]["default"]["methods"]
        logging.info(
            "WHEN EOS login authentication method list is set to "
            f"|{actual_output}|"
        )

        test_result = actual_output == expected_output
        logging.info(f"THEN test case result is |{test_result}|")
        logging.info(f"OUTPUT of |{show_cmd}| is :\n\n{show_cmd_txt}")

        print(
            f"\nOn router |{dut_name}| AAA authentication methods for "
            f"default login: |{actual_output}|"
        )

        assert actual_output == expected_output

    @pytest.mark.authentication
    def test_if_login_authentication_methods_set_on_(
        self, dut, tests_definitions
    ):
        """Verify AAA login authentication are method-lists set correct

        Args:
          dut (dict): Encapsulates dut details including name, connection
          tests_definitions (dict): Test parameters
        """

        test_case = inspect.currentframe().f_code.co_name
        test_parameters = tests_tools.get_parameters(
            tests_definitions, TEST_SUITE, test_case
        )

        expected_output = test_parameters["expected_output"]
        dut_name = dut["name"]
        login_auth = test_parameters["login_auth"]
        expected_output = login_auth

        show_cmd = test_parameters["show_cmd"]
        tests_tools.verify_show_cmd(show_cmd, dut)
        show_cmd_txt = dut["output"][show_cmd]["text"]

        logging.info(
            "TEST is login authentication methods list set correct "
            f"on |{dut_name}| "
        )
        logging.info(f"GIVEN login authentication method list: |{login_auth}|")

        if login_auth:
            ptr = dut["output"][show_cmd]["json"]["authentication"]
            actual_output = ptr["loginAuthenMethods"]["login"]["methods"]
            logging.info(
                "WHEN EOS login authentication method list is set "
                f"to |{actual_output}|"
            )

            test_result = actual_output == expected_output
            logging.info(f"THEN test case result is |{test_result}|")
            logging.info(f"OUTPUT of |{show_cmd}| is :\n\n{show_cmd_txt}")

            print(
                f"\nOn router |{dut_name}| AAA authentication methods for "
                f"login: |{actual_output}|"
            )

            assert actual_output == expected_output
        else:
            logging.info(
                "WHEN EOS login authentication method list is set to " "|None|"
            )
            logging.info("THEN test case result is |True|")
            logging.info(f"OUTPUT of |{show_cmd}| is :\n\n{show_cmd_txt}")

            assert True

    @pytest.mark.authentication
    def test_if_dot1x_authentication_methods_set_on_(
        self, dut, tests_definitions
    ):
        """Verify AAA dot1x authentication are method-lists set correct

        Args:
          dut (dict): Encapsulates dut details including name, connection
          tests_definitions (dict): Test parameters
        """

        test_case = inspect.currentframe().f_code.co_name
        test_parameters = tests_tools.get_parameters(
            tests_definitions, TEST_SUITE, test_case
        )

        expected_output = test_parameters["expected_output"]
        dut_name = dut["name"]
        dot1x_auth = test_parameters["dot1x_auth"]
        expected_output = dot1x_auth

        show_cmd = test_parameters["show_cmd"]
        tests_tools.verify_show_cmd(show_cmd, dut)
        show_cmd_txt = dut["output"][show_cmd]["text"]

        logging.info(
            f"TEST is dot1x authentication methods list set correct "
            f"on |{dut_name}| "
        )
        logging.info(f"GIVEN dot1x authentication method list: |{dot1x_auth}|")

        ptr = dut["output"][show_cmd]["json"]["authentication"]
        actual_output = ptr["dot1xAuthenMethods"]["default"]["methods"]
        logging.info(
            "WHEN EOS dot1x authentication method list is set to "
            f"|{actual_output}|"
        )

        test_result = actual_output == expected_output
        logging.info(f"THEN test case result is |{test_result}|")
        logging.info(f"OUTPUT of |{show_cmd}| is :\n\n{show_cmd_txt}")

        print(
            f"\nOn router |{dut_name}| AAA authentication methods for dot1x "
            f"default: |{actual_output}|"
        )

        assert actual_output == expected_output

    @pytest.mark.authentication
    def test_if_enable_authentication_methods_set_on_(
        self, dut, tests_definitions
    ):
        """Verify AAA enable authentication method-lists are set correct

        Args:
          dut (dict): Encapsulates dut details including name, connection
          tests_definitions (dict): Test parameters
        """

        test_case = inspect.currentframe().f_code.co_name
        test_parameters = tests_tools.get_parameters(
            tests_definitions, TEST_SUITE, test_case
        )

        expected_output = test_parameters["expected_output"]
        dut_name = dut["name"]
        enable_auth = test_parameters["enable_auth"]
        expected_output = enable_auth

        logging.info(
            "TEST is enable authentication methods list set correct "
            f"on |{dut_name}| "
        )
        logging.info(
            "GIVEN enable authentication method list: " f"|{enable_auth}|"
        )

        show_cmd = test_parameters["show_cmd"]
        tests_tools.verify_show_cmd(show_cmd, dut)
        show_cmd_txt = dut["output"][show_cmd]["text"]

        ptr = dut["output"][show_cmd]["json"]["authentication"]
        actual_output = ptr["enableAuthenMethods"]["default"]["methods"]

        print(
            f"\nOn router |{dut['name']}| AAA authentication methods for "
            f"enable default: |{actual_output}|"
        )
        logging.info(
            f"WHEN EOS enable authentication method list is set to "
            f"|{actual_output}|"
        )

        test_result = actual_output == expected_output
        logging.info(f"THEN test case result is |{test_result}|")
        logging.info(f"OUTPUT of |{show_cmd}| is :\n\n{show_cmd_txt}")

        assert actual_output == expected_output

    @pytest.mark.accounting
    def test_if_system_accounting_methods_set_on_(self, dut, tests_definitions):
        """Verify AAA system accounting method-lists are set correct

        Args:
          dut (dict): Encapsulates dut details including name, connection
          tests_definitions (dict): Test parameters
        """

        test_case = inspect.currentframe().f_code.co_name
        test_parameters = tests_tools.get_parameters(
            tests_definitions, TEST_SUITE, test_case
        )

        expected_output = test_parameters["expected_output"]
        dut_name = dut["name"]
        default_acct = test_parameters["default_acct"]
        console_acct = test_parameters["console_acct"]
        expected_output = [default_acct, console_acct]

        logging.info(
            f"TEST is system accounting methods list set correct "
            f"on |{dut_name}| "
        )
        logging.info(
            f"GIVEN default system accounting method list: "
            f"|{default_acct}| and console system accounting method"
            f"list: |{console_acct}|"
        )

        show_cmd = test_parameters["show_cmd"]
        tests_tools.verify_show_cmd(show_cmd, dut)
        show_cmd_txt = dut["output"][show_cmd]["text"]

        dut_ptr = dut["output"][show_cmd]["json"]
        acct_ptr = dut_ptr["accounting"]["systemAcctMethods"]
        eos_default_acct = acct_ptr["system"]["defaultMethods"]
        eos_console_acct = acct_ptr["system"]["consoleMethods"]
        actual_output = [eos_default_acct, eos_console_acct]

        print(
            f"\nOn router |{dut['name']}| AAA accounting methods for "
            f"default: |{eos_default_acct}|"
        )
        logging.info(
            f"WHEN default system accounting method list: "
            f"|{eos_default_acct}| and console system accounting "
            f"method list: |{eos_console_acct}|"
        )

        test_result = expected_output == actual_output
        logging.info(f"THEN test case result is |{test_result}|")
        logging.info(f"OUTPUT of |{show_cmd}| is :\n\n{show_cmd_txt}")

        assert expected_output == actual_output

    @pytest.mark.accounting
    def test_if_exec_accounting_methods_set_on_(self, dut, tests_definitions):
        """Verify AAA exec accounting method-lists are set correct

        Args:
          dut (dict): Encapsulates dut details including name, connection
          tests_definitions (dict): Test parameters
        """

        test_case = inspect.currentframe().f_code.co_name
        test_parameters = tests_tools.get_parameters(
            tests_definitions, TEST_SUITE, test_case
        )

        expected_output = test_parameters["expected_output"]
        dut_name = dut["name"]
        default_acct = test_parameters["default_acct"]
        console_acct = test_parameters["console_acct"]
        expected_output = [default_acct, console_acct]

        logging.info(
            f"TEST is exec accounting methods list set correct "
            f"on |{dut_name}| "
        )
        logging.info(
            f"GIVEN exec system accounting method list: "
            f"|{default_acct}| and exec system accounting method"
            f"list: |{console_acct}|"
        )

        show_cmd = test_parameters["show_cmd"]
        tests_tools.verify_show_cmd(show_cmd, dut)
        show_cmd_txt = dut["output"][show_cmd]["text"]

        dut_ptr = dut["output"][show_cmd]["json"]
        acct_ptr = dut_ptr["accounting"]["execAcctMethods"]
        eos_default_acct = acct_ptr["exec"]["defaultMethods"]
        eos_console_acct = acct_ptr["exec"]["consoleMethods"]
        actual_output = [eos_default_acct, eos_console_acct]

        print(
            f"\nOn router |{dut['name']}| AAA accounting exec methods for "
            f"console: |{eos_console_acct}|"
        )
        logging.info(
            f"WHEN default exec accounting method list: "
            f"|{eos_default_acct}| and console exec accounting method"
            f"list: |{eos_console_acct}|"
        )

        test_result = expected_output == actual_output
        logging.info(f"THEN test case result is |{test_result}|")
        logging.info(f"OUTPUT of |{show_cmd}| is :\n\n{show_cmd_txt}")

        assert expected_output == actual_output

    @pytest.mark.accounting
    def test_if_priviledge_accounting_methods_set_on_(
        self, dut, tests_definitions
    ):
        """Verify AAA priviledge accounting method-lists are set correct

        Args:
          dut (dict): Encapsulates dut details including name, connection
          tests_definitions (dict): Test parameters
        """

        test_case = inspect.currentframe().f_code.co_name
        test_parameters = tests_tools.get_parameters(
            tests_definitions, TEST_SUITE, test_case
        )

        expected_output = test_parameters["expected_output"]
        dut_name = dut["name"]
        default_acct = test_parameters["default_acct"]
        console_acct = test_parameters["console_acct"]
        expected_output = [default_acct, console_acct]

        logging.info(
            f"TEST is priviledge accounting methods list set correct "
            f"on |{dut_name}| "
        )
        logging.info(
            f"GIVEN priviledge system accounting method list: "
            f"|{default_acct}| and priviledge system accounting "
            f"method list: |{console_acct}|"
        )

        show_cmd = test_parameters["show_cmd"]
        tests_tools.verify_show_cmd(show_cmd, dut)
        show_cmd_txt = dut["output"][show_cmd]["text"]

        dut_ptr = dut["output"][show_cmd]["json"]
        acct_ptr = dut_ptr["accounting"]["commandsAcctMethods"]
        eos_default_acct = acct_ptr["privilege0-15"]["defaultMethods"]
        eos_console_acct = acct_ptr["privilege0-15"]["consoleMethods"]
        actual_output = [eos_default_acct, eos_console_acct]

        print(
            f"\nOn router |{dut['name']}| AAA accounting exec methods for "
            f"console: |{eos_console_acct}|"
        )
        logging.info(
            f"WHEN default privilege accounting method list: "
            f"|{eos_default_acct}| and console privilege accounting "
            f"method list: |{eos_console_acct}|"
        )

        test_result = expected_output == actual_output
        logging.info(f"THEN test case result is |{test_result}|")
        logging.info(f"OUTPUT of |{show_cmd}| is :\n\n{show_cmd_txt}")

        assert expected_output == actual_output

    @pytest.mark.accounting
    def test_if_dot1x_accounting_methods_set_on_(self, dut, tests_definitions):
        """Verify AAA dot1x accounting method-lists are set correct

        Args:
         dut (dict): Encapsulates dut details including name, connection
         tests_definitions (dict): Test parameters
        """

        test_case = inspect.currentframe().f_code.co_name
        test_parameters = tests_tools.get_parameters(
            tests_definitions, TEST_SUITE, test_case
        )

        expected_output = test_parameters["expected_output"]
        dut_name = dut["name"]
        default_acct = test_parameters["default_acct"]
        console_acct = test_parameters["console_acct"]
        expected_output = [default_acct, console_acct]

        logging.info(
            f"TEST is dot1x accounting methods list set correct on "
            f"|{dut_name}|"
        )
        logging.info(
            f"GIVEN dot1x system accounting method list: "
            f"|{default_acct}| and dot1x system accounting method"
            f"list: |{console_acct}|"
        )

        show_cmd = test_parameters["show_cmd"]
        tests_tools.verify_show_cmd(show_cmd, dut)
        show_cmd_txt = dut["output"][show_cmd]["text"]

        ptr = dut["output"][show_cmd]["json"]["accounting"]
        eos_default_acct = ptr["dot1xAcctMethods"]["dot1x"]["defaultMethods"]
        eos_console_acct = ptr["dot1xAcctMethods"]["dot1x"]["consoleMethods"]
        actual_output = [eos_default_acct, eos_console_acct]

        print(
            f"\nOn router |{dut_name}| AAA accounting exec methods for "
            f"dot1x: |{eos_console_acct}|"
        )
        logging.info(
            f"WHEN default dot1x accounting method list: "
            f"|{eos_default_acct}| and console dot1x accounting "
            f"method list: |{eos_console_acct}|"
        )

        test_result = expected_output == actual_output
        logging.info(f"THEN test case result is |{test_result}|")
        logging.info(f"OUTPUT of |{show_cmd}| is :\n\n{show_cmd_txt}")

        assert expected_output == actual_output
