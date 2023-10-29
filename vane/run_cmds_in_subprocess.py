# Copyright (c) 2022 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.

"""Command execution on dut/server using paramiko and subprocess popen method"""

import sys
import logging
from vane import utils

logging.basicConfig(
    level=logging.INFO,
    filename="run_tcpdump_on_server.log",
    filemode="w",
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logging.info("Starting the sub-process")

HOST = sys.argv[1]
USER = sys.argv[2]
PASSWORD = sys.argv[3]
WAIT = int(sys.argv[4])
CMDS = sys.argv[5:]

logging.info("Host: %s\nUser: %s\nPassword: %s\nCommand: %s", HOST, USER, PASSWORD, CMDS)
OUTPUT = utils.get_ssh_cmd_output(HOST, USER, PASSWORD, CMDS, WAIT)
logging.info("SSH Command output in subprocess: %s", OUTPUT)
