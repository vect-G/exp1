#!/usr/bin/env python3
import sys
import time

import numpy as np
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from std_msgs.msg import Header
from tf2_ros.buffer import Buffer
from tf2_ros.transform_listener import TransformListener

from visualization_msgs.msg import Marker, MarkerArray


class RvizVisualizer(Node):
    def __init__(self):
        super().__init__('rviz_visualizer')

        # define a publisher to publish JointState message
        self.joint_state_pub = self.create_publisher(
            JointState, '/visualize/robot_joint_states', 10
        )
        self.joint_name = [
            'shoulder_pan_joint',
            'shoulder_lift_joint',
            'elbow_joint',
            'wrist_1_joint',
            'wrist_2_joint',
            'wrist_3_joint',
        ]

        self.timer = self.create_timer(0.1, self.on_timer)
        self.step = 0

    def publish_robot_joint_states(self, joints_pos, joints_name):
        # publish a JointState type message
        joint_state_msg = JointState()
        joint_state_msg.header = Header()
        joint_state_msg.header.stamp = self.get_clock().now().to_msg()
        joint_state_msg.name = list(joints_name)
        joint_state_msg.position = list(joints_pos)

        self.joint_state_pub.publish(joint_state_msg)

    def publish_marker(self):
        # use lookup_transform to get transform from visualize/wrist_3_link to visualize/base_link
        # publish a Marker type message

        pass

    def on_timer(self):
        if self.step < 100:
            t = self.step * 0.1
            joint_pos = np.array(
                [
                    0.6 * np.sin(t),
                    -0.8 + 0.4 * np.sin(t),
                    0.8 * np.sin(t * 0.8),
                    0.6 * np.sin(t * 1.2),
                    0.5 * np.sin(t * 0.6),
                    0.7 * np.sin(t),
                ]
            )

            self.publish_robot_joint_states(joint_pos, self.joint_name)
            self.publish_marker()
        self.step += 1


if __name__ == "__main__":

    rclpy.init()
    node = RvizVisualizer()
    time.sleep(1)
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass

    rclpy.shutdown()
