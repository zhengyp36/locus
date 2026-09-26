set -u
export XDG_RUNTIME_DIR=/run/user/1001
export DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1001/bus
export WAYLAND_DISPLAY=screenlab-0
unset NO_AT_BRIDGE

echo "### start client"
systemctl --user start pipewire pipewire-pulse wireplumber 2>&1 | tail -2
printf "pipewire=%s\n" "$(systemctl --user is-active pipewire)"
ls -l /run/user/1001/pipewire-0 2>&1
python3 /tmp/e2-client.py --secs 60 > /tmp/a1-client.log 2>&1 &
CPID=$!
sleep 4
grep -E "monitor\[|toplevel" /tmp/a1-client.log | head -4

echo "### a11y target"
python3 /tmp/e4-atspi.py > /tmp/a1-atspi.log 2>&1
grep -E "FOUND|CENTER|NOT-FOUND" /tmp/a1-atspi.log

echo "### screencast frame"
python3 /tmp/p0-screencast.py 2>&1 | tail -25

echo "### frame info"
python3 - <<'PY'
import os
p = '/tmp/p0-frame.png'
if os.path.exists(p):
    from PIL import Image
    im = Image.open(p)
    print("frame", im.size, im.mode, os.path.getsize(p), "bytes")
else:
    print("NO-FRAME")
PY
kill "$CPID" 2>/dev/null
echo "### DONE-A1"
