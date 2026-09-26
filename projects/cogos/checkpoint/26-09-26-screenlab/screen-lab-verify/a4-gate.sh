#!/bin/bash
set -u
export XDG_RUNTIME_DIR=/run/user/1001
export DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1001/bus

pkill -f "a4-serve.py" 2>/dev/null
pkill -u tangyu -x chrome 2>/dev/null
sleep 2
rm -f /tmp/a4-requests.log /tmp/a4-accepts.log
setsid python3 /tmp/a4-serve.py >/tmp/a4-serve.log 2>&1 </dev/null &
SRV=$!
sleep 1

echo "=== A: MAP * ~NOTFOUND, loopback ==="
rm -rf /tmp/a4hR
timeout 40 google-chrome --headless=new --no-sandbox --disable-gpu --user-data-dir=/tmp/a4hR \
  --host-resolver-rules="MAP * ~NOTFOUND" --dump-dom "http://127.0.0.1:8765/" \
  >/tmp/a4hR.out 2>/dev/null
echo "rc=$? bytes=$(wc -c </tmp/a4hR.out)"
echo "accepts=$(wc -l </tmp/a4-accepts.log 2>/dev/null) requests=$(wc -l </tmp/a4-requests.log 2>/dev/null)"

echo "=== B: long timeout plain loopback (75s) ==="
rm -f /tmp/a4-requests.log
rm -rf /tmp/a4hR2
timeout 75 google-chrome --headless=new --no-sandbox --disable-gpu --user-data-dir=/tmp/a4hR2 \
  --dump-dom "http://127.0.0.1:8765/" >/tmp/a4hR2.out 2>/dev/null
echo "rc=$? bytes=$(wc -c </tmp/a4hR2.out)"
echo "requests=$(wc -l </tmp/a4-requests.log 2>/dev/null)"

kill $SRV 2>/dev/null
pkill -f "user-data-dir=/tmp/a4hR" 2>/dev/null
echo "### DONE-GATE"
