#!/bin/bash
set -u
export XDG_RUNTIME_DIR=/run/user/1001
export DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1001/bus

pkill -f "a4-serve.py" 2>/dev/null
pkill -u tangyu -x chrome 2>/dev/null
sleep 2
rm -f /tmp/a4-requests.log /tmp/a4-accepts.log /tmp/ch.strace
python3 /tmp/a4-serve.py >/tmp/a4-serve.log 2>&1 &
SRV=$!
sleep 1

rm -rf /tmp/a4hS
timeout 25 strace -f -tt -e trace=connect,sendto,sendmsg,recvfrom,recvmsg,accept,accept4 \
  -o /tmp/ch.strace \
  google-chrome --headless=new --no-sandbox --disable-gpu \
  --user-data-dir=/tmp/a4hS --dump-dom "http://127.0.0.1:8765/" \
  >/tmp/a4hS.out 2>/tmp/a4hS.err
echo "chrome rc=$?"

echo "### strace lines mentioning 8765 or the port"
grep -n "8765" /tmp/ch.strace | head -20
echo "### direct network syscalls (first 40)"
grep -nE "sendto|sendmsg|recvfrom|recvmsg" /tmp/ch.strace | head -40
echo "### accepts / requests"
cat /tmp/a4-accepts.log 2>/dev/null | tail -5 || echo "(no accepts)"
cat /tmp/a4-requests.log 2>/dev/null | tail -5 || echo "(no requests)"
kill $SRV 2>/dev/null
pkill -f "user-data-dir=/tmp/a4hS" 2>/dev/null
echo "### DONE-STRACE"
