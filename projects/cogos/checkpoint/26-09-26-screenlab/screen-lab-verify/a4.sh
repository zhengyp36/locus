#!/bin/bash
set -u
export XDG_RUNTIME_DIR=/run/user/1001
export DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1001/bus
export WAYLAND_DISPLAY=screenlab-0
unset NO_AT_BRIDGE
export GTK_MODULES=gail:atk-bridge

FORCE="${FORCE:-0}"
ACT="${ACT:-1}"
BACKEND="${BACKEND:-x11}"

echo "### display probe"
export DISPLAY=""
export XAUTHORITY=""
for d in :1 :0 :2; do
  for f in $(ls -t /run/user/1001/.mutter-Xwaylandauth.* 2>/dev/null); do
    out=$(DISPLAY="$d" XAUTHORITY="$f" timeout 5 xdotool getdisplaygeometry 2>/dev/null)
    if echo "$out" | grep -qE '^[0-9]+ [0-9]+$'; then
      export DISPLAY="$d"
      export XAUTHORITY="$f"
      echo "X-OK display=$d auth=$(basename "$f") geom=$out"
      break 2
    fi
  done
done
echo "DISPLAY=${DISPLAY:-NONE} XAUTHORITY=${XAUTHORITY:-NONE}"
if [ "$BACKEND" = "x11" ] && [ -z "$DISPLAY" ]; then
  echo "no X -> fallback wayland"
  BACKEND=wayland
fi
echo "BACKEND=$BACKEND"

echo "### a11y enable"
systemctl --user start at-spi-dbus-bus.service >/dev/null 2>&1
gdbus call --session --dest org.a11y.Bus --object-path /org/a11y/bus \
  --method org.freedesktop.DBus.Properties.Set org.a11y.Status IsEnabled "<true>" >/dev/null 2>&1
gdbus call --session --dest org.a11y.Bus --object-path /org/a11y/bus \
  --method org.freedesktop.DBus.Properties.Set org.a11y.Status ScreenReaderEnabled "<true>" >/dev/null 2>&1
gsettings set org.gnome.desktop.interface toolkit-accessibility true 2>/dev/null
gdbus call --session --dest org.a11y.Bus --object-path /org/a11y/bus \
  --method org.freedesktop.DBus.Properties.GetAll org.a11y.Status 2>&1

echo "### server"
pkill -f "a4-serve.py" 2>/dev/null
sleep 1
rm -f /tmp/a4-hits.log
nohup python3 /tmp/a4-serve.py >/tmp/a4-serve.log 2>&1 &
sleep 1
curl -s -o /dev/null -w "server-http=%{http_code}\n" http://127.0.0.1:8765/

echo "### chrome (FORCE=$FORCE)"
pkill -f "user-data-dir=/tmp/a4-chrome" 2>/dev/null
sleep 2
rm -rf /tmp/a4-chrome
FLAGS="--no-sandbox --disable-gpu --disable-dev-shm-usage --no-first-run --no-default-browser-check --user-data-dir=/tmp/a4-chrome --window-size=1200,900"
[ "$FORCE" = "1" ] && FLAGS="$FLAGS --force-renderer-accessibility"
[ "$BACKEND" = "wayland" ] && FLAGS="$FLAGS --ozone-platform=wayland"
nohup google-chrome $FLAGS "http://127.0.0.1:8765/" >/tmp/a4-chrome.log 2>&1 &
sleep 14
echo "chrome procs: $(pgrep -c chrome)"
grep -iE "error|fail|crash" /tmp/a4-chrome.log | head -5

echo "### a11y scan"
if [ "$ACT" = "1" ]; then
  python3 /tmp/a4-atspi.py --act
else
  python3 /tmp/a4-atspi.py
fi
RC=$?
echo "a4-atspi rc=$RC"

echo "### hits"
if [ -s /tmp/a4-hits.log ]; then cat /tmp/a4-hits.log; else echo "(no hits)"; fi
echo "### shutdown chrome"
pkill -f "user-data-dir=/tmp/a4-chrome" 2>/dev/null
pkill -f "a4-serve.py" 2>/dev/null
echo "### DONE-A4"
