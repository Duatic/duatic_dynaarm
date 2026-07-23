#!/usr/bin/env python3
import math
import rclpy
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from geometry_msgs.msg import TwistStamped
from sensor_msgs.msg import JointState
import threading
import time
from duatic_helpers.duatic_controller_helper import DuaticControllerHelper

# "Really slow" homing speed used for the initial move to the zero position.
SLOW_HOME_SPEED = 0.2  # rad/s
MIN_HOME_DURATION = 2.0  # seconds, floor so a near-zero start doesn't skip the slow move

class SingleArmMover:
    def __init__(self, node):
        self.node = node
        self.controller_helper = DuaticControllerHelper(self.node)

        # Publisher for the arm
        self.arm_pub = self.node.create_publisher(
            JointTrajectory, "joint_trajectory_controller/joint_trajectory", 10
        )

        # Joint names
        self.joint_names = [
            "shoulder_rotation",
            "shoulder_flexion",
            "elbow_flexion",
            "forearm_rotation",
            "wrist_flexion",
            "wrist_rotation",
        ]

        # Joint positions (radians)
        self.positions = [
            [0.5, 0.0, 0.0, 0.0, 0.0, 0.0],  # Home Position
            [1.2, 0.6, 1.2, 0.5, -0.8, 0.0],  # Position 1
            [0.9, 0.1, 0.1, 0.3, -0.5, 0.2],  # Position 2
            [2.0, 0.8, 0.8, 0.0, -1.0, -0.3],  # Position 3
            [0.5, 0.0, 0.0, 0.0, 0.0, 0.0],  # Home Position
            [1.2, 0.6, 1.2, 0.5, -0.8, 0.0],  # Position 1
            [0.9, 0.1, 0.1, 0.3, -0.5, 0.2],  # Position 2
            [2.0, 0.8, 0.8, 0.0, -1.0, -0.3],  # Position 3
            [0.5, 0.0, 0.0, 0.0, 0.0, 0.0],  # Home Position
        ]

        # Time (seconds) to reach each position
        self.times_from_start = [1.5, 1.5, 1.5, 1.5, 0.8, 0.8, 0.8, 0.8, 1.0]

        self.move_arm()

    def get_current_positions(self, timeout=5.0):
        """Reads the current position of each joint from joint_states, in self.joint_names order."""
        joint_positions = {}

        def cb(msg):
            for name, pos in zip(msg.name, msg.position):
                joint_positions[name] = pos

        sub = self.node.create_subscription(JointState, "joint_states", cb, 10)

        start_time = time.time()
        while (
            rclpy.ok()
            and not all(name in joint_positions for name in self.joint_names)
            and (time.time() - start_time) < timeout
        ):
            rclpy.spin_once(self.node, timeout_sec=0.1)

        self.node.destroy_subscription(sub)
        return [joint_positions.get(name, 0.0) for name in self.joint_names]

    def move_to_home_slowly(self):
        """Moves every joint to zero, at a pace set by whichever joint has the farthest to go."""
        current_positions = self.get_current_positions()
        max_distance = max(abs(p) for p in current_positions)
        duration = max(max_distance / SLOW_HOME_SPEED, MIN_HOME_DURATION)

        self.node.get_logger().info(
            f"Moving slowly to home (zero) position: farthest joint is {max_distance:.3f} rad away, "
            f"duration={duration:.1f}s"
        )

        traj_msg = JointTrajectory()
        traj_msg.joint_names = self.joint_names

        point = JointTrajectoryPoint()
        point.positions = [0.0] * len(self.joint_names)
        point.velocities = [0.0] * len(self.joint_names)
        point.accelerations = [0.0] * len(self.joint_names)
        point.time_from_start.sec = int(duration)
        point.time_from_start.nanosec = int((duration % 1) * 1e9)
        traj_msg.points.append(point)

        self.arm_pub.publish(traj_msg)
        time.sleep(duration + 0.5)

    def move_arm(self):
        self.controller_helper.switch_controller(
            ["joint_trajectory_controller"],
            ["freeze_controller"],
        )
        time.sleep(1)

        self.move_to_home_slowly()

        for idx in range(len(self.positions)):
            self.node.get_logger().info(f"Moving to position {idx + 1}")

            traj_msg = JointTrajectory()
            traj_msg.joint_names = self.joint_names

            point = JointTrajectoryPoint()
            point.positions = self.positions[idx]
            point.velocities = [0.0] * len(self.joint_names)
            point.accelerations = [0.0] * len(self.joint_names)
            duration = self.times_from_start[idx]
            point.time_from_start.sec = int(duration)
            point.time_from_start.nanosec = int((duration % 1) * 1e9)

            traj_msg.points.append(point)

            self.arm_pub.publish(traj_msg)

            # Wait before sending the next command
            time.sleep(self.times_from_start[idx] + 0.5)

        self.node.get_logger().info("All positions executed.")


def main(args=None):
    rclpy.init(args=args)
    node = rclpy.create_node("single_arm_mover")

    try:
        SingleArmMover(node)
    except KeyboardInterrupt:
        node.get_logger().info("KeyboardInterrupt received, shutting down.")
    finally:
        node.destroy_node()

    rclpy.shutdown()


if __name__ == "__main__":
    main()