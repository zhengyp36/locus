#!/bin/bash
set -u
export XDG_RUNTIME_DIR=/run/user/1001
export DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1001/bus
export WAYLAND_DISPLAY=screenlab-0
unset NO_AT_BRIDGE
export GTK_MODULES=gail:atk-bridge

pkill -f "gtk-entry" 2>/dev/null
sleep 1
setsid python3 /tmp/gtk-entry.py client >/tmp/gtk-entry.log 2>&1 < /dev/null &
sleep 4
echo "### client log"; cat /tmp/gtk-entry.log
echo "### probe"
python3 /tmp/gtk-entry.py probe 2>&1 | grep -vi deprecat | grep -v "return f"
pkill -f "gtk-entry" 2>/dev/null
echo "### done"
