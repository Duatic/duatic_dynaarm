^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Changelog for package duatic_dynaarm_driver
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

2.0.0 (2026-11-07)
------------------
* feat!: remove the arowana4 version and its configuration (#22)
* feat(urdf)!: remove the option to enable or disable the covers (#16)
* feat(control): Read and apply joint limits from the URDF (#25)
* feat: record per arm version whether it has brakes, with freeze controller gains to match (#18)
* feat: support ROS 2 lyrical (#13)
* fix: remove obsolete dof parameter (#23)
* fix: pass the dof argument through to the hardware description
* fix: adapt the controller gains for corydoras12
* refactor: remove the remains of the migrated duatic_dynaarm_controllers package (#12)
* docs: date the changelog history the packages brought into this repository (#64)

1.0.0 (2026-05-08)
------------------
* First public release of the duatic_dynaarm_driver package
* Supports the *arowana4* and *baracuda12* model of the arm
