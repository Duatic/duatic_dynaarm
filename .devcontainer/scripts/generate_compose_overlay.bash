#!/bin/bash
# Generate a docker-compose-overlay.yml with the mounts of this repository and every repository of repos.list that is present next to it, plus GPU devices if available.

# Sources: this repository plus every repository of repos.list that is present next to it
repo_root="$(realpath "$(dirname "$0")/../..")"
repos_dir="$(dirname "${repo_root}")"
sources=("${repo_root}")
for name in $(sed -n 's/^  \([^ :]*\):$/\1/p' "${repo_root}/repos.list"); do
    [[ -d "${repos_dir}/${name}" ]] && sources+=("${repos_dir}/${name}")
done

# Mounts: every source directory mounted into the container at /ros2_ws/src/<name>
mounts=()
for dir in "${sources[@]}"; do
    mounts+=("      - ${dir}:/ros2_ws/src/$(basename "${dir}")")
done

# GPU: NVIDIA runtime if usable, else AMD (ROCm), else plain DRI devices
gpu=()
gpu_env=()
if command -v nvidia-smi >/dev/null 2>&1 && nvidia-smi -L >/dev/null 2>&1 &&
    docker info --format '{{json .Runtimes}}' 2>/dev/null | grep -q '"nvidia"'; then
    gpu=(
        "    runtime: nvidia"
        "    gpus: all"
    )
    gpu_env=(
        "      NVIDIA_VISIBLE_DEVICES: all"
        "      NVIDIA_DRIVER_CAPABILITIES: all"
    )
elif [[ -e /dev/kfd && -e /dev/dri ]]; then
    gpu=(
        "    devices:"
        "      - /dev/kfd:/dev/kfd"
        "      - /dev/dri:/dev/dri"
        "    group_add:"
        "      - video"
    )
elif [[ -e /dev/dri ]]; then
    gpu=(
        "    devices:"
        "      - /dev/dri:/dev/dri"
        "    group_add:"
        "      - video"
    )
fi

# Export docker-compose-overlay.yml
host_ip="$(hostname -I | awk '{print $1}')"
{
    echo "services:"
    echo "  dynaarm:"
    echo "    volumes:"
    for line in "${mounts[@]}" "${gpu[@]}"; do
        echo "${line}"
    done
    echo "    environment:"
    for line in "${gpu_env[@]}"; do
        echo "${line}"
    done
    echo "      HOST_IP: \"${host_ip}\""
} >"$(realpath "$(dirname "$0")/../docker/docker-compose-overlay.yml")"
