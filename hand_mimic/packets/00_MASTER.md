# 00 — MASTER PACKET: Hand-Mimic Demo (read this first, every agent)

You are one of several Claude Code agents building a **one-day, quick-and-dirty demo** on branch
`add/visualization-for-scientastic` of `ARM-SOFT-Simulation`. Read this file fully, then your own packet
(`P<n>_*.md`). Do only your packet. This file is the shared contract — do not change it unless your packet says so.

## Goal
Laptop webcam watches for a hand. While a hand is visible, the simulated prosthesis (Gazebo, ROS 2 Jazzy, Linux VM)
mirrors the **finger** movements in real time. When the hand leaves, the prosthesis shows **thumbs up** (fallback:
**peace**) until the next hand appears. It runs **unattended for hours**; each visitor interacts a few minutes.
Gazebo goes on an external monitor; the camera preview stays on the laptop screen.

## Hard constraints
- **Quick & dirty wins.** One day total. No new ROS packages, no custom msg types, no test frameworks, no refactors
  of existing code. Hardcode constants at the top of files. Single-file scripts where possible.
- **Arm base never moves** (`joint_base_*`). Phase 1 = fingers only. Wrist joints only used by idle poses (P1)
  and optional P6.
- Don't modify existing files except where a packet explicitly says so (CMakeLists `install(PROGRAMS ...)`, new launch file).
- `.gitignore` ignores `*.sh` → use `.py`, `.command`, or a launch file for run scripts (or `git add -f`).
- **Commit after your packet** (one or a few commits), prefix `hand-mimic(P<n>): ...`. **Never push** unless the user says so.
- End your work with a **"Manual test"** section in your final message: exact commands for the user, what they should see.
- Append anything other agents need (joint semantics, measured ranges, IPs, gotchas) to `hand_mimic/NOTES.md`
  (create if missing; dated bullet, packet id). Read NOTES.md before starting.

## Machines
| Machine | What runs there | Agent |
|---|---|---|
| **VM**: UTM, Ubuntu 24.04, ARM64 (Apple Silicon host), ROS 2 Jazzy + Gazebo Harmonic | Gazebo sim, `hand_mimic_bridge.py` | VM agent (P1, P2, P5-VM) |
| **Mac**: macOS, Apple Silicon, has webcam | `tracker.py` (OpenCV + MediaPipe) | Mac agent (P3, P4, P5-Mac) |

Code sync between Mac and VM: via git on this branch (or a UTM shared directory) — decided in P0, recorded in NOTES.md.
The camera is **never** passed into the VM. Only small UDP packets cross.

## Architecture
```
[Mac] webcam → tracker.py (MediaPipe HandLandmarker → joint angles, preview window)
          │  UDP JSON, ~30 Hz, port 5005
          ▼
[VM]  hand_mimic_bridge.py (ROS 2 node) ──► /joint_trajectory_controller/joint_trajectory ──► Gazebo
          state machine: IDLE (thumbs up) ⇄ MIMIC (stream smoothed finger angles)
```
The existing `trajectory_control.py` (listens on `/pose_goals`) stays untouched and keeps running; we publish to the
same controller topic directly. The controller has `allow_partial_joints_goal: true`, so sending only finger joints is fine.

## Interface contract (UDP, Mac → VM)
- Transport: UDP, one JSON object per datagram, UTF-8. Default port **5005**. VM binds `0.0.0.0:5005`.
- Tracker sends **continuously at ~30 Hz**, also when no hand is visible (acts as heartbeat).
- VM address on Mac side: CLI `--host` or env `SIM_HOST` (UTM "Shared Network" usually gives `192.168.64.x`).

```json
{"v": 1, "seq": 1234, "t": 1762370000.123, "hand": true,
 "joints": {"joint_index_1": 0.81, "joint_index_2": 0.62, "...": 0.0}}
```
- `hand`: true only if a hand is (debounced) detected. If false, `joints` is `{}`.
- `joints`: radians, **already mapped to the prosthesis range and clamped to [0.0, 1.57]**. 0 = straight/open.
  The tracker owns all calibration; the bridge only smooths and forwards.
- Phase 1 sends the 16 hand joints below. Unknown keys must be ignored by the bridge (forward compatibility, e.g. P6 wrist).

### Joint names (from `model/prosthesis.urdf.xacro`, all revolute, limits 0..1.57 rad)
```
joint_index_1  joint_index_2  joint_index_3      # MCP, PIP, DIP
joint_middle_1 joint_middle_2 joint_middle_3
joint_ring_1   joint_ring_2   joint_ring_3
joint_little_1 joint_little_2 joint_little_3
joint_thumb_1_x joint_thumb_1_y joint_thumb_2 joint_thumb_3   # semantics → P1 writes to NOTES.md
```
Wrist (used by idle poses / P6 only, limits ±1.57): `joint_wrist_x` (axis x), `joint_wrist_y` (axis y).
Base joints `joint_base_{x,y,z,roll,pitch,yaw}`: **never command**.

## Bridge behaviour (spec, implemented in P2)
- States: **IDLE** (start state) and **MIMIC**.
- IDLE → MIMIC: first packet with `hand: true`. On entry, reset wrist joints to 0 if the idle pose moved them.
- MIMIC → IDLE: no `hand: true` packet for **1.0 s** (covers both `hand:false` and the tracker dying).
- MIMIC: exponential smoothing per joint (alpha ≈ 0.4), publish a `JointTrajectory` with one point,
  `time_from_start` = 0.1 s, at 20 Hz.
- IDLE: send idle pose on entry, then re-send every 5 s (self-heals after glitches).
- Log state transitions only (no per-packet logs).

## Packets & order
| ID | Title | Where | Depends on | Est. |
|---|---|---|---|---|
| P0 | Setup & connectivity check | user + both | — | 30 min |
| P1 | Idle poses (thumbs up / peace) + thumb semantics | VM | P0 | 1 h |
| P2 | UDP → ROS bridge node + fake sender | VM | P1 | 1.5 h |
| P3 | Mac tracker: camera + landmarks + angles (no network) | Mac | P0 | 1.5 h |
| P4 | Tracker → UDP, mapping/calibration, end-to-end | Mac (+VM running) | P2, P3 | 1.5 h |
| P5 | Demo mode: launchers, auto-restart, kiosk | both | P4 | 1.5 h |
| P6 | (optional) Wrist tilt/rotation | both | P5 | 1 h |

Parallel tracks: **VM: P1 → P2** and **Mac: P3** at the same time. Then P4, P5, P6.

## File layout (create only what your packet needs)
```
hand_mimic/
  packets/            # these packets
  NOTES.md            # shared findings log (append-only)
  tools/fake_sender.py   # P2: sends synthetic packets (no deps)
  tools/udp_dump.py      # P3: prints received packets (no deps)
  tracker/tracker.py, requirements.txt, run_demo.command   # P3/P4/P5
ros2_ws/src/prosthesis_description/
  scripts/demo_poses.py         # P1: POSES dict + CLI
  scripts/hand_mimic_bridge.py  # P2
  launch/demo.launch.py         # P5
```
New ROS scripts must be added to `install(PROGRAMS ...)` in `CMakeLists.txt` and be `chmod +x` with a
`#!/usr/bin/env python3` shebang. Installed scripts live in the same `lib/` dir, so `from demo_poses import POSES` works.

## Testing protocol
- VM agent: `cd ros2_ws && colcon build && source install/setup.bash`. Gazebo GUI may be slow in UTM; verify
  headlessly with `ros2 topic echo /joint_states --once` (positions reached?) and `ros2 topic hz`.
  Visual check is the user's job — tell them exactly what to look for.
- Mac agent: Python 3.11 or 3.12 venv in `hand_mimic/tracker/.venv` (gitignored). The terminal app needs camera
  permission (System Settings → Privacy & Security → Camera). Test without VM using `tools/udp_dump.py`.

## Later (out of scope unless asked)
Option B: run the demo under a separate macOS user account so personal data is out of reach. Docker/portable version.
