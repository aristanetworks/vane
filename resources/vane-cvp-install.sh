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
cp /root/vane-cvp*.rpm /home/cvp/
cvpi install -f /home/cvp/vane-cvp*.rpm
rm -f /home/cvp/vane-cvp*.rpm

# # Enable the extension
# echo -e $divider
# echo -e "Enable the extension\n"
# cvpi enable -f vane-cvp

# Start the extension
echo -e $divider
echo -e "Start the extension\n"
cvpi start -f vane-cvp

# Check the status of the extension
echo -e $divider
echo -e "Check the status of the extension\n"
cvpi status -f vane-cvp

# # Disable the extension so it will not start automatically on reboot
# echo -e $divider
# echo -e "Disable the extension\n"
# cvpi disable -f vane-cvp

# # Add a cron job to uninstall the extension in 24 hours
# echo -e $divider
# echo -e "Create a cron job to uninstall the extension\n"
# #   Get the current Minute and Hour
# timestamp=$(date +"%M %H")
# #   Get the path to this file (should be /root)
# filepath=$(dirname $(realpath $0))
# #   Build the command for the cron job
# #     We need to set the BASH_ENV so the root environment is loaded properly when run
# croncmd="BASH_ENV=/root/.bash_profile $filepath/vane-cvp-uninstall.sh > $filepath/vane-cvp-uninstall.log 2>&1"
# #   Create the cronjob to run every day at this Minute and Hour
# #     It won't run now, because this minute's start point has already passed. The next instance is
# #     24 hours from now.
# cronjob="$timestamp * * * $croncmd"
# #   Add the cronjob to the crontab by echoing the crontab, removing any lines that reference the
# #   vane-cvp-uninstall.sh script, appending the new cronjob, and writing that back to the crontab.
# ( crontab -l | grep -v -F "vane-cvp-uninstall.sh" ; echo "$cronjob" ) | crontab -
# #   Print the cronjob as it appears in the crontab, for reference
# crontab -l | grep -F "vane-cvp-uninstall.sh"

# Print a final divider before finishing
echo -e $divider

# Exit the script
# (this triggers the exit_trap to give our final success/failure message)
exit
