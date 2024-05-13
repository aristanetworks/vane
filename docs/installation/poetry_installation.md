# Via Poetry

!!! eos-config "Note"

    If you do not want to follow the steps below we have an installation
    script which automates the manual installation procedure via poetry. Follow the
    instructions in [Installation Script for Vane](../InstallationScriptforVane.pdf)
    to install Vane using the Installation script.

Vane can be installed using poetry which sets up a python virtual
environment by following the steps below:

## Clone the Vane Repository

``` text
git clone https://github.com/aristanetworks/vane.git
```

## Install Poetry

Check if you already have poetry installed using the following command

``` text
poetry --version
```

!!! failure "Error"
    If you get a command not found error, install poetry using the
    following command and ensure it has been installed correctly and
    its path has been set correctly by trying the version command again.

    ``` text
    curl -sSL https://install.python-poetry.org | python3 -
    ```

### Resources

- [Troubleshooting while installing poetry](https://stackoverflow.com/questions/70003829/poetry-installed-but-poetry-command-not-found)
- [Official documentation for installing](https://python-poetry.org/docs/#installing-with-the-official-installer)

## Configuring Poetry

We will now configure poetry to spin up the virtual environment
in the project root directory instead of its default location

Check currently configured location by running the following
command and checking the *virtualenvs.path* field

``` text
poetry config --list
```

We need to change this default to reflect our project root directory,
enter the following command to achieve that and replace [path_to_project_root_folder]
with actual path to the project root directory

``` text
poetry config virtualenvs.path [path_to_project_root_folder]
```

Verify the change has taken place by viewing the config again

## Spinning Up the Virtual Environment

Now we need to spin up the virtual environment with all the dependencies
mentioned in the pyproject.toml file, enter the following command for poetry
to generate a poetry.lock file and create a virtual environment in the project
root folder with the needed dependencies.

``` text
poetry install
```

To enter the virtual environment run the following command

``` text
poetry shell 
or
source path_to_virtual-environment/bin/activate
```

In either case, the prompt will change to indicate the virtual
environment is active by prefixing the project name and python version,
and Vane can now be executed in the environment.

Vane is now ready to be executed and the prompt will look as follows:

``` text
(vane-py3.9) vane #
```

```text
(vane-py3.9) vane # vane --help
```

![Screenshot](../images/vane_cli.png)

To exit out of the virtual environment execute the following command:

``` text
deactivate
```

!!! success "Success"
    Now that you are all set up, navigate to the
    [Executing Vane](../executing_vane/executing_vane.md) Section
    to learn about how to use Vane and its different commands to
    execute test cases on your network.
