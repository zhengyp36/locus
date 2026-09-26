#!/usr/bin/env bash
# Drive one probe measurement: start probe (auto-accept MediaProjection),
# idle window, then a load window, and collect stats.
# Usage: probe-run.sh <tag> <w> <h> <cell> <thresh> <idle_s> <load_s> [install]
set -euo pipefail
D=192.168.1.175:5555
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PY=/usr/bin/python3.11
TAG="$1"; W="$2"; H="$3"; CELL="$4"; THRESH="$5"; IDLE="$6"; LOAD="$7"; INSTALL="${8:-}"

tap_text() {
  local tries="${1:-25}"; shift
  for _ in $(seq 1 "$tries"); do
    adb -s $D shell uiautomator dump /sdcard/wd.xml >/dev/null 2>&1 || true
    local xml; xml="$(adb -s $D exec-out cat /sdcard/wd.xml 2>/dev/null || true)"
    local t
    for t in "$@"; do
      local xy
      xy="$(printf '%s' "$xml" | $PY -c "
import sys,re
xml=sys.stdin.read()
for m in re.finditer(r'text=\"([^\"]*)\"[^>]*bounds=\"\[(\d+),(\d+)\]\[(\d+),(\d+)\]\"',xml):
    if '''$t''' in m.group(1):
        print((int(m.group(2))+int(m.group(4)))//2,(int(m.group(3))+int(m.group(5)))//2); break
")"
      if [ -n "$xy" ]; then
        adb -s $D shell input tap $xy
        echo "tap '$t' -> $xy"
        return 0
      fi
    done
    sleep 0.5
  done
  echo "WARN: no tap target among: $*" >&2
  return 1
}

if [ -n "$INSTALL" ]; then
  echo "[install] $HERE/probe.apk"
  adb -s $D install -r "$HERE/probe.apk" >/tmp/kilo/probe-install.log 2>&1 &
  IPID=$!
  tap_text 8 "继续安装" "继续" "安装" "Install" || true
  wait $IPID || true
  tail -2 /tmp/kilo/probe-install.log
fi

adb -s $D shell am broadcast -n com.screenlab.probe/.ProbeCmdReceiver -a com.screenlab.probe.CMD --es op stop >/dev/null 2>&1 || true
adb -s $D shell am force-stop com.screenlab.probe || true
adb -s $D shell rm -f "/sdcard/Android/data/com.screenlab.probe/files/probe-stats.txt" \
    "/sdcard/Android/data/com.screenlab.probe/files/a11y-stats.txt" || true

# ensure probe a11y still enabled alongside product app
adb -s $D shell settings put secure enabled_accessibility_services \
  com.screenlab.assist/.InjectService:com.screenlab.probe/.ProbeA11yService

echo "[start] probe ${W}x${H} cell=$CELL thresh=$THRESH"
adb -s $D shell logcat -c || true
adb -s $D shell am start -n com.screenlab.probe/.ProbeActivity \
  --ei w "$W" --ei h "$H" --ei cell "$CELL" --ei thresh "$THRESH"
tap_text 30 "立即开始" "开始" "Start now" "Start" "允许" "Allow" || true

echo "[idle] ${IDLE}s (screen left static)"
sleep "$IDLE"
adb -s $D shell am broadcast -n com.screenlab.probe/.ProbeCmdReceiver -a com.screenlab.probe.CMD --es op dump >/dev/null 2>&1 || true
$PY "$HERE/drive.py" collect --tag "${TAG}-idle" | tail -3

echo "[load] ${LOAD}s (scroll settings list)"
adb -s $D shell am broadcast -n com.screenlab.probe/.ProbeCmdReceiver -a com.screenlab.probe.CMD --es op reset >/dev/null 2>&1 || true
adb -s $D shell am start -a android.settings.SETTINGS >/dev/null 2>&1 || true
sleep 1
END=$(( $(date +%s) + LOAD ))
while [ "$(date +%s)" -lt "$END" ]; do
  adb -s $D shell input swipe 540 1800 540 700 250 >/dev/null 2>&1 || true
  sleep 0.2
done
sleep 1
$PY "$HERE/drive.py" collect --tag "${TAG}-load" | tail -3

echo "[stop]"
adb -s $D shell am broadcast -n com.screenlab.probe/.ProbeCmdReceiver -a com.screenlab.probe.CMD --es op a11ydump >/dev/null 2>&1 || true
adb -s $D shell am broadcast -n com.screenlab.probe/.ProbeCmdReceiver -a com.screenlab.probe.CMD --es op stop >/dev/null 2>&1 || true
sleep 1
adb -s $D shell pidof com.screenlab.probe || echo "(process gone)"
