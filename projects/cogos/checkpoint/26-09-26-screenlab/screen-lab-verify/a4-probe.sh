#!/bin/bash
set -u
export XDG_RUNTIME_DIR=/run/user/1001
export DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1001/bus
export WAYLAND_DISPLAY=screenlab-0
unset NO_AT_BRIDGE
export GTK_MODULES=gail:atk-bridge
export XAUTHORITY="$(ls -t /run/user/1001/.mutter-Xwaylandauth.* 2>/dev/null | head -1)"
export DISPLAY=":1"

systemctl --user start at-spi-dbus-bus.service >/dev/null 2>&1
gdbus call --session --dest org.a11y.Bus --object-path /org/a11y/bus \
  --method org.freedesktop.DBus.Properties.Set org.a11y.Status IsEnabled "<true>" >/dev/null 2>&1
gdbus call --session --dest org.a11y.Bus --object-path /org/a11y/bus \
  --method org.freedesktop.DBus.Properties.Set org.a11y.Status ScreenReaderEnabled "<true>" >/dev/null 2>&1

pkill -f "user-data-dir=/tmp/a4c2" 2>/dev/null
pkill -f "a4-serve.py" 2>/dev/null
sleep 2
rm -f /tmp/a4-hits.log /tmp/a4-requests.log
nohup python3 /tmp/a4-serve.py >/tmp/a4-serve.log 2>&1 &
sleep 1
rm -rf /tmp/a4c2

echo "### launch blank"
nohup google-chrome --no-sandbox --disable-gpu --disable-dev-shm-usage \
  --no-first-run --no-default-browser-check --force-renderer-accessibility \
  --enable-logging=stderr --v=1 --log-level=0 \
  --user-data-dir=/tmp/a4c2 --window-size=1200,900 about:blank \
  >/tmp/a4c2.log 2>&1 &
sleep 9
echo "### navigate"
DISPLAY=:1 google-chrome --user-data-dir=/tmp/a4c2 "http://127.0.0.1:8765/" >/dev/null 2>&1
sleep 6
echo "### requests"
cat /tmp/a4-requests.log 2>/dev/null || echo "(none)"
echo "### probe"
python3 /tmp/a4-probe.py
echo "### chrome log: accessibility lines"
grep -iE "accessib|axplatform|ax_platform|Getting a11y|AT-SPI|atspi" /tmp/a4c2.log | head -40
