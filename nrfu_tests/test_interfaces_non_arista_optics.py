# Copyright (c) 2023 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.

"""
Test case to verify that no non-Arista optics are installed on the device
"""

import pytest
from pyeapi.eapilib import EapiError
from vane import test_case_logger
from vane.config import dut_objs, test_defs
from vane import tests_tools


TEST_SUITE = "nrfu_tests"
logging = test_case_logger.setup_logger(__file__)


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
        TD: Test case to verify that no unapproved optics are installed on the device.
        Args:
            dut(dict): details related to a particular DUT
            tests_definitions(dict): test suite and test case parameters.
        """

        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)
        self.output = ""
        tops.actual_output = {"transceiver_slots": {}}
        tops.expected_output = {"transceiver_slots": {}}
        test_parameters = tops.test_parameters

        # Create approved optics list
        approved_optics = ["Arista Networks", "Not Present"] + test_parameters["approved_optics"]
        approved_list = ["Arista Networks"] + test_parameters["approved_optics"]
        approved_string = ", ".join(approved_list)
        logging.info(f"Test case will check the following approved optics: {approved_string}")

        # Output message if the test result is passed
        tops.output_msg = f"Arista approved optics ({approved_string}) are installed on the device."

        try:
            """
            TS: Running 'show inventory' command on the device and verifying
            that non-Arista optics should not be installed on the device.
            """
            inventory_output = dut["output"][tops.show_cmd]["json"]
            logging.info(
                (
                    f"On device {tops.dut_name}, output of {tops.show_cmd} command is:"
                    f" \n{inventory_output}\n"
                ),
            )
            self.output += f"\n\nOutput of {tops.show_cmd} command is: \n{inventory_output}"
            transceiver_slots = inventory_output.get("xcvrSlots")
            assert transceiver_slots, "Transceiver slots are not found on the device."

            # Updating expected and actual optics manufacturer for transceiver
            for transceiver, transceiver_details in transceiver_slots.items():
                manufacturer_name = transceiver_details.get("mfgName")
                tops.expected_output["transceiver_slots"].update(
                    {transceiver: {"manufacture_name": "Arista Networks"}}
                )
                if manufacturer_name in approved_optics:
                    tops.expected_output["transceiver_slots"].update(
                        {transceiver: {"manufacture_name": manufacturer_name}}
                    )
                tops.actual_output["transceiver_slots"].update(
                    {transceiver: {"manufacture_name": manufacturer_name}}
                )

            # Forming output message in case of test case failure
            if tops.output_msg != tops.expected_output:
                non_arista_optics = []
                for transceiver, expected_transceiver_info in tops.expected_output[
                    "transceiver_slots"
                ].items():
                    actual_transceiver_info = tops.actual_output["transceiver_slots"][transceiver][
                        "manufacture_name"
                    ]
                    if actual_transceiver_info == expected_transceiver_info["manufacture_name"]:
                        continue
                    non_arista_optics.append(f"{transceiver} - {actual_transceiver_info}")
                if non_arista_optics:
                    non_arista_optic = "\n".join(non_arista_optics)
                    tops.output_msg = (
                        "\nFollowing transceiver optics are found as non-Arista and current"
                        f" manufacturer installed on them are as follows:\n{non_arista_optic}"
                    )

        except (AssertionError, AttributeError, LookupError, EapiError) as excep:
            tops.output_msg = tops.actual_output = str(excep).split("\n", maxsplit=1)[0]
            logging.error(
                f"On device {tops.dut_name}, Error while running the test case"
                f" is:\n{tops.actual_output}"
            )

        tops.test_result = tops.expected_output == tops.actual_output
        tops.parse_test_steps(self.test_interfaces_non_arista_optics)
        tops.generate_report(tops.dut_name, self.output)
        assert tops.expected_output == tops.actual_output
