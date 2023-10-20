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

from ixnetwork_restpy.testplatform.testplatform import TestPlatform
from ixnetwork_restpy.assistants.statistics.statviewassistant import StatViewAssistant
from ixnetwork_restpy.files import Files
from vane.vane_logging import logging
from vane import config
import time

"""
Module 1

Connects to the IXNetwork API Server, authenticates with credentials,
starts a session after specifying license details
"""


def authenticate():
    # Initialise credentials and other details required to connect to Ixia Web API

    API_SERVER_IP = config.test_duts["ixia"][0]["api_server_ip"]
    LICENSING_SERVERS = config.test_duts["ixia"][0]["licensing_servers_ip"]
    LICENSING_MODE = config.test_duts["ixia"][0]["licensing_mode"]
    LICENSING_TIER = config.test_duts["ixia"][0]["licensing_tier"]
    REST_PORT = config.test_duts["ixia"][0]["rest_port"]
    USERNAME = config.test_duts["ixia"][0]["username"]
    PASSWORD = config.test_duts["ixia"][0]["password"]

    # Connect to the IxNetwork API Server

    logging.info("Authenticating into Ixia API")

    api_server_ip = API_SERVER_IP

    test_platform = TestPlatform(api_server_ip, rest_port=REST_PORT)

    # Set the console output verbosity (none, info, request, request_response)

    test_platform.Trace = "info"

    # Authenticate with the Linux-based API server and start a new session

    # TODO: Handle passing in credentials to Ixia (Single user, multiple users)
    # Affects the handling of shared resources

    test_platform.Authenticate(USERNAME, PASSWORD)

    new_session = test_platform.Sessions.add()

    ixNetwork = new_session.Ixnetwork

    ixNetwork.NewConfig()

    # Specify the license server details

    ixNetwork.Globals.Licensing.LicensingServers = [LICENSING_SERVERS]

    # Specify the license mode (mixed, subscription, perpetual)

    ixNetwork.Globals.Licensing.Mode = LICENSING_MODE

    # Specify the license tier (tier1, tier2, tier3, tier3-10g, etc.)

    ixNetwork.Globals.Licensing.Tier = LICENSING_TIER

    return new_session, ixNetwork


"""
Module 2

Saves and loads .ixcnfg file into session which configures ports/protocols/traffic items.
Starts and verifies protocols
"""


def configure(ixNetwork, fileName):
    # Load the saved configuration :
    # Sets up the physical ports, the stacks to be tested,
    # and the traffic item details

    logging.info("Loading in test config")

    ixNetwork.LoadConfig(Files(fileName))

    # Connect to ports and error out if port is already occupied

    ports = ixNetwork.Vport.find()
    ports.ConnectPorts(False)

    # Start the protocols

    logging.info("Starting Protocols")

    ixNetwork.StartAllProtocols(Arg1="sync")

    # Verify generic protocol sessions

    protocols = StatViewAssistant(ixNetwork, "Protocols Summary")

    protocols.CheckCondition("Sessions Not Started", StatViewAssistant.EQUAL, 0)

    protocols.CheckCondition("Sessions Down", StatViewAssistant.EQUAL, 0)

    logging.info("Protocols Summary Statistics:\n%s" % protocols)

    return ixNetwork


"""
Module 3

Generates and starts traffic
"""


def generate_traffic(ixNetwork):
    # Generate, apply and start the traffic item

    logging.info("Starting Traffic generation")

    traffic_item = ixNetwork.Traffic.TrafficItem.find()

    traffic_item.Generate()

    ixNetwork.Traffic.Apply()

    time.sleep(5)

    ixNetwork.Traffic.Start()

    # TODO: Decide on how to handle continuous traffic if allowed

    # We can loop and check the state of the traffic item until the transmission stops

    while ixNetwork.Traffic.State in [
        "started",
        "startedWaitingForStats",
        "startedWaitingForStreams",
        "stoppedWaitingForStats",
        "txStopWatchExpected",
    ]:
        time.sleep(2)

    logging.info("Stopped Traffic Generation")

    return ixNetwork


"""
Module 4

Releases the ports and clears the session
"""


def clear_session(ixNetwork, session):
    logging.info("Clearing Session")

    if "ixNetwork" in locals():
        ixNetwork.Vport.find().ReleasePort()

    if "session" in locals():
        session.remove()

    logging.info("Session cleared successfully")
