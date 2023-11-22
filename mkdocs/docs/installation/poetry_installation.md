**Note:** If you do not want to follow the steps below we have an installation script which automates the manual installation procedure via poetry.
Follow the instructions in [Installation Script for Vane](../InstallationScriptforVane.pdf) to install Vane using the Installation script.

Vane can be installed using poetry which sets up a python virtual environment by following the steps below:

### Clone the Vane Repository

```
git clone https://github.com/aristanetworks/vane.git
```

### Install Poetry

Check if you already have poetry installed using the following command 

```
poetry --version
```

!!! failure "Error"

    If you get a command not found error, install poetry using the following command and ensure it has been installed correctly and its Path has been set correctly by trying the version command again.


    ```
    curl -sSL https://install.python-poetry.org | python3 -
    ```

#### Resources: 

- [Troubleshooting while installing poetry](https://stackoverflow.com/questions/70003829/poetry-installed-but-poetry-command-not-found)
- [Official documentation for installing](https://python-poetry.org/docs/#installing-with-the-official-installer)

### Configuring Poetry
We will now configure poetry to spin up the virtual environment in the project root directory instead of its default location

Check currently configured location by running the following command and checking the virtualenvs.path field 
```
poetry config --list
```

We need to change this default to reflect our project root directory, enter the following command to achieve that and replace [path_to_project_root_folder] with actual path to the project root directory

```
poetry config virtualenvs.path [path_to_project_root_folder]
```

Verify the change has taken place by viewing the config again

### Spinning Up the Virtual Environment

Now we need to spin up the virtual environment with all the dependencies mentioned in the pyproject.toml file, enter the following command for poetry to generate a poetry.lock file and create a virtual environment in the project root folder with the needed dependencies.

```
poetry install
```

To enter the virtual environment run the following command

```
poetry shell 
or
source path_to_virtual-environment/bin/activate
```

In either case, the prompt will change to indicate the virtual environment is active by prefixing
the project name and python version, and Vane can now be executed in the environment.

!!! info "Info"
    Vane is currently supported in python versions 3.9 and lower

Vane is now ready to be executed and the prompt will look as follows:
```
(vane-py3.9) vane #
```

```
(vane-py3.9) vane # vane --help

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
  --environment ENVIRONMENT
                        Specify the test execution environment
  --generate-duts-file topology_file inventory_file
                        Create a duts file from topology and inventory
                        file
  --generate-duts-from-topo topology_file
                        Generate a duts file from an ACT topology
                        file.
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