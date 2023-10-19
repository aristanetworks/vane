#! /usr/bin/env bash

# Installs and starts the Vane CVP extension.
#
# Expects the extension RPM package and this script to be located in the /root directory of the
# CVP host, and this script should be run as the root user.
#
# The script will cop the RPM package to the /home/cvp directory (required by cvpi installation) and
# install the RPM, enable the extension, start the extension, and display the status of the running
# extension. After the extension is running, it disables the extension so that when CVP is stopped
# and restarted, the extension is not loaded. This prevents any issues during CVP upgrades or other
# operations.
#
# If the extension needs to be restarted after a stop and restart of CVP, use the associated
# vane-cvp-start.sh script.

# Exit when any command fails
set -e

divider="\n--------------------------------------------------------------\n"

# Get the path to where the script is located
script_path=$(dirname "$0")

function exit_trap {
  # Check the failed command. If it was an exit command, we finished what we were doing.
  # Otherwise, log the command and the error code.
  if [ "$last_command" = "exit" ]; then
    echo -e "\n-- Vane CVP extension installed --\n"
  else
    echo -e "\n\"${last_command}\" command failed with exit code $?.\n"
    rm -f /home/cvp/vane-cvp*.rpm
  fi
}

# Keep track of the last executed command
trap 'last_command=$current_command; current_command=$BASH_COMMAND' DEBUG
# Handle errors then exit
trap exit_trap EXIT

# Install the RPM
echo -e $divider
echo -e "Install the rpm\n"
rm -f /home/cvp/vane-cvp*.rpm
cp ${script_path}/vane-cvp*.rpm /home/cvp/
cvpi install -f /home/cvp/vane-cvp*.rpm
rm -f /home/cvp/vane-cvp*.rpm

# Enable the extension
#   Needs to be enabled to start the extension
echo -e $divider
echo -e "Enable the extension\n"
cvpi enable -f vane-cvp

# Start the extension
echo -e $divider
echo -e "Start the extension\n"
cvpi start -f vane-cvp

# Check the status of the extension
echo -e $divider
echo -e "Check the status of the extension\n"
cvpi status -f vane-cvp

# Disable the extension so it will not start automatically on reboot
#   Once started, the extension can be disabled
echo -e $divider
echo -e "Disable the extension\n"
cvpi disable -f vane-cvp

# Print a final divider before finishing
echo -e $divider

# Exit the script
# (this triggers the exit_trap to give our final success/failure message)
exit
