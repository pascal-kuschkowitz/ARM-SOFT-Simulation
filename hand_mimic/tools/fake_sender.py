#!/usr/bin/env python3
"""Fake tracker: sends synthetic hand packets over UDP. --mode wave|fist|open|off|blink"""
import argparse
import json
import math
import socket
import time

ap = argparse.ArgumentParser()
ap.add_argument('--host', default='127.0.0.1')
ap.add_argument('--port', type=int, default=5005)
ap.add_argument('--mode', default='wave', choices=['wave', 'fist', 'open', 'off', 'blink'])
a = ap.parse_args()

FINGERS = ['index', 'middle', 'ring', 'little']
THUMB = ['joint_thumb_1_x', 'joint_thumb_1_y', 'joint_thumb_2', 'joint_thumb_3']
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
t0 = time.time()
seq = 0


def joints(mode, t):
    j = {}
    for k, f in enumerate(FINGERS):
        if mode == 'wave':
            c = 0.75 * (1 - math.cos(t * 2 + k * 0.6))
        else:
            c = 1.5 if mode == 'fist' else 0.0
        for i in (1, 2, 3):
            j[f'joint_{f}_{i}'] = c
    for n in THUMB:
        j[n] = 0.0 if mode != 'fist' else 0.8
    return j


try:
    while True:
        t = time.time() - t0
        hand = a.mode != 'off' and (a.mode != 'blink' or t % 7 < 4)
        mode = 'wave' if a.mode == 'blink' else a.mode
        pkt = {'v': 1, 'seq': seq, 't': time.time(), 'hand': hand, 'joints': joints(mode, t) if hand else {}}
        sock.sendto(json.dumps(pkt).encode(), (a.host, a.port))
        seq += 1
        time.sleep(1 / 30)
except KeyboardInterrupt:
    pass
