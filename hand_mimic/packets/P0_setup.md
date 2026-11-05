# P0 — Setup & connectivity check

**Where:** user, with help from whichever agent is open. **Goal:** remove all environment unknowns before coding.
Record every result in `hand_mimic/NOTES.md` (create it).

## Checklist
1. **Code sync Mac ↔ VM.** Pick one and write it to NOTES.md:
   - (a) *git* (default): Mac commits → `git push` the branch → VM `git pull`. Needs the user's OK to push this branch.
   - (b) *local git remote, no GitHub*: in the VM, `git remote add mac ssh://<user>@<mac-ip>/<path-to-repo>` (needs Remote Login on Mac) and `git pull mac add/visualization-for-scientastic`.
   - (c) *UTM shared directory* (VirtFS) pointing at the repo; mount in VM (`sudo mount -t 9p -o trans=virtio share /mnt/share`). Build dirs then also land on the share (they're gitignored).
2. **VM IP.** In VM: `ip -4 addr | grep 192.168` → note it (`SIM_HOST`). UTM network mode should be "Shared Network".
3. **UDP Mac → VM.** VM: `nc -ul 5005`. Mac: `echo hello | nc -u -w1 <VM_IP> 5005`. "hello" must appear in VM.
   If not: `sudo ufw status` in VM (disable/allow 5005/udp), check UTM network mode.
4. **Sim runs.** VM: `cd ros2_ws && colcon build && source install/setup.bash && ros2 launch prosthesis_description gazebo.launch.py`.
   Note Gazebo's real-time factor (bottom right) and whether the GUI is usable. If RTF ≪ 1 or the GUI is too slow,
   check UTM display is `virtio-gpu-gl-pci` (GPU acceleration) and note it.
5. **Controller accepts streaming.** With sim running:
   ```
   ros2 topic pub --once /joint_trajectory_controller/joint_trajectory trajectory_msgs/msg/JointTrajectory \
   "{joint_names: [joint_index_1], points: [{positions: [1.2], time_from_start: {sec: 0, nanosec: 200000000}}]}"
   ```
   Index finger should bend. `ros2 topic echo /joint_states --once` confirms.
6. **Mac Python.** `python3 --version`; need 3.11 or 3.12 for MediaPipe wheels (`brew install python@3.12` if not).
7. **External monitor.** Confirm the UTM window can go full screen on the external monitor.
8. **(Optional) Claude Code in the VM.** Install it so the VM agent can build and test on its own. Worth it for P1/P2/P5.

## Done when
NOTES.md has: sync method, VM IP, UDP ok, RTF, Python version, monitor ok.
