^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Changelog for package duatic_dynaarm_description
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

2.0.0 (2026-11-07)
------------------
* fix(urdf)!: Fix mesh offsets (#56)
* feat(urdf)!: remove the option to enable or disable the covers (#16)
* feat(urdf): Split base frames (#62)
* feat(control): Read and apply joint limits from the URDF (#25)
* feat(urdf): new meshes, with corrected wrist2 and shoulder origins (#33)
* feat(urdf): adapt limits for new wrist rotation cover (#10)
* deprecate: the arowana4 version (#22)
* fix: set version default to corydoras12 (#28)
* fix: remove obsolete dof parameter (#23)
* fix(urdf): remove the cables from the mesh, and correct its color (#34)
* fix(urdf): reference meshes with package:// instead of file://, for current ROS 2 and remote
  streaming (#1)
* fix: typo in README.md (#29)
* refactor(description): drop unused elements from the DynaArm model (#50)
* refactor(description): declutter the DynaArm URDF (#48)
* docs: date the changelog history the packages brought into this repository (#64)

1.1.0 (2026-05-08)
------------------
The releases before the package moved into this repository, 0.0.1 to 1.1.0, folded into one entry.

* 1.1.0: add the DynaArm version 'corydoras12', the same as 'baracuda12' with brake support, so it
  can carry different default configurations
* 1.1.0: rework the URDF to integrate better into other Duatic systems, and fix the CI integration
* 1.0.0: first public release of the DynaArm description, with minor fixes
* 1.0.0: allow overrides for the drive configuration files
* 1.0.0: lower case names for links and joints
* 1.0.0: define the final names of the arm
* 0.0.1: pre-release for testing workflows; tested with DynaArm v1 and v2, with license and
  documentation
