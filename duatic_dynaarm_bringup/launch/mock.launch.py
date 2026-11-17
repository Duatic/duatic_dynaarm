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

import xacro
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    OpaqueFunction,
    GroupAction,
)
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration

from launch_ros.actions import PushRosNamespace

from duatic_control.core import core_stage
from duatic_bringup_stages.stages import stage_arguments, staged
from duatic_helpers import ReplaceString


def launch_setup(context, *args, **kwargs):
    # Process URDF file
    doc = xacro.parse(open(LaunchConfiguration("urdf_file_path").perform(context)))
    tf_prefix = LaunchConfiguration("tf_prefix").perform(context)
    xacro.process_doc(
        doc,
        mappings={
            "namespace": LaunchConfiguration("namespace").perform(context),
            "mode": "mock",
            "version": LaunchConfiguration("version").perform(context),
            "tf_prefix": tf_prefix + "/" if tf_prefix else "",
            "joint_limits_yaml": LaunchConfiguration("joint_limits_yaml").perform(context),
            "calibration_yaml": LaunchConfiguration("calibration_yaml").perform(context),
        },
    )

    # Process SRDF file
    srdf_doc = xacro.parse(open(LaunchConfiguration("srdf_file").perform(context)))
    xacro.process_doc(
        srdf_doc,
        mappings={
            "version": LaunchConfiguration("version").perform(context),
            "mode": "mock",
        },
    )

    # Process controllers_config file
    srdf_str = srdf_doc.toxml().replace("\n", "\\n").replace('"', '\\"')
    controllers_params = ReplaceString(
        source_file=LaunchConfiguration("controllers_config"),
        replacements={
            "<srdf>": f'"{srdf_str}"',
        },
    )

    # A parent robot starts the core itself
    if IfCondition(LaunchConfiguration("start_as_subcomponent")).evaluate(context):
        return []

    core = core_stage(
        doc.toxml(),
        controllers_params.perform(context),
        namespace=LaunchConfiguration("namespace").perform(context),
    )
    return [GroupAction([PushRosNamespace(LaunchConfiguration("namespace")), staged([core])])]


def generate_launch_description():

    # Declare the launch arguments
    declared_arguments = [
        DeclareLaunchArgument(
            name="version",
            default_value="corydoras12",
            choices=["baracuda12", "corydoras12"],
            description="Select the desired version of robot ",
        ),
        DeclareLaunchArgument(
            name="urdf_file_path",
            description="Path to the robot URDF file",
        ),
        DeclareLaunchArgument(
            name="srdf_file",
            default_value=get_package_share_directory("duatic_dynaarm_description")
            + "/srdf/dynaarm_standalone.srdf.xacro",
            description="Path to the robot SRDF file",
        ),
        DeclareLaunchArgument(
            "start_as_subcomponent",
            default_value="false",
            description="Whether the dynaarm is started as a subcomponent",
        ),
        DeclareLaunchArgument(
            "controllers_config",
            default_value="",
            description="Path to the controllers config file",
        ),
        DeclareLaunchArgument(
            name="namespace",
            default_value="",
            description="Robot namespace",
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

    return LaunchDescription(
        declared_arguments + stage_arguments([]) + [OpaqueFunction(function=launch_setup)]
    )
