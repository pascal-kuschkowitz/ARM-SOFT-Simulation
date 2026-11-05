#!/usr/bin/env python3
"""Hand-mimic demo poses. Import POSES / IDLE_POSE / make_trajectory, or use the CLI:

  ros2 run prosthesis_description demo_poses.py thumbs_up|peace|open|fist|cycle|sweep <joint>

Values verified on VM via tf (thumbs_up: wrist_x=1.5 rolls thumb to the top).
"""
import sys
import time

import rclpy
from builtin_interfaces.msg import Duration
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint

TOPIC = '/joint_trajectory_controller/joint_trajectory'

FINGERS = ['index', 'middle', 'ring', 'little']
THUMB = ['joint_thumb_1_x', 'joint_thumb_1_y', 'joint_thumb_2', 'joint_thumb_3']
WRIST = ['joint_wrist_x', 'joint_wrist_y']

# Wrist values that make the thumb point "up" in the default camera view. TUNE ON VM.
THUMBS_UP_WRIST_X = -1.5  # roll forearm: palm faces sideways, thumb side up
THUMBS_UP_WRIST_Y = 0.0


def _pose(curl=(0, 0, 0, 0), thumb=(0, 0, 0, 0), wrist=(0.0, 0.0)):
    """curl: per-finger curl (index, middle, ring, little), applied to all 3 joints."""
    p = {}
    for name, c in zip(FINGERS, curl):
        for i in (1, 2, 3):
            p[f'joint_{name}_{i}'] = float(c)
    p.update(zip(THUMB, map(float, thumb)))
    p.update(zip(WRIST, map(float, wrist)))
    return p


POSES = {
    'open': _pose(),
    'fist': _pose(curl=(1.5,) * 4, thumb=(0.8, 0.5, 0.8, 0.8)),
    # four fingers curled, thumb straight out
    'thumbs_up': _pose(curl=(1.45,) * 4, thumb=(1.5, 0.0, 0.2, 0.2),
                       wrist=(THUMBS_UP_WRIST_X, THUMBS_UP_WRIST_Y)),
    # index+middle straight, ring+little curled, thumb tucked across them
    'peace': _pose(curl=(0.0, 0.0, 1.5, 1.5), thumb=(1.0, 0.3, 0.8, 0.8)),
}

IDLE_POSE = 'peace'  # thumbs_up is geometrically awkward on this model (thumb hangs down from palm); see NOTES.md


def make_trajectory(pose, seconds):
    msg = JointTrajectory()
    msg.joint_names = list(pose.keys())
    pt = JointTrajectoryPoint()
    pt.positions = [float(v) for v in pose.values()]
    pt.time_from_start = Duration(sec=int(seconds), nanosec=int((seconds % 1) * 1e9))
    msg.points = [pt]
    return msg


def _wait_for_subscriber(node, pub, timeout=2.0):
    end = time.time() + timeout
    while pub.get_subscription_count() == 0 and time.time() < end:
        rclpy.spin_once(node, timeout_sec=0.1)
    return pub.get_subscription_count() > 0


def main():
    args = sys.argv[1:]
    if not args or (args[0] not in POSES and args[0] not in ('cycle', 'sweep')):
        print(__doc__)
        print('poses:', ', '.join(POSES))
        sys.exit(1)
    rclpy.init()
    node = rclpy.create_node('demo_poses')
    pub = node.create_publisher(JointTrajectory, TOPIC, 10)
    if not _wait_for_subscriber(node, pub):
        node.get_logger().warn('no subscriber on controller topic after 2 s; publishing anyway')

    def send(pose, secs=1.5):
        pub.publish(make_trajectory(pose, secs))

    cmd = args[0]
    if cmd == 'cycle':
        try:
            while True:
                for name in ('open', 'fist', 'thumbs_up', 'peace'):
                    node.get_logger().info(name)
                    send(POSES[name])
                    time.sleep(2.0)
        except KeyboardInterrupt:
            pass
    elif cmd == 'sweep':
        # sweep one joint alone: 0 -> 0.8 -> 1.57 -> 0, 2 s each (others at 0)
        joint = args[1]
        for v in (0.0, 0.8, 1.57, 0.0):
            node.get_logger().info(f'{joint} = {v}')
            send({joint: v})
            time.sleep(2.0)
    else:
        send(POSES[cmd])
        time.sleep(0.3)  # let the message flush
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
