# Project: VANE

Network Certification Tool

![Coverage](./resources/coverage.svg)

## Description

A weather vane is an instrument used for showing the direction of the wind.
Just like a weather vane, Vane is a network certification tool that shows a
network's readiness for production based on validation tests.

## Installation

Let user know how to install

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

3. Listing the inputs from excel_definitions file.

```
    python3 vane.py --input
```

4. Listing the available test markers.

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

5. Running specific markers (specific test suites)
	

    Change the 'mark' parameter value in definitions.yaml file to one of the above supported markers (for example, 'nrfu') and then run vane.py script

```
    python3 vane.py
```

### Testing Vane Package using Docker development container

Build and run the docker development container using:
```
    make dev
    ...
    🐳 c39d4cd0a377 project # 
```

The prompt indicates we are in a container (the Docker whale) and a container ID, as well as the
current path. The container is run with the local development environment shared as a mount point.
Working done in the local development environment will be reflected in the container environment.

The container is also built using the Python poetry packaging system. When the container is first
started, the Vane dependencies are installed in the container in a virtual environment, but the Vane
package itself is not installed. The virtual environment is also not active when the container is
first started up.

To start the poetry virtual environment, while in the `project` directory issue the following command:
```
    🐳 c39d4cd0a377 project # poetry shell
    ...
    (vane-py3.9) 🐳 c39d4cd0a377 project #
```
An alias, `activate`, has also been created for the command `source $(poetry env info
--path)/bin/activate`, which is an equivalent command to the `poetry shell` command.
```
    🐳 c39d4cd0a377 project # activate
    ...
    (vane-py3.9) 🐳 c39d4cd0a377 project #
```

In either case, the prompt will change to indicate the virtual environment is active by prefixing
the project name and python version, and Vane work can now be done in the environment.

If you will be running Vane, install vane with the following command (make sure the prompt indicates
the virtual environment is active):
```
    (vane-py3.9) 🐳 c39d4cd0a377 project # poetry install
```
This command always installs the package in a modifiable state, similar to the `pip install -e`
option. Any changes made to the Vane source (outside the container) will be reflected in the poetry
virtual environment (inside the container).

Running the unit tests:
```
    (vane-py3.9) 🐳 c39d4cd0a377 project # make unittest
```

The system tests require virtual or physical EOS switches to test on. For
testing the Vane package we typically use vEOS devices. The default Makefile
uses the Arista Cloud Test environment for testing.

Running the system tests:
```
    (vane-py3.9) 🐳 c39d4cd0a377 project # make systest
```

Running the unit and system tests together.
```
    (vane-py3.9) 🐳 c39d4cd0a377 project # make tests
```

The coverage report is printed after running the unittest or systest. You can
run the coverage report at any time after running the tests.
```
    (vane-py3.9) 🐳 c39d4cd0a377 project # make coverage_report
```

### Testing Vane Package using python virtual env

Build and run the docker development container using:
```
    python3.9 -m venv venv
    source venv/bin/activate
    ...
    (venv) $ 
```

First step is to install Vane. If you are just running tests and will not be
modifying the source, running in a pipeline, then use the following command:
```
    (venv) $ pip3.9 install -r requirements.txt
    (venv) $ make install
```
Running the unit tests:
```
    (venv) $ pytest --cov-report term-missing --cov=vane tests/unittests
```

Running the system tests:
```
    (venv) $ vane --definitions_file tests/systests/fixtures/definitions.yaml --duts_file tests/fixtures/duts.yaml
```

The coverage report is printed after running the unittest or systest. You can
run the coverage report at any time after running the tests.
```
   (venv) $ make coverage_report
```

### Test Directory Hierarchy

```
tests
├── fixtures
│   ├── spreadsheets
│   └── templates
├── systests
│   ├── aaa
│   ├── api
│   ├── cpu
│   ├── daemon
│   ├── dns
│   ├── environment
│   ├── extension
│   ├── filesystem
│   ├── fixtures
│   │   └── reports
│   │       ├── assets
│   │       └── results
│   ├── host
│   ├── interface
│   ├── lldp
│   ├── log
│   ├── memory
│   ├── ntp
│   ├── system
│   ├── tacacs
│   ├── users
│   └── ztp
└── unittests
    └── fixtures
        ├── reports
        │   └── results
        └── spreadsheets
```

The tests/fixtures file contains fixtures that are used by both the unittest
and the systest.

### Build Docker Container

The docker container approach for development can be used to ensure that
everybody is using the same development environment while still being flexible
enough to use the repo you are making changes in. You can inspect the
Dockerfile to see what packages have been installed. Note that specifying the
build arguments allows you to run the container as your user-id and not as the
default user docker.

```
    $ docker build -t repo-name . --build-arg UID=$(id -u) --build-arg GID=$(id -g) --build-arg UNAME=$(id -un)
```

### Run the Docker Container

Start up the docker container from the root of the repo directory with the
following command.

```
    $ docker run -it --volume "$(pwd):/repo-name" repo-name
```

## Contributing

Contributing pull requests are gladly welcomed for this repository.
Please note that all contributions that modify the library behavior
require corresponding test cases otherwise the pull request will be
rejected.

## License

Copyright (c) 2020, Arista Networks EOS+
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
