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

from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    IncludeLaunchDescription,
    OpaqueFunction,
    GroupAction,
)
from launch.conditions import UnlessCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution

from launch_ros.substitutions import FindPackageShare
from launch_ros.actions import Node, PushRosNamespace

from duatic_helpers import process_robot_description


def launch_setup(context, *args, **kwargs):
    # Package Directories
    pkg_duatic_control = FindPackageShare("duatic_control")

    # Process URDF file
    tf_prefix = LaunchConfiguration("tf_prefix").perform(context)
    robot_description = process_robot_description(
        urdf_file_path=LaunchConfiguration("urdf_file_path").perform(context),
        srdf_file_path=LaunchConfiguration("srdf_file_path").perform(context),
        mappings={
            "namespace": LaunchConfiguration("namespace").perform(context),
            "mode": "real",
            "version": LaunchConfiguration("version").perform(context),
            "ethercat_bus": LaunchConfiguration("ethercat_bus").perform(context),
            "tf_prefix": tf_prefix + "/" if tf_prefix else "",
            "joint_limits_yaml": LaunchConfiguration("joint_limits_yaml").perform(context),
            "calibration_yaml": LaunchConfiguration("calibration_yaml").perform(context),
        },
    )

    group_action = GroupAction(
        actions=[
            # Push Namespace, if the component is started as a standalone component
            PushRosNamespace(
                LaunchConfiguration("namespace"),
                condition=UnlessCondition(LaunchConfiguration("start_as_subcomponent")),
            ),
            # Robot State Publisher
            Node(
                package="robot_state_publisher",
                executable="robot_state_publisher",
                output="screen",
                parameters=[{"robot_description": robot_description}],
                remappings=[("/tf", "tf"), ("/tf_static", "tf_static")],
                condition=UnlessCondition(LaunchConfiguration("start_as_subcomponent")),
            ),
            # Controller Manager
            Node(
                package="controller_manager",
                executable="ros2_control_node",
                parameters=[LaunchConfiguration("controllers_config")],
                output={
                    "stdout": "screen",
                    "stderr": "screen",
                },
                condition=UnlessCondition(LaunchConfiguration("start_as_subcomponent")),
            ),
            # Start Controllers
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    PathJoinSubstitution([pkg_duatic_control, "launch", "control.launch.py"])
                ),
                launch_arguments={
                    "namespace": LaunchConfiguration("namespace"),
                    "config_path": LaunchConfiguration("controllers_config"),
                }.items(),
                condition=UnlessCondition(LaunchConfiguration("start_as_subcomponent")),
            ),
            # Brake Release
            Node(
                package="duatic_e_stop",
                executable="brake_release_node",
                name="brake_release_node",
                output="screen",
                condition=UnlessCondition(LaunchConfiguration("start_as_subcomponent")),
            ),
            # Emergency Stop
            Node(
                package="duatic_e_stop",
                executable="e_stop_node",
                name="e_stop_node",
                output="screen",
                parameters=[{"emergency_stop_button": 9}],  # Change button index here
                condition=UnlessCondition(LaunchConfiguration("start_as_subcomponent")),
            ),
        ]
    )

    return [group_action]


def generate_launch_description():

    declared_arguments = [
        DeclareLaunchArgument(
            name="ethercat_bus",
            description="The ethercat bus id or name.",
        ),
        DeclareLaunchArgument(
            name="version",
            default_value="corydoras12",
            choices=["baracuda12", "corydoras12"],
            description="Select the desired version of robot ",
        ),
        DeclareLaunchArgument(name="namespace", default_value="", description="Robot namespace"),
        DeclareLaunchArgument(
            name="urdf_file_path",
            description="Path to the robot URDF file",
        ),
        DeclareLaunchArgument(
            "srdf_file_path",
            default_value="",
            description="(Optional) Path to the robot SRDF file",
        ),
        DeclareLaunchArgument(
            "controllers_config",
            default_value="",
            description="Path to the controllers config file",
        ),
        DeclareLaunchArgument(
            "start_as_subcomponent",
            default_value="false",
            description="Whether the dynaarm is started as a subcomponent",
        ),
        DeclareLaunchArgument("tf_prefix", default_value="", description="Arm identifier"),
        DeclareLaunchArgument(
            "joint_limits_yaml",
            default_value="",
            description="Path to the joint limits file; empty for nominal limits",
        ),
        DeclareLaunchArgument(
            "calibration_yaml",
            default_value="",
            description="Path to the robot calibration file; empty for nominal structure",
        ),
    ]

    return LaunchDescription(declared_arguments + [OpaqueFunction(function=launch_setup)])
