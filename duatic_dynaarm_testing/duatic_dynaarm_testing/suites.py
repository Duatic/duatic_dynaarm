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

"""Canonical Duatic DynaArm operator test suites."""

from duatic_dynaarm_testing.models import Step, Suite, Test


SUITE_1 = Suite(
    name="Initialization & Safety Hardware Tests",
    tests=[
        Test(
            name="Boot Up",
            steps=[
                Step.action("Ensure test area is clear."),
                Step.auto(
                    "start_robot",
                    "Start the robot.",
                    abort_on_fail=True,
                ),
                Step.action("Wait for the robot to finish booting."),
                Step.verify("Does the visualization in RVIZ match the physical robot orientation?"),
                Step.verify("Are the mechanical brakes currently engaged?"),
            ],
        ),
        Test(
            name="Brake Release",
            steps=[
                Step.auto(
                    "release_brakes",
                    "Release the brakes.",
                    abort_on_fail=True,
                ),
                Step.auto(
                    "switch_controllers",
                    "Switch to freedrive.",
                    abort_on_fail=True,
                    activate=["freedrive_controller"],
                    deactivate=["freeze_controller"],
                ),
                Step.verify("Move all joints by hand. Are the brakes released?"),
            ],
        ),
        Test(
            name="Encoder Validation",
            steps=[
                Step.verify(
                    "Move all joints by hand from stop to stop. Does the visualization in "
                    "RVIZ match the physical robot orientation?"
                ),
            ],
        ),
        Test(
            name="Gravity Compensation",
            steps=[
                Step.verify("Does the movement feel smooth and compliant?"),
                Step.verify("Does the robot remain stationary when you stop pushing?"),
            ],
        ),
        Test(
            name="Static E-Stop",
            steps=[
                Step.action("Press the hardware E-Stop button."),
                Step.verify("Did the power cut immediately?"),
                Step.verify("Did the brakes engage?"),
                Step.auto("stop_robot", "Stop the robot.", abort_on_fail=True),
                Step.action("Release the hardware E-Stop button. Wait for the drives to power on."),
            ],
        ),
    ],
)


SUITE_2 = Suite(
    name="Functional Control Tests",
    tests=[
        Test(
            name="Software E-Stop",
            steps=[
                Step.action("Ensure test area is clear."),
                Step.auto("start_robot", "Start the robot.", abort_on_fail=True),
                Step.action("Wait for the robot to finish booting."),
                Step.auto("release_brakes", "Release the brakes.", abort_on_fail=True),
                Step.action(
                    "Hold the Software E-Stop button for five seconds to release the "
                    "Software E-Stop."
                ),
                Step.verify(
                    "Try to move the robot arm by hand. Did the freeze controller deactivate?"
                ),
            ],
        ),
        Test(
            name="Deadman Switch",
            steps=[
                Step.auto(
                    "switch_controllers",
                    "Switch to joint trajectory controller.",
                    abort_on_fail=True,
                    activate=["joint_trajectory_controller"],
                ),
                Step.verify(
                    "Initiate a trajectory movement with the gamepad and release the dead-man button mid-motion. "
                    "Did the robot halt immediately?"
                ),
            ],
        ),
        Test(
            name="Position Limits",
            steps=[
                Step.verify(
                    "Move all joints from their Minimum to Maximum positions with the gamepad. "
                    "Do the software position limits stop you from moving before you hit any "
                    "mechanical hard stop?"
                ),
            ],
        ),
        Test(
            name="Dynamic E-Stop",
            steps=[
                Step.action(
                    "Initiate a slow trajectory movement with the gamepad and press the hardware E-Stop button."
                ),
                Step.verify("Did the power cut immediately?"),
                Step.verify("Did the brakes engage?"),
                Step.auto("stop_robot", "Stop the robot.", abort_on_fail=True),
            ],
        ),
    ],
)


ALL_SUITES = [SUITE_1, SUITE_2]
