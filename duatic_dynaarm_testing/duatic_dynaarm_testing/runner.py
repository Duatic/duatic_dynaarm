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

"""Interactive runner for the simplified DynaArm operator test CLI."""

from collections.abc import Callable
from datetime import datetime

from duatic_dynaarm_testing import automation
from duatic_dynaarm_testing.models import (
    Session,
    Step,
    StepResult,
    StepType,
    Suite,
    Test,
    TestResult,
)
from duatic_dynaarm_testing.report import write_report

InputFn = Callable[[str], str]
PrintFn = Callable[..., None]


def _ask_yes_no(prompt: str, input_fn: InputFn, print_fn: PrintFn) -> str:
    """Prompt until the operator answers yes or no."""

    print_fn(f"\n[VERIFY] {prompt}")
    while True:
        raw = input_fn("         [Y/n]: ").strip().lower()
        if raw in ("", "y"):
            return "Yes"
        if raw == "n":
            return "No"
        print_fn("         Please enter Y or N.")


def _run_step(
    step: Step,
    session: Session,
    input_fn: InputFn = input,
    print_fn: PrintFn = print,
) -> StepResult:
    """Execute one step and return its normalized report response."""

    if step.step_type == StepType.ACTION:
        print_fn(f"\n[ACTION] {step.text}")
        input_fn("         Press ENTER when done...")
        return StepResult(prompt=step.text, step_type=step.step_type, response="Done")

    if step.step_type == StepType.VERIFY:
        response = _ask_yes_no(step.text, input_fn, print_fn)
        return StepResult(prompt=step.text, step_type=step.step_type, response=response)

    if step.step_type != StepType.AUTO:
        raise AssertionError(f"Unhandled step type: {step.step_type}")

    print_fn(f"\n[AUTO] {step.text}")
    if step.automation is None:
        print_fn("         [FAIL] Automated step is missing a function name.")
        return StepResult(prompt=step.text, step_type=step.step_type, response="No")

    action = automation.ACTIONS.get(step.automation)
    if action is None:
        print_fn(f"         [FAIL] Unknown automation: {step.automation}")
        return StepResult(prompt=step.text, step_type=step.step_type, response="No")

    try:
        action(**step.kwargs)
    except Exception as exc:
        print_fn(f"         [FAIL] {exc}")
        return StepResult(
            prompt=step.text,
            step_type=step.step_type,
            response="No",
            details={"error": str(exc)},
        )

    return StepResult(prompt=step.text, step_type=step.step_type, response="Done")


def _stop_robot_after_failure(print_fn: PrintFn) -> None:
    """Best-effort cleanup of system software after a failed test."""

    print_fn("\n[AUTO] Stopping system software after failure.")
    try:
        automation.stop_robot()
    except Exception as exc:
        print_fn(f"         [FAIL] stop_robot cleanup failed: {exc}")


def _run_test(
    test: Test,
    test_id: str,
    session: Session,
    input_fn: InputFn = input,
    print_fn: PrintFn = print,
) -> TestResult:
    """Run one test case and collect its step results."""

    print_fn(f"\n{'-' * 60}")
    print_fn(f"Test {test_id}: {test.name}")
    print_fn(f"{'-' * 60}")

    start = datetime.now()
    step_results: list[StepResult] = []
    failed_step: str | None = None
    abort_on_fail = False

    for step in test.steps:
        result = _run_step(step, session, input_fn=input_fn, print_fn=print_fn)
        step_results.append(result)
        if result.response == "No":
            failed_step = result.prompt
            abort_on_fail = step.abort_on_fail
            break

    status = "FAIL" if failed_step else "PASS"
    print_fn(f"\n  Result: {status}", end="")
    if failed_step:
        print_fn(f'  - failed on: "{failed_step}"')
    else:
        print_fn()

    return TestResult(
        id=test_id,
        name=test.name,
        status=status,
        timestamp=start,
        steps=step_results,
        abort_on_fail=abort_on_fail,
    )


def run_suites(
    suites: list[Suite],
    session: Session,
    input_fn: InputFn = input,
    print_fn: PrintFn = print,
) -> bool:
    """Run all suites, write a final or partial report, and return pass status."""

    automation.set_session(session)
    passed = True
    for suite_index, suite in enumerate(suites, start=1):
        suite_id = str(suite_index)
        print_fn(f"\n{'=' * 60}")
        print_fn(f"Suite {suite_id}: {suite.name}")
        print_fn(f"{'=' * 60}")

        for test_index, test in enumerate(suite.tests, start=1):
            test_id = f"{suite_id}.{test_index}"
            result = _run_test(test, test_id, session, input_fn=input_fn, print_fn=print_fn)
            session.results.append(result)
            if result.status == "FAIL":
                passed = False
                if result.abort_on_fail:
                    print_fn(
                        f"\n[ABORT] Test {result.id} failed. "
                        "Writing partial report and stopping."
                    )
                    _stop_robot_after_failure(print_fn)
                    write_report(session, overall="FAIL")
                    return False

    write_report(session, overall="PASS" if passed else "FAIL")
    return passed
