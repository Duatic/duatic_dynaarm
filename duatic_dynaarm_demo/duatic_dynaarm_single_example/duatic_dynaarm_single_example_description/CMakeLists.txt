cmake_minimum_required(VERSION 3.22)
project(duatic_dynaarm_single_example_description)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies
find_package(ament_cmake REQUIRED)
find_package(duatic_dynaarm_description REQUIRED)

install(DIRECTORY
  config launch srdf urdf worlds
  DESTINATION share/${PROJECT_NAME}/
)

if(BUILD_TESTING)
  find_package(duatic_helpers REQUIRED)

  duatic_add_urdf_tests(urdf/dynaarm_single_example.urdf.xacro)

  duatic_add_srdf_test(
    srdf/dynaarm_single_example.srdf.xacro
    urdf/dynaarm_single_example.urdf.xacro
  )
endif()

ament_package()
