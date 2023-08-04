# Project: VANE

Network Certification Tool

![Coverage](./resources/coverage.svg)

## Description

Vane is an open source, network validation tool which runs tests against Arista networking 
devices, by connecting to devices on a given network, executing commands and performing 
tests against their output.  Vane eliminates repetitive testing tasks by automating network
validation which can take users months to complete.

## Installation

The Vane application is installed using the Python poetry packaging system. 

Install vane with the following command:
```
    vane # poetry install
```

This command always installs the package in a modifiable state, similar to the `pip install -e`
option. Any changes made to the Vane source will be reflected in the poetry
virtual environment.

The virtual environment is also not active when the application is first installed.

To start the poetry virtual environment, issue the following command:
```
    vane # poetry shell
    ...
    (vane-py3.9) vane #
```
An alias, `activate`, has also been created for the command `source $(poetry env info
--path)/bin/activate`, which is an equivalent command to the `poetry shell` command.
```
    vane # activate
    ...
    (vane-py3.9) vane #
```

In either case, the prompt will change to indicate the virtual environment is active by prefixing
the project name and python version, and Vane work can now be done in the environment.

Running the unit tests (validating Vane Framework):
```
    (vane-py3.9) vane # make unittest
```

The system tests require virtual or physical EOS switches to test on. For
testing the Vane package we typically use vEOS devices. The default Makefile
uses the Arista Cloud Test environment for testing.

Running the system tests:
```
    (vane-py3.9) vane # make sample_network_tests
```

Running the unit and system tests together.
```
    (vane-py3.9) vane # make tests
```

The coverage report is printed after running the unittest or systest. You can
run the coverage report at any time after running the tests.
```
    (vane-py3.9) vane # make coverage_report
```

For detailed information on the installation, please refer to [Getting Started with Vane docuement](docs/GettingStartedwithVane.pdf)

## Development

Contributed pull requests are gladly welcomed for this project.

### Vane Commands

1. Running help command.

```
    python3 vane.py --help
```

2. Running with custom definitions file.

```
    python3 vane.py --definitions_file definitions.yaml
```

3. Listing the available test markers.

    filesystem
    daemons
    extensions
    users
    tacacs
    aaa
    host
    base_feature
    platform_status
    authorization
    authentication
    accounting
    api
    dns
    logging
    ztp
    ntp
    nrfu
    pytest
    environment
    cpu
    memory
    interface
    interface_baseline_health
    l2_protocols
    lldp
    system
    demo
    physical
    virtual
    eos_424
	
```
    python3 vane.py --marker
```

4. Running specific markers (specific test suites)
	

    Change the 'mark' parameter value in definitions.yaml file to one of the above supported markers (for example, 'nrfu') and then run vane.py script

```
    python3 vane.py
```

## Contributing

Contributing pull requests are gladly welcomed for this repository.
Please note that all contributions that modify the library behavior
require corresponding test cases otherwise the pull request will be
rejected.

## License

Copyright (c) 2023, Arista Networks EOS+
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice, this
  list of conditions and the following disclaimer.
* Redistributions in binary form must reproduce the above copyright notice,
  this list of conditions and the following disclaimer in the documentation
  and/or other materials provided with the distribution.
* Neither the name of the Arista nor the names of its
  contributors may be used to endorse or promote products derived from
  this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
