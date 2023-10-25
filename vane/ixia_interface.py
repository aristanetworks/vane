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

"""Ixia modules to interact with IXIA API"""

import time
from ixnetwork_restpy.testplatform.testplatform import TestPlatform
from ixnetwork_restpy.assistants.statistics.statviewassistant import StatViewAssistant
from ixnetwork_restpy.files import Files
from vane.vane_logging import logging
from vane import config


"""
Module 1

Connects to the IXNetwork API Server, authenticates with credentials,
starts a session after specifying license details
"""


def authenticate():
    """Initialise credentials and other details required
    to connect to Ixia Web API"""

    api_server_ip = config.test_duts["traffic_generators"][0]["api_server_ip"]
    licensing_servers = config.test_duts["traffic_generators"][0]["licensing_servers_ip"]
    licensing_mode = config.test_duts["traffic_generators"][0]["licensing_mode"]
    licensing_tier = config.test_duts["traffic_generators"][0]["licensing_tier"]
    rest_port = config.test_duts["traffic_generators"][0]["rest_port"]
    username = config.test_duts["traffic_generators"][0]["username"]
    password = config.test_duts["traffic_generators"][0]["password"]

    # Connect to the IxNetwork API Server

    logging.info("Authenticating into Ixia API")

    test_platform = TestPlatform(api_server_ip, rest_port=rest_port)

    # Set the console output verbosity (none, info, request, request_response)

    test_platform.Trace = "info"

    # Authenticate with the Linux-based API server and start a new session

    test_platform.Authenticate(username, password)

    new_session = test_platform.Sessions.add()

    ix_network = new_session.Ixnetwork

    ix_network.NewConfig()

    # Specify the license server details

    ix_network.Globals.Licensing.LicensingServers = [licensing_servers]

    # Specify the license mode (mixed, subscription, perpetual)

    ix_network.Globals.Licensing.Mode = licensing_mode

    # Specify the license tier (tier1, tier2, tier3, tier3-10g, etc.)

    ix_network.Globals.Licensing.Tier = licensing_tier

    return new_session, ix_network


"""
Module 2

Saves and loads .ixcnfg file into session which configures ports/protocols/traffic items.
Starts and verifies protocols
"""


def configure(ix_network, file_name):
    """Load the saved configuration :
    Sets up the physical ports, the stacks to be tested,
    and the traffic item details

    Args:
    ix_network: ixnetwork created to run this test session
    file_name: configuration file to be loaded for current session"""

    logging.info("Loading in test config")

    ix_network.LoadConfig(Files(file_name))

    # Connect to ports and error out if port is already occupied

    ports = ix_network.Vport.find()
    ports.ConnectPorts(False)

    # Start the protocols

    logging.info("Starting Protocols")

    ix_network.StartAllProtocols(Arg1="sync")

    # Verify generic protocol sessions

    protocols = StatViewAssistant(ix_network, "Protocols Summary")

    protocols.CheckCondition("Sessions Not Started", StatViewAssistant.EQUAL, 0)

    protocols.CheckCondition("Sessions Down", StatViewAssistant.EQUAL, 0)

    logging.info(f"Protocols Summary Statistics:\n{protocols}")

    return ix_network


"""
Module 3

Generates and starts traffic
"""


def generate_traffic(ix_network):
    """Generate, apply and start the traffic item

    Args:
    ix_network: ixnetwork created to run this test session"""

    logging.info("Starting Traffic generation")

    traffic_item = ix_network.Traffic.TrafficItem.find()

    traffic_item.Generate()

    ix_network.Traffic.Apply()

    time.sleep(5)

    ix_network.Traffic.Start()

    # We can loop and check the state of the traffic item until the transmission stops

    while ix_network.Traffic.State in [
        "started",
        "startedWaitingForStats",
        "startedWaitingForStreams",
        "stoppedWaitingForStats",
        "txStopWatchExpected",
    ]:
        time.sleep(2)

    logging.info("Stopped Traffic Generation")

    return ix_network


"""
Module 4

Releases the ports and clears the session
"""


def clear_session(ix_network, session):
    """Clears the Ixia session and releases the ports occupied

    Args:
    ix_network: ixnetwork created to run this test session
    session: current test session"""

    logging.info("Clearing Session")

    if "ixNetwork" in locals():
        ix_network.Vport.find().ReleasePort()

    if "session" in locals():
        session.remove()

    logging.info("Session cleared successfully")
