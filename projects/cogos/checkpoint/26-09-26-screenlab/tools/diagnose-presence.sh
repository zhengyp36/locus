#!/usr/bin/env bash
# Isolate the presence (physical-vs-injected) monitor without needing consent.
# Stops the attach daemon so this can own `xinput test-xi2`, then restarts it.
#
#   tools/diagnose-presence.sh          # baseline XTEST vs suppression window
#   tools/diagnose-presence.sh --xi2    # also dump raw XI2 source ids for an injected click
set -uo pipefail
. "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/env.sh"

XI2=""
[ "${1:-}" = "--xi2" ] && XI2="1"

sl_root_script <<EOS
set +e
$(sl_remote_vars)
echo "== stop attach (free test-xi2) =="
run systemctl --user stop screenlab-attach.service
sleep 1

echo "== xtest_device_ids =="
run $SL_TARGET_PY -c "import sys;sys.path.insert(0,'/opt/screenlab');from screenlab.service.presence import xtest_device_ids;print(sorted(xtest_device_ids('$SL_DISPLAY','$SL_XAUTH')))"

echo "== isolation probe: raw monitor vs note_injection window =="
run $SL_TARGET_PY - <<'PY'
import subprocess, sys, time
sys.path.insert(0, "/opt/screenlab")
from screenlab.service.presence import PresenceMonitor

fired = []
m = PresenceMonitor("$SL_DISPLAY", "$SL_XAUTH", lambda: fired.append(time.time()))
m.start()
time.sleep(0.8)
print("injected ids =", sorted(m.injected or []), flush=True)

subprocess.run(["xdotool", "mousemove", "400", "400"])
subprocess.run(["xdotool", "click", "1"])
time.sleep(0.8)
print("baseline fires on XTEST click =", len(fired), flush=True)

fired.clear()
m.note_injection(window=0.5)
subprocess.run(["xdotool", "mousemove", "410", "410"])
subprocess.run(["xdotool", "click", "1"])
time.sleep(0.8)
print("suppressed fires in window   =", len(fired), flush=True)
m.stop()
PY

if [ -n "$XI2" ]; then
  echo "== XI2 source ids for an injected click/key =="
  ( run bash -c 'timeout 3 xinput test-xi2 --root > /tmp/sl-xi2.log 2>&1' ) &
  sleep 1
  run xdotool mousemove 420 420
  run xdotool click 1
  run xdotool key a
  sleep 1.5; wait
  grep -nE 'EVENT type|device:|detail:' /tmp/sl-xi2.log | head -60
fi

echo "== restart attach =="
run systemctl --user start screenlab-attach.service
sleep 1
echo -n "attach="; run systemctl --user is-active screenlab-attach.service
echo -n "8911="; ss -ltn 2>/dev/null | grep -c ":$SL_PORT "
EOS
