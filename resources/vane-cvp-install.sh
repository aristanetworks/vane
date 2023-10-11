#! /usr/bin/env bash

# Exit when any command fails
set -e

divider="\n--------------------------------------------------------------\n"

function exit_trap {
  # Check the failed command. If it was an exit command, we finished what we were doing.
  # Otherwise, log the command and the error code.
  if [ "$last_command" = "exit" ]; then
    echo -e "\n-- Vane CVP extension installed --\n"
  else
    echo -e "\n\"${last_command}\" command failed with exit code $?.\n"
  fi
}

# Keep track of the last executed command
trap 'last_command=$current_command; current_command=$BASH_COMMAND' DEBUG
# Handle errors then exit
trap exit_trap EXIT

echo -e $divider
echo -e "Install the rpm\n"
cvpi install -f /home/cvp/vane*.rpm

echo -e $divider
echo -e "Enable the extension\n"
cvpi enable -f vane-cvp

echo -e $divider
echo -e "Start the extension\n"
cvpi start -f vane-cvp

echo -e $divider
echo -e "Check the status of the extension\n"
cvpi status -f vane-cvp

# Add a cron job to uninstall the extension in 24 hours
echo -e $divider
echo -e "Create a cron job to uninstall the extension\n"
timestamp=$(date +"%M %H")
filepath=$(dirname $(realpath $0))
croncmd="BASH_ENV=/root/.bash_profile $filepath/vane-cvp-uninstall.sh > $filepath/vane-cvp-uninstall.log 2>&1"
cronjob="$timestamp * * * $croncmd"
# The below command first deletes any existing vane-cvp-uninstall commands from the crontab, then
# adds the cronjob to the crontab and writes it back
( crontab -l | grep -v -F "vane-cvp-uninstall.sh" ; echo "$cronjob" ) | crontab -

echo -e $divider

# Exit the script
# (this triggers the exit_trap to give our final success/failure message)
exit
