# tools/win — Windows 3a dev/ops helpers

Same idea as the Linux-side `tools/`: the repetitive Windows ops in one place.
Run these from the dev box (Linux) with `../env.sh` sourced (`win_ssh` / `win_admin`
are defined there). All target the real Windows machine (`SL_WIN_HOST`), account
`SL_WIN_USER` (default `assist`), admin ssh `SL_WIN_ADMIN_SSH` (default `zhengyp`).

## Why these exist

The daemon/tray must run inside the human's **interactive session** (assist is
signed in on the Console / session 6). An ssh logon lands in Session 0, where a
process sees no desktop, so it cannot capture/act or show the tray. These scripts
use the Task Scheduler **COM API** as admin to start the process with the assist
**interactive token** (`LogonType=3`). That is a test harness for W1/W3; the
product path ("the human opens a program") is W4 — do not ship the task.

## Usage

```bash
source /home/zhengyp/work/A/checkpoint/tools/env.sh

# 1) identity + consent addr (once; rewrites registry.json as a JSON ARRAY)
ssh "$SL_WIN_SSH" 'powershell -NoProfile -ExecutionPolicy Bypass -Command -' \
    < tools/win/setup_registry.ps1

# 2) daemon + resident tray entry, in assist's interactive session
ssh "$SL_WIN_ADMIN_SSH" 'powershell -NoProfile -ExecutionPolicy Bypass -Command -' \
    < tools/win/launch_daemon.ps1
ssh "$SL_WIN_ADMIN_SSH" 'powershell -NoProfile -ExecutionPolicy Bypass -Command -' \
    < tools/win/launch_tray.ps1

# 3) one-glance state (ports, pids, log, consent.addr)
ssh "$SL_WIN_ADMIN_SSH" 'powershell -NoProfile -ExecutionPolicy Bypass -Command -' \
    < tools/win/status.ps1

# 4) ground-truth desktop shot (runs a one-shot grab task, writes blob locally)
ssh "$SL_WIN_ADMIN_SSH" 'powershell -NoProfile -ExecutionPolicy Bypass -Command -' \
    < tools/win/shot_task.ps1
scp "$SL_WIN_SSH:C:/Users/assist/AppData/Local/screenlab/tray_shot.png" /tmp/win_shot.png

# 5) stop everything (daemon + tray + launcher stubs)
ssh "$SL_WIN_ADMIN_SSH" 'taskkill /F /IM pythonw.exe /IM python.exe'
```

## Notes / gotchas (learned the hard way)

- `registry.json` must be a **JSON array** `[{...}]`; PowerShell `ConvertTo-Json`
  on a one-element array unwraps it to an object → server raises
  `registry file must be a JSON array`.
- The machine has **no PIL / cryptography** for `C:\Program Files\Python311`
  (despite an earlier handoff claim); `install.ps1` installs them over the network.
- `venv\Scripts\pythonw.exe` shows up as **two** processes: a ~6 MB launcher stub
  plus the real interpreter (~25 MB). Not a duplicate instance.
- A `Global\` mutex / NIM_ADD bugs were fixed in `consent_app_win.py` (see the
  commit-pending diff); tray single-instance now uses `Local\`.
- Answer consent from the Windows side so no tunnel is needed for it:
  `consent_app_win` (tray) or the CLI
  `venv\Scripts\python.exe -m screenlab.service.cli --auth <regdir> consent --once`
  (needs `cd /d <prefix>` so `screenlab` is importable).
- Agent side connects through `ssh -N -L 9911:127.0.0.1:9911 -L 9912:127.0.0.1:9912`;
  daemon binds loopback only.
