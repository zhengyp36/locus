#!/usr/bin/env bash
# Mechanical Android backend for the screenlab visual loop (Slice 2).
#
# Pure device I/O over adb: full-screen capture, InjectService gesture injection
# (the app's own dispatchGesture path), foreground readback, and a UI-bounds
# helper for ground truth. No semantics, no consent handshake.
#
#   tools/android.sh status            # adb / package / a11y / service-port facts
#   tools/android.sh connect           # (re)attach wifi adb, print devices
#   tools/android.sh capture [PNG]     # full-screen PNG -> unique blobs/ path
#   tools/android.sh geometry          # "W H" physical size
#   tools/android.sh tap X Y           # InjectService tap (device px, float)
#   tools/android.sh key KEYCODE       # adb keyevent (cleanup / navigation)
#   tools/android.sh foreground        # current resumed activity (package/act)
#   tools/android.sh ui-bounds TEXT    # bounds of first node whose text/desc contains TEXT
#   tools/android.sh consent-auto      # dev: allow screen/1 auth without a human
set -uo pipefail
. "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/env.sh"

DEV="${SL_ANDROID_DEV}"
PKG="${SL_ANDROID_PKG}"
A11Y="${SL_ANDROID_A11Y}"
RECV="${SL_ANDROID_CMD}"
CMD_ACTION="com.screenlab.assist.CMD"
PY="${SL_PY:-/usr/bin/python3.11}"

a() { adb -s "$DEV" "$@"; }

case "${1:-}" in
  status)
    echo -n "adb="; adb get-state 2>/dev/null || echo offline
    echo -n "serial="; echo "$DEV"
    echo -n "versionName="; a shell "dumpsys package $PKG | grep -m1 versionName" 2>/dev/null | tr -d '\r'
    echo -n "process="; a shell "pidof $PKG" 2>/dev/null | tr -d '\r'; echo
    echo -n "a11y="; a shell "settings get secure enabled_accessibility_services" 2>/dev/null | tr -d '\r' | tr ':' ' '
    echo " "
    echo -n "listen="; a shell "ss -ltn 2>/dev/null | grep -c :${SL_ANDROID_SVC_PORT}" 2>/dev/null | tr -d '\r'
    ;;
  connect)
    adb connect "$DEV" 2>&1 | tail -1
    adb devices -l
    ;;
  capture)
    NAME="frame-$(date +%Y%m%d-%H%M%S-%N).png"
    OUT="${2:-$SL_BLOB_ROOT/$NAME}"
    mkdir -p "$(dirname "$OUT")"
    a exec-out screencap -p > "$OUT"
    [ -s "$OUT" ] || { echo "capture failed" >&2; exit 1; }
    printf '%s\n' "$OUT"
    ;;
  geometry)
    a shell wm size | sed -n 's/Physical size: //p' | tr -d '\r'
    ;;
  tap)
    X="$2"; Y="$3"
    a shell am broadcast -n "$RECV" -a "$CMD_ACTION" \
      --es op tap --ef x "$X" --ef y "$Y" >/dev/null 2>&1
    sleep 0.8
    echo "tap ${X},${Y}"
    ;;
  key)
    a shell input keyevent "$2" >/dev/null 2>&1
    echo "key $2"
    ;;
  foreground)
    a shell "dumpsys activity activities | grep -E 'mResumedActivity' | head -1" 2>/dev/null \
      | tr -d '\r' | grep -oE '[A-Za-z0-9._]+/[A-Za-z0-9._$]+' | head -1
    ;;
  ui-bounds)
    TXT="$2"
    a shell "uiautomator dump /sdcard/sl-wd.xml >/dev/null 2>&1"
    a exec-out cat /sdcard/sl-wd.xml 2>/dev/null | "$PY" -c '
import sys, re
xml = sys.stdin.read()
want = sys.argv[1]
for seg in re.findall(r"<node[^>]*>", xml):
    t = re.search(r"text=\"([^\"]*)\"", seg)
    d = re.search(r"content-desc=\"([^\"]*)\"", seg)
    label = (t.group(1) if t else "") or (d.group(1) if d else "")
    if want in label:
        b = re.search(r"bounds=\"\[(\d+),(\d+)\]\[(\d+),(\d+)\]\"", seg)
        if b:
            x1, y1, x2, y2 = map(int, b.groups())
            print(label + "\t" + str((x1 + x2) // 2) + "," + str((y1 + y2) // 2)
                  + "\t" + str(x1) + "," + str(y1) + "," + str(x2) + "," + str(y2))
            break
' "$TXT"
    ;;
  consent-auto)
    a shell am broadcast -n "$RECV" -a "$CMD_ACTION" --es op consent --es mode auto >/dev/null 2>&1
    echo "consent auto on"
    ;;
  *)
    sed -n '2,18p' "$0"
    ;;
esac
