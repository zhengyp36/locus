# checkpoint/tools — screenlab dev/ops helpers

Encapsulates the repetitive, per-session work (find password, re-type long ssh/rsync
commands, re-derive coordinates, re-write throwaway probe scripts). Source `env.sh`
once and use the commands below; the environment facts live in one place.

Rules & discipline: locus `rules/task.md` (task execution); the archived
`../screenlab-rules.md` is superseded. Target/account values here are
*environment facts* (rediscoverable), not rules.

## Bootstrap a new session

```bash
source /home/zhengyp/work/A/checkpoint/tools/env.sh
tools/snapshot.sh          # local repo state + live target status, as JSON
```
`snapshot.sh` is the "one command to get oriented" — prefer it over re-reading a long
handoff to reconstruct the world. It also writes `tools/state.json`.

## Commands

| Command | What it does |
|---|---|
| `tools/status.sh [--json]` | One glance at the target: attach / port / consent_app / tray / tcp / lock / aliases. |
| `tools/snapshot.sh` | `status.sh` + local `cogos` git state, merged JSON → `tools/state.json`. |
| `tools/deploy.sh` | rsync `$SL_COGOS` → target, `install-machine --desktop-user`, restart attach, verify code. |
| `tools/desktop.sh coords\|tray\|shot\|dblclick\|reset` | Real-session desktop ops (XTEST). `shot`/`tray` pull a PNG locally. |
| `tools/agent.py probe\|act\|key\|hold\|watch` | Agent-side driver over the 3a endpoint (each fresh connection = one consent prompt). |
| `tools/diagnose-presence.sh [--xi2]` | Isolate the physical-vs-injected monitor; baseline vs `note_injection` window. |
| `tools/imgctx.py see\|mark\|adjust-mark\|unmark\|coord ...` | Slice 0 thin CLI over `cogos/image_ctx`; `--root`/`--state` (flock'd) persist FIG/ANNO across processes; emits one JSON line (read `image` as attachment). |
| `tools/imgctx_selftest.py` | Slice 0 known-truth acceptance (synthetic PNG → see/mark/coord); exit 0 = pass. |
| `tools/x11.sh start\|stop\|capture\|click\|pointer\|geometry\|windows\|zenity\|status` | Slice 1 device backend: throwaway owned Xvfb `:101` + openbox + zenity click target on the target (systemd-run units `sl1-*`); `capture` pulls a unique full-screen PNG into `blobs/`; `zenity` counts the dialog by class (raw `windows` matches openbox/GTK internals). |
| `tools/x11_selftest.py` | Slice 1 known-truth acceptance: (re)starts the surface, then `look -> mark -> coord -> act`; asserts coord/pointer px == (726,458) and zenity closes 1->0. Exit 0 = pass. |
| `tools/android.sh status\|connect\|capture\|geometry\|tap\|key\|foreground\|ui-bounds\|consent-auto` | Slice 2 Android backend: full-screen `screencap` to a unique blobs/ PNG; `tap` injects via the app's InjectService (`am broadcast op tap`, device px); `foreground` reads the resumed activity; `ui-bounds TEXT` gives device-truth bounds (uiautomator). No consent needed. |
| `tools/android_selftest.py` | Slice 2 known-truth acceptance: home-screen Chrome icon bounds (uiautomator) -> `look -> mark -> coord -> zoom -> act`; asserts coord/device == icon center, Chrome becomes foreground, and a self-computed diff localizes the change. Exit 0 = pass. |
| `tools/windows.sh deploy\|capture\|tap\|click\|info\|active-window\|target-start\|target-state\|cat\|rm` | Slice 3 Windows backend: runs the **product** path (`platform_backends`: DXGI/dxcam capture + SendInput injection) inside assist's interactive session over ssh + the 62c Task-Scheduler harness (`launch_probe.ps1` + `win_io.py` one-shot request/result). `capture` pulls a unique full-screen PNG into `blobs/`; `target-start` opens a topmost Tk ground-truth window. No daemon, no consent. |
| `tools/windows_selftest.py` | Slice 3 known-truth acceptance: DPI-aware Tk target reports its physical rect -> `look -> mark -> coord -> zoom -> act`; asserts coord/device == target center, the injected click flips the target READY->HIT, and a self-computed diff localizes the change. Exit 0 = pass. |
| `tools/screendiff.py fp\|A B` | Generic change signal (x8 fingerprint + block-diff bbox) over `screenlab.service.change`; the universal fallback where no native damage exists. |

## imgctx (Slice 0 vision CLI)

Wraps `cogos/image_ctx` (`see`/`mark`/`adjust-mark`/`unmark`/`coord`) as a process-per-call
CLI with a flock'd state file, so FIG/ANNO ids survive across invocations. Default state
root = `tools/.imgctx` (`IMGCTX_ROOT` overrides); `SL_COGOS` points at the repo.

```bash
PY=/usr/bin/python3.11
$PY tools/imgctx.py see  --ref PATH:/abs/img.png            # -> FIG:1000 + cache png path
$PY tools/imgctx.py mark --ref FIG:1000 --kind cross --center 0.75,0.25
$PY tools/imgctx.py coord --ref FIG:1000 --anno ANNO:1      # -> @原图 normalized + px
$PY tools/imgctx_selftest.py                                # known-truth acceptance
```

Each call prints one JSON line: `{"ok","command","text","image","image_size"}`. `image` is a
real cached PNG path — read that file as an attachment (never inline pixels/base64 here).

### Slice 1 (X11 live loop)

`tools/x11.sh` brings up an owned Xvfb surface on the target (no consent, no human
session needed) with a `zenity` click target; `imgctx.py look` captures it into
image_ctx and `imgctx.py act` clicks an annotation's `@原图` coord and returns the
post-click screen with a landing mark.

```bash
tools/x11.sh start                         # Xvfb :101 + openbox + zenity on the target
PY=/usr/bin/python3.11
$PY tools/imgctx.py --state s.json look                          # -> FIG + frame PNG
$PY tools/imgctx.py --state s.json mark --ref FIG:1000 --kind cross --center 0.567,0.572
$PY tools/imgctx.py --state s.json act  --ref FIG:1000 --anno ANNO:1
# -> {screen:[W,H], norm:[..], device:[px], pointer:"X=.. Y=..", landing_fig:".."}
$PY tools/x11_selftest.py                   # known-truth acceptance (all of the above)
```

Target must be up first (it is a VBox VM, `VBoxManage startvm centos9 --type headless`
on `zhengyp@100.112.50.115`).

### Slice 2 (Android live loop)

The same loop against the phone, selected with `--backend android` (or
`SL_SCREEN_BACKEND=android`). `tools/android.sh` captures via `adb exec-out screencap`
and injects via the assist app's `InjectService` (`am broadcast op tap`, the app's own
`dispatchGesture` path). No consent: the dev receiver is reachable from adb shell.

```bash
export SL_SCREEN_BACKEND=android
PY=/usr/bin/python3.11
$PY tools/imgctx.py --state a.json look                       # -> FIG + 1080x2312 frame
$PY tools/imgctx.py --state a.json mark --ref FIG:1000 --kind cross --center 0.31,0.92
$PY tools/imgctx.py --state a.json coord --ref FIG:1000 --anno ANNO:1   # -> px (338,2125)
$PY tools/imgctx.py --state a.json act  --ref FIG:1000 --anno ANNO:1
$PY tools/android_selftest.py                                 # known-truth acceptance
```

`act` takes its device pixel size from the FIG's **own frame** (`orig_w/orig_h`), not a
separately-queried geometry: the model acts on the image it saw (the #61 fix).

### Slice 3 (Windows live loop)

The same loop against Windows, selected with `--backend win` (or
`SL_SCREEN_BACKEND=win`). Capture is the product **DXGI Desktop Duplication** backend
(`DxcamCapture` via `dxcam`, GDI/Pillow fallback; `platform_backends.pick` prefers it,
`SCREENLAB_CAPTURE=dxcam|gdi` forces). Injection is the product `SendInputAct`. Both
must run in assist's interactive session (an ssh logon is Session 0 with no desktop),
so `windows.sh` drives them per-op through the 62c Task-Scheduler harness.

```bash
tools/windows.sh deploy                       # push win_io.py / target_tk.py / launcher
tools/windows.sh info                         # backend=dxcam, act=sendinput, displays
export SL_SCREEN_BACKEND=win
PY=/usr/bin/python3.11
$PY tools/imgctx.py --state w.json look                          # -> FIG + 1920x1280 frame
$PY tools/imgctx.py --state w.json mark --ref FIG:1000 --kind cross --center 0.469,0.430
$PY tools/imgctx.py --state w.json act  --ref FIG:1000 --anno ANNO:1
$PY tools/windows_selftest.py                 # known-truth acceptance
```

`win_io.py` reads a one-shot `win_io.req` (JSON `{op,args}`) and writes `win_io.result`,
both under `C:\Users\assist\screenlab-62c\`; screenshots land in `blobs/`.

## Environment facts (in `env.sh`)

- Target: `zhengyp@100.100.137.78`; sudo password stdin `~/.secrets/centos.key`.
- Human session: user `human` uid `1002`, `:0`, xauth `/run/user/1002/gdm/Xauthority`.
- Endpoint: `tcp:100.100.137.78:8911`; registry `/home/human/.config/screenlab/registry`
  (agent alias `kilocode`); agent test key `tools/keys/agent.key` (persisted — no more
  hunting in `/tmp/kilo`).
- UI coords: launcher `70,405`; tray padlock `1692,18`; tray crop `1494,0,1707,26`.
  Rediscover with `tools/desktop.sh coords` / `tray`; override via `SL_*` env.
- Takeback hotkey: `Ctrl+Alt+Shift+Escape` (`SL_TAKEBACK_KEYS`).

## Output discipline (keep the context small)

- Scripts print **verdicts / one-line summaries**, not raw tool output. Big blobs
  (screenshots) are written to `tools/blobs/` and only their **path** is printed — read
  the image only when human eyes are actually needed.
- `status.sh` / `snapshot.sh` emit compact JSON for machine consumption.
- Prefer these tools over ad-hoc `/tmp` scripts; if something will be needed twice or
  across sessions, add it here instead.

## Notes

- `deploy.sh` and the `desktop.sh` / `diagnose-presence.sh` scripts need sudo on the
  target; `env.sh`'s `sl_root*` helpers feed the password automatically.
- `agent.py` uses the same implementation as the `computer` tool; every invocation
  opens a new connection and therefore raises a fresh consent request on the desktop.
- XTEST clicks in `desktop.sh` prove wiring, not real-mouse feel (that needs the VBox
  console — see the handoff).
