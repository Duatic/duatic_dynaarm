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

"""Small data model for the Duatic DynaArm operator test CLI."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class StepType(str, Enum):
    """Kinds of steps the interactive runner can execute."""

    ACTION = "action"
    VERIFY = "verify"
    AUTO = "auto"


@dataclass(frozen=True)
class Step:
    """Single operator instruction, verification prompt, or automation action."""

    step_type: StepType
    text: str
    automation: str | None = None
    kwargs: dict[str, Any] = field(default_factory=dict)
    abort_on_fail: bool = False

    @classmethod
    def action(cls, text: str) -> "Step":
        """Create an operator action step completed with ENTER."""

        return cls(step_type=StepType.ACTION, text=text)

    @classmethod
    def verify(cls, text: str, *, abort_on_fail: bool = False) -> "Step":
        """Create a yes-or-no verification step."""

        return cls(step_type=StepType.VERIFY, text=text, abort_on_fail=abort_on_fail)

    @classmethod
    def auto(
        cls,
        automation: str,
        text: str,
        *,
        abort_on_fail: bool = False,
        **kwargs: Any,
    ) -> "Step":
        """Create an automation step resolved through the automation action registry."""

        return cls(
            step_type=StepType.AUTO,
            text=text,
            automation=automation,
            kwargs=kwargs,
            abort_on_fail=abort_on_fail,
        )


@dataclass(frozen=True)
class Test:
    """Named sequence of steps that produces one test result."""

    name: str
    steps: list[Step]


@dataclass(frozen=True)
class Suite:
    """Named collection of operator tests shown as one report section."""

    name: str
    tests: list[Test]


@dataclass
class StepResult:
    """Recorded outcome for a single executed step."""

    prompt: str
    step_type: StepType
    response: str
    timestamp: datetime = field(default_factory=datetime.now)
    details: dict[str, Any] = field(default_factory=dict)


@dataclass
class TestResult:
    """Recorded outcome for a completed or aborted test."""

    id: str
    name: str
    status: str
    timestamp: datetime
    steps: list[StepResult]
    abort_on_fail: bool = False


@dataclass
class Session:
    """Metadata and accumulated results for one CLI test run."""

    operator: str
    robot_id: str
    arm_version: str
    ethercat_bus: str
    output_path: str
    start_time: datetime
    results: list[TestResult] = field(default_factory=list)


# Keep pytest from treating model classes as test containers.
Test.__test__ = False
TestResult.__test__ = False
