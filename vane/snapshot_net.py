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

""" Utility script for taking a snapshot of the operational data within a network and converting
    it into Ansible-AVD structured data.  Ansible-AVD structured data is then written to 
    config.yml file for use with Vane test cases        
"""

import argparse
from vane import tests_tools
import vane.config

def parse_cli():
    """Parse cli options.

    Returns:
        args (obj): An object containing the CLI arguments.
    """
    parser = argparse.ArgumentParser(description="Utility snapshots network data for use with "
                                      "Vane test cases")

    parser.add_argument(
        "--definitions-file",
        default=vane.config.DEFINITIONS_FILE,
        help="Specify the name of the definitions file",
    )

    parser.add_argument(
        "--duts-file",
        default=vane.config.DUTS_FILE,
        help="Specify the name of the duts file",
    )

    return parser.parse_args()


def setup_snapshots():
    ...

def take_snapshots():
    ...

def process_snapshots():
    ...

def output_snapshots():
    ...

def main():
    """main function"""

    print("Starting Network Snapshot ... ")

    args = parse_cli()

    if args.definitions_file:
        vane.config.DEFINITIONS_FILE = args.definitions_file

    if args.duts_file:
        vane.config.DUTS_FILE = args.duts_file
    
    setup_snapshots()
    take_snapshots()
    process_snapshots()
    output_snapshots()

    print("Finished Network Snapshot! ")


if __name__ == "__main__":
    main()