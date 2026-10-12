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
  if ! vcs --version &>/dev/null; then
    echo "Please install the newer vcstool version ('pipx install vcs2l'), not the older one ('pipx install vcstool')"
    echo "Skipping repository import"
  else
    vcs import --skip-existing "$(dirname "${repo_root}")" <"${repo_root}/repos.list"
  fi
else
  echo "vcs not found, skipping repository import (use 'pipx install vcs2l')..."
fi

# Setup pre-commit hooks for every repo
if command -v pre-commit >/dev/null 2>&1; then
  for dir in "${repo_root}"/*; do
    if [[ -d "${dir}/.git" && -f "${dir}/.pre-commit-config.yaml" ]]; then
      cd "${dir}"
      pre-commit install -c "${repo_root}/.pre-commit-config.yaml" --install-hooks
      cd -
    fi
  done
else
  echo "pre-commit not found, skipping pre-commit hook installation (sudo apt install pre-commit)"
fi

# X11 Forwarding
if command -v xhost >/dev/null 2>&1; then
  xhost +SI:localuser:"$(whoami)" >/dev/null 2>&1 || true
fi

# Create missing docker mounts
mkdir -p "${devcontainer_dir}"/mounts/{build,install,log,ccache}

# Generate a docker-compose-overlay.yml
"${devcontainer_dir}/scripts/generate_compose_overlay.bash"
