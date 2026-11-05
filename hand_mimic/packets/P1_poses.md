# P1 — Idle poses (thumbs up / peace) + thumb semantics

**Where:** VM. **Depends on:** P0. **Read:** 00_MASTER.md, NOTES.md.

## Why
The idle pose is the riskiest visual piece (thumb kinematics are unknown). Do it first and record what the thumb joints do,
because the Mac tracker (P3/P4) needs that to map the human thumb.

## Tasks
1. **Thumb semantics.** With the sim running, sweep each thumb joint alone (0 → 0.8 → 1.57) and note what it does
   visually/geometrically (abduction away from palm? opposition across palm? flexion?). Use the URDF axes as a hint:
   `thumb_1_x` axis −x, `thumb_1_y` axis −y, `thumb_2`/`thumb_3` axis −y. Also check `joint_wrist_x` / `joint_wrist_y`:
   which is forearm roll (pronation/supination) and which is flexion/extension, and which sign points the thumb "up"
   in the default Gazebo camera view. Write the findings to NOTES.md (needed by P3/P4/P6).
   If you can't judge visually, ask the user to look and describe; keep the question short.
2. **`scripts/demo_poses.py`** (new, executable, add to CMakeLists `install(PROGRAMS ...)`):
   - `POSES: dict[str, dict[str, float]]` — joint name → radians. At least `open`, `fist`, `thumbs_up`, `peace`.
     - `thumbs_up`: four fingers curled (~1.4–1.5 on all three joints), thumb extended/up. Use wrist joints so the thumb
       points roughly up in the default camera view, if that's possible within limits.
     - `peace`: index + middle straight, ring + little curled, thumb tucked over ring/little.
     - Every pose that uses the wrist must set both wrist joints; poses that don't use it set them to 0.
   - `IDLE_POSE = "thumbs_up"` (switch to `"peace"` if thumbs up looks bad — note why in NOTES.md).
   - `make_trajectory(pose: dict, seconds: float) -> JointTrajectory` helper (single point), reused by P2.
   - CLI: `ros2 run prosthesis_description demo_poses.py thumbs_up` publishes once to
     `/joint_trajectory_controller/joint_trajectory` and exits (wait until a subscriber exists before publishing, ~2 s timeout).
     `cycle` argument: loop through all poses every 2 s (handy for visual checks).
3. Check that curled fingers and the thumb don't collide or jitter (there are collision boxes). Adjust values if needed.

## Not in scope
Changing the URDF, `trajectory_control.py`, or controller config.

## Done when
`demo_poses.py thumbs_up|peace|open|fist|cycle` works; `/joint_states` shows targets reached; NOTES.md has thumb + wrist semantics
and the chosen IDLE_POSE. Commit `hand-mimic(P1): idle poses`.

## Manual test (for the user)
`ros2 launch prosthesis_description gazebo.launch.py`, then in a 2nd terminal `ros2 run prosthesis_description demo_poses.py cycle`.
Expect open → fist → thumbs up → peace, repeating.
