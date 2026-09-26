#!/bin/bash
set -u
export XDG_RUNTIME_DIR=/run/user/1001
export DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1001/bus

pkill -f "a4-serve.py" 2>/dev/null
pkill -u tangyu -x chrome 2>/dev/null
sleep 2
rm -f /tmp/a4-requests.log /tmp/a4-accepts.log
python3 /tmp/a4-serve.py >/tmp/a4-serve.log 2>&1 &
SRV=$!
sleep 1

t() {
  local label="$1"; local url="$2"; shift 2
  rm -rf /tmp/a4hT
  local out
  out=$(timeout 30 google-chrome --headless=new --no-sandbox --disable-gpu \
    --user-data-dir=/tmp/a4hT "$@" --dump-dom "$url" 2>/tmp/a4hT.err)
  local rc=$?
  echo "### $label rc=$rc bytes=${#out}"
  echo "$out" | head -c 160 | tr '\n' ' '; echo
}

t "loopback"        "http://127.0.0.1:8765/"
echo "  accepts=$(wc -l </tmp/a4-accepts.log 2>/dev/null) requests=$(wc -l </tmp/a4-requests.log 2>/dev/null)"

t "external http"   "http://example.com/"
t "external https"  "https://example.com/"

t "loopback +noSB"  "http://127.0.0.1:8765/" \
  --disable-background-networking --disable-client-side-phishing-detection \
  --safebrowsing-disable-auto-update --disable-component-update --disable-sync \
  --no-pings --disable-domain-reliability

t "external +noSB"  "https://example.com/" \
  --disable-background-networking --disable-client-side-phishing-detection \
  --safebrowsing-disable-auto-update --disable-component-update --disable-sync \
  --no-pings --disable-domain-reliability

echo "### total accepts=$(wc -l </tmp/a4-accepts.log 2>/dev/null) requests=$(wc -l </tmp/a4-requests.log 2>/dev/null)"
kill $SRV 2>/dev/null
pkill -f "user-data-dir=/tmp/a4hT" 2>/dev/null
echo "### DONE-CLASSIFY"
