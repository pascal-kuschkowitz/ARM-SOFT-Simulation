# P6 — (optional) Wrist tilt & rotation

**Where:** Mac (tracker) + VM (bridge param only). **Depends on:** P5 stable. Do this only if the user asks and time is left.
**Read:** 00_MASTER.md, NOTES.md (wrist semantics from P1).

## Tasks
1. Tracker: from world landmarks, palm frame: `y` = wrist(0)→middle MCP(9), palm normal = cross(0→5, 0→17)
   (flip sign for the user's right hand so both hands give the same normal direction).
   - Roll (pronation/supination) = rotation of the palm normal around `y` vs. "palm facing camera".
   - Flex/extension = tilt of `y` toward/away from the camera.
   - **Mirror:** the user's hand is shown mirrored on the right-hand prosthesis → negate roll if it looks backwards. Decide by eye.
   - Map to `joint_wrist_x` / `joint_wrist_y` per NOTES.md semantics, clamp to ±1.0 (not full ±1.57; keeps it sane), heavier EMA.
   - Add them to `joints` in the UDP packet (contract already allows unknown/extra keys).
2. VM: run the bridge with `allow_wrist:=true` (launch arg in `demo.launch.py`). Make sure IDLE → MIMIC still resets wrist correctly.
3. Feature flag in tracker: `--wrist` (default off) so the demo can fall back instantly.

## Done when
Rotating/tilting the hand moves the prosthesis wrist the matching way without flipping or jitter. Commit `hand-mimic(P6): wrist`.
