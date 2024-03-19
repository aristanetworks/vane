# Copyright (c) 2024 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.

"""
Test case to verify that no non-Arista optics are installed on the device
"""

import pytest
from pyeapi.eapilib import EapiError
from vane import test_case_logger, tests_tools
from vane.config import dut_objs, test_defs


TEST_SUITE = "nrfu_tests"
logger = test_case_logger.setup_logger(__file__)


@pytest.mark.nrfu_test
@pytest.mark.interfaces
class InterfaceOpticsTests:
    """
    Test case to verify that no non-Arista optics are installed on the device
    """

    dut_parameters = tests_tools.parametrize_duts(TEST_SUITE, test_defs, dut_objs)
    test_duts = dut_parameters["test_interfaces_non_arista_optics"]["duts"]
    test_ids = dut_parameters["test_interfaces_non_arista_optics"]["ids"]

    @pytest.mark.parametrize("dut", test_duts, ids=test_ids)
    def test_interfaces_non_arista_optics(self, dut, tests_definitions):
        """
        TD: Test case to verify that no non-Arista optics are installed on the device.
        Args:
            dut(dict): details related to a particular DUT
            tests_definitions(dict): test suite and test case parameters.
        """

        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)
        self.output = ""
        tops.actual_output = {"accepted_transceiver_manufacturer_found": {"slots": {}}}
        tops.expected_output = {"accepted_transceiver_manufacturer_found": {"slots": {}}}
        test_params = tops.test_parameters
        accepted_transceiver = test_params["input"]["accepted_transceiver_manufacturers"]
        non_arista_optics = []

        # Output message if the test result is passed
        tops.output_msg = "Non-Arista optics are not installed on the device."

        try:
            """
            TS: Running 'show inventory' command on the device and verifying
            that non-Arista optics should not be installed on the device.
            """
            inventory_output = dut["output"][tops.show_cmd]["json"]
            logger.info(
                (
                    f"On device {tops.dut_name}, output of {tops.show_cmd} command is:"
                    f" \n{inventory_output}\n"
                ),
            )
            self.output += (
                f"\n\nOutput of {tops.show_cmd}, output of {tops.show_cmd} command is:"
                f" \n{inventory_output}"
            )

            # Collecting all transceiver slots from the command output.
            transceiver_slots = inventory_output.get("xcvrSlots", {})

            # Verifying that at least 1 transceiver is installed on the device
            not_installed_transceiver = [
                transceiver_detail.get("mfgName")
                for transceiver_detail in transceiver_slots.values()
                if transceiver_detail.get("mfgName") != "Not Present"
            ]
            assert not_installed_transceiver, "Transceiver slots are not installed on the device."

            # Updating expected and actual optics manufacturer for transceiver
            for transceiver, transceiver_details in transceiver_slots.items():
                manufacturer = transceiver_details.get("mfgName")

                # Checking for transceiver slot having manufacturing information present and in
                # accepted transceiver list.
                if manufacturer != "Not Present":
                    tops.expected_output["accepted_transceiver_manufacturer_found"]["slots"].update(
                        {transceiver: True}
                    )
                    tops.actual_output["accepted_transceiver_manufacturer_found"]["slots"].update(
                        {transceiver: True}
                    )
                    if manufacturer not in accepted_transceiver:
                        tops.actual_output["accepted_transceiver_manufacturer_found"][
                            "slots"
                        ].update({transceiver: False})
                        non_arista_optics.append(f"{transceiver} - {manufacturer}")

            # Forming output message in case of test case failure
            if tops.actual_output != tops.expected_output:
                if non_arista_optics:
                    non_arista_optic = "\n".join(non_arista_optics)
                    tops.output_msg = (
                        "\nFollowing transceiver optics are found as non-Arista and current"
                        f" manufacturer installed on them are as follows:\n{non_arista_optic}"
                    )

        except (AssertionError, AttributeError, LookupError, EapiError) as excep:
            tops.output_msg = tops.actual_output = str(excep).split("\n", maxsplit=1)[0]
            logger.error(
                f"On device {tops.dut_name}, Error while running the test case"
                f" is:\n{tops.actual_output}"
            )

        tops.test_result = tops.expected_output == tops.actual_output
        tops.parse_test_steps(self.test_interfaces_non_arista_optics)
        tops.generate_report(tops.dut_name, self.output)
        assert tops.expected_output == tops.actual_output
