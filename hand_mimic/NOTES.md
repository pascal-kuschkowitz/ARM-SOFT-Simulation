# Hand-Mimic NOTES (append-only, dated bullets)

## P0 — setup & connectivity (2026-11-05)
Checked from the Mac side. VM-side items are still open (marked TODO).

- **Mac**: macOS 15.8.1, arm64, UTM.app installed. Mac LAN IP `10.7.15.37`. Built-in display + one more display listed by macOS.
- **Mac Python**: default `python3` = **3.15.2** (too new for MediaPipe). Installed: 3.13, 3.14, 3.15. **No 3.11/3.12** → run `brew install python@3.12` before P3.
  (3.13 might work with the newest mediapipe wheels, not verified.)
- **Code sync**: git remote `origin` = `git@github.com:N-Pulse/ARM-SOFT-Simulation.git`. Default plan (a): Mac commits → push branch → VM `git pull`.
  **TODO: user must OK pushing `add/visualization-for-scientastic`** (or pick (b)/(c)). Not pushed.
  Note: `hand_mimic/` is currently untracked (packets not committed).
- **Remote Login (SSH) on Mac**: not checked (needs admin); only needed for sync option (b).
- **VM IP (`SIM_HOST`)**: TODO. In VM: `ip -4 addr | grep 192.168`. No `192.168.64.x` bridge visible on the Mac now (VM probably not running).
- **UDP Mac → VM on 5005**: TODO. VM: `nc -ul 5005`; Mac: `echo hello | nc -u -w1 <VM_IP> 5005`.
- **Sim RTF / GUI usability**: TODO (VM).
- **Controller streaming test (step 5)**: TODO (VM).
- **External monitor full-screen**: TODO (user).
- **Claude Code in VM**: TODO (optional).
