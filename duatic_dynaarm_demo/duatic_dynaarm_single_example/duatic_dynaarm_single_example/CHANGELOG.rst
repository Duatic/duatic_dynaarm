2.0.0 (2026-11-07)
------------------
* chore!: removed unused node move_to_predefined_position (#39)
* feat(control): Read and apply joint limits from the URDF (#25)
* feat: forward headless to gazebo in sim launch (#41)
* feat(control): default configuration for the cartesian pose controller to control the flange (#35)
* feat: set controller_manager update frequency through controllers.yaml (#32)
* feat: deprecate arowana4 (#22)
* deprecate: sim doesn't need a seperate controllers.yaml anymore (#31)
* fix: set version default to corydoras12 (#28)
* refactor(controllers): rename status broadcaster to duadrive_status_broadcaster (#27)
* Disable the pid tuner controller which is active by default. (#17)
* revert parts of the previous patch - did not want to commit 500Hz update rate
* Added launch argument for version selection
* bump cmake minimum version for all packages to 3.22
* added support for lyrical (#13)
* fix controllers dependency (#9)
* Fix/gazebo collision meshes (#5)
* removed dynaarm_controllers (but left empty package for future use) as they are migrated to
  duatic_Ros2control
* moved dynaarm extensions (#3)
* fix demo deps
* fix brake release controller config in demo
* added migrate controller branch
