#!/bin/bash

# NOTE: "-u" not used as the ROS source will trigger it
set -eo pipefail

# Build the workspace
cd /ros2_ws
source "/opt/ros/${ROS_DISTRO}/setup.bash"
colcon build

# Trigger a restart of clangd (via VSCode extension)
#   so it reads the new compile_commands.json
pkill clangd || true
