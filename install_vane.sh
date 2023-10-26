#!/bin/bash

# Declare global variables

# Initialising variables for color formatting messages

default="\e[0m"
yellow="\e[33m"
green="\e[32m"
red="\e[31m"

# Check if destination folder has been passed as parameter
if [ ! $# -eq 0 ]; then
    DESTINATION_FOLDER=$1
    last_char="${DESTINATION_FOLDER: -1}"
    if [ ! "$last_char" = "/" ]; then
        DEFAULT="/"
    fi
fi
DEFAULT+="vane"
DESTINATION_FOLDER+=$DEFAULT

function remove_vane() {
    echo -e  "${yellow}Enter yes below to remove the cloned vane repo${default}"
    rm -r $DESTINATION_FOLDER
}

# (1) Check if Git is installed
if command -v git &>/dev/null; then
    echo -e  "${green}Git is installed.${default}"
else
    echo -e  "${red}Git is not installed. Install Git before running the script${default}"
    exit 1
fi

# (2) Download Vane repo into current directory
echo -e  "${yellow}Cloning Vane Repo${default}"
git clone https://github.com/aristanetworks/vane.git $DESTINATION_FOLDER

# Exit the script if cloning fails
if [ $? -eq 0 ]; then
    echo -e  "${green}Repository cloned successfully.${default}"
else
    echo -e  "${red}Failed to clone repository. Exiting script.${default}"
    exit 1  # Exit the script with a non-zero status
fi

# (3) Check if Python 3.9 version exists
if command -v python3.9 &>/dev/null; then
    echo -e  "${green}Python 3.9 is installed.${default}"
else
    echo -e  "${red}Python 3.9 is not installed. Install Python 3.9 before running the script${default}"
    remove_vane
    exit 1
fi

# (4) Check if Poetry is installed
if poetry --version &>/dev/null; then
    echo -e  "${green}Poetry is installed.${default}"
    poetry="poetry"
else
    echo -e  "${yellow}Checking for Poetry installation. Installing Poetry via curling of installation script if needed${default}"
    # Check if curl exists on the system
    echo -e  "${yellow}Checking for Curl on the system...${default}"
    if command -v curl &> /dev/null; then
        echo -e "${green}Curl is installed on your system.${default}"
    else
        echo -e  "${red}Curl is not installed. Install Curl before running the script in order to be able to install Poetry.${default}"
        remove_vane
        exit 1  # Exit the script with a non-zero status
        # fi
    fi
    # Install poetry
    curl -sSL https://install.python-poetry.org | python3.9 -
    # Check if installation of poetry was succesfull
    if [ $? -eq 0 ]; then
        echo -e  "${green}Poetry has been installed successfully by curling installation script.${default}"
    else
        echo -e  "${red}Failed to install Poetry. Exiting script.${default}"
        remove_vane
        exit 1  # Exit the script with a non-zero status
    fi
    current_user=$(whoami)
    # Initialise the path of poetry bin (where poetry got installed)
    # depending on the user
    if [ "$current_user" == "root" ]; then
        poetry="/root/.local/bin/poetry"
        echo -e  "${green}Invoking Poetry using ${poetry}.${default}"
    else
        poetry="/home/${current_user}/.local/bin/poetry"
        echo -e  "${green}Invoking Poetry using ${poetry}.${default}"
    fi
fi

# (5) Set up virtual environment in downloaded vane folder

cd $DESTINATION_FOLDER
echo -e  "${yellow}Entering $DESTINATION_FOLDER folder${default}"
path=$(pwd)
$poetry config virtualenvs.path "$path"
python=$(command -v python3.9)
$poetry env use "$python"
# Check if python virtual environment got created with correct version
if [ $? -eq 0 ]; then
        echo -e  "${green}Python version set correctly for vane's virtual environment.${default}"
    else
        echo -e  "${red}Failed to set Python version for virtual environment correctly. Exiting script${default}"
        remove_vane
        exit 1  # Exit the script with a non-zero status
fi
echo -e  "${green}Activating the poetry virtual environment${default}"
$poetry install 

# (6) Activate poetry environment within the root folder
echo -e  "${green}Entering the poetry virtual environment${default}"
$poetry shell