#!/usr/bin/env python3
import time

import numpy as np
import rclpy
from rclpy.duration import Duration
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from rclpy.time import Time
from sensor_msgs.msg import JointState
from std_msgs.msg import Header
from tf2_ros import TransformException
from tf2_ros.buffer import Buffer
from tf2_ros.transform_listener import TransformListener
from visualization_msgs.msg import Marker


class RvizVisualizer(Node):
    def __init__(self):
        super().__init__('rviz_visualizer')

        self.publish_period_sec = 0.1
        self.publish_duration_sec = 100.0
        self.max_steps = int(self.publish_duration_sec / self.publish_period_sec)

        # define a publisher to publish JointState message
        self.joint_state_pub = self.create_publisher(
            JointState, '/visualize/robot_joint_states', 10
        )
        self.marker_pub = self.create_publisher(Marker, '/visualize/wrist_marker', 10)
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)
        self.base_frame = 'visualize/base_link'
        self.wrist_frame = 'visualize/wrist_3_link'
        self.marker_frame = 'visualize/base_link'
        self.logged_tf_warning = False
        self.tf_startup_grace_steps = 20
        self.joint_name = [
            'shoulder_pan_joint',
            'shoulder_lift_joint',
            'elbow_joint',
            'wrist_1_joint',
            'wrist_2_joint',
            'wrist_3_joint',
        ]

        self.timer = self.create_timer(self.publish_period_sec, self.on_timer)
        self.step = 0
        self.get_logger().info(
            'Publishing JointState on /visualize/robot_joint_states for 100 seconds.'
        )
        self.get_logger().info(
            'Publishing Marker on /visualize/wrist_marker using TF from '
            'visualize/base_link to visualize/wrist_3_link.'
        )

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
        try:
            wrist_transform = self.tf_buffer.lookup_transform(
                self.base_frame,
                self.wrist_frame,
                Time(),
                timeout=Duration(seconds=0.2),
            )
        except TransformException as ex:
            if not self.logged_tf_warning and self.step > self.tf_startup_grace_steps:
                self.get_logger().warn(
                    f'Cannot lookup transform {self.base_frame} <- {self.wrist_frame}: {ex}'
                )
                self.logged_tf_warning = True
            return

        self.logged_tf_warning = False
        marker_msg = Marker()
        marker_msg.header.frame_id = self.marker_frame
        marker_msg.header.stamp = self.get_clock().now().to_msg()
        marker_msg.ns = 'wrist_marker'
        marker_msg.id = 0
        marker_msg.type = Marker.CUBE
        marker_msg.action = Marker.ADD

        marker_msg.pose.position.x = wrist_transform.transform.translation.x
        marker_msg.pose.position.y = wrist_transform.transform.translation.y
        marker_msg.pose.position.z = wrist_transform.transform.translation.z
        marker_msg.pose.orientation = wrist_transform.transform.rotation

        marker_msg.scale.x = 0.18
        marker_msg.scale.y = 0.03
        marker_msg.scale.z = 0.03

        marker_msg.color.a = 1.0
        marker_msg.color.r = 1.0
        marker_msg.color.g = 0.3
        marker_msg.color.b = 0.1

        self.marker_pub.publish(marker_msg)

    def on_timer(self):
        if self.step < self.max_steps:
            t = self.step * self.publish_period_sec
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
        elif self.step == self.max_steps:
            self.get_logger().info('Finished JointState publishing after 100 seconds.')
        self.step += 1


if __name__ == "__main__":

    rclpy.init()
    node = RvizVisualizer()
    time.sleep(1)
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass

    if rclpy.ok():
        rclpy.shutdown()
