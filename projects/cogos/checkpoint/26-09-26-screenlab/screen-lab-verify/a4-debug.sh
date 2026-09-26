#!/bin/bash
set -u

if [ "${1:-}" = "stop" ]; then
  echo "### stopping"
  pkill -f "user-data-dir=/tmp/a4-chrome" 2>/dev/null
  pkill -f "a4-serve.py" 2>/dev/null
  echo "stopped"
  exit 0
fi

export XDG_RUNTIME_DIR=/run/user/1001
export DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1001/bus
export WAYLAND_DISPLAY=screenlab-0
unset NO_AT_BRIDGE
export GTK_MODULES=gail:atk-bridge

export DISPLAY=""
export XAUTHORITY=""
for d in :1 :0 :2; do
  for f in $(ls -t /run/user/1001/.mutter-Xwaylandauth.* 2>/dev/null); do
    out=$(DISPLAY="$d" XAUTHORITY="$f" timeout 5 xdotool getdisplaygeometry 2>/dev/null)
    if echo "$out" | grep -qE '^[0-9]+ [0-9]+$'; then
      export DISPLAY="$d"
      export XAUTHORITY="$f"
      break 2
    fi
  done
done
echo "DISPLAY=$DISPLAY XAUTHORITY=$XAUTHORITY"

systemctl --user start at-spi-dbus-bus.service >/dev/null 2>&1
gdbus call --session --dest org.a11y.Bus --object-path /org/a11y/bus \
  --method org.freedesktop.DBus.Properties.Set org.a11y.Status IsEnabled "<true>" >/dev/null 2>&1
gdbus call --session --dest org.a11y.Bus --object-path /org/a11y/bus \
  --method org.freedesktop.DBus.Properties.Set org.a11y.Status ScreenReaderEnabled "<true>" >/dev/null 2>&1
gsettings set org.gnome.desktop.interface toolkit-accessibility true 2>/dev/null

pkill -f "user-data-dir=/tmp/a4-chrome" 2>/dev/null
pkill -f "a4-serve.py" 2>/dev/null
sleep 2
rm -f /tmp/a4-hits.log /tmp/a4-requests.log
nohup python3 /tmp/a4-serve.py >/tmp/a4-serve.log 2>&1 &
sleep 1
rm -rf /tmp/a4-chrome
FLAGS="--no-sandbox --disable-gpu --disable-dev-shm-usage --no-first-run --no-default-browser-check --user-data-dir=/tmp/a4-chrome --window-size=1200,900"
[ "${FORCE:-1}" = "1" ] && FLAGS="$FLAGS --force-renderer-accessibility"
echo "LAUNCH: google-chrome $FLAGS http://127.0.0.1:8765/"
nohup google-chrome $FLAGS "http://127.0.0.1:8765/" >/tmp/a4-chrome.log 2>&1 &
sleep 12
echo "### requests so far"
cat /tmp/a4-requests.log 2>/dev/null || echo "(none)"
echo "READY"
