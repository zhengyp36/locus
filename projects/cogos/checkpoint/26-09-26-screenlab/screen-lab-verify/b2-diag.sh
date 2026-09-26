#!/bin/bash
set -u
export XDG_RUNTIME_DIR=/run/user/1001
export DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1001/bus
source /tmp/screenlab-x11.sh

pgrep -f "[a]4-serve-t.py" >/dev/null || { nohup python3 /tmp/a4-serve-t.py >/tmp/a4t-serve.log 2>&1 & }
sleep 1
pkill -f "user-data-dir=/tmp/screenlab-chrome" 2>/dev/null
sleep 2
rm -rf /tmp/screenlab-chrome
setsid bash /tmp/screenlab-chrome.sh "http://127.0.0.1:8765/" >/tmp/b2-diag.log 2>&1 &
sleep 14

echo "=== alive chrome main procs ==="
for p in $(pgrep -f "user-data-dir=/tmp/screenlab-chrome"); do
  flags=$(tr '\0' ' ' < "/proc/$p/cmdline" | grep -o -- '--force-renderer-accessibility\|--ozone-platform=[a-z]*\|--disable-gpu' | tr '\n' ' ')
  echo "pid=$p flags=[$flags]"
done
echo "pid count=$(pgrep -cf 'user-data-dir=/tmp/screenlab-chrome')"

echo "=== requests tail ==="
tail -3 /tmp/a4t-requests.log

echo "=== a11y count ==="
python3 /tmp/a4-atspi.py 2>/dev/null | grep -E "ATTEMPT|SUMMARY|NO-A4"
echo "=== DONE-DIAG ==="
