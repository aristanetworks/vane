#! /usr/bin/env bash

# Uninstalls the Vane CVP extension from CVP
#
# This script will remove any container images associated with the Vane CVP extension, then stop
# and disable the vane-cvp extension and uninstall the extension from CVP, which should remove
# the copied RPM package from the /data/apprpms directory.

# Exit when any command fails
set -e

divider="\n--------------------------------------------------------------\n"

function exit_trap {
  # Check the failed command. If it was an exit command, we finished what we were doing.
  # Otherwise, log the command and the error code.

  # Set the match string for when vane-cvp is not installed
  #   'Unknown' sometimes starts with capital, sometimes lowercase, so we just compare after the U
  not_installed='nknown component "vane-cvp"'

  if [ "$last_command" = "exit" ]; then
    # If we reached the exit signal, notify the user that Vane CVP has been started
    echo -e "\n-- Vane CVP extension uninstalled --\n"

  elif [[ $result == *${not_installed}* ]]; then
    # If the result contains the not installed string, notify the user that Vane CVP is
    # already uninstalled
    echo -e "Vane CVP extension is not installed, no further steps necessary"

  else
    echo -e "\n\"${mycommand}\" command failed with exit code $?.\n"
  fi
}

# Set the CONTAINER_CMD to either docker or nerdctl. Use docker if nerdctl is not available.
# Docker is used on older releases of CVP, nerdctl is used on newer releases.
CONTAINER_CMD=nerdctl
if ! command -v ${CONTAINER_CMD} &> /dev/null; then
  CONTAINER_CMD=docker
fi

# Keep track of the last executed command
trap 'last_command=$current_command; current_command=$BASH_COMMAND' DEBUG
# Handle errors then exit
trap exit_trap EXIT

# Stop the extension first
#  - Later iterations seem to require the extension to be stopped before the
#    containers can be removed (containers must not be in use)
echo -e $divider
echo -e "Stop the extension\n"
mycommand="cvpi stop -f vane-cvp"
result=$($mycommand 2>&1)

# Remove the container images
#  - If the uninstallation fails for some reason, at least the containers are removed
#  - If the containers do not exist, the commands do not fail and the uninstallation will
#    still proceed afterwards
echo -e $divider
echo -e "Remove the container images\n"
img_id=`${CONTAINER_CMD} images | grep vane-cvp | awk '{print $3}'`
${CONTAINER_CMD} rmi -f vane-cvp
if [ ! -z ${img_id:+x} ]; then
  ${CONTAINER_CMD} rmi -f ${img_id}
fi

# Disable the extension
echo -e $divider
echo -e "Disable the extension\n"
mycommand="cvpi disable -f vane-cvp"
result=$($mycommand 2>&1)

# Uninstall the extension
echo -e $divider
echo -e "Uninstall the extension\n"
mycommand="cvpi uninstall -f vane-cvp"
result=$($mycommand 2>&1)

# Print a final divider before finishing
echo -e $divider

# Exit the script
# (this triggers the exit_trap to give our final success/failure message)
exit
