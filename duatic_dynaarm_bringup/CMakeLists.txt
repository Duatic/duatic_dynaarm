cmake_minimum_required(VERSION 3.22)
project(duatic_dynaarm_bringup)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies
find_package(ament_cmake REQUIRED)
find_package(ament_cmake_python REQUIRED)

install(DIRECTORY
  launch
  DESTINATION share/${PROJECT_NAME}/
)

ament_python_install_package(${PROJECT_NAME})

if(BUILD_TESTING)
endif()

ament_package()
