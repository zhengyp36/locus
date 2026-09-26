#!/bin/bash
set -u
export XDG_RUNTIME_DIR=/run/user/1001
export DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1001/bus
export WAYLAND_DISPLAY=screenlab-0
export XAUTHORITY="$(ls -t /run/user/1001/.mutter-Xwaylandauth.* 2>/dev/null | head -1)"
export DISPLAY=":1"
unset NO_AT_BRIDGE

pkill -f "a4-serve.py" 2>/dev/null
pkill -u tangyu -x chrome 2>/dev/null
sleep 2
rm -f /tmp/a4-requests.log /tmp/a4-hits.log
python3 /tmp/a4-serve.py >/tmp/a4-serve.log 2>&1 &
SRV=$!
sleep 1
echo "server pid=$SRV alive=$(kill -0 $SRV 2>/dev/null && echo yes || echo no)"

echo "### curl self-test"
curl -s -o /dev/null -w "curl=%{http_code}\n" http://127.0.0.1:8765/
sleep 1
echo "requests after curl:"; cat /tmp/a4-requests.log 2>/dev/null || echo "(none)"

echo "### chrome headless dump-dom"
rm -rf /tmp/a4hC
timeout 30 google-chrome --headless=new --no-sandbox --disable-gpu \
  --user-data-dir=/tmp/a4hC --dump-dom "http://127.0.0.1:8765/" \
  >/tmp/a4hC.out 2>/tmp/a4hC.err
echo "dump rc=$? out_bytes=$(wc -c </tmp/a4hC.out)"
echo "requests after chrome:"; cat /tmp/a4-requests.log 2>/dev/null || echo "(none)"
echo "dom head:"; head -c 150 /tmp/a4hC.out; echo

kill $SRV 2>/dev/null
pkill -f "user-data-dir=/tmp/a4hC" 2>/dev/null
echo "### DONE-ONE"
