#!/bin/bash
set -u
export XDG_RUNTIME_DIR=/run/user/1001
export DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1001/bus
export WAYLAND_DISPLAY=screenlab-0
unset NO_AT_BRIDGE

echo "### shell: $(systemctl --user is-active screenlab-shell)"
pkill -x chrome 2>/dev/null
pkill -f screencast-mon 2>/dev/null
sleep 1

systemctl --user start pipewire wireplumber >/dev/null 2>&1
sleep 2
echo "### pipewire=$(systemctl --user is-active pipewire) wireplumber=$(systemctl --user is-active wireplumber)"

echo "### hold screencast session"
python3 /tmp/screencast-mon.py 50 > /tmp/a2-hold.log 2>&1 &
H=$!
sleep 7
grep -E "monitor connector|RecordMonitor|NODE=" /tmp/a2-hold.log
NODE=$(wpctl status 2>&1 | awk '/^Video/{p=1} p&&/^ *[0-9]+\./{gsub(/\./,"",$1); print $1; exit}')
echo "NODE=$NODE"

echo "### two consumers on same node (A2)"
rm -f /tmp/a2-a.png /tmp/a2-b.png
timeout 20 gst-launch-1.0 -q pipewiresrc path="$NODE" num-buffers=1 ! videoconvert ! pngenc ! filesink location=/tmp/a2-a.png >/tmp/a2-a.log 2>&1 &
A=$!
timeout 20 gst-launch-1.0 -q pipewiresrc path="$NODE" num-buffers=1 ! videoconvert ! pngenc ! filesink location=/tmp/a2-b.png >/tmp/a2-b.log 2>&1 &
B=$!
wait $A; echo "consumerA rc=$? size=$(stat -c%s /tmp/a2-a.png 2>/dev/null || echo 0)"
wait $B; echo "consumerB rc=$? size=$(stat -c%s /tmp/a2-b.png 2>/dev/null || echo 0)"
echo "--- A log ---"; tail -2 /tmp/a2-a.log
echo "--- B log ---"; tail -2 /tmp/a2-b.log

echo "### frame check"
python3 - <<'PY'
import os
from PIL import Image
for n in ('a', 'b'):
    p = '/tmp/a2-%s.png' % n
    if os.path.exists(p) and os.path.getsize(p) > 0:
        im = Image.open(p).convert('RGB')
        print("frame %s size=%s center_px=%s" % (n, im.size, im.getpixel((im.size[0]//2, im.size[1]//2))))
    else:
        print("frame %s NONE" % n)
PY

echo "### stop hold (no Session.Stop -> avoid shell crash)"
kill $H 2>/dev/null
sleep 1
echo "### done"
