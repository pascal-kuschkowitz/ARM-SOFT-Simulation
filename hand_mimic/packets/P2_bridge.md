# P2 — UDP → ROS bridge node + fake sender

**Where:** VM. **Depends on:** P1 (`demo_poses.py`). **Read:** 00_MASTER.md (Interface contract + Bridge behaviour), NOTES.md.

## Tasks
1. **`ros2_ws/src/prosthesis_description/scripts/hand_mimic_bridge.py`** (new, executable, add to CMakeLists):
   - rclpy node `hand_mimic_bridge`. Non-blocking UDP socket on `0.0.0.0:<port>`; drain all pending datagrams in a
     50 Hz timer, keep only the newest valid one. Bad JSON / unknown keys → ignore silently.
   - Implement the IDLE/MIMIC state machine exactly as in the master "Bridge behaviour" section.
   - Uses `POSES`, `IDLE_POSE`, `make_trajectory` from `demo_poses`.
   - Only forward joints from the master joint list (+ wrist joints only if param `allow_wrist` is true; default false,
     for P6). Clamp to [0, 1.57] (wrist: ±1.57) as a safety net.
   - ROS params with defaults: `port=5005`, `alpha=0.4`, `rate_hz=20.0`, `hand_timeout_s=1.0`, `idle_resend_s=5.0`,
     `idle_pose=IDLE_POSE`, `allow_wrist=false`.
   - Log: startup (port), and each transition `IDLE -> MIMIC` / `MIMIC -> IDLE`. Nothing per packet.
   - Leave the trajectory header stamp at zero (= "start now").
2. **`hand_mimic/tools/fake_sender.py`** (plain Python, stdlib only, runs on VM or Mac):
   - `--host` (default 127.0.0.1), `--port` 5005, `--mode wave|fist|open|off|blink`.
   - `wave`: all finger joints follow `0.75*(1-cos(t))` with a small phase shift per finger, `hand: true`, 30 Hz.
   - `off`: sends `hand: false` heartbeats. `blink`: 4 s hand / 3 s no hand, repeating (tests the state machine).
   - Packet format exactly as in the master contract (incl. `v`, `seq`, `t`).

## Done when
With the sim + bridge running: `fake_sender.py --mode wave` → fingers wave; Ctrl-C the sender → thumbs up within ~1 s;
`--mode blink` alternates cleanly; the bridge survives garbage (`echo junk | nc -u -w1 127.0.0.1 5005`).
Verify headlessly via `/joint_states`. Commit `hand-mimic(P2): udp bridge + fake sender`.

## Manual test (for the user)
T1: `ros2 launch prosthesis_description gazebo.launch.py` · T2: `ros2 run prosthesis_description hand_mimic_bridge.py` ·
T3: `python3 hand_mimic/tools/fake_sender.py --mode blink`. Also run the sender **from the Mac** with `--host <VM_IP>`.
