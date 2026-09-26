#!/bin/bash
set -u
export XDG_RUNTIME_DIR=/run/user/1001
export DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1001/bus

pkill -f "a4-serve.py" 2>/dev/null
pkill -u tangyu -x chrome 2>/dev/null
sleep 2

echo "### enforce: $(getenforce 2>&1)"
echo "### chrome binary context: $(ls -Z /opt/google/chrome/chrome 2>&1 | awk '{print $1}')"
echo "### user context: $(id -Z 2>&1)"

rm -f /tmp/a4-requests.log
python3 /tmp/a4-serve.py >/tmp/a4-serve.log 2>&1 &
SRV=$!
sleep 1

test_url() {
  local label="$1"; shift
  echo "### $label"
  rm -rf /tmp/a4hM
  timeout 25 google-chrome --headless=new --no-sandbox --disable-gpu \
    --user-data-dir=/tmp/a4hM "$@" >/tmp/a4hM.out 2>/tmp/a4hM.err
  echo "rc=$? out=$(wc -c </tmp/a4hM.out)"
}

test_url "A: single-process" --single-process --dump-dom "http://127.0.0.1:8765/"
echo "req:"; wc -l </tmp/a4-requests.log 2>/dev/null || echo 0

test_url "B: no-zygote" --no-zygote --dump-dom "http://127.0.0.1:8765/"
echo "req:"; wc -l </tmp/a4-requests.log 2>/dev/null || echo 0

test_url "C: proxy direct" --proxy-server="direct://" --proxy-bypass-list="*" --dump-dom "http://127.0.0.1:8765/"
echo "req:"; wc -l </tmp/a4-requests.log 2>/dev/null || echo 0

test_url "D: external example.com" --dump-dom "http://example.com/"
echo "req:"; wc -l </tmp/a4-requests.log 2>/dev/null || echo 0

echo "### requests total"; wc -l </tmp/a4-requests.log 2>/dev/null || echo 0
kill $SRV 2>/dev/null
pkill -f "user-data-dir=/tmp/a4hM" 2>/dev/null
echo "### DONE-MATRIX"
