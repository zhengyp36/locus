#!/bin/bash
set -u
export XDG_RUNTIME_DIR=/run/user/1001
export DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1001/bus

pkill -f "user-data-dir=/tmp/a4h" 2>/dev/null
sleep 1
rm -f /tmp/a4-requests.log /tmp/netlog.json
rm -rf /tmp/a4hA

timeout 30 google-chrome --headless=new --no-sandbox --disable-gpu \
  --log-net-log=/tmp/netlog.json --net-log-capture-mode=IncludeSensitive \
  --user-data-dir=/tmp/a4hA --dump-dom "http://127.0.0.1:8765/" \
  >/tmp/a4hA.out 2>/tmp/a4hA.err

echo "### OUT (head)"; head -3 /tmp/a4hA.out
echo "### ERR (tail)"; tail -8 /tmp/a4hA.err
echo "### requests"; cat /tmp/a4-requests.log 2>/dev/null || echo "(none)"
echo "### netlog size"; wc -c /tmp/netlog.json 2>/dev/null
echo "### ERR_ codes in netlog"
grep -oE 'ERR_[A-Z_]+' /tmp/netlog.json 2>/dev/null | sort | uniq -c | sort -rn | head -15
pkill -f "user-data-dir=/tmp/a4hA" 2>/dev/null
echo "### DONE-NET"
