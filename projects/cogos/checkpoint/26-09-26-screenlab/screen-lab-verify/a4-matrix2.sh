#!/bin/bash
set -u
export XDG_RUNTIME_DIR=/run/user/1001
export DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1001/bus

pkill -f "a4-serve.py" 2>/dev/null
pkill -u tangyu -x chrome 2>/dev/null
sleep 2

echo "### enforce: $(getenforce 2>&1)"
rm -f /tmp/a4-requests.log /tmp/a4-accepts.log
python3 /tmp/a4-serve.py >/tmp/a4-serve.log 2>&1 &
SRV=$!
sleep 1

echo "### curl"
curl -s -o /dev/null -w "curl=%{http_code}\n" http://127.0.0.1:8765/
sleep 1
echo "accepts:"; cat /tmp/a4-accepts.log 2>/dev/null || echo "(none)"
echo "requests:"; cat /tmp/a4-requests.log 2>/dev/null || echo "(none)"

run() {
  echo "### $1"
  rm -rf /tmp/a4hM
  timeout 25 google-chrome --headless=new --no-sandbox --disable-gpu \
    --user-data-dir=/tmp/a4hM "${@:2}" >/tmp/a4hM.out 2>/tmp/a4hM.err
  echo "rc=$? out=$(wc -c </tmp/a4hM.out)"
}

run "single-process" --single-process --dump-dom "http://127.0.0.1:8765/"
echo "accepts:"; cat /tmp/a4-accepts.log 2>/dev/null | tail -3
echo "requests:"; cat /tmp/a4-requests.log 2>/dev/null | tail -3

run "plain" --dump-dom "http://127.0.0.1:8765/"
echo "accepts:"; cat /tmp/a4-accepts.log 2>/dev/null | tail -3
echo "requests:"; cat /tmp/a4-requests.log 2>/dev/null | tail -3

run "external" --dump-dom "http://example.com/"
echo "accepts:"; cat /tmp/a4-accepts.log 2>/dev/null | tail -3

kill $SRV 2>/dev/null
pkill -f "user-data-dir=/tmp/a4hM" 2>/dev/null
echo "### DONE-MATRIX2"
