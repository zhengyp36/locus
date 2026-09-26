#!/bin/bash
set -u
export XDG_RUNTIME_DIR=/run/user/1001
export DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1001/bus
export WAYLAND_DISPLAY=screenlab-0
unset NO_AT_BRIDGE

# --- probe X (Xwayland) ---
for d in :2 :3 :1 :0; do
  for f in $(ls -t /run/user/1001/.mutter-Xwaylandauth.* 2>/dev/null); do
    out=$(DISPLAY=$d XAUTHORITY=$f timeout 4 xdotool getdisplaygeometry 2>/dev/null)
    if echo "$out" | grep -qE '^[0-9]+ [0-9]+$'; then
      export DISPLAY="$d"; export XAUTHORITY="$f"
      echo "X-OK display=$d auth=$(basename "$f") geom=$out"
      break 2
    fi
  done
done
echo "DISPLAY=${DISPLAY:-NONE} XAUTHORITY=${XAUTHORITY:-NONE}"

# --- a11y enable ---
systemctl --user start at-spi-dbus-bus.service >/dev/null 2>&1
gdbus call --session --dest org.a11y.Bus --object-path /org/a11y/bus \
  --method org.freedesktop.DBus.Properties.Set org.a11y.Status IsEnabled "<true>" >/dev/null 2>&1
gdbus call --session --dest org.a11y.Bus --object-path /org/a11y/bus \
  --method org.freedesktop.DBus.Properties.Set org.a11y.Status ScreenReaderEnabled "<true>" >/dev/null 2>&1
gsettings set org.gnome.desktop.interface toolkit-accessibility true 2>/dev/null

# --- server ---
pkill -f "a4-serve-t.py" 2>/dev/null
sleep 1
rm -f /tmp/a4t-hits.log /tmp/a4t-requests.log
nohup python3 /tmp/a4-serve-t.py >/tmp/a4t-serve.log 2>&1 &
sleep 1
curl -s -o /dev/null -w "server-http=%{http_code}\n" http://127.0.0.1:8765/

# --- chrome as X11 client (NO --ozone-platform=wayland) ---
pkill -f "user-data-dir=/tmp/a4-x11" 2>/dev/null
sleep 2
rm -rf /tmp/a4-x11
FLAGS="--no-sandbox --disable-gpu --disable-dev-shm-usage --no-first-run
--no-default-browser-check --password-store=basic --force-renderer-accessibility
--user-data-dir=/tmp/a4-x11 --window-size=1200,900"
setsid google-chrome $FLAGS "http://127.0.0.1:8765/" >/tmp/a4-x11-app.log 2>&1 < /dev/null &
sleep 12
echo "chrome procs: $(pgrep -c chrome)"
echo "--- app log (errors) ---"
grep -iE "error|fail|Missing X|ozone|wayland" /tmp/a4-x11-app.log | head -10

# --- X11 window geometry ---
echo "### window"
WID=""
for want in "A4 Ground Truth" "A4"; do
  WID=$(DISPLAY="$DISPLAY" XAUTHORITY="$XAUTHORITY" xdotool search --name "$want" 2>/dev/null | head -1)
  [ -n "$WID" ] && break
done
echo "WID=$WID"
if [ -n "$WID" ]; then
  DISPLAY="$DISPLAY" XAUTHORITY="$XAUTHORITY" xdotool getwindowgeometry "$WID"
  echo "### extents BEFORE move"
  python3 /tmp/a4-extents.py
  echo "### move window +300+200"
  DISPLAY="$DISPLAY" XAUTHORITY="$XAUTHORITY" xdotool windowmove "$WID" 300 200
  sleep 1
  DISPLAY="$DISPLAY" XAUTHORITY="$XAUTHORITY" xdotool getwindowgeometry "$WID"
  echo "### extents AFTER move"
  python3 /tmp/a4-extents.py
fi

echo "### doAction scan"
python3 /tmp/a4-atspi.py --act
echo "### hits"
if [ -s /tmp/a4t-hits.log ]; then cat /tmp/a4t-hits.log; else echo "(no hits)"; fi
echo "### DONE-X11"
