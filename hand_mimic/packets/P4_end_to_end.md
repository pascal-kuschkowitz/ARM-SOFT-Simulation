# P4 — Tracker → UDP, calibration, end-to-end

**Where:** Mac (VM running sim + bridge from P2). **Depends on:** P2, P3. **Read:** 00_MASTER.md, NOTES.md.

## Tasks
1. In `tracker.py`: send `frame_to_msg` output as UDP JSON per the master contract at ~30 Hz, **every frame incl. no-hand
   frames**. Flags: `--host` (default env `SIM_HOST`, else 127.0.0.1), `--port 5005`, `--no-send`.
   Socket errors (VM down) must never crash the tracker — swallow and keep going.
2. First verify locally: `python ../tools/udp_dump.py` + `python tracker.py --host 127.0.0.1`.
3. Then end-to-end with the VM. Tune for a convincing demo, not accuracy:
   - Fix `CAL` ranges so open hand → fully open and fist → fully closed on the prosthesis.
   - Thumb: use P1's thumb semantics from NOTES.md. Must look right for: open hand, fist, thumbs up, peace, pinch.
     If a thumb DOF looks wrong/jittery, hold it at a constant instead — fine for the demo.
   - If jitter shows: add a light EMA in the tracker too, or ask to raise `alpha` smoothing in the bridge (param, no code change).
4. Optional calibration key: `c` while showing an open hand records `raw_open`, `f` with a fist records `raw_closed`,
   saved to `hand_mimic/tracker/calib.json` (loaded on start if present). Skip if the hardcoded values are good enough.
5. Note final tuning + observed latency in NOTES.md.

## Done when
User moves fingers → prosthesis follows with < ~300 ms perceived lag; hand leaves → thumbs up within ~1–1.5 s; hand returns → mimicking resumes.
Commit `hand-mimic(P4): end-to-end mimic`.

## Manual test (for the user)
VM: sim + bridge running (see P2). Mac: `source .venv/bin/activate && SIM_HOST=<VM_IP> python tracker.py`.
Try: open/close, single fingers, peace, thumbs up, remove hand.
