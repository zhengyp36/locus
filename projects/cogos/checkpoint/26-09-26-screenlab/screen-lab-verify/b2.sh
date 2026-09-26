#!/bin/bash
set -u
export XDG_RUNTIME_DIR=/run/user/1001
export DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1001/bus
export WAYLAND_DISPLAY=screenlab-0

echo "### probe via B2 helper"
source /tmp/screenlab-x11.sh
echo "probe rc=$? DISPLAY=${DISPLAY:-NONE}"

systemctl --user start at-spi-dbus-bus.service >/dev/null 2>&1
gdbus call --session --dest org.a11y.Bus --object-path /org/a11y/bus \
  --method org.freedesktop.DBus.Properties.Set org.a11y.Status IsEnabled "<true>" >/dev/null 2>&1
gdbus call --session --dest org.a11y.Bus --object-path /org/a11y/bus \
  --method org.freedesktop.DBus.Properties.Set org.a11y.Status ScreenReaderEnabled "<true>" >/dev/null 2>&1

pkill -f "[a]4-serve-t.py" 2>/dev/null
sleep 1
rm -f /tmp/a4t-hits.log
nohup python3 /tmp/a4-serve-t.py >/tmp/a4t-serve.log 2>&1 &
sleep 1
curl -s -o /dev/null -w "server-http=%{http_code}\n" http://127.0.0.1:8765/

echo "### install launcher to ~/screenlab"
mkdir -p "$HOME/screenlab"
cp /tmp/screenlab-x11.sh /tmp/screenlab-chrome.sh "$HOME/screenlab/"
chmod +x "$HOME/screenlab/screenlab-x11.sh" "$HOME/screenlab/screenlab-chrome.sh"

echo "### launch via B2 launcher"
pkill -f "user-data-dir=/tmp/screenlab-chrome" 2>/dev/null
sleep 2
rm -rf /tmp/screenlab-chrome
setsid bash "$HOME/screenlab/screenlab-chrome.sh" "http://127.0.0.1:8765/" >/tmp/b2-chrome.log 2>&1 < /dev/null &
sleep 12
echo "chrome=$(pgrep -c chrome)"
echo "launcher log:"; head -3 /tmp/b2-chrome.log

echo "### a11y + doAction"
python3 /tmp/a4-atspi.py --act 2>/dev/null | tail -24
echo "### hits"
if [ -s /tmp/a4t-hits.log ]; then tail -6 /tmp/a4t-hits.log; else echo "(no hits)"; fi
echo "### DONE-B2"
pkill -f "user-data-dir=/tmp/screenlab-chrome" 2>/dev/null
pkill -f "[a]4-serve-t.py" 2>/dev/null
