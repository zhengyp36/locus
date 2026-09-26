#!/bin/bash
set -u
export XDG_RUNTIME_DIR=/run/user/1001
export DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1001/bus

echo "=== before ==="
pgrep -a -u tangyu -x chrome | head -2
pgrep -a -u tangyu -f "[a]4-serve" | head -2
pgrep -a -u tangyu -f "[g]tk-entry" | head -2
echo "shell=$(systemctl --user is-active screenlab-shell 2>/dev/null)"

pkill -x chrome 2>/dev/null
pkill -f "[a]4-serve" 2>/dev/null
pkill -f "[g]tk-entry" 2>/dev/null
sleep 2

echo "=== after ==="
pgrep -a -u tangyu -x chrome | head -2 || true
pgrep -a -u tangyu -f "[a]4-serve" | head -2 || true
pgrep -a -u tangyu -f "[g]tk-entry" | head -2 || true
echo "shell=$(systemctl --user is-active screenlab-shell 2>/dev/null)"
echo "=== done ==="
