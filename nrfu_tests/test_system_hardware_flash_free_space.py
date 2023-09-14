# Copyright (c) 2023 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.

"""
Test case for verification of free space on flash file system
"""

import pytest
from pyeapi.eapilib import EapiError
from vane.config import dut_objs, test_defs
from vane import tests_tools, test_case_logger

TEST_SUITE = "nrfu_tests"
logging = test_case_logger.setup_logger(__file__)


@pytest.mark.nrfu_test
@pytest.mark.system
class FlashFreeSpaceTests:
    """
    Test case for verification of free space on flash file system
    """

    dut_parameters = tests_tools.parametrize_duts(TEST_SUITE, test_defs, dut_objs)
    test_duts = dut_parameters["test_system_flash_free_space"]["duts"]
    test_ids = dut_parameters["test_system_flash_free_space"]["ids"]

    @pytest.mark.parametrize("dut", test_duts, ids=test_ids)
    def test_system_flash_free_space(self, dut, tests_definitions):
        """
        TD: Test case for verification of free space on the flash file system
        Args:
            dut(dict): details related to a particular DUT
            tests_definitions(dict): test suite and test case parameters.
        """

        tops = tests_tools.TestOps(tests_definitions, TEST_SUITE, dut)
        tops.actual_output = {}
        self.output = ""
        flash_size = ""
        flash_free = ""
        peer_flash_size = ""
        peer_flash_free = ""
        peer_supervisor_cmd = 'bash timeout 60 FastCli -p15 -c "session peer-supervisor dir flash:"'
        tops.output_msg = "Primary and peer supervisor flash file system utilization is below 70%."

        try:
            """
            TS: Running `show file systems` command on dut and verifying that the primary supervisor
            flash file system utilization is within the range.
            """
            output = dut["output"][tops.show_cmd]["json"]
            logging.info(
                f"On device {tops.dut_name}, output of {tops.show_cmd} command is:\n{output}\n"
            )
            self.output += f"Output of {tops.show_cmd} command is:\n{output}\n"

            for drive in output["fileSystems"]:
                if "flash:" in drive["prefix"]:
                    flash_size = drive["size"]
                    flash_free = drive["free"]
                    break
            flash_utilization = round(100 - int(flash_free) / int(flash_size) * 100, 2)
            tops.actual_output["primary_supervisor_flash_utilization_within_range"] = (
                flash_utilization <= 70
            )

            """
            TS: Running `bash timeout 60 FastCli -p15 -c "session peer-supervisor dir flash:"`
            command on dut and verifying that peer supervisor flash file system utilization is
            within the range.
            """
            output = tops.run_show_cmds([peer_supervisor_cmd])
            logging.info(
                f"On device {tops.dut_name}, output of {peer_supervisor_cmd} command"
                f" is:\n{output}\n"
            )
            self.output += f"\nOutput of {peer_supervisor_cmd} command is:\n{output}"
            output = output[0]["result"]["messages"][0].split("\n")

            for line in output:
                if "bytes total" in line:
                    peer_flash_size = line.split(" ")[0]
                    peer_flash_free = line.split(" ")[3].split("(")[1]
            peer_flash_utilization = round(
                100 - int(peer_flash_free) / int(peer_flash_size) * 100, 2
            )
            tops.actual_output["peer_supervisor_flash_utilization_within_range"] = (
                peer_flash_utilization <= 70
            )

            # Output message formation in case of test case fails.
            if tops.actual_output != tops.expected_output:
                tops.output_msg = "\n"
                for utilization, supervisor in zip(
                    [flash_utilization, peer_flash_utilization], tops.actual_output.keys()
                ):
                    if utilization > 70:
                        msg = supervisor.replace("_within_range", "").replace("_", " ").capitalize()
                        tops.output_msg += (
                            f"{msg} is not correct. Expected utilization is below '70%' however in"
                            f" actual found as '{utilization}%'.\n"
                        )

        except (AttributeError, LookupError, EapiError) as excep:
            tops.output_msg = tops.actual_output = str(excep).split("\n", maxsplit=1)[0]
            logging.error(
                f"On device {tops.dut_name}, Error while running the test case"
                f" is:\n{tops.actual_output}"
            )

        tops.test_result = tops.expected_output == tops.actual_output
        tops.parse_test_steps(self.test_system_flash_free_space)
        tops.generate_report(tops.dut_name, self.output)
        assert tops.expected_output == tops.actual_output
