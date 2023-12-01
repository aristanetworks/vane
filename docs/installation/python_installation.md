Vane can be installed using **venv** which is a module in Python's standard library (as of Python 3.3) that provides support for creating lightweight, isolated Python environments.

The following steps should get you started:

### Clone the Vane Repository

```
git clone https://github.com/aristanetworks/vane.git
```

### Enter the Project Root Directory and Create a Virtual environment

```
cd vane
python3.9 -m venv venv
```

### Activate the Virtual Environment

```
source venv/bin/activate
```

### Install the requirements

```
pip install .
```
!!! warning "Warning"
    You might have to exit and enter the venv again for the installation changes to reflect. Additionally, for any source code change to reflect in the virtual environment, the above command needs to be issued everytime after the change.

Vane is now ready to be executed and the prompt will look as follows:

```
(venv) vane #

(venv) vane # vane --help

usage: vane [-h] [--definitions-file DEFINITIONS_FILE]
            [--duts-file DUTS_FILE] [--environment ENVIRONMENT]
            [--generate-duts-file topology_file inventory_file]
            [--generate-duts-from-topo topology_file]
            [--generate-test-steps test_dir] [--markers] [--nrfu]

Network Certification Tool

optional arguments:
  -h, --help            show this help message and exit

Main Command Options:
  --definitions-file DEFINITIONS_FILE
                        Specify the name of the definitions file
  --duts-file DUTS_FILE
                        Specify the name of the duts file
  --generate-duts-file topology_file inventory_file
                        Create a duts file from topology and inventory
                        file
  --generate-test-steps test_dir
                        Generate test steps for all the tests in the
                        test directory mentioned in the definitions
                        file
  --markers             List of supported technology tests. Equivalent
                        to pytest --markers

NRFU Command Options:
  --nrfu                Starts NRFU tests and will prompt users for
                        required input.
```

!!! success "Success"

    Now that you are all set up, navigate to the [Executing Vane](../executing_vane/executing_vane.md) Section to learn about how to use Vane and its different commands to execute test cases on your network.