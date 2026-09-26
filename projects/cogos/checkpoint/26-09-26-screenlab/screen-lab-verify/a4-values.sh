#!/bin/bash
set -u
export XDG_RUNTIME_DIR=/run/user/1001
export DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1001/bus
export WAYLAND_DISPLAY=screenlab-0
unset DISPLAY
unset NO_AT_BRIDGE

URL="${URL:-http://127.0.0.1:8765/}"
PROFILE=/tmp/a4val
HITS=/tmp/a4t-hits.log
REQ=/tmp/a4t-requests.log

systemctl --user start at-spi-dbus-bus.service >/dev/null 2>&1
for i in 1 2 3 4 5; do
  gdbus call --session --dest org.a11y.Bus --object-path /org/a11y/bus \
    --method org.freedesktop.DBus.Properties.Set org.a11y.Status IsEnabled "<true>" >/dev/null 2>&1 && break
  sleep 1
done

pkill -x chrome 2>/dev/null
pkill -f a4-serve 2>/dev/null
sleep 2
rm -f "$HITS" "$REQ"
cd /tmp
nohup python3 /tmp/a4-serve-t.py >/tmp/a4t-serve.log 2>&1 &
sleep 2
echo "### server check"
curl -s -o /dev/null -w "GET / -> %{http_code}\n" --max-time 5 http://127.0.0.1:8765/
curl -s -o /dev/null -w "GET /hit -> %{http_code}\n" --max-time 5 "http://127.0.0.1:8765/hit?c=PROBE"
echo "### serve log"; tail -3 /tmp/a4t-serve.log
rm -rf "$PROFILE"

setsid google-chrome --no-sandbox --disable-gpu --disable-dev-shm-usage \
  --no-first-run --no-default-browser-check --password-store=basic \
  --force-renderer-accessibility --ozone-platform=wayland \
  --user-data-dir="$PROFILE" --window-size=1200,900 "$URL" \
  >/tmp/a4val-app.log 2>&1 < /dev/null &
sleep 12
echo "### requests"; cat "$REQ" 2>/dev/null || echo "(none)"
echo "### values experiment"
python3 /tmp/a4-values.py
sleep 2
echo "### hits (new)"; cat "$HITS" 2>/dev/null || echo "(none)"
echo "### app log"; tail -3 /tmp/a4val-app.log
