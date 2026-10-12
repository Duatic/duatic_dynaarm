#!/bin/bash

set -euo pipefail

# Build the custom devcontainer image
devcontainer_dir="$(realpath "$(dirname "$0")/..")"
docker buildx build \
  -t devcontainer:dynaarm \
  --build-arg BASE_IMAGE=docker.io/osrf/ros:jazzy-desktop-full \
  --build-arg USER="$(whoami)" \
  --pull \
  --load \
  "${devcontainer_dir}/docker"

# Clone the repositories of repos.list that are missing next to this repository
repo_root="$(dirname "${devcontainer_dir}")"
if command -v vcs &>/dev/null; then
  if ! vcs --version | grep -q "vcs 2"; then
    echo "Please install the newer vcstool version ('pipx install vcs2l'), not the older one ('pipx install vcstool')"
    echo "Skipping repository import"
  else
    vcs import --skip-existing "$(dirname "${repo_root}")" <"${repo_root}/repos.list"
  fi
else
  echo "vcs not found, skipping repository import (use 'pipx install vcs2l')..."
fi

# X11 Forwarding
if command -v xhost >/dev/null 2>&1; then
  xhost +SI:localuser:"$(whoami)" >/dev/null 2>&1 || true
fi

# Create missing docker mounts
mkdir -p "${devcontainer_dir}"/mounts/{build,install,log}

# Generate a docker-compose-overlay.yml
"${devcontainer_dir}/scripts/generate_compose_overlay.bash"
