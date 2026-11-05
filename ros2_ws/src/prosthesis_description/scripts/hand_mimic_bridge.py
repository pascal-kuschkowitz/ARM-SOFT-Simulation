#!/usr/bin/env python3
"""UDP -> ROS bridge for the hand-mimic demo. IDLE (idle pose) <-> MIMIC (smoothed finger angles from UDP JSON)."""
import json
import socket
import time

import rclpy
from rclpy.node import Node
from trajectory_msgs.msg import JointTrajectory

from demo_poses import IDLE_POSE, POSES, TOPIC, make_trajectory

HAND_JOINTS = [f'joint_{f}_{i}' for f in ('index', 'middle', 'ring', 'little') for i in (1, 2, 3)] + [
    'joint_thumb_1_x', 'joint_thumb_1_y', 'joint_thumb_2', 'joint_thumb_3']
WRIST_JOINTS = ['joint_wrist_x', 'joint_wrist_y']


class Bridge(Node):
    def __init__(self):
        super().__init__('hand_mimic_bridge')
        for k, v in dict(port=5005, alpha=0.4, rate_hz=20.0, hand_timeout_s=1.0, idle_resend_s=5.0,
                         idle_pose=IDLE_POSE, allow_wrist=False).items():
            self.declare_parameter(k, v)
        g = lambda k: self.get_parameter(k).value
        self.alpha, self.timeout, self.resend = g('alpha'), g('hand_timeout_s'), g('idle_resend_s')
        self.idle_pose = POSES[g('idle_pose')]
        self.allowed = HAND_JOINTS + (WRIST_JOINTS if g('allow_wrist') else [])
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('0.0.0.0', int(g('port'))))
        self.sock.setblocking(False)
        self.pub = self.create_publisher(JointTrajectory, TOPIC, 10)
        self.state, self.last_hand, self.last_idle_send = 'IDLE', 0.0, 0.0
        self.smoothed = {}
        self.latest = None
        self.create_timer(0.02, self.poll)               # 50 Hz drain
        self.create_timer(1.0 / g('rate_hz'), self.tick)  # 20 Hz publish
        self.get_logger().info(f'listening on UDP {g("port")}, state IDLE')

    def poll(self):
        while True:
            try:
                data, _ = self.sock.recvfrom(65535)
            except (BlockingIOError, InterruptedError):
                break
            except OSError:
                break
            try:
                pkt = json.loads(data.decode('utf-8'))
                if isinstance(pkt, dict):
                    self.latest = pkt
            except Exception:
                pass
        pkt, self.latest = self.latest, None
        if pkt is None:
            return
        try:
            if pkt.get('hand') is True and isinstance(pkt.get('joints'), dict):
                self.last_hand = time.monotonic()
                self.apply(pkt['joints'])
        except Exception:
            pass

    def apply(self, joints):
        for name, val in joints.items():
            if name not in self.allowed:
                continue
            try:
                v = float(val)
            except (TypeError, ValueError):
                continue
            lim = 1.57
            v = max(-lim if name in WRIST_JOINTS else 0.0, min(lim, v))
            prev = self.smoothed.get(name)
            self.smoothed[name] = v if prev is None else prev + self.alpha * (v - prev)
        if self.state == 'IDLE':
            self.state = 'MIMIC'
            self.get_logger().info('IDLE -> MIMIC')
            # start from the current idle values so fingers don't jump; wrist back to 0
            self.smoothed = {j: self.smoothed.get(j, 0.0) for j in self.allowed}

    def tick(self):
        now = time.monotonic()
        if self.state == 'MIMIC' and now - self.last_hand > self.timeout:
            self.state = 'IDLE'
            self.smoothed = {}
            self.last_idle_send = 0.0
            self.get_logger().info('MIMIC -> IDLE')
        if self.state == 'MIMIC':
            pose = dict(self.smoothed)
            if 'joint_wrist_x' not in pose:   # leave the idle wrist pose
                pose.update({w: 0.0 for w in WRIST_JOINTS})
            self.pub.publish(make_trajectory(pose, 0.1))
        elif now - self.last_idle_send >= self.resend:
            self.last_idle_send = now
            self.pub.publish(make_trajectory(self.idle_pose, 1.5))


def main():
    rclpy.init()
    node = Bridge()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.try_shutdown()


if __name__ == '__main__':
    main()
