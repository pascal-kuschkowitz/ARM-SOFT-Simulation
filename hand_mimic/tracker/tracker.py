#!/usr/bin/env python3
"""Hand-mimic tracker: webcam -> MediaPipe HandLandmarker -> 16 prosthesis joint angles (P3: no network yet)."""
import argparse, math, os, time, urllib.request
import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision

MODEL_URL = ("https://storage.googleapis.com/mediapipe-models/hand_landmarker/"
             "hand_landmarker/float16/latest/hand_landmarker.task")
MODEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "hand_landmarker.task")
PRESENT_AFTER, ABSENT_AFTER = 3, 5      # debounce (consecutive frames)
MAX_ANGLE = 1.57

FINGERS = {"index": 5, "middle": 9, "ring": 13, "little": 17}   # MCP landmark index
JOINT_NAMES = [f"joint_{f}_{i}" for f in FINGERS for i in (1, 2, 3)] + \
              ["joint_thumb_1_x", "joint_thumb_1_y", "joint_thumb_2", "joint_thumb_3"]

# CAL: joint -> (raw_open, raw_closed); linear map to [0, 1.57], clamped. P4 tunes.
CAL = {n: (0.1, 1.5) for n in JOINT_NAMES}
CAL["joint_thumb_1_x"] = (0.0, 1.0)   # raw = opposition 0..1
CAL["joint_thumb_1_y"] = (0.1, 1.0)   # raw = CMC flexion (rad)

BONES = [(0,1),(1,2),(2,3),(3,4),(0,5),(5,6),(6,7),(7,8),(5,9),(9,10),(10,11),(11,12),
         (9,13),(13,14),(14,15),(15,16),(13,17),(17,18),(18,19),(19,20),(0,17)]


def ensure_model():
    if not os.path.exists(MODEL_PATH):
        print("downloading hand_landmarker.task ...")
        urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)


def bend(a, b, c):
    """Angle between (b-a) and (c-b) in radians; 0 = straight."""
    u, v = b - a, c - b
    n = np.linalg.norm(u) * np.linalg.norm(v)
    if n < 1e-9:
        return 0.0
    return float(math.acos(np.clip(np.dot(u, v) / n, -1.0, 1.0)))


def mapc(name, raw):
    lo, hi = CAL[name]
    t = (raw - lo) / (hi - lo)
    return float(np.clip(t, 0.0, 1.0) * MAX_ANGLE)


def raw_angles(w):
    """w: (21,3) world landmarks -> dict joint -> raw value."""
    r = {}
    for f, mcp in FINGERS.items():
        r[f"joint_{f}_1"] = bend(w[0], w[mcp], w[mcp + 1])
        r[f"joint_{f}_2"] = bend(w[mcp], w[mcp + 1], w[mcp + 2])
        r[f"joint_{f}_3"] = bend(w[mcp + 1], w[mcp + 2], w[mcp + 3])
    r["joint_thumb_2"] = bend(w[1], w[2], w[3])
    r["joint_thumb_3"] = bend(w[2], w[3], w[4])
    # Per NOTES (P1): thumb_1_x swings thumb across palm (opposition); thumb_1_y flexes toward fingertips.
    palm = np.linalg.norm(w[0] - w[9]) + 1e-9
    r["joint_thumb_1_x"] = 1.0 - float(np.clip(np.linalg.norm(w[4] - w[17]) / palm / 1.6, 0, 1))
    r["joint_thumb_1_y"] = bend(w[0], w[1], w[2])   # TODO(P4): tune thumb mapping against the real prosthesis
    return r


def frame_to_msg(present, world=None):
    """Output dict for P4 to send: {"hand": bool, "joints": {...}} (joints mapped to [0,1.57])."""
    if not present or world is None:
        return {"hand": False, "joints": {}}
    raw = raw_angles(world)
    return {"hand": True, "joints": {n: round(mapc(n, raw[n]), 3) for n in JOINT_NAMES}}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--camera", type=int, default=0)
    ap.add_argument("--fullscreen", action="store_true")
    ap.add_argument("--print", action="store_true", help="print mapped joints once per second")
    args = ap.parse_args()

    ensure_model()
    opts = vision.HandLandmarkerOptions(
        base_options=mp_python.BaseOptions(model_asset_path=MODEL_PATH),
        running_mode=vision.RunningMode.VIDEO, num_hands=1)
    landmarker = vision.HandLandmarker.create_from_options(opts)

    cap = cv2.VideoCapture(args.camera)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    if not cap.isOpened():
        raise SystemExit(f"cannot open camera {args.camera} (macOS: grant camera permission to your terminal)")
    win = "hand-mimic tracker"
    cv2.namedWindow(win, cv2.WINDOW_NORMAL)
    if args.fullscreen:
        cv2.setWindowProperty(win, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    hits = misses = 0
    present = False
    last_world = None
    t_start, fps, t_prev, t_print = time.time(), 0.0, time.time(), 0.0
    while True:
        ok, frame = cap.read()
        if not ok:
            time.sleep(0.05)
            continue
        frame = cv2.flip(frame, 1)   # selfie view; flexion angles are mirror-invariant
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        ts = int((time.time() - t_start) * 1000)
        res = landmarker.detect_for_video(mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb), ts)

        detected = bool(res.hand_landmarks) and bool(res.hand_world_landmarks)
        if detected:
            hits, misses = hits + 1, 0
            last_world = np.array([[p.x, p.y, p.z] for p in res.hand_world_landmarks[0]])
            if hits >= PRESENT_AFTER:
                present = True
            h, w = frame.shape[:2]
            pts = [(int(p.x * w), int(p.y * h)) for p in res.hand_landmarks[0]]
            for a, b in BONES:
                cv2.line(frame, pts[a], pts[b], (0, 255, 0), 2)
            for p in pts:
                cv2.circle(frame, p, 4, (0, 0, 255), -1)
        else:
            misses, hits = misses + 1, 0
            if misses >= ABSENT_AFTER:
                present = False

        msg = frame_to_msg(present, last_world)
        if args.print and time.time() - t_print >= 1.0:
            t_print = time.time()
            if msg["hand"]:
                print(" ".join(f"{k[6:]}={v:.2f}" for k, v in msg["joints"].items()), flush=True)
            else:
                print("no hand", flush=True)

        now = time.time()
        fps = 0.9 * fps + 0.1 / max(now - t_prev, 1e-6)
        t_prev = now
        cv2.putText(frame, f"FPS {fps:4.1f}", (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        text, color = ("Tracking", (0, 200, 0)) if present else ("Show your hand to the camera", (0, 140, 255))
        cv2.putText(frame, text, (10, frame.shape[0] - 20), cv2.FONT_HERSHEY_SIMPLEX, 1.1, color, 3)
        cv2.imshow(win, frame)
        if (cv2.waitKey(1) & 0xFF) in (ord("q"), 27):
            break
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
