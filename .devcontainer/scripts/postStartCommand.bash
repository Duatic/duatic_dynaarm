#!/bin/bash

set -euo pipefail

# Allow gdb to attach to non-child processes
echo 0 | sudo tee /proc/sys/kernel/yama/ptrace_scope

# Coredumps
# NOTE: These are potentially gigantic, so not mounted on purpose
mkdir -p /ros2_ws/.coredump
echo "/ros2_ws/.coredump/core.%e.%p.%h.%t" | sudo tee /proc/sys/kernel/core_pattern
