# Hand-Mimic NOTES (append-only, dated bullets)

## P0 — setup & connectivity (2026-11-05)
Checked from the Mac side. VM-side items are still open (marked TODO).

- **Mac**: macOS 15.8.1, arm64, UTM.app installed. Mac LAN IP `10.7.15.37`. Built-in display + one more display listed by macOS.
- **Mac Python**: default `python3` = **3.15.2** (too new for MediaPipe). Installed: 3.13, 3.14, 3.15. **3.12.16 installed via brew** (2026-11-05) → use `/opt/homebrew/bin/python3.12 -m venv hand_mimic/tracker/.venv` for P3.
  (3.13 might work with the newest mediapipe wheels, not verified.)
- **Code sync**: git remote `origin` = `git@github.com:N-Pulse/ARM-SOFT-Simulation.git`. Default plan (a): Mac commits → push branch → VM `git pull`.
  Decision: plan (a). User pushes manually; agents never push.
  Note: `hand_mimic/` is currently untracked (packets not committed).
- **Remote Login (SSH) on Mac**: not checked (needs admin); only needed for sync option (b).
- **VM IP (`SIM_HOST`)**: `192.168.64.5` (user `pengu@pengus-vm`, iface enp0s1, UTM Shared Network; Mac side is `192.168.64.1` on bridge100). May change via DHCP — re-check if it stops working.
- **UDP Mac → VM on 5005**: OK (2026-11-05, verified by user). Gotcha: send to the VM IP, not the .255 broadcast address.
- **Sim RTF / GUI usability**: not measured; user judged unnecessary.
- **Controller streaming test (step 5)**: OK (user confirmed; index finger bends via /joint_trajectory_controller/joint_trajectory).
- **External monitor full-screen**: not checked; user judged unnecessary.
- **Claude Code in VM**: skipped (optional).

## P1 — idle poses (2026-11-05) — CODE DONE, VISUAL TUNING STILL TODO (written on Mac, no ROS/Gazebo there)
- `scripts/demo_poses.py` added (POSES open/fist/thumbs_up/peace, `IDLE_POSE="thumbs_up"`, `make_trajectory(pose, seconds)`,
  CLI `thumbs_up|peace|open|fist|cycle|sweep <joint>`), registered in CMakeLists. Pose values are **guesses from URDF axes**, not verified in sim.
- Geometry derived from URDF (unverified visually): fingers extend along palm +x and curl about +y (toward palm side, −z). Thumb links hang along −z
  from `palm_link` at (0.05, 0.04): `thumb_1_x` (axis −x) should swing the thumb sideways toward −y (across the palm toward the fingers = opposition/adduction);
  `thumb_1_y`, `thumb_2`, `thumb_3` (axis −y) should flex it toward +x (fingertip direction). Thumb joints = 0 → thumb straight (extended).
- Wrist: `joint_wrist_x` axis x (forearm roll, pronation/supination), `joint_wrist_y` axis y (flex/extension). Which sign points the thumb up in the camera view: **TODO on VM** —
  tune `THUMBS_UP_WRIST_X/Y` at top of demo_poses.py (currently 0).
- TODO on VM: `colcon build`, run `demo_poses.py cycle` and `sweep <joint>`, fix values, check collisions/jitter, check `/joint_states`, update this entry.
