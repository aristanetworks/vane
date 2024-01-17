#! /usr/bin/env bash

# Enables and starts the Vane CVP extension. After the extension is running, disables the
# extension so that when CVP is stopped and restarted, the extension is not loaded. This prevents
# any issues during CVP upgrades or other operations.
#
# Assumes that the Vane CVP extension has been installed using the associated vane-cvp-install.sh
# script.

# Exit when any command fails
set -e

divider="\n--------------------------------------------------------------\n"

function exit_trap {
  # Check the failed command. If it was an exit command, we finished what we were doing.
  # Otherwise, log the command and the error code.

  # Set the match string for when vane-cvp is not installed
  #   'Unknown' sometimes starts with capital, sometimes lowercase, so we just compare after the U
  not_installed='nknown component "vane-cvp"'

  # Check for conditions
  if [ "$last_command" = "exit" ]; then
    # If we reached the exit signal, notify the user that Vane CVP has been started
    echo -e "\n-- Vane CVP extension started --\n"

  elif [[ $result == *${not_installed}* ]]; then
    # If the result contains the not installed string, notify the user to install Vane CVP
    echo -e "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
    echo -e "  Vane CVP extension is not installed"
    echo -e "    Please run vane-cvp-install.sh"
    echo -e "    to install the extension"
    echo -e "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n"
    rm -f /home/cvp/vane-cvp*.rpm

  else
    # Some other error was received, post the command and the error code for information
    echo -e "\n\"${mycommand}\" command failed with exit code $?.\n"
    rm -f /home/cvp/vane-cvp*.rpm
  fi
}

# Keep track of the last executed command
trap 'last_command=$current_command; current_command=$BASH_COMMAND' DEBUG
# Handle errors then exit
trap exit_trap EXIT

# Enable the extension
echo -e $divider
echo -e "Enable the extension\n"
mycommand="cvpi enable -f vane-cvp"
result=$($mycommand 2>&1)

# Start the extension
echo -e $divider
echo -e "Start the extension\n"
mycommand="cvpi start -f vane-cvp"
result=$($mycommand 2>&1)

# Check the status of the extension
echo -e $divider
echo -e "Check the status of the extension\n"
mycommand="cvpi status -f vane-cvp"
result=$($mycommand 2>&1)

# Disable the extension so it will not start automatically on reboot
echo -e $divider
echo -e "Disable the extension\n"
mycommand="cvpi disable -f vane-cvp"
result=$($mycommand 2>&1)

# Print a final divider before finishing
echo -e $divider

# Exit the script
# (this triggers the exit_trap to give our final success/failure message)
exit
