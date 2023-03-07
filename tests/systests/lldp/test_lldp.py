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
import pytest
from vane import tests_tools
from vane.fixtures import dut, tests_definitions


TEST_SUITE = __file__

@pytest.mark.nrfu
@pytest.mark.l2_protocols
@pytest.mark.lldp
@pytest.mark.virtual
@pytest.mark.physical
@pytest.mark.eos424
class LldpTests:
    """LLDP Test Suite"""

    def test_if_lldp_rx_is_enabled_on_(self, dut, tests_definitions):
        """Verify LLDP receive is enabled on interesting interfaces

        Args:
            dut (dict): Encapsulates dut details including name, connection
        """

        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)

        print(f"\nOn router |{tops.dut_name}|:")

        for interface in tops.interface_list:
            interface_name = interface["interface_name"].replace(" ", "")
            int_ptr = dut["output"][tops.show_cmd]["json"]["lldpInterfaces"]
            tops.actual_output = int_ptr[interface_name]["rxEnabled"]

            tops.output_msg += (
                f"On interface |{interface_name}|: interface LLDP"
                f"rxEnabled is in state |{tops.actual_output}|, correct "
                f"LLDP rxEnabled state is |{tops.expected_output}|"
            )

            tops.test_result = tops.actual_output == tops.expected_output

            tops.actual_results.append(tops.actual_output)
            tops.expected_results.append(tops.expected_output)


        print(f"{tops.output_msg}\n{tops.comment}")

        tops.actual_output, tops.expected_output = (
            tops.actual_results,
            tops.expected_results,
        )
        tops.post_testcase()

        assert tops.actual_results == tops.expected_results

    def test_if_lldp_tx_is_enabled_on_(self, dut, tests_definitions):
        """Verify LLDP transmit is enabled on interesting interfaces

        Args:
            dut (dict): Encapsulates dut details including name, connection
        """

        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)

        print(f"\nOn router |{tops.dut_name}|:")

        for interface in tops.interface_list:
            interface_name = interface["interface_name"].replace(" ", "")
            int_ptr = dut["output"][tops.show_cmd]["json"]["lldpInterfaces"]
            tops.actual_output = int_ptr[interface_name]["txEnabled"]

            tops.output_msg += (
                f"On interface |{interface_name}|: interface LLDP"
                f"txEnabled is in state |{tops.actual_output}|, correct "
                f"LLDP txEnabled state is |{tops.expected_output}|.\n\n"
            )

            tops.test_result = tops.actual_output == tops.expected_output

            tops.actual_results.append(tops.actual_output)
            tops.expected_results.append(tops.expected_output)


        print(f"{tops.output_msg}\n{tops.comment}")

        tops.actual_output, tops.expected_output = (
            tops.actual_results,
            tops.expected_results,
        )
        tops.post_testcase()

        assert tops.actual_results == tops.expected_results


@pytest.mark.nrfu
@pytest.mark.l2_protocols
@pytest.mark.lldp
@pytest.mark.virtual
@pytest.mark.physical
@pytest.mark.eos424
class LldpLocalInfoTests:
    """LLDP Local-Info Test Suite"""

    def test_if_lldp_system_name_is_correct_on_(self, dut, tests_definitions):
        """Verify show lldp local-info hostname is the system's name

        Args:
            dut (dict): Encapsulates dut details including name, connection
        """

        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)

        tops.expected_output = tops.dut_name
        tops.actual_output = dut["output"][tops.show_cmd]["json"]["systemName"]

        tops.output_msg = (
            f"On router |{tops.dut_name}|: the LLDP local-info system "
            f"name is |{tops.actual_output}|, correct name is "
            f"|{tops.expected_output}|.\n\n"
        )
        tops.test_result = tops.actual_output == tops.expected_output


        print(f"{tops.output_msg}\n{tops.comment}")

        tops.post_testcase()

        assert tops.actual_output == tops.expected_output

    def test_if_lldp_max_frame_size_is_correct_on_(
        self, dut, tests_definitions
    ):
        """Verify show lldp local-info maxFrameSize is correct

        Args:
            dut (dict): Encapsulates dut details including name, connection
        """

        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)

        print(f"\nOn router |{tops.dut_name}|:")

        for interface in tops.interface_list:
            interface_name = interface["interface_name"].replace(" ", "")
            int_ptr = dut["output"][tops.show_cmd]["json"]["localInterfaceInfo"]
            tops.actual_output = int_ptr[interface_name]["maxFrameSize"]

            tops.output_msg += (
                f"On interface |{interface_name}|: LLDP local-info "
                f"maxFrameSize is |{tops.actual_output}|, correct "
                f"maxFrameSize is |{tops.expected_output}|.\n\n"
            )
            tops.test_result = tops.actual_output == tops.expected_output


            tops.actual_results.append(tops.actual_output)
            tops.expected_results.append(tops.expected_output)

        print(f"{tops.output_msg}\n{tops.comment}")

        tops.actual_output, tops.expected_output = (
            tops.actual_results,
            tops.expected_results,
        )
        tops.post_testcase()

        assert tops.actual_results == tops.expected_results

    def test_if_lldp_interface_id_is_correct_on_(self, dut, tests_definitions):
        """Verify show lldp local-info interfaceIdType is correct

        Args:
            dut (dict): Encapsulates dut details including name, connection
        """

        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)

        print(f"\nOn router |{tops.dut_name}|:")

        for interface in tops.interface_list:
            interface_name = interface["interface_name"].replace(" ", "")
            int_ptr = dut["output"][tops.show_cmd]["json"]["localInterfaceInfo"]
            tops.actual_output = int_ptr[interface_name]["interfaceIdType"]

            tops.output_msg += (
                f"On interface |{interface_name}|: LLDP local-info "
                f"interfaceIdType is |{tops.actual_output}|, correct "
                f"interfaceIdType is |{tops.expected_output}|.\n\n"
            )
            tops.test_result = tops.actual_output == tops.expected_output

            tops.actual_results.append(tops.actual_output)
            tops.expected_results.append(tops.expected_output)

        print(f"{tops.output_msg}\n{tops.comment}")

        tops.actual_output, tops.expected_output = (
            tops.actual_results,
            tops.expected_results,
        )
        tops.post_testcase()

        assert tops.actual_results == tops.expected_results
