_source_if_exists() {
  [ -f "$1" ] && source "$1"
}

# Source ROS
_source_if_exists "/opt/ros/${ROS_DISTRO}/setup.bash"
_source_if_exists "/ros2_ws/install/setup.bash"

# Edit PATH
# -- local binaries
export PATH=$PATH:$HOME/.local/bin
