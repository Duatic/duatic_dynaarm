cmake_minimum_required(VERSION 3.22)
project(duatic_dynaarm_description VERSION 1.0.0)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(ament_cmake REQUIRED)

install(DIRECTORY
  config launch meshes srdf urdf
  DESTINATION share/${PROJECT_NAME}/
)

if(BUILD_TESTING)
  find_package(launch_testing_ament_cmake REQUIRED)
  find_package(duatic_helpers REQUIRED)

  add_launch_test(
      test/test_launch_view.py
      TIMEOUT 60
  )

  duatic_add_urdf_tests(
    urdf/dynaarm_standalone.urdf.xacro
    urdf/dynaarm_standalone_dual.urdf.xacro
  )

  duatic_add_srdf_test(
    srdf/dynaarm_standalone.srdf.xacro
    urdf/dynaarm_standalone.urdf.xacro
  )
endif()

ament_package()
