^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Changelog for package duatic_dynaarm_single_example
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

2.0.0 (2026-11-07)
------------------
* chore!: remove the unused node move_to_predefined_position (#39)
* feat!: remove the arowana4 version from the launch choices (#22)
* feat(control): Read and apply joint limits from the URDF (#25)
* feat: forward headless to gazebo in sim launch (#41)
* feat(control): default configuration for the cartesian pose controller to control the flange (#35)
* feat: set controller_manager update frequency through controllers.yaml (#32)
* feat: a launch argument to select the arm version
* feat: support ROS 2 lyrical (#13)
* deprecate: sim doesn't need a separate controllers.yaml anymore (#31)
* fix: set version default to corydoras12 (#28)
* fix: disable the PID tuner controller, which was active by default (#17)
* fix: pass the Gazebo models path, so the collision meshes load (#5)
* fix: lower the brake release position kick in the demo configuration
* refactor(controllers): rename status broadcaster to duadrive_status_broadcaster (#27)
* refactor: use the controllers from duatic_controllers instead of duatic_dynaarm_controllers (#9)
* refactor: launch the e-stop from duatic_e_stop instead of duatic_dynaarm_extensions (#3)
