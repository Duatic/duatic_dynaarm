# duatic_dynaarm_testing

Operator-guided ROS 2 CLI for running Duatic DynaArm functional safety checks and writing a Markdown report.

The package intentionally keeps physical motion and safety observations in the operator's hands. It automates only repeatable ROS actions such as bringup, controller switching, brake release, shutdown, and report generation.

## Dependencies

This package is an `ament_python` package. Runtime dependencies are declared in `package.xml`:

- `rclpy`
- `controller_manager_msgs`
- `duatic_dynaarm_single_example`
- `duatic_gamepad_interface`

The active ROS environment must also provide the controllers referenced by the test plan, including `freeze_controller`, `brake_release_controller`, `freedrive_controller`, and `joint_trajectory_controller`.

## Build

```bash
colcon build --packages-select duatic_dynaarm_testing
source install/setup.bash
```

## Run

```bash
ros2 run duatic_dynaarm_testing run_tests
```

The CLI prompts for:

- Operator name
- Robot / system ID
- Arm version: `arowana4`, `baracuda12`, or `corydoras12`
- EtherCAT bus
- Existing output directory for the Markdown report

Defaults are provided for `corydoras12`, the EtherCAT bus, and the current output directory. Non-`corydoras12` arm versions are accepted, but the CLI prints a warning because the suite was written for `corydoras12`.

After setup, follow each prompt:

- `[ACTION]`: perform the physical action, then press ENTER.
- `[VERIFY]`: answer `Y` or `n`; ENTER defaults to `Y`.
- `[AUTO]`: wait while the CLI performs a ROS action.

## Automation

The CLI manages these ROS actions:

- System bringup:
  `ros2 launch duatic_dynaarm_single_example real.launch.py ethercat_bus:=<bus> version:=<version> start_rviz:=true`
- Gamepad interface bringup:
  `ros2 run duatic_gamepad_interface gamepad_interface`
- Brake release by briefly activating `brake_release_controller`, then returning to `freeze_controller`.
- Controller switching through `/controller_manager/switch_controller` with strict activation semantics.
- Best-effort cleanup of managed ROS processes after aborts and shutdown steps.

Bringup logs are written to `/tmp/dynaarm_bringup.log`. Gamepad interface logs are written to `/tmp/dynaarm_gamepad_interface.log`.

## Suites

### Suite 1: Initialization & Safety Hardware Tests

1. Boot Up
2. Brake Release
3. Encoder Validation
4. Gravity Compensation
5. Static E-Stop

### Suite 2: Functional Control Tests

1. Software E-Stop
2. Deadman Switch
3. Position Limits
4. Dynamic E-Stop

## Failure Behavior

Answering `n` to a `[VERIFY]` step marks that test as failed. Failed steps that are marked `abort_on_fail`, including critical automated bringup, brake release, controller switching, and shutdown steps, stop the run immediately.

When the run aborts, the CLI attempts to stop managed ROS processes, writes a partial Markdown report, and returns a failed result from the runner.

## Report

Reports are written to the selected output directory as:

```text
dynaarm_test_report_YYYYMMDD_HHMMSS.md
```

Each report includes session metadata, the overall result, and one table per executed test with the step prompt, step type, and operator or automation response.
