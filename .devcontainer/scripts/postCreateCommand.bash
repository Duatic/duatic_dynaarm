#!/bin/bash

set -euo pipefail

# Docker creates the mount parents as root - make them user-owned
sudo chown "$(id -u):$(id -g)" /ros2_ws /ros2_ws/src /ros2_ws/.cache

# Install missing dependencies of the workspace packages
sudo apt-get update && rosdep update
rosdep install --from-paths /ros2_ws/src --ignore-src -y --rosdistro "${ROS_DISTRO}"
