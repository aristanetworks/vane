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

""" Tests to validate base feature status."""

import pytest
from pyeapi.eapilib import EapiError
from vane import tests_tools, test_case_logger
from vane.config import dut_objs, test_defs


TEST_SUITE = __file__
LOG_FILE = {"parameters": {"show_log": "show_output.log"}}

dut_parameters = tests_tools.parametrize_duts(TEST_SUITE, test_defs, dut_objs)
test1_duts = dut_parameters["test_if_authentication_counters_are_incrementing_on_"]["duts"]
test1_ids = dut_parameters["test_if_authentication_counters_are_incrementing_on_"]["ids"]

test2_duts = dut_parameters["test_if_aaa_session_logging_is_working_on_"]["duts"]
test2_ids = dut_parameters["test_if_aaa_session_logging_is_working_on_"]["ids"]

test3_duts = dut_parameters["test_if_commands_authorization_methods_set_on_"]["duts"]
test3_ids = dut_parameters["test_if_commands_authorization_methods_set_on_"]["ids"]

test4_duts = dut_parameters["test_if_exec_authorization_methods_set_on_"]["duts"]
test4_ids = dut_parameters["test_if_exec_authorization_methods_set_on_"]["ids"]

test5_duts = dut_parameters["test_if_default_login_authentication_methods_set_on_"]["duts"]
test5_ids = dut_parameters["test_if_default_login_authentication_methods_set_on_"]["ids"]

test6_duts = dut_parameters["test_if_login_authentication_methods_set_on_"]["duts"]
test6_ids = dut_parameters["test_if_login_authentication_methods_set_on_"]["ids"]

test7_duts = dut_parameters["test_if_dot1x_authentication_methods_set_on_"]["duts"]
test7_ids = dut_parameters["test_if_dot1x_authentication_methods_set_on_"]["ids"]

test8_duts = dut_parameters["test_if_enable_authentication_methods_set_on_"]["duts"]
test8_ids = dut_parameters["test_if_enable_authentication_methods_set_on_"]["ids"]

test9_duts = dut_parameters["test_if_system_accounting_methods_set_on_"]["duts"]
test9_ids = dut_parameters["test_if_system_accounting_methods_set_on_"]["ids"]

test10_duts = dut_parameters["test_if_exec_accounting_methods_set_on_"]["duts"]
test10_ids = dut_parameters["test_if_exec_accounting_methods_set_on_"]["ids"]

test11_duts = dut_parameters["test_if_privilege_accounting_methods_set_on_"]["duts"]
test11_ids = dut_parameters["test_if_privilege_accounting_methods_set_on_"]["ids"]

test12_duts = dut_parameters["test_if_dot1x_accounting_methods_set_on_"]["duts"]
test12_ids = dut_parameters["test_if_dot1x_accounting_methods_set_on_"]["ids"]

logging = test_case_logger.setup_logger(__file__)


@pytest.mark.nrfu
@pytest.mark.base_feature
@pytest.mark.aaa
class AAATests:
    """AAA Test Suite"""

    # @pytest.mark.skip(reason="No AAA setup on DUTs")
    @pytest.mark.parametrize("dut", test1_duts, ids=test1_ids)
    def test_if_authentication_counters_are_incrementing_on_(self, dut, tests_definitions):
        """TD: Verify AAA counters are working correctly

        Args:
          dut (dict): Encapsulates dut details including name, connection
          tests_definitions (dict): Test parameters
        """

        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)

        try:
            """
            TS: Collecting output of show command 'show aaa counters' from dut
            """
            self.output = dut["output"][tops.show_cmd]["json"]
            assert self.output, "AAA Counter details are not collected."
            logging.info(
                f"On device {tops.dut_name} output of {tops.show_cmd} command is: {self.output}"
            )
            auth_allowed_1 = self.output["authorizationAllowed"]

            """
            TS: Running show command 'show aaa counters' on dut again to check for
            counter increments
            """
            self.output = tops.run_show_cmds(tops.show_cmd, encoding="json")[0]["result"]
            assert self.output, "AAA Counter details are not collected."
            logging.info(
                f"On device {tops.dut_name} output of {tops.show_cmd} command is: {self.output}"
            )
            auth_allowed_2 = self.output["authorizationAllowed"]

            if auth_allowed_1 < auth_allowed_2:
                tops.test_result = True
                tops.output_msg = (
                    f"\nOn router {tops.dut_name} AAA authorization allowed "
                    f"messages2: {auth_allowed_2} increments from AAA "
                    f"authorization allowed message1: {auth_allowed_1}"
                )
            else:
                tops.test_result = False
                tops.output_msg = (
                    f"\nOn router {tops.dut_name} AAA authorization allowed "
                    f"messages2: {auth_allowed_2} doesn't increment from AAA "
                    f"authorization allowed message1: {auth_allowed_1}"
                )

            assert auth_allowed_1 < auth_allowed_2

        except (
            AssertionError,
            AttributeError,
            LookupError,
            EapiError,
        ) as exception:
            logging.error(
                f"Error occurred during the testsuite execution on dut:"
                f" {tops.dut_name} is {str(exception)}"
            )
            tops.actual_output = str(exception)
            tops.output_msg += (
                f" EXCEPTION encountered on device {tops.dut_name}, while "
                f"investigating AAA Counters. Vane recorded error: {exception} "
            )

        """
        TS: Creating test report based on results
        """
        tops.parse_test_steps(self.test_if_authentication_counters_are_incrementing_on_)
        tops.generate_report(tops.dut_name, tops.output_msg)

    @pytest.mark.parametrize("dut", test2_duts, ids=test2_ids)
    def test_if_aaa_session_logging_is_working_on_(self, dut, tests_definitions):
        """TD: Verify AAA session logging is working by identifying eapi connection

        Args:
          dut (dict): Encapsulates dut details including name, connection
          tests_definitions (dict): Test parameters
        """

        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)

        try:
            """
            TS: Run show command `show users detail` on dut
            """

            self.output = dut["output"][tops.show_cmd]["json"]
            assert self.output, "User details are not collected."
            logging.info(
                f"On device {tops.dut_name} output of {tops.show_cmd} command is: {self.output}"
            )

            non_interactives = self.output["nonInteractives"]

            aaa_flag = False
            for non_interactive in non_interactives:
                tops.actual_output = non_interactives[non_interactive]["service"]
                if tops.actual_output == tops.expected_output:
                    tops.output_msg += (
                        f"\nOn router {tops.dut_name} identified eAPi AAA session: "
                        f"{tops.actual_output} which is correct.\n\n"
                    )
                else:
                    tops.output_msg += (
                        f"\nOn router {tops.dut_name} identified eAPi AAA session: "
                        f"{tops.actual_output} while the expected session "
                        f"is {tops.expected_output}.\n\n"
                    )
                tops.actual_results.append(tops.actual_output)
                tops.expected_results.append(tops.expected_output)

                if tops.actual_output == "commandApi":
                    aaa_flag = True

            if not aaa_flag:
                tops.output_msg += (
                    f"\nOn router {tops.dut_name} did NOT identify eAPi AAA "
                    f"session: {tops.actual_output}"
                )

            tops.actual_output, tops.expected_output = (
                tops.actual_results,
                tops.expected_results,
            )
        except (
            AssertionError,
            AttributeError,
            LookupError,
            EapiError,
        ) as exception:
            logging.error(
                f"Error occurred during the testsuite execution on dut:"
                f" {tops.dut_name} is {str(exception)}"
            )
            tops.actual_output = str(exception)
        """
        TS: Creating test report based on results
        """
        tops.parse_test_steps(self.test_if_aaa_session_logging_is_working_on_)
        tops.test_result = tops.actual_output == tops.expected_output
        tops.generate_report(tops.dut_name, self.output)
        assert tops.actual_output == tops.expected_output

    @pytest.mark.authorization
    @pytest.mark.parametrize("dut", test3_duts, ids=test3_ids)
    def test_if_commands_authorization_methods_set_on_(self, dut, tests_definitions):
        """TD: Verify AAA command authorization are method-lists set correct

        Args:
          dut (dict): Encapsulates dut details including name, connection
          tests_definitions (dict): Test parameters
        """

        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)

        try:
            """
            TS: Collecting output of show command 'show aaa methods all' from dut
            """
            self.output = dut["output"][tops.show_cmd]["json"]["authorization"]
            assert self.output, "No AAA method details are available"
            logging.info(
                f"On device {tops.dut_name}" f" output of {tops.show_cmd} command is: {self.output}"
            )

            tops.actual_output = self.output["commandsAuthzMethods"]["privilege0-15"]["methods"]
        except (
            AssertionError,
            AttributeError,
            LookupError,
            EapiError,
        ) as exception:
            logging.error(
                f"Error occurred during the testsuite execution on dut:"
                f" {tops.dut_name} is {str(exception)}"
            )
            tops.actual_output = str(exception)

        if tops.actual_output == tops.expected_output:
            tops.test_result = True
            tops.output_msg += (
                f"On router {tops.dut_name} EOS command authorization method "
                f"list is set to: {tops.actual_output}, which is correct.\n\n"
            )
        else:
            tops.test_result = False
            tops.output_msg += (
                f"On router {tops.dut_name} EOS command authorization method "
                f"list is set to: {tops.actual_output}, while "
                f"the expected authorization method list is {tops.expected_output}.\n\n"
            )
        """
        TS: Creating test report based on results
        """
        tops.parse_test_steps(self.test_if_commands_authorization_methods_set_on_)
        tops.generate_report(tops.dut_name, self.output)
        assert tops.actual_output == tops.expected_output

    @pytest.mark.authorization
    @pytest.mark.parametrize("dut", test4_duts, ids=test4_ids)
    def test_if_exec_authorization_methods_set_on_(self, dut, tests_definitions):
        """TD: Verify AAA exec authorization are method-lists set correct

        Args:
          dut (dict): Encapsulates dut details including name, connection
          tests_definitions (dict): Test parameters
        """

        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)

        try:
            """
            TS: Collecting output of show command 'show aaa methods all' from dut
            """
            self.output = dut["output"][tops.show_cmd]["json"]["authorization"]
            assert self.output, "No AAA method details are available"
            logging.info(
                f"On device {tops.dut_name}" f" output of {tops.show_cmd} command is: {self.output}"
            )

            tops.actual_output = self.output["execAuthzMethods"]["exec"]["methods"]
        except (
            AssertionError,
            AttributeError,
            LookupError,
            EapiError,
        ) as exception:
            logging.error(
                f"Error occurred during the testsuite execution on dut:"
                f" {tops.dut_name} is {str(exception)}"
            )
            tops.actual_output = str(exception)

        if tops.actual_output == tops.expected_output:
            tops.test_result = True
            tops.output_msg += (
                f"On router {tops.dut_name} EOS exec authorization method "
                f"list is set to: {tops.actual_output}, which is correct.\n\n"
            )
        else:
            tops.test_result = False
            tops.output_msg += (
                f"On router {tops.dut_name} EOS exec authorization method "
                f"list is set to: {tops.actual_output}, while "
                f"the expected exec authorization method list is {tops.expected_output}.\n\n"
            )
        """
        TS: Creating test report based on results
        """
        tops.parse_test_steps(self.test_if_exec_authorization_methods_set_on_)
        tops.generate_report(tops.dut_name, self.output)
        assert tops.actual_output == tops.expected_output

    @pytest.mark.authentication
    @pytest.mark.parametrize("dut", test5_duts, ids=test5_ids)
    def test_if_default_login_authentication_methods_set_on_(self, dut, tests_definitions):
        """TD: Verify AAA default login authentication are method-lists set correct

        Args:
          dut (dict): Encapsulates dut details including name, connection
          tests_definitions (dict): Test parameters
        """

        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)

        try:
            """
            TS: Run show command 'show aaa methods all' on dut
            """
            self.output = dut["output"][tops.show_cmd]["json"]["authentication"]
            assert self.output, "No AAA method details are available"
            logging.info(
                f"On device {tops.dut_name}" f" output of {tops.show_cmd} command is: {self.output}"
            )
            tops.actual_output = self.output["loginAuthenMethods"]["default"]["methods"]
        except (
            AssertionError,
            AttributeError,
            LookupError,
            EapiError,
        ) as exception:
            logging.error(
                f"Error occurred during the testsuite execution on dut:"
                f" {tops.dut_name} is {str(exception)}"
            )
            tops.actual_output = str(exception)

        if tops.actual_output == tops.expected_output:
            tops.test_result = True
            tops.output_msg += (
                f"On router {tops.dut_name} EOS login authentication method "
                f"list is set to: {tops.actual_output}, which is correct.\n\n"
            )
        else:
            tops.test_result = False
            tops.output_msg += (
                f"On router {tops.dut_name} EOS login authentication method "
                f"list is set to: {tops.actual_output}, while "
                f"the expected EOS login authentication method list is {tops.expected_output}.\n\n"
            )

        """
        TS: Creating test report based on results
        """
        tops.parse_test_steps(self.test_if_default_login_authentication_methods_set_on_)
        tops.generate_report(tops.dut_name, self.output)
        assert tops.actual_output == tops.expected_output

    @pytest.mark.authentication
    @pytest.mark.parametrize("dut", test6_duts, ids=test6_ids)
    def test_if_login_authentication_methods_set_on_(self, dut, tests_definitions):
        """TD: Verify AAA login authentication are method-lists set correct

        Args:
          dut (dict): Encapsulates dut details including name, connection
          tests_definitions (dict): Test parameters
        """

        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)

        try:
            if tops.expected_output:
                """
                TS: Collecting output of show command 'show aaa methods all' from dut
                """
                self.output = dut["output"][tops.show_cmd]["json"]["authentication"]
                assert self.output, "No AAA method details are available"
                logging.info(
                    f"On device {tops.dut_name}"
                    f" output of {tops.show_cmd} command is: {self.output}"
                )

                tops.actual_output = self.output["loginAuthenMethods"]["login"]["methods"]
                if tops.expected_output == tops.actual_output:
                    tops.test_result = True

                    tops.output_msg += (
                        f"On router {tops.dut_name} EOS login authentication method "
                        f"list is set to: {tops.actual_output}, while "
                        f"correct EOS login authentication method list is "
                        f" {tops.expected_output}.\n\n"
                    )
                else:
                    tops.test_result = False
                    tops.output_msg += (
                        f"On router {tops.dut_name} EOS login authentication method "
                        f"list is set to: {tops.actual_output}, while "
                        f"the expected EOS login authentication method list is "
                        f" {tops.expected_output}.\n\n"
                    )
            else:
                tops.actual_output = None
                tops.test_result = True
                tops.output_msg += (
                    "EOS login authentication method list is set to None"
                    " hence test case result is True"
                )
        except (
            AssertionError,
            AttributeError,
            LookupError,
            EapiError,
        ) as exception:
            logging.error(
                f"Error occurred during the testsuite execution on dut:"
                f" {tops.dut_name} is {str(exception)}"
            )
            tops.actual_output = str(exception)
            tops.output_msg += (
                f" EXCEPTION encountered on device {tops.dut_name}, while "
                f"investigating login authentication methods. "
                f"Vane recorded error: {exception} "
            )

        """
        TS: Creating test report based on results
        """
        tops.parse_test_steps(self.test_if_login_authentication_methods_set_on_)
        tops.generate_report(tops.dut_name, tops.output_msg)
        assert tops.actual_output == tops.expected_output

    @pytest.mark.authentication
    @pytest.mark.parametrize("dut", test7_duts, ids=test7_ids)
    def test_if_dot1x_authentication_methods_set_on_(self, dut, tests_definitions):
        """TD: Verify AAA dot1x authentication are method-lists set correct

        Args:
          dut (dict): Encapsulates dut details including name, connection
          tests_definitions (dict): Test parameters
        """

        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)

        try:
            """
            TS: Collecting output of show command 'show aaa methods all' from dut
            """
            self.output = dut["output"][tops.show_cmd]["json"]["authentication"]
            assert self.output, "No AAA method details are available"
            logging.info(
                f"On device {tops.dut_name}" f" output of {tops.show_cmd} command is: {self.output}"
            )

            tops.actual_output = self.output["dot1xAuthenMethods"]["default"]["methods"]
        except (
            AssertionError,
            AttributeError,
            LookupError,
            EapiError,
        ) as exception:
            logging.error(
                f"Error occurred during the testsuite execution on dut:"
                f" {tops.dut_name} is {str(exception)}"
            )
            tops.actual_output = str(exception)

        if tops.actual_output == tops.expected_output:
            tops.test_result = True
            tops.output_msg += (
                f"On router {tops.dut_name} EOS dot1x authentication method "
                f"list is set to: {tops.actual_output}, which is correct.\n\n"
            )
        else:
            tops.test_result = False
            tops.output_msg += (
                f"On router {tops.dut_name} EOS dot1x authentication method "
                f"list is set to: {tops.actual_output}, while "
                f"the expected EOS dot1x authentication method list is {tops.expected_output}.\n\n"
            )
        """
        TS: Creating test report based on results
        """
        tops.parse_test_steps(self.test_if_dot1x_authentication_methods_set_on_)
        tops.generate_report(tops.dut_name, self.output)
        assert tops.actual_output == tops.expected_output

    @pytest.mark.authentication
    @pytest.mark.parametrize("dut", test8_duts, ids=test8_ids)
    def test_if_enable_authentication_methods_set_on_(self, dut, tests_definitions):
        """TD: Verify AAA enable authentication method-lists are set correct

        Args:
          dut (dict): Encapsulates dut details including name, connection
          tests_definitions (dict): Test parameters
        """

        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)

        try:
            """
            TS: Collecting output of show command 'show aaa methods all' from dut
            """
            self.output = dut["output"][tops.show_cmd]["json"]["authentication"]
            assert self.output, "No AAA method details are available"
            logging.info(
                f"On device {tops.dut_name}" f" output of {tops.show_cmd} command is: {self.output}"
            )

            tops.actual_output = self.output["enableAuthenMethods"]["default"]["methods"]
        except (
            AssertionError,
            AttributeError,
            LookupError,
            EapiError,
        ) as exception:
            logging.error(
                f"Error occurred during the testsuite execution on dut:"
                f" {tops.dut_name} is {str(exception)}"
            )
            tops.actual_output = str(exception)

        if tops.actual_output == tops.expected_output:
            tops.test_result = True
            tops.output_msg += (
                f"On router {tops.dut_name} EOS enable authentication method "
                f"list is set to: {tops.actual_output}, which is correct.\n\n"
            )
        else:
            tops.test_result = False
            tops.output_msg += (
                f"On router {tops.dut_name} EOS enable authentication method "
                f"list is set to: {tops.actual_output}, while "
                f"the expected EOS enable authentication method list is {tops.expected_output}.\n\n"
            )
        """
        TS: Creating test report based on results
        """
        tops.parse_test_steps(self.test_if_enable_authentication_methods_set_on_)
        tops.generate_report(tops.dut_name, self.output)
        assert tops.actual_output == tops.expected_output

    @pytest.mark.accounting
    @pytest.mark.parametrize("dut", test9_duts, ids=test9_ids)
    def test_if_system_accounting_methods_set_on_(self, dut, tests_definitions):
        """TD: Verify AAA system accounting method-lists are set correct

        Args:
          dut (dict): Encapsulates dut details including name, connection
          tests_definitions (dict): Test parameters
        """

        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)

        try:
            """
            TS: Collecting output of show command 'show aaa methods all' from dut
            """

            self.output = dut["output"][tops.show_cmd]["json"]["accounting"]["systemAcctMethods"]
            assert self.output, "No AAA method details are available"
            logging.info(
                f"On device {tops.dut_name}" f" output of {tops.show_cmd} command is: {self.output}"
            )

            eos_default_acct = self.output["system"]["defaultMethods"]
            eos_console_acct = self.output["system"]["consoleMethods"]

            tops.expected_output = [
                tops.test_parameters["default_acct"],
                tops.test_parameters["console_acct"],
            ]
            tops.actual_output = [eos_default_acct, eos_console_acct]

        except (
            AssertionError,
            AttributeError,
            LookupError,
            EapiError,
        ) as exception:
            logging.error(
                f"Error occurred during the testsuite execution on dut:"
                f" {tops.dut_name} is {str(exception)}"
            )
            tops.actual_output = str(exception)

        if tops.actual_output == tops.expected_output:
            tops.test_result = True
            tops.output_msg += (
                f"On router {tops.dut_name} default system and "
                f"console system accounting method list "
                f"is {tops.actual_output}, which is correct.\n\n"
            )
        else:
            tops.test_result = False
            tops.output_msg += (
                f"On router {tops.dut_name} default system and "
                f"console system accounting method list "
                f"is {tops.actual_output}, while the expected default system and "
                f"console system accounting method list "
                f"is {tops.expected_output}.\n\n"
            )

        """
        TS: Creating test report based on results
        """
        tops.parse_test_steps(self.test_if_system_accounting_methods_set_on_)
        tops.generate_report(tops.dut_name, self.output)
        assert tops.actual_output == tops.expected_output

    @pytest.mark.accounting
    @pytest.mark.parametrize("dut", test10_duts, ids=test10_ids)
    def test_if_exec_accounting_methods_set_on_(self, dut, tests_definitions):
        """TD: Verify AAA exec accounting method-lists are set correct

        Args:
          dut (dict): Encapsulates dut details including name, connection
          tests_definitions (dict): Test parameters
        """

        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)

        try:
            """
            TS: Collecting output of show command 'show aaa methods all' from dut
            """

            self.output = dut["output"][tops.show_cmd]["json"]["accounting"]["execAcctMethods"]
            assert self.output, "No AAA method details are available"
            logging.info(
                f"On device {tops.dut_name}" f" output of {tops.show_cmd} command is: {self.output}"
            )

            eos_default_acct = self.output["exec"]["defaultMethods"]
            eos_console_acct = self.output["exec"]["consoleMethods"]

            tops.expected_output = [
                tops.test_parameters["default_acct"],
                tops.test_parameters["console_acct"],
            ]
            tops.actual_output = [eos_default_acct, eos_console_acct]

        except (
            AssertionError,
            AttributeError,
            LookupError,
            EapiError,
        ) as exception:
            logging.error(
                f"Error occurred during the testsuite execution on dut:"
                f" {tops.dut_name} is {str(exception)}"
            )
            tops.actual_output = str(exception)

        if tops.actual_output == tops.expected_output:
            tops.test_result = True
            tops.output_msg += (
                f"On router {tops.dut_name} default exec and "
                f"console exec accounting method list "
                f"is {tops.actual_output}, which is correct.\n\n"
            )
        else:
            tops.test_result = False
            tops.output_msg += (
                f"On router {tops.dut_name} default exec and "
                f"console exec accounting method list "
                f"is {tops.actual_output}, while the expected default exec "
                f"and console exec accounting method list "
                f"is {tops.expected_output}.\n\n"
            )

        """
        TS: Creating test report based on results
        """
        tops.parse_test_steps(self.test_if_exec_accounting_methods_set_on_)
        tops.generate_report(tops.dut_name, self.output)
        assert tops.actual_output == tops.expected_output

    @pytest.mark.accounting
    @pytest.mark.parametrize("dut", test11_duts, ids=test11_ids)
    def test_if_privilege_accounting_methods_set_on_(self, dut, tests_definitions):
        """TD: Verify AAA privilege accounting method-lists are set correct

        Args:
          dut (dict): Encapsulates dut details including name, connection
          tests_definitions (dict): Test parameters
        """

        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)

        try:
            """
            TS: Collecting output of show command 'show aaa methods all' from dut
            """

            self.output = dut["output"][tops.show_cmd]["json"]["accounting"]["commandsAcctMethods"]
            assert self.output, "No AAA method details are available"
            logging.info(
                f"On device {tops.dut_name}" f" output of {tops.show_cmd} command is: {self.output}"
            )

            eos_default_acct = self.output["privilege0-15"]["defaultMethods"]
            eos_console_acct = self.output["privilege0-15"]["consoleMethods"]

            tops.expected_output = [
                tops.test_parameters["default_acct"],
                tops.test_parameters["console_acct"],
            ]
            tops.actual_output = [eos_default_acct, eos_console_acct]

        except (
            AssertionError,
            AttributeError,
            LookupError,
            EapiError,
        ) as exception:
            logging.error(
                f"Error occurred during the testsuite execution on dut:"
                f" {tops.dut_name} is {str(exception)}"
            )
            tops.actual_output = str(exception)

        if tops.actual_output == tops.expected_output:
            tops.test_result = True
            tops.output_msg += (
                f"On router {tops.dut_name} default privilege and "
                f"console privilege accounting method list "
                f"is {tops.actual_output}, which is correct.\n\n"
            )
        else:
            tops.test_result = False
            tops.output_msg += (
                f"On router {tops.dut_name} default privilege and "
                f"console privilege accounting method list "
                f"is {tops.actual_output}, while the expected default privilege and "
                f"console privilege accounting method list "
                f"is {tops.expected_output}.\n\n"
            )

        """
        TS: Creating test report based on results
        """
        tops.parse_test_steps(self.test_if_privilege_accounting_methods_set_on_)
        tops.generate_report(tops.dut_name, self.output)
        assert tops.actual_output == tops.expected_output

    @pytest.mark.accounting
    @pytest.mark.parametrize("dut", test12_duts, ids=test12_ids)
    def test_if_dot1x_accounting_methods_set_on_(self, dut, tests_definitions):
        """TD: Verify AAA dot1x accounting method-lists are set correct

        Args:
         dut (dict): Encapsulates dut details including name, connection
         tests_definitions (dict): Test parameters
        """

        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)

        try:
            """
            TS: Collecting output of show command 'show aaa methods all' from dut
            """

            self.output = dut["output"][tops.show_cmd]["json"]["accounting"]["dot1xAcctMethods"]
            assert self.output, "No AAA method details are available"
            logging.info(
                f"On device {tops.dut_name}" f" output of {tops.show_cmd} command is: {self.output}"
            )

            eos_default_acct = self.output["dot1x"]["defaultMethods"]
            eos_console_acct = self.output["dot1x"]["consoleMethods"]

            tops.expected_output = [
                tops.test_parameters["default_acct"],
                tops.test_parameters["console_acct"],
            ]
            tops.actual_output = [eos_default_acct, eos_console_acct]

        except (
            AssertionError,
            AttributeError,
            LookupError,
            EapiError,
        ) as exception:
            logging.error(
                f"Error occurred during the testsuite execution on dut:"
                f" {tops.dut_name} is {str(exception)}"
            )
            tops.actual_output = str(exception)

        if tops.actual_output == tops.expected_output:
            tops.test_result = True
            tops.output_msg += (
                f"On router {tops.dut_name} default dot1x and "
                f"console dot1x accounting method list "
                f"is {tops.actual_output}, which is correct.\n\n"
            )
        else:
            tops.test_result = False
            tops.output_msg += (
                f"On router {tops.dut_name} default dot1x and "
                f"console dot1x accounting method list "
                f"is {tops.actual_output}, while the expected default dot1x and "
                f"console dot1x accounting method list "
                f"is {tops.expected_output}.\n\n"
            )

        """
        TS: Creating test report based on results
        """
        tops.parse_test_steps(self.test_if_dot1x_accounting_methods_set_on_)
        tops.generate_report(tops.dut_name, self.output)
        assert tops.actual_output == tops.expected_output
