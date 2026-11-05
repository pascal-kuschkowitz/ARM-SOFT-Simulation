# P5 — Demo mode: one-command start, auto-restart, kiosk

**Where:** both (VM part + Mac part, can be two agents). **Depends on:** P4. **Read:** 00_MASTER.md, NOTES.md.
Goal: runs for hours unattended; the user starts it with one command per machine.

## VM part
1. `launch/demo.launch.py` (new): includes `gazebo.launch.py` and starts `hand_mimic_bridge.py` with `respawn=True`,
   `respawn_delay=2.0`. Bridge params overridable via launch args (`idle_pose`, `alpha`).
2. Restart loop in the VM for when Gazebo itself dies: document in NOTES.md
   `while true; do ros2 launch prosthesis_description demo.launch.py; sleep 3; done` (or a small `.py` wrapper —
   remember `*.sh` is gitignored).
3. Camera framing: set a good default GUI camera pose so the hand fills the view on the external monitor (Gazebo Harmonic
   `<gui>` / GzScene3D camera pose in the world file, or whatever works quickest). Only if it's < 30 min; otherwise
   tell the user to set it manually.
4. Soak test headless: `fake_sender.py --mode blink` for 20+ min; check memory/CPU of bridge stays flat
   (`ps -o rss,pcpu -p <pid>`), no stuck state.

## Mac part
1. In `tracker.py`: if camera reads fail for > 2 s, release and reopen the camera (loop forever, show "camera reconnecting").
   Wrap the main loop so any exception logs and restarts the loop instead of exiting.
2. `hand_mimic/tracker/run_demo.command` (double-clickable, `chmod +x`): `cd` to its folder, activate venv,
   `caffeinate -dimsu` around a `while true; do python tracker.py --fullscreen; sleep 2; done` loop. Reads `SIM_HOST`
   from `hand_mimic/tracker/sim_host.txt` if present.
3. Preview polish (cheap only): big "Show your hand!" text when idle, small "N-Pulse prosthesis demo" header.

## Checklist for the user (put in final message)
Mac: Focus/Do Not Disturb on, display sleep off, notifications off, power connected, UTM window full screen on the
external monitor, tracker full screen on the laptop. Note: locking the Mac stops the demo → see Option B in master (separate user).

## Done when
Both one-command starts work; killing the bridge, the tracker, or Gazebo each recovers by itself within ~10 s.
Commit `hand-mimic(P5): demo mode`.
