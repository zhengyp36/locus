#!/bin/bash
set -u
export XDG_RUNTIME_DIR=/run/user/1001
export DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1001/bus
export WAYLAND_DISPLAY=screenlab-0
unset DISPLAY
unset NO_AT_BRIDGE

URL="${URL:-https://react.dev/}"
PROFILE="${PROFILE:-/tmp/a4real}"
LAZY="${LAZY:-0}"

systemctl --user start at-spi-dbus-bus.service >/dev/null 2>&1
for i in 1 2 3 4 5; do
  gdbus call --session --dest org.a11y.Bus --object-path /org/a11y/bus \
    --method org.freedesktop.DBus.Properties.Set org.a11y.Status IsEnabled "<true>" >/dev/null 2>&1 && break
  sleep 1
done
gdbus call --session --dest org.a11y.Bus --object-path /org/a11y/bus \
  --method org.freedesktop.DBus.Properties.Set org.a11y.Status ScreenReaderEnabled "<true>" >/dev/null 2>&1

pkill -x chrome 2>/dev/null
pkill -f "user-data-dir=/tmp/a4real" 2>/dev/null
sleep 2
rm -rf "$PROFILE"

FLAGS="--no-sandbox --disable-gpu --disable-dev-shm-usage --no-first-run
--no-default-browser-check --password-store=basic --ozone-platform=wayland
--user-data-dir=$PROFILE --window-size=1200,900"
if [ "$LAZY" != "1" ]; then
  FLAGS="$FLAGS --force-renderer-accessibility"
fi
echo "### URL=$URL LAZY=$LAZY"
setsid google-chrome $FLAGS "$URL" >/tmp/a4real-app.log 2>&1 < /dev/null &
sleep 18
echo "### app log"; tail -6 /tmp/a4real-app.log 2>&1
