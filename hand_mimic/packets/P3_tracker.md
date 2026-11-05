# P3 — Mac tracker: camera, landmarks, joint angles (no network yet)

**Where:** Mac. **Depends on:** P0. Can run in parallel with P1/P2. **Read:** 00_MASTER.md, NOTES.md (thumb semantics may
arrive later from P1 — if missing, use the defaults below and leave a `TODO(P4)`).

## Tasks
1. `hand_mimic/tracker/requirements.txt`: `opencv-python`, `mediapipe`, `numpy` (pin the versions you actually install).
   Venv in `hand_mimic/tracker/.venv` (add `.venv/` and `*.task` to a `hand_mimic/.gitignore`).
2. Model: MediaPipe Tasks **HandLandmarker** (`hand_landmarker.task`, float16, from Google's mediapipe-models storage).
   Download on first run if missing (stdlib `urllib`). Use the Tasks API in `VIDEO` mode, `num_hands=1`.
   (Don't rely on the legacy `mp.solutions.hands` API; recent mediapipe releases may not ship it.)
3. **`hand_mimic/tracker/tracker.py`**:
   - Opens camera `--camera 0`, 640x480. Preview window flipped horizontally (selfie view), landmarks + bones drawn,
     FPS, and a big status line: no hand → "Show your hand to the camera" (OpenCV text is ASCII only), hand → "Tracking".
   - `--fullscreen` flag. `q`/Esc quits.
   - **Debounce:** hand counts as present after 3 consecutive detections, absent after 5 consecutive misses.
   - **Angles from world landmarks** (`hand_world_landmarks`, metric, 3D). These are flexion angles, so they don't depend
     on whether it's a left or right hand. Accept either hand (user wants left-hand input mirrored onto the right
     prosthesis; for flexion that's automatic).
     `bend(a,b,c)` = angle between vectors (b−a) and (c−b), in radians (0 = straight).
     MediaPipe indices: wrist 0; thumb 1–4; index 5–8; middle 9–12; ring 13–16; little 17–20.
     - `<f>_1` = bend(0, MCP, PIP), `<f>_2` = bend(MCP, PIP, DIP), `<f>_3` = bend(PIP, DIP, TIP).
     - `thumb_2` = bend(1,2,3), `thumb_3` = bend(2,3,4).
     - `thumb_1_x`/`thumb_1_y` (default until P1's NOTES say otherwise): opposition ≈ 1 − clamp(dist(4,17)/dist(0,9)/1.6, 0, 1) mapped
       to 0..1.57; abduction ≈ angle between (1→2) and (0→5) mapped to 0..1.57. Crude is fine; P4 tunes.
   - Mapping layer: a dict at the top `CAL = {joint: (raw_open, raw_closed)}` that maps raw → [0, 1.57] linearly with clamping.
     Start with raw_open=0.1, raw_closed=1.5 for finger joints; P4 tunes.
   - `--print` flag: print the 16 mapped joint values (2 decimals) once per second.
   - Produce the output dict `{"hand": bool, "joints": {...}}` in a function `frame_to_msg(...)` so P4 only adds sending.
4. **`hand_mimic/tools/udp_dump.py`** (stdlib): listen on a port, pretty-print received packets at most 2×/s with
   packet rate. Used by P4 to test without the VM.

## Done when
`python tracker.py --print` shows a live preview; open hand ≈ all near 0, fist ≈ fingers near 1.3–1.57; the status line
switches correctly when the hand enters/leaves. Commit `hand-mimic(P3): mac tracker preview`.

## Manual test (for the user)
```
cd hand_mimic/tracker && python3.12 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt
python tracker.py --print
```
Give camera permission to your terminal app if macOS asks (then restart the terminal).
