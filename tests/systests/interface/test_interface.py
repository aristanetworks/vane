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

import pytest
from vane import tests_tools


TEST_SUITE = __file__
LOG_FILE = {"parameters": {"show_log": "show_output.log"}}


@pytest.mark.demo
@pytest.mark.nrfu
@pytest.mark.interface_baseline_health
@pytest.mark.interface
class InterfaceStatusTests:
    """Interface Status Test Suite"""

    @pytest.mark.virtual
    @pytest.mark.physical
    @pytest.mark.eos424
    def test_if_intf_protocol_status_is_connected_on_(
        self, dut, tests_definitions
    ):
        """Verify the interfaces of interest protocol statuses are up

        Args:
            dut (dict): Encapsulates dut details including name, connection
            tests_definitions (dict): Test parameters
        """

        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)

        print(f"\nOn router |{tops.dut_name}|:")

        for interface in tops.interface_list:
            interface_name = interface["interface_name"].replace(" ", "")
            int_ptr = dut["output"][tops.show_cmd]["json"]["interfaceStatuses"]
            tops.actual_output = int_ptr[interface_name]["lineProtocolStatus"]
            tops.test_result = tops.actual_output == tops.expected_output

            tops.output_msg += (
                f"On interface |{interface_name}|: interface link "
                f"line protocol status is set to: |{tops.actual_output}|"
                f", correct state is |{tops.expected_output}|.\n\n"
            )

            tops.actual_results.append(tops.actual_output)
            tops.expected_results.append(tops.expected_output)


        print(f"{tops.output_msg}\n{tops.comment}")

        tops.actual_output, tops.expected_output = (
            tops.actual_results,
            tops.expected_results,
        )
        tops.post_testcase()

        assert tops.actual_results == tops.expected_results

    @pytest.mark.virtual
    @pytest.mark.physical
    @pytest.mark.eos424
    def test_if_intf_link_status_is_connected_on_(self, dut, tests_definitions):
        """Verify the interfaces of interest link statuses are up

        Args:
            dut (dict): Encapsulates dut details including name, connection
            tests_definitions (dict): Test parameters
        """

        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)

        print(f"\nOn router |{tops.dut_name}|:")

        for interface in tops.interface_list:
            interface_name = interface["interface_name"].replace(" ", "")
            int_ptr = dut["output"][tops.show_cmd]["json"]["interfaceStatuses"]
            tops.actual_output = int_ptr[interface_name]["linkStatus"]
            tops.test_result = tops.actual_output == tops.expected_output

            tops.output_msg += (
                f"On interface |{interface_name}|: interface link "
                f" status is set to: |{tops.actual_output}|"
                f", correct state is |{tops.expected_output}|.\n\n"
            )

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
@pytest.mark.interface_baseline_health
@pytest.mark.interface
class InterfacePhyTests:
    """Interface Status Test Suite"""

    @pytest.mark.physical
    @pytest.mark.eos424
    def test_if_intf_phy_status_connected_on_(self, dut, tests_definitions):
        """Verify the interfaces of interest physical state is link up

        Args:
            dut (dict): Encapsulates dut details including name, connection
            tests_definitions (dict): Test parameters
        """

        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)
        veos_bool = tests_tools.verify_veos(dut)

        if not veos_bool:
            print(f"\nOn router |{tops.dut_name}|:")

            for interface in tops.interface_list:
                interface_name = interface["interface_name"].replace(" ", "")
                int_ptr = dut["output"][show_cmd]["json"][
                    "interfacePhyStatuses"
                ]
                raw_output = int_ptr[interface_name]["phyStatuses"][0]["text"]
                split_output = raw_output.split("\n")

                for line_output in split_output:
                    if "PHY state" in line_output:
                        tops.actual_output = line_output.split()[2]
                        tops.test_result = (
                            tops.actual_output == tops.expected_output
                        )

                        tops.output_msg += (
                            f"On interface |{interface_name}|: "
                            f"physical detail PHY state is set to: "
                            f"|{tops.actual_output}|, correct state is "
                            f"|{tops.expected_output}|.\n\n"
                        )


                        tops.actual_results.append(tops.actual_output)
                        tops.expected_results.append(tops.expected_output)

            print(f"{tops.output_msg}\n{tops.comment}")

            tops.actual_output, tops.expected_output = (
                tops.actual_results,
                tops.expected_results,
            )
            tops.post_testcase()

            assert tops.actual_results == tops.expected_results
        else:

            tops.test_result, tops.output_msg, tops.actual_output = (
                True,
                None,
                None,
            )

            tops.post_testcase()


@pytest.mark.nrfu
@pytest.mark.interface_baseline_health
@pytest.mark.interface
class InterfaceCountersTests:
    """Interface Status Test Suite"""

    @pytest.mark.virtual
    @pytest.mark.physical
    @pytest.mark.eos424
    def test_if_intf_counters_has_input_errors_on_(
        self, dut, tests_definitions
    ):
        """Verify the interfaces of interest does not have input errors

        Args:
            dut (dict): Encapsulates dut details including name, connection
        """

        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)

        print(f"\nOn router |{tops.dut_name}|:")

        for interface in tops.interface_list:
            interface_name = interface["interface_name"].replace(" ", "")
            int_ptr = dut["output"][tops.show_cmd]["json"][
                "interfaceErrorCounters"
            ]
            tops.actual_output = int_ptr[interface_name]["inErrors"]
            tops.test_result = tops.actual_output <= tops.expected_output

            tops.output_msg += (
                f"On interface |{interface_name}|: interface "
                f"counter errors has |{tops.actual_output}| inErrors"
                f", correct state is |{tops.expected_output}|.\n\n"
            )

            tops.actual_results.append(tops.actual_output)
            tops.expected_results.append(tops.expected_output)

        print(f"{tops.output_msg}\n{tops.comment}")

        tops.actual_output, tops.expected_output = (
            tops.actual_results,
            tops.expected_results,
        )
        tops.post_testcase()

        assert tops.actual_results == tops.expected_results

    @pytest.mark.virtual
    @pytest.mark.physical
    @pytest.mark.eos424
    def test_if_intf_counters_has_output_errors_on_(
        self, dut, tests_definitions
    ):
        """Verify the interfaces of interest does not have output errors

        Args:
            dut (dict): Encapsulates dut details including name, connection
        """

        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)

        print(f"\nOn router |{tops.dut_name}|:")

        for interface in tops.interface_list:
            interface_name = interface["interface_name"].replace(" ", "")
            int_ptr = dut["output"][tops.show_cmd]["json"][
                "interfaceErrorCounters"
            ]
            tops.actual_output = int_ptr[interface_name]["outErrors"]
            tops.test_result = tops.actual_output <= tops.expected_output

            tops.output_msg += (
                f"On interface |{interface_name}|: interface "
                f"counter errors has |{tops.actual_output}| outErrors"
                f", correct state is |{tops.expected_output}|.\n\n"
            )

            tops.actual_results.append(tops.actual_output)
            tops.expected_results.append(tops.expected_output)

        print(f"{tops.output_msg}\n{tops.comment}")

        tops.actual_output, tops.expected_output = (
            tops.actual_results,
            tops.expected_results,
        )
        tops.post_testcase()

        assert tops.actual_results == tops.expected_results

    @pytest.mark.virtual
    @pytest.mark.physical
    @pytest.mark.eos424
    def test_if_intf_counters_has_frame_too_short_errors_on_(
        self, dut, tests_definitions
    ):
        """Verify the interfaces of interest have no frameTooShorts errors

        Args:
            dut (dict): Encapsulates dut details including name, connection
        """

        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)

        print(f"\nOn router |{tops.dut_name}|:")

        for interface in tops.interface_list:
            interface_name = interface["interface_name"].replace(" ", "")
            int_ptr = dut["output"][tops.show_cmd]["json"][
                "interfaceErrorCounters"
            ]
            tops.actual_output = int_ptr[interface_name]["frameTooShorts"]
            tops.test_result = tops.actual_output <= tops.expected_output

            tops.output_msg += (
                f"On interface |{interface_name}|: interface "
                f"counter errors has |{tops.actual_output}| "
                "frameTooShorts, correct state is "
                f"|{tops.expected_output}|.\n\n"
            )

            tops.actual_results.append(tops.actual_output)
            tops.expected_results.append(tops.expected_output)

        print(f"{tops.output_msg}\n{tops.comment}")

        tops.actual_output, tops.expected_output = (
            tops.actual_results,
            tops.expected_results,
        )
        tops.post_testcase()

        assert tops.actual_results == tops.expected_results

    @pytest.mark.virtual
    @pytest.mark.physical
    @pytest.mark.eos424
    def test_if_intf_counters_has_frame_too_long_errors_on_(
        self, dut, tests_definitions
    ):
        """Verify the interfaces of interest have no frameLongShorts errors

        Args:
            dut (dict): Encapsulates dut details including name, connection
        """

        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)

        print(f"\nOn router |{tops.dut_name}|:")

        for interface in tops.interface_list:
            interface_name = interface["interface_name"].replace(" ", "")
            int_ptr = dut["output"][tops.show_cmd]["json"][
                "interfaceErrorCounters"
            ]
            tops.actual_output = int_ptr[interface_name]["frameTooLongs"]
            tops.test_result = tops.actual_output <= tops.expected_output

            tops.output_msg += (
                f"On interface |{interface_name}|: interface "
                f"counter errors has |{tops.actual_output}| "
                "frameTooLongs, correct state is "
                f"|{tops.expected_output}|.\n\n"
            )

            tops.actual_results.append(tops.actual_output)
            tops.expected_results.append(tops.expected_output)

        print(f"{tops.output_msg}\n{tops.comment}")

        tops.actual_output, tops.expected_output = (
            tops.actual_results,
            tops.expected_results,
        )
        tops.post_testcase()

        assert tops.actual_results == tops.expected_results

    @pytest.mark.virtual
    @pytest.mark.physical
    @pytest.mark.eos424
    def test_if_intf_counters_has_fcs_errors_on_(self, dut, tests_definitions):
        """Verify the interfaces of interest have no fcsErrors errors

        Args:
            dut (dict): Encapsulates dut details including name, connection
        """

        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)

        print(f"\nOn router |{tops.dut_name}|:")

        for interface in tops.interface_list:
            interface_name = interface["interface_name"].replace(" ", "")
            int_ptr = dut["output"][tops.show_cmd]["json"][
                "interfaceErrorCounters"
            ]
            tops.actual_output = int_ptr[interface_name]["fcsErrors"]
            tops.test_result = tops.actual_output <= tops.expected_output

            tops.output_msg += (
                f"On interface |{interface_name}|: interface "
                f"counter errors has |{tops.actual_output}| "
                "fcsErrors, correct state is "
                f"|{tops.expected_output}|.\n\n"
            )

            tops.actual_results.append(tops.actual_output)
            tops.expected_results.append(tops.expected_output)

        print(f"{tops.output_msg}\n{tops.comment}")

        tops.actual_output, tops.expected_output = (
            tops.actual_results,
            tops.expected_results,
        )
        tops.post_testcase()

        assert tops.actual_results == tops.expected_results

    @pytest.mark.virtual
    @pytest.mark.physical
    @pytest.mark.eos424
    def test_if_intf_counters_has_alignment_errors_on_(
        self, dut, tests_definitions
    ):
        """Verify the interfaces of interest have no alignmentErrors errors

        Args:
            dut (dict): Encapsulates dut details including name, connection
        """

        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)

        print(f"\nOn router |{tops.dut_name}|:")

        for interface in tops.interface_list:
            interface_name = interface["interface_name"].replace(" ", "")
            int_ptr = dut["output"][tops.show_cmd]["json"][
                "interfaceErrorCounters"
            ]
            tops.actual_output = int_ptr[interface_name]["alignmentErrors"]
            tops.test_result = tops.actual_output <= tops.expected_output

            tops.output_msg += (
                f"On interface |{interface_name}|: interface "
                f"counter errors has |{tops.actual_output}| "
                "alignmentErrors, correct state is "
                f"|{tops.expected_output}|.\n\n"
            )

            tops.actual_results.append(tops.actual_output)
            tops.expected_results.append(tops.expected_output)


        print(f"{tops.output_msg}\n{tops.comment}")

        tops.actual_output, tops.expected_output = (
            tops.actual_results,
            tops.expected_results,
        )
        tops.post_testcase()

        assert tops.actual_results == tops.expected_results

    @pytest.mark.virtual
    @pytest.mark.physical
    @pytest.mark.eos424
    def test_if_intf_counters_has_symbol_errors_on_(
        self, dut, tests_definitions
    ):
        """Verify the interfaces of interest have no alignmentErrors errors

        Args:
            dut (dict): Encapsulates dut details including name, connection
        """

        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)

        print(f"\nOn router |{tops.dut_name}|:")

        for interface in tops.interface_list:
            interface_name = interface["interface_name"].replace(" ", "")
            int_ptr = dut["output"][tops.show_cmd]["json"][
                "interfaceErrorCounters"
            ]
            tops.actual_output = int_ptr[interface_name]["symbolErrors"]
            tops.test_result = tops.actual_output <= tops.expected_output

            tops.output_msg += (
                f"On interface |{interface['interface_name']}|: "
                f"interface counter errors has |{tops.actual_output}| "
                "symbolErrors, correct state is "
                f"|{tops.expected_output}|.\n\n"
            )


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
@pytest.mark.interface_baseline_health
@pytest.mark.interface
class InterfaceDiscardTests:
    """Interface Discard Test Suite"""

    @pytest.mark.virtual
    @pytest.mark.physical
    @pytest.mark.eos424
    def test_if_intf_out_counters_are_discarding_on_(
        self, dut, tests_definitions
    ):
        """Verify the interfaces of interest have no outDiscards

        Args:
            dut (dict): Encapsulates dut details including name, connection
        """

        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)

        print(f"\nOn router |{tops.dut_name}|:")

        for interface in tops.interface_list:
            interface_name = interface["interface_name"].replace(" ", "")
            int_ptr = dut["output"][tops.show_cmd]["json"]["interfaces"]
            tops.actual_output = int_ptr[interface_name]["outDiscards"]
            tops.test_result = tops.actual_output <= tops.expected_output

            tops.output_msg += (
                f"On interface |{interface_name}|: interface "
                f"counter discards has |{tops.actual_output}| "
                f"outDiscards, correct state is |{tops.expected_output}|.\n\n"
            )


            tops.actual_results.append(tops.actual_output)
            tops.expected_results.append(tops.expected_output)


        print(f"{tops.output_msg}\n{tops.comment}")

        tops.actual_output, tops.expected_output = (
            tops.actual_results,
            tops.expected_results,
        )
        tops.post_testcase()

        assert tops.actual_results == tops.expected_results

    @pytest.mark.virtual
    @pytest.mark.physical
    @pytest.mark.eos424
    def test_if_intf_in_counters_are_discarding_on_(
        self, dut, tests_definitions
    ):
        """Verify the interfaces of interest have no inDiscards

        Args:
            dut (dict): Encapsulates dut details including name, connection
        """

        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)

        print(f"\nOn router |{tops.dut_name}|:")

        for interface in tops.interface_list:
            interface_name = interface["interface_name"].replace(" ", "")
            int_ptr = dut["output"][tops.show_cmd]["json"]["interfaces"]
            tops.actual_output = int_ptr[interface_name]["inDiscards"]
            tops.test_result = tops.actual_output <= tops.expected_output

            tops.output_msg += (
                f"On interface |{interface_name}|: interface "
                f"counter discards has |{tops.actual_output}| "
                f"inDiscards, correct state is |{tops.expected_output}|.\n\n"
            )

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
@pytest.mark.interface_baseline_health
@pytest.mark.interface
class InterfaceMtuTests:
    """Interface MTU Test Suite"""

    @pytest.mark.virtual
    @pytest.mark.physical
    def test_if_intf_mtu_is_correct_on_(self, dut, tests_definitions):
        """Verify the interfaces of interest have no inDiscards

        Args:
            dut (dict): Encapsulates dut details including name, connection
        """

        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)

        print(f"\nOn router |{tops.dut_name}|:")

        for interface in tops.interface_list:
            interface_name = interface["interface_name"].replace(" ", "")
            int_ptr = dut["output"][tops.show_cmd]["json"]["interfaces"]
            tops.actual_output = int_ptr[interface_name]["mtu"]
            tops.test_result = tops.actual_output == tops.expected_output

            tops.output_msg += (
                f"On interface |{interface_name}|: interface "
                f"MTU is |{tops.actual_output}|, correct MTU is "
                f"|{tops.expected_output}|.\n\n"
            )

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
@pytest.mark.interface_baseline_health
@pytest.mark.interface
class InterfaceCountersTests:
    """Interface Errors Test Suite"""

    @pytest.mark.virtual
    @pytest.mark.physical
    @pytest.mark.eos424
    def test_if_interface_errors_on_(self, dut, tests_definitions):
        """Verify the interfaces of interest have no inDiscards

        Args:
            dut (dict): Encapsulates dut details including name, connection
        """

        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)

        print(f"\nOn router |{tops.dut_name}|:")

        for interface in tops.interface_list:
            interface_name = interface["interface_name"].replace(" ", "")
            int_ptr = dut["output"][tops.show_cmd]["json"]["interfaces"][
                interface_name
            ]
            tops.actual_output = int_ptr["interfaceCounters"]["totalInErrors"]
            tops.test_result = tops.actual_output <= tops.expected_output

            tops.output_msg += (
                f"On interface |{interface_name}|: interface "
                f"Rx errors is |{tops.actual_output}|, correct Rx errors is "
                f"|{tops.expected_output}|.\n\n"
            )

            tops.actual_results.append(tops.actual_output)
            tops.expected_results.append(tops.expected_output)

            tops.actual_output = int_ptr["interfaceCounters"][
                "inputErrorsDetail"
            ]["giantFrames"]
            tops.test_result = tops.actual_output <= tops.expected_output

            tops.output_msg += (
                f"On interface |{interface_name}|: interface "
                f"Giant Frames is |{tops.actual_output}|, correct Giant Frames is "
                f"|{tops.expected_output}|.\n\n"
            )

            tops.actual_results.append(tops.actual_output)
            tops.expected_results.append(tops.expected_output)

            tops.actual_output = int_ptr["interfaceCounters"]["totalOutErrors"]
            tops.test_result = tops.actual_output <= tops.expected_output

            tops.output_msg += (
                f"On interface |{interface_name}|: interface "
                f"Tx Errors is |{tops.actual_output}|, correct Tx Errors is "
                f"|{tops.expected_output}|.\n\n"
            )

            tops.actual_results.append(tops.actual_output)
            tops.expected_results.append(tops.expected_output)

            tops.actual_output = int_ptr["interfaceCounters"][
                "inputErrorsDetail"
            ]["runtFrames"]
            tops.test_result = tops.actual_output <= tops.expected_output

            tops.output_msg += (
                f"On interface |{interface_name}|: interface "
                f"Runt Frames is |{tops.actual_output}|, correct Runt Frames is "
                f"|{tops.expected_output}|.\n\n"
            )

            tops.actual_results.append(tops.actual_output)
            tops.expected_results.append(tops.expected_output)

            tops.actual_output = int_ptr["interfaceCounters"][
                "inputErrorsDetail"
            ]["fcsErrors"]
            tops.test_result = tops.actual_output <= tops.expected_output

            tops.output_msg += (
                f"On interface |{interface_name}|: interface "
                f"FCS Errors is |{tops.actual_output}|, correct FCS Errors is "
                f"|{tops.expected_output}|.\n\n"
            )


            tops.actual_results.append(tops.actual_output)
            tops.expected_results.append(tops.expected_output)

            tops.actual_output = int_ptr["interfaceCounters"][
                "inputErrorsDetail"
            ]["alignmentErrors"]
            tops.test_result = tops.actual_output <= tops.expected_output

            tops.output_msg += (
                f"On interface |{interface_name}|: interface "
                f"Alignment Errors is |{tops.actual_output}|, correct Alignment Errors is "
                f"|{tops.expected_output}|.\n\n"
            )

            tops.actual_results.append(tops.actual_output)
            tops.expected_results.append(tops.expected_output)

        print(f"{tops.output_msg}\n{tops.comment}")

        tops.actual_output, tops.expected_output = (
            tops.actual_results,
            tops.expected_results,
        )
        tops.post_testcase()

        assert tops.actual_results == tops.expected_results

    def test_interface_utilization_on_(self, dut, tests_definitions):
        """Verify the interfaces of interest have no inDiscards

        Args:
            dut (dict): Encapsulates dut details including name, connection
        """

        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)

        print(f"\nOn router |{tops.dut_name}|:")

        for interface in tops.interface_list:
            interface_name = interface["interface_name"].replace(" ", "")
            int_ptr = dut["output"][tops.show_cmd]["json"]["interfaces"][
                interface_name
            ]
            in_bps = int_ptr["interfaceStatistics"]["inBitsRate"]

            if tops.verify_veos():
                bandwidth = 10000000000
            else:
                bandwidth = int_ptr["bandwidth"]

            if in_bps == 0:
                tops.actual_output = in_bps
            else:
                tops.actual_output = (in_bps / bandwidth) * 100.00

            tops.test_result = tops.actual_output <= tops.expected_output

            tops.output_msg += (
                f"On interface |{interface_name}|: input bandwidth "
                f"utilization is |{tops.actual_output}%|, "
                f"bandwidth utilization should be less than |{tops.expected_output}%|.\n\n"
            )


            tops.actual_results.append(tops.test_result)
            tops.expected_results.append(True)

            out_bps = int_ptr["interfaceStatistics"]["outBitsRate"]

            if out_bps == 0:
                tops.actual_output = out_bps
            else:
                tops.actual_output = (out_bps / bandwidth) * 100.00

            tops.test_result = tops.actual_output <= tops.expected_output

            tops.output_msg += (
                f"On interface |{interface_name}|: output bandwidth "
                f"utilization is |{tops.actual_output}%|, "
                f"bandwidth utilization should be less than |{tops.expected_output}%|.\n\n"
            )


            tops.actual_results.append(tops.test_result)
            tops.expected_results.append(True)


        print(f"{tops.output_msg}\n{tops.comment}")

        tops.actual_output, tops.expected_output = (
            tops.actual_results,
            tops.expected_results,
        )
        tops.post_testcase()

        assert tops.actual_results == tops.expected_results
