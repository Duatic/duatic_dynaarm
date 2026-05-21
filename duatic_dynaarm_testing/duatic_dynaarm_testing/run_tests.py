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

"""Console entry point for the simplified Duatic DynaArm test CLI."""

import os
from datetime import datetime

import rclpy

from duatic_dynaarm_testing.models import Session
from duatic_dynaarm_testing.runner import run_suites
from duatic_dynaarm_testing.suites import ALL_SUITES

_ARM_VERSIONS = {"arowana4", "baracuda12", "corydoras12"}
_DEFAULT_ARM_VERSION = "corydoras12"
_DEFAULT_ETHERCAT_BUS = "enx70886b8ab832"


def _prompt_with_default(label: str, default: str) -> str:
    """Prompt for a value and fall back to the provided default."""

    value = input(f"  {label} [{default}]: ").strip()
    return value if value else default


def _prompt_arm_version() -> str:
    """Prompt for one of the supported arm hardware versions."""

    choices = ", ".join(sorted(_ARM_VERSIONS))
    while True:
        value = input(f"  Arm version [{_DEFAULT_ARM_VERSION}] ({choices}): ").strip()
        if not value:
            return _DEFAULT_ARM_VERSION
        if value in _ARM_VERSIONS:
            if value != "corydoras12":
                print(f"  Warning: this testing suite was written for {_DEFAULT_ARM_VERSION}.")
            return value
        print(f"  Invalid version. Choose one of: {choices}")


def _prompt_output_path() -> str:
    """Prompt for an existing directory where reports will be written."""

    default = os.getcwd()
    while True:
        raw = input(f"  Output directory [{default}]: ").strip()
        path = os.path.expanduser(raw) if raw else default
        if os.path.isdir(path):
            return path
        print(f"  Directory does not exist: {path}")


def main() -> None:
    """Run the interactive CLI entry point."""

    rclpy.init()
    try:
        print("\nSession Setup")
        session = Session(
            operator=_prompt_with_default("Operator name", ""),
            robot_id=_prompt_with_default("Robot / System ID: ", ""),
            arm_version=_prompt_arm_version(),
            ethercat_bus=_prompt_with_default("EtherCAT bus", _DEFAULT_ETHERCAT_BUS),
            output_path=_prompt_output_path(),
            start_time=datetime.now(),
        )

        passed = run_suites(ALL_SUITES, session)
        print(f"\n{'=' * 60}")
        if passed:
            print("[SYSTEM] Testing complete. Markdown report generated successfully.")
        else:
            print("[SYSTEM] Testing did not pass. Markdown report generated.")
    finally:
        rclpy.shutdown()


if __name__ == "__main__":
    main()
