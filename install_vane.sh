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

PACKAGE_MANAGER=""
PYTHON_VERSION="3.9"
INSTALL_OPTION=""

# Function to install Homebrew (macOS) if not already installed
function install_homebrew() {
    echo -e  "${yellow}Installing Homebrew...${default}"
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
}

# Function to setup package manager to be used to install commands needed
function set_up_package_manager() {

    # Determine the package manager based on the system's OS and implement initial configuration

    # Debian based Linux distribution
    if command -v apt-get &>/dev/null; then
        echo -e  "${yellow}Using apt-get as found Linux Subsystem${default}"
        PACKAGE_MANAGER="apt-get"
        INSTALL_OPTION="-y"
        apt update
    # CentOS and older versions
    elif command -v yum &>/dev/null; then
        echo -e  "${yellow}Using yum as found CentOS${default}"
        PACKAGE_MANAGER="yum"
        INSTALL_OPTION="-y"
        path=$(pwd)
        cd /etc/yum.repos.d/
        sed -i 's/mirrorlist/#mirrorlist/g' /etc/yum.repos.d/CentOS-*
        sed -i 's|#baseurl=http://mirror.centos.org|baseurl=http://vault.centos.org|g' /etc/yum.repos.d/CentOS-*
        cd "$path"
        yum install -y glibc-langpack-en
    # For MacOs
    elif command -v brew &>/dev/null; then
        echo -e  "${yellow}Using brew as found MacOS${default}"
        PACKAGE_MANAGER="brew"
        INSTALL_OPTION="--force"
    else
	    # Install Homebrew on macOS
    	if [[ "$OSTYPE" =~ ^darwin ]]; then
            install_homebrew
	        PACKAGE_MANAGER="brew"
            INSTALL_OPTION="--force"
	    else
            # Add support for other package managers if needed, like chocolatey for Windows
            echo -e  "${red}Error: Package manager not found."
            exit 1
        fi
    fi
}

# (1) Set up package manager
set_up_package_manager

# (2) Check if Git is installed
if command -v git &>/dev/null; then
    echo -e  "${yellow}Git is installed.${default}"
else
    echo -e  "${yellow}Git is not installed. Installing Git${default}"
    $PACKAGE_MANAGER install $INSTALL_OPTION git
    if [ $? -eq 0 ]; then
        echo -e  "${green}Git installed successfully.${default}"
    else
        echo -e  "${red}Failed to install git. Exiting script.${default}"
        exit 1  # Exit the script with a non-zero status
    fi
fi

# (3) Download Vane repo into current directory
echo -e  "${yellow}Cloning Vane Repo${default}"
git clone https://github.com/aristanetworks/vane.git $DESTINATION_FOLDER

# Exit the script if cloning fails
if [ $? -eq 0 ]; then
    echo -e  "${green}Repository cloned successfully.${default}"
else
    echo -e  "${red}Failed to clone repository. Exiting script.${default}"
    exit 1  # Exit the script with a non-zero status
fi

# (4) Install Python 3.9 if version does not exist
if ! command -v python3.9 &>/dev/null; then
    echo -e  "${yellow}Python 3.9 not found. Installing Python 3.9${default}"
    if [ "$PACKAGE_MANAGER" = "brew" ]; then
        brew install $INSTALL_OPTION python@3.9
    elif [ "$PACKAGE_MANAGER" = "apt-get" ]; then
        apt install $INSTALL_OPTION software-properties-common
        add-apt-repository $INSTALL_OPTION ppa:deadsnakes/ppa
        apt install $INSTALL_OPTION python3.9
        apt-get install $INSTALL_OPTION python3-pip
    else
        $PACKAGE_MANAGER install $INSTALL_OPTION python3.9
    fi
    if [ $? -eq 0 ]; then
        echo -e  "${green}Python3.9 installed successfully.${default}"
    else
        echo -e  "${red}Failed to install Python3.9. Exiting script.${default}"
        exit 1  # Exit the script with a non-zero status
    fi
else
    echo -e  "${yellow}Python 3.9 is already installed.${default}"
fi

# (5) Check if Poetry is installed
if poetry --version &>/dev/null; then
    echo -e  "${yellow}Poetry is already installed.${default}"
    poetry="poetry"
else
    echo -e  "${yellow}Poetry is not installed. Installing Poetry via installation script${default}"
    # Check if curl exists on the system
    if command -v curl &> /dev/null; then
        echo -e "${green}Curl is already installed on your system.${default}"
    else
        echo -e "${yellow}Curl is not installed on your system. Installing curl.${default}"
        # Installing curl
        $PACKAGE_MANAGER install $INSTALL_OPTION curl
        # Check if curl installation was succesfull
        if [ $? -eq 0 ]; then
            echo -e "${green}Curl installation was successful.${default}"
        else
            echo -e  "${red}Failed to install Curl. Exiting script.${default}"
            exit 1  # Exit the script with a non-zero status
        fi
    fi
    # Install poetry
    curl -sSL https://install.python-poetry.org | python3.9 -
    # Check if installation of poetry was succesfull
    if [ $? -eq 0 ]; then
        echo -e  "${green}Poetry installed successfully by curling installation script.${default}"
    else
        echo -e  "${red}Failed to install Poetry. Exiting script.${default}"
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

# (6) Set up virtual environment in downloaded vane folder
cd $DESTINATION_FOLDER
echo -e  "${yellow}Entering $DESTINATION_FOLDER folder${default}"
path=$(pwd)
$poetry config virtualenvs.path "$path"
python=$(command -v python3.9)
$poetry env use "$python"
# Check if python virtual environment got created with correct version
if [ $? -eq 0 ]; then
        echo -e  "${green}Python version set correctly.${default}"
    else
        echo -e  "${red}Failed to set Python version for environment correctly. exiting script${default}"
        exit 1  # Exit the script with a non-zero status
fi
echo -e  "${green}Activating the poetry virtual environment${default}"
$poetry install 

# (7) Activate poetry environment within the root folder
echo -e  "${green}Entering the poetry virtual environment${default}"
$poetry shell