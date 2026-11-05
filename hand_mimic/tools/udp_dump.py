#!/usr/bin/env python3
"""Listen for hand-mimic UDP packets and pretty-print them (max 2x/s)."""
import argparse, json, socket, time

ap = argparse.ArgumentParser()
ap.add_argument("--port", type=int, default=5005)
args = ap.parse_args()

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("0.0.0.0", args.port))
print(f"listening on UDP :{args.port}")
count, t0, last_print = 0, time.time(), 0.0
while True:
    data, addr = sock.recvfrom(65535)
    count += 1
    now = time.time()
    if now - last_print < 0.5:
        continue
    rate = count / (now - t0)
    count, t0, last_print = 0, now, now
    try:
        msg = json.loads(data.decode())
        j = " ".join(f"{k.replace('joint_', '')}={v:.2f}" for k, v in msg.get("joints", {}).items())
        print(f"[{rate:5.1f} pkt/s from {addr[0]}] seq={msg.get('seq')} hand={msg.get('hand')} {j}")
    except Exception as e:
        print(f"[{rate:5.1f} pkt/s] bad packet ({e}): {data[:80]!r}")
