#! /usr/bin/env bash

# Exit when any command fails
set -e

divider="\n--------------------------------------------------------------\n"

function exit_trap {
  # Check the failed command. If it was an exit command, we finished what we were doing.
  # Otherwise, log the command and the error code.
  if [ "$last_command" = "exit" ]; then
    echo -e "\n-- Vane CVP extension uninstalled --\n"
  else
    echo -e "\n\"${last_command}\" command failed with exit code $?.\n"
  fi
}

# Keep track of the last executed command
trap 'last_command=$current_command; current_command=$BASH_COMMAND' DEBUG
# Handle errors then exit
trap exit_trap EXIT

# Remove the container images first
#  - If the uninstallation fails for some reason, at least the containers are removed
#  - If the containers do not exist, the commands do not fail and the uninstallation will
#    still proceed afterwards
echo -e $divider
echo -e "Remove the container images\n"
img_id=`nerdctl images | grep vane-cvp | awk '{print $3}'`
nerdctl rmi -f vane-cvp
if [ ! -z ${img_id:+x} ]; then
  nerdctl rmi -f ${img_id}
fi

# Stop the extension
echo -e $divider
echo -e "Stop the extension\n"
cvpi stop -f vane-cvp

# Disable the extension
echo -e $divider
echo -e "Disable the extension\n"
cvpi disable -f vane-cvp

# Uninstall the extension
echo -e $divider
echo -e "Uninstall the extension\n"
cvpi uninstall -f vane-cvp

# Remove the cron job from the crontab
echo -e $divider
echo -e "Remove the cron job from the crontab\n"
croncmd=$(realpath $0)
( crontab -l | grep -v -F "$croncmd" ) | crontab -

# Print a final divider before finishing
echo -e $divider

# Exit the script
# (this triggers the exit_trap to give our final success/failure message)
exit
