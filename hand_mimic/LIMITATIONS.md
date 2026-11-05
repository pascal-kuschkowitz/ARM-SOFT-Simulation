# Prosthesis model limitations for hand mimicry

Findings from P1 (2026-11-06), from the URDF (`model/prosthesis.urdf.xacro`) and tests in Gazebo. Poses were checked through tf link positions and by eye.

## Joint limits
| Joints | Range | Consequence |
|---|---|---|
| Finger joints (`index/middle/ring/little_1..3`) | 0 .. 1.57 rad | Curl only, no hyperextension |
| Thumb joints (`thumb_1_x`, `thumb_1_y`, `thumb_2`, `thumb_3`) | 0 .. 1.57 rad | One direction only; no thumb abduction away from the palm |
| `joint_wrist_x` (forearm roll) | -1.57 .. 1.57 | 180 deg total; no full supination/pronation |
| `joint_wrist_y` (flexion/extension) | -1.57 .. 1.57 | |
| `joint_base_*` | not commanded | Arm base never moves in this demo |

## Thumb geometry
- At 0 the thumb hangs along -z from the palm, base at palm (0.05, 0.04), perpendicular to the fingers.
- `thumb_1_x` (axis -x, only positive) swings it across the palm toward -y.
- `thumb_1_y`, `thumb_2`, `thumb_3` (axis -y, only positive) flex it toward the fingertips (+x).
- In palm frame the thumb can reach -z, -y and +x, but never +y or +z.

## What this rules out
- **Natural thumbs-up.** Thumb up needs a 180 deg wrist roll, but the roll is limited to +/-90 deg. Options tried:
  - roll -90 + `thumb_1_x` 1.5: thumb up, but swung across the palm (judged unnatural);
  - wrist pitched back 90 + `thumb_1_y` 1.5: thumb up, wrist bent (judged wrong).
  - At +90 roll the thumb points sideways, horizontal, and cannot be raised.
- **Thumb abduction, "stop" hand, spread fingers.** There is no finger abduction/adduction joint at all, and the thumb cannot move away from the palm.
- **Pronation/supination beyond 90 deg.**
- **Independent DIP/PIP behaviour.** Real fingers coupling is approximated; each of the 3 joints is commanded separately.

## What works
- Finger curl for all four fingers (fist, open, peace, pointing, counting 1..4).
- Wrist roll +/-90 and pitch +/-90 (used in idle poses, P6).
- Thumb flex across the palm (opposition-like) and toward the fingertips.
- Idle pose: **peace** (user-confirmed).

## Proposed model changes (outside P1; one-line URDF edits)
1. `joint_thumb_1_x` lower limit 0 -> -1.57: thumb can go up at +90 roll, which probably gives a natural thumbs-up.
2. `joint_wrist_x` limits -> +/-3.14: allows the 180 deg roll for thumb up.
3. Add a finger abduction joint (bigger change; needed for spread fingers).
4. Move the thumb mount toward the side of the palm instead of the palm underside.
Retest all poses after any URDF change; the pose values in `demo_poses.py` depend on this geometry.
