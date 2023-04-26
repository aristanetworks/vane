# Copyright (c) 2022 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.
# pylint: disable=pointless-string-statement

"""
Testcase for verification of dynamic BGP functionality on spine
"""

import pytest
from pyeapi.eapilib import EapiError
from vane.logger import logger
from vane.config import dut_objs, test_defs
from vane import tests_tools


TEST_SUITE = "TestBGP"


@pytest.mark.bgp
@pytest.mark.nrfu
class BGPTests:
    """
    Testcases for verification of BGP
    """

    dut_parameters = tests_tools.parametrize_duts(TEST_SUITE, test_defs, dut_objs)
    test_duts = dut_parameters["test_bgp_session_peer_state"]["duts"]
    test_ids = dut_parameters["test_bgp_session_peer_state"]["ids"]

    @pytest.mark.parametrize("dut", test_duts, ids=test_ids)
    def test_bgp_session_peer_state(self, dut, tests_definitions):
        """
        TD: Testcase for verification of BGP session peer state - BGP summary

        Args:
            dut(dict): details related to a particular DUT
            tests_definitions(dict): test suite and test case parameters
        """

        """
        TS: Initializing test case
        """
        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)
        tops.actual_output = {}
        tops.expected_output = {}

        try:
            """
            TS: Collecting the output of 'show ip bgp summary' command from DUT
            """
            output = dut["output"][tops.show_cmd]["json"]
            assert (output.get("vrfs")).get("default"), "Bgp summary details are not found"

            bgp_output = dut["output"][tops.show_cmd]["json"]

            for neighbor in dut["network_configs"]["router_bgp"]["neighbors"]:
                peer_state = dut["network_configs"]["router_bgp"]["neighbors"][neighbor][
                    "peerState"
                ]
                tops.expected_output[neighbor] = peer_state

            for neighbor in bgp_output["vrfs"]["default"]["peers"]:
                peer_state = bgp_output["vrfs"]["default"]["peers"][neighbor]["peerState"]
                tops.actual_output[neighbor] = peer_state

            """
            TS: Comparing BGP neighbor peer states and finding the deltas
            """
            expected_set = set(tops.expected_output.items())
            actual_set = set(tops.actual_output.items())
            expected_deltas = expected_set - actual_set
            actual_deltas = actual_set - expected_set

            if expected_deltas or actual_deltas:
                if expected_deltas:
                    tops.output_msg += (
                        "The following BGP peer state(s) are expected but NOT found on "
                        f"{dut['name']}: "
                    )
                    for delta in expected_deltas:
                        tops.output_msg += (
                            f"\n  - Expected BGP neighbor {delta[0]} with a peer state: {delta[1]}"
                        )

                if actual_deltas:
                    tops.output_msg += (
                        f"\nThe following INCORRECT BGP peer state(s) are found on {dut['name']}: "
                    )
                    for delta in actual_deltas:
                        tops.output_msg += (
                            f"\n  - BGP neighbor {delta[0]} with a peer state: {delta[1]}"
                        )
            else:
                tops.output_msg = f"BGP sesssions peer state(s) are correct on {dut['name']}:"

            tops.output_msg += "\n"

            # Output test data to HTML Report
            print(dut["output"][tops.show_cmd]["text"])

        except (AttributeError, LookupError, EapiError) as exp:
            tops.actual_output = str(exp)
            logger.error(
                "On device %s: Error while running testcase on DUT is: %s", tops.dut_name, str(exp)
            )

        """
        TS: Creating test report based
        """
        tops.parse_test_steps(self.test_bgp_session_peer_state)
        tops.test_result = tops.actual_output == tops.expected_output
        tops.generate_report(tops.dut_name, output)

        """
        TS: Determing pass or fail based on test criteria
        """
        assert tops.actual_output == tops.expected_output
