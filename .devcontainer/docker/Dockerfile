# syntax=docker/dockerfile:1

ARG BASE_IMAGE=docker.io/osrf/ros:jazzy-desktop-full
FROM ${BASE_IMAGE}
USER root

# Rename user ubuntu to ${USER} and move home directory
ARG USER
RUN usermod -l ${USER} ubuntu && \
  usermod -d /home/${USER} -m ${USER} && \
  groupmod -n ${USER} ubuntu && \
  echo "${USER} ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/${USER}
USER ${USER}

# ccache
RUN sudo apt-get update && sudo apt-get upgrade -y && sudo apt-get install -y --no-install-recommends \
  ccache \
  && sudo /usr/sbin/update-ccache-symlinks \
  && sudo apt-get clean && sudo rm -rf /var/lib/apt/lists/*

# colcon mixins
ENV COLCON_HOME=/etc/colcon
RUN sudo mkdir -p ${COLCON_HOME}/mixin/default \
  && sudo git clone --depth 1 https://github.com/colcon/colcon-mixin-repository /tmp/colcon-mixin-repository \
  && sudo mv /tmp/colcon-mixin-repository/*.mixin ${COLCON_HOME}/mixin/default/ \
  && sudo rm -rf /tmp/colcon-mixin-repository

# install some tools
RUN sudo apt-get update && sudo apt-get upgrade -y && sudo apt-get install -y --no-install-recommends \
  black \
  clangd \
  gdb \
  git-lfs \
  htop \
  mesa-utils \
  nano \
  neovim \
  pre-commit && \
  sudo apt-get clean && sudo rm -rf /var/lib/apt/lists/*

# Source the bashrc overlay file in the bashrc
RUN echo "[ -f \${HOME}/.bashrc_overlay.bash ] && source \${HOME}/.bashrc_overlay.bash" >> /home/${USER}/.bashrc
