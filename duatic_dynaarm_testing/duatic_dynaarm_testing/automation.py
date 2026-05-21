# Copyright 2026 Duatic AG
#
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that
# the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions, and
#    the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions, and
#    the following disclaimer in the documentation and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or
#    promote products derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED
# WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
# PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED
# TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

"""Minimal ROS automation used by the operator-guided test CLI."""

import os
import signal
import subprocess
import time
from collections.abc import Callable

from duatic_dynaarm_testing.models import Session

BRINGUP_LOG_PATH = "/tmp/dynaarm_bringup.log"
GAMEPAD_LOG_PATH = "/tmp/dynaarm_gamepad_interface.log"
SERVICE_TIMEOUT_S = 5.0

_robot_process: subprocess.Popen | None = None
_gamepad_process: subprocess.Popen | None = None
_session: Session | None = None


def set_session(session: Session) -> None:
    """Store session metadata used by automation actions that launch ROS processes."""

    global _session
    _session = session


def _terminate(proc: subprocess.Popen | None) -> None:
    """Terminate a managed process group, escalating if it does not stop."""

    if proc is None or proc.poll() is not None:
        return
    try:
        os.killpg(proc.pid, signal.SIGTERM)
    except ProcessLookupError:
        proc.terminate()
    try:
        proc.wait(timeout=10)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(proc.pid, signal.SIGKILL)
        except ProcessLookupError:
            proc.kill()
        proc.wait(timeout=5)


def _start_process(command: list[str], log_path: str) -> subprocess.Popen:
    """Start a subprocess in its own session and redirect output to a log file."""

    log = open(log_path, "w", encoding="utf-8")
    try:
        proc = subprocess.Popen(command, stdout=log, stderr=log, start_new_session=True)
    finally:
        log.close()
    return proc


def start_robot() -> None:
    """Launch the Robot ROS bringup for the configured session."""

    # Dynaarm
    global _robot_process
    if _session is None:
        raise RuntimeError("set_session() must be called before start_robot()")
    command = [
        "ros2",
        "launch",
        "duatic_dynaarm_single_example",
        "real.launch.py",
        f"ethercat_bus:={_session.ethercat_bus}",
        f"version:={_session.arm_version}",
        "start_rviz:=true",
    ]
    _robot_process = _start_process(command, BRINGUP_LOG_PATH)

    # Gamepad interface
    global _gamepad_process
    if _gamepad_process is None or _gamepad_process.poll() is not None:
        _gamepad_process = _start_process(
            ["ros2", "run", "duatic_gamepad_interface", "gamepad_interface"],
            GAMEPAD_LOG_PATH,
        )


def stop_robot() -> None:
    """Stop the managed ROS bringup process if it is running."""

    # Dynaarm
    global _robot_process
    _terminate(_robot_process)
    _robot_process = None

    # Gamepad interface
    global _gamepad_process
    _terminate(_gamepad_process)
    _gamepad_process = None


def switch_controllers(
    *,
    activate: tuple[str, ...] | list[str] = (),
    deactivate: tuple[str, ...] | list[str] = (),
) -> None:
    """Switch controller-manager controllers using strict activation semantics."""

    import rclpy
    from controller_manager_msgs.srv import SwitchController

    activate = list(activate)
    deactivate = list(deactivate)
    node = rclpy.create_node("dynaarm_testing_switch_controller")
    try:
        client = node.create_client(SwitchController, "/controller_manager/switch_controller")
        if not client.wait_for_service(timeout_sec=SERVICE_TIMEOUT_S):
            raise RuntimeError("switch_controller service not available")

        request = SwitchController.Request()
        request.activate_controllers = activate
        request.deactivate_controllers = deactivate
        request.strictness = SwitchController.Request.STRICT
        future = client.call_async(request)
        rclpy.spin_until_future_complete(node, future, timeout_sec=SERVICE_TIMEOUT_S)
        response = future.result()
        if response is None or not response.ok:
            raise RuntimeError(
                f"switch_controller failed (activate={activate}, deactivate={deactivate})"
            )
    finally:
        node.destroy_node()


def release_brakes(hold_time: float = 1.0) -> None:
    """Briefly activate brake release, then return to freeze control."""

    switch_controllers(activate=["brake_release_controller"])
    time.sleep(hold_time)
    switch_controllers(activate=["freeze_controller"], deactivate=["brake_release_controller"])


ACTIONS: dict[str, Callable[..., None]] = {
    "start_robot": start_robot,
    "stop_robot": stop_robot,
    "release_brakes": release_brakes,
    "switch_controllers": switch_controllers,
}
