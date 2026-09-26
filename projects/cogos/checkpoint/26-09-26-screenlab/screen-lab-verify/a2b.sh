#!/bin/bash
set -u
export XDG_RUNTIME_DIR=/run/user/1001
export DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1001/bus
export WAYLAND_DISPLAY=screenlab-0
unset NO_AT_BRIDGE

systemctl --user start pipewire wireplumber >/dev/null 2>&1
sleep 2
echo "### shell=$(systemctl --user is-active screenlab-shell) pipewire=$(systemctl --user is-active pipewire) wp=$(systemctl --user is-active wireplumber)"

python3 /tmp/screencast-mon.py 60 > /tmp/a2b-hold.log 2>&1 &
H=$!
sleep 7
grep -E "RecordMonitor|^NODE=" /tmp/a2b-hold.log
NODE=$(wpctl status 2>&1 | awk '/^Video/{p=1} p&&/^ *[0-9]+\./{gsub(/\./,"",$1); print $1; exit}')
echo "NODE=$NODE"

echo "### control: single consumer C"
rm -f /tmp/a2b-c.png
timeout 15 gst-launch-1.0 -q pipewiresrc path="$NODE" num-buffers=1 ! videoconvert ! pngenc ! filesink location=/tmp/a2b-c.png >/tmp/a2b-c.log 2>&1
echo "consumerC rc=$? size=$(stat -c%s /tmp/a2b-c.png 2>/dev/null || echo 0)"

echo "### long consumer A (holds stream), then B joins while A active"
rm -f /tmp/a2b-a.png /tmp/a2b-b.png
timeout 16 gst-launch-1.0 -q pipewiresrc path="$NODE" num-buffers=100000 ! videoconvert ! pngenc ! filesink location=/tmp/a2b-a.png >/tmp/a2b-a.log 2>&1 &
A=$!
sleep 4
timeout 10 gst-launch-1.0 -q pipewiresrc path="$NODE" num-buffers=1 ! videoconvert ! pngenc ! filesink location=/tmp/a2b-b.png >/tmp/a2b-b.log 2>&1
echo "consumerB(concurrent with A) rc=$? size=$(stat -c%s /tmp/a2b-b.png 2>/dev/null || echo 0)"
kill $A 2>/dev/null; wait $A 2>/dev/null; echo "consumerA(held) size=$(stat -c%s /tmp/a2b-a.png 2>/dev/null || echo 0)"

echo "### log tails"
echo "A:"; tail -1 /tmp/a2b-a.log
echo "B:"; tail -1 /tmp/a2b-b.log

python3 - <<'PY'
import os
from PIL import Image
for n in ('a', 'b', 'c'):
    p = '/tmp/a2b-%s.png' % n
    if os.path.exists(p) and os.path.getsize(p) > 0:
        im = Image.open(p).convert('RGB')
        print("frame %s size=%s center_px=%s" % (n, im.size, im.getpixel((im.size[0]//2, im.size[1]//2))))
    else:
        print("frame %s NONE" % n)
PY

kill $H 2>/dev/null
echo "### done"
