#!/bin/bash
set -u
export XDG_RUNTIME_DIR=/run/user/1001
export DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1001/bus
export WAYLAND_DISPLAY=screenlab-0
unset NO_AT_BRIDGE

for d in :2 :3 :1 :0; do
  for f in $(ls -t /run/user/1001/.mutter-Xwaylandauth.* 2>/dev/null); do
    out=$(DISPLAY=$d XAUTHORITY=$f timeout 4 xdotool getdisplaygeometry 2>/dev/null)
    if echo "$out" | grep -qE '^[0-9]+ [0-9]+$'; then
      export DISPLAY="$d"; export XAUTHORITY="$f"; break 2
    fi
  done
done
echo "X-OK display=${DISPLAY:-NONE} geom=$(DISPLAY=$DISPLAY XAUTHORITY=$XAUTHORITY xdotool getdisplaygeometry 2>/dev/null)"

systemctl --user start at-spi-dbus-bus.service >/dev/null 2>&1
gdbus call --session --dest org.a11y.Bus --object-path /org/a11y/bus \
  --method org.freedesktop.DBus.Properties.Set org.a11y.Status IsEnabled "<true>" >/dev/null 2>&1
gdbus call --session --dest org.a11y.Bus --object-path /org/a11y/bus \
  --method org.freedesktop.DBus.Properties.Set org.a11y.Status ScreenReaderEnabled "<true>" >/dev/null 2>&1
gsettings set org.gnome.desktop.interface toolkit-accessibility true 2>/dev/null

pkill -f "[e]4-serve.py" 2>/dev/null
sleep 1
rm -f /tmp/e4t-fp.log
nohup python3 /tmp/e4-serve.py >/tmp/e4t-serve.log 2>&1 &
sleep 1
curl -s -o /dev/null -w "server-http=%{http_code}\n" http://127.0.0.1:8766/e4-fp.html

run_cfg() {
  local C="$1"; shift
  local EXTRA="$*"
  echo "### CONFIG $C  flags=[$EXTRA]"
  pkill -f "user-data-dir=/tmp/e4-$C" 2>/dev/null
  sleep 1; rm -rf "/tmp/e4-$C"
  setsid google-chrome --no-sandbox --disable-dev-shm-usage --no-first-run \
    --no-default-browser-check --password-store=basic \
    --user-data-dir="/tmp/e4-$C" --window-size=1200,900 $EXTRA \
    "http://127.0.0.1:8766/e4-fp.html?c=$C" >"/tmp/e4-$C-app.log" 2>&1 < /dev/null &
  if [ "$C" = "C" ]; then
    ( timeout 20 python3 /tmp/e4-atspi.py >/tmp/e4-C-scan.log 2>&1 ) &
  fi
  for i in $(seq 1 30); do
    grep -q "	$C	" /tmp/e4t-fp.log 2>/dev/null && break
    sleep 1
  done
  sleep 1
  pkill -f "user-data-dir=/tmp/e4-$C" 2>/dev/null
  sleep 2
}

run_cfg A
run_cfg B --force-renderer-accessibility
run_cfg C --force-renderer-accessibility

echo "### raw log"
cat /tmp/e4t-fp.log
echo "### DONE-E4FP"
