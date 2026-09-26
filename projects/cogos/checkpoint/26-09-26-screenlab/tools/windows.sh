#!/usr/bin/env bash
# Mechanical Windows backend for the screenlab visual loop (Slice 3).
#
# Runs the *product* capture/act path (screenlab.service.platform_backends:
# DXGI/dxcam capture + SendInput injection) inside assist's INTERACTIVE session
# on the Windows box, driven from Linux over ssh + the 62c Task-Scheduler
# harness. No daemon, no consent handshake — pure mechanical I/O.
#
#   tools/windows.sh deploy             # push win_io.py / target_tk.py / launcher
#   tools/windows.sh capture [PNG]      # full-screen PNG -> unique blobs/ path
#   tools/windows.sh tap X Y           # SendInput click at physical px
#   tools/windows.sh click X Y         # alias (x11-style verb)
#   tools/windows.sh info              # backend names, displays, active window
#   tools/windows.sh target-start      # launch topmost Tk ground-truth target
#   tools/windows.sh target-state      # read target.marker JSON (compact)
#   tools/windows.sh cat PATH          # type a remote file
#   tools/windows.sh rm PATH           # delete a remote file
set -uo pipefail
. "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/env.sh"

WIN_DIR='C:\Users\assist\screenlab-62c'
WIN_FWD='C:/Users/assist/screenlab-62c'
PY_BASE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

wssh() { ssh -o BatchMode=yes -o ConnectTimeout=8 "$SL_WIN_ADMIN_SSH" "$@"; }

_json1() { "$SL_PY" -c 'import json,sys;print(json.dumps(json.load(sys.stdin),ensure_ascii=False))'; }

# _req <op> <compact-json-args> -> prints the compact JSON result line
_req() {
  local op="$1" args="$2" req r i
  req=$(mktemp)
  "$SL_PY" -c 'import json,sys;print(json.dumps({"op":sys.argv[1],"args":json.loads(sys.argv[2])}))' \
      "$op" "$args" > "$req"
  scp -q -o BatchMode=yes -o ConnectTimeout=8 "$req" "$SL_WIN_SSH:$WIN_FWD/win_io.req" || { rm -f "$req"; return 1; }
  rm -f "$req"
  wssh "del \"$WIN_DIR\\win_io.result\"" >/dev/null 2>&1
  wssh "powershell -NoProfile -ExecutionPolicy Bypass -File \"$WIN_DIR\\launch_probe.ps1\" -Script win_io.py" >/dev/null 2>&1
  for i in $(seq 1 80); do
    r=$(wssh "type \"$WIN_DIR\\win_io.result\"" 2>/dev/null)
    if [ -n "$(printf '%s' "$r" | tr -d '[:space:]')" ]; then
      printf '%s' "$r" | _json1
      return 0
    fi
    sleep 0.25
  done
  echo '{"ok":false,"error":"timeout waiting for win_io.result"}'
  return 1
}

case "${1:-}" in
  deploy)
    scp -q -o BatchMode=yes "$PY_BASE/win/62c/win_io.py" \
        "$SL_WIN_SSH:$WIN_FWD/win_io.py"
    scp -q -o BatchMode=yes "$PY_BASE/win/62c/target_tk.py" \
        "$SL_WIN_SSH:$WIN_FWD/target_tk.py"
    scp -q -o BatchMode=yes "$PY_BASE/win/62c/launch_probe.ps1" \
        "$SL_WIN_SSH:$WIN_FWD/launch_probe.ps1"
    scp -q -o BatchMode=yes "$PY_BASE/win/62c/it_daemon.ps1" \
        "$SL_WIN_SSH:$WIN_FWD/it_daemon.ps1"
    echo "deployed win_io.py target_tk.py launch_probe.ps1 it_daemon.ps1 -> $WIN_FWD"
    ;;
  capture)
    NAME="frame-$(date +%Y%m%d-%H%M%S-%N).png"
    OUT="${2:-$SL_BLOB_ROOT/$NAME}"
    mkdir -p "$(dirname "$OUT")"
    res=$(  _req capture "{\"path\": \"$WIN_FWD/win_io_frame.png\"}" )
    if ! printf '%s' "$res" | grep -q '"ok": *true'; then
      echo "$res" >&2; exit 1
    fi
    scp -q -o BatchMode=yes "$SL_WIN_SSH:$WIN_FWD/win_io_frame.png" "$OUT" || exit 1
    [ -s "$OUT" ] || { echo "capture empty" >&2; exit 1; }
    printf '%s\n' "$OUT"
    ;;
  tap|click)
    X="$2"; Y="$3"
    res=$( _req tap "{\"x\": $X, \"y\": $Y}" )
    echo "tap ${X},${Y} :: $res"
    printf '%s' "$res" | grep -q '"ok": *true'
    ;;
  info)
    _req info "{}"
    ;;
  active-window)
    _req info "{}" | "$SL_PY" -c 'import json,sys;d=json.load(sys.stdin);print(json.dumps(d.get("active"),ensure_ascii=False))'
    ;;
  target-start)
    wssh "del \"$WIN_DIR\\target.marker\"" >/dev/null 2>&1
    wssh "powershell -NoProfile -ExecutionPolicy Bypass -File \"$WIN_DIR\\launch_probe.ps1\" -Script target_tk.py -Name screenlab-62c-target -Out target.out"
    ;;
  it-daemon)
    # Integration-test screen/1 daemon in the interactive session (loopback TCP
    # 19911, consent auto) so imgctx can drive the real product service over an
    # ssh tunnel without a human consent prompt.
    wssh "powershell -NoProfile -ExecutionPolicy Bypass -File \"$WIN_DIR\\it_daemon.ps1\" -Action ${2:-start}"
    ;;
  target-state)
    wssh "type \"$WIN_DIR\\target.marker\"" 2>/dev/null | _json1
    ;;
  cat)
    wssh "type \"$2\"" 2>/dev/null
    ;;
  rm)
    wssh "del \"$2\"" >/dev/null 2>&1
    ;;
  *)
    "$SL_PY" - "$0" <<'PY'
import sys
src = open(sys.argv[1], encoding="utf-8").read().splitlines()
print("\n".join(ln[1:].strip() for ln in src if ln.startswith("#") and not ln.startswith("#!")))
PY
    ;;
esac
