set -u
export XDG_RUNTIME_DIR=/run/user/1001
export DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1001/bus
export WAYLAND_DISPLAY=screenlab-0
unset NO_AT_BRIDGE

echo "### cleanup leftovers"
pkill -x python3 2>/dev/null; sleep 1
pgrep -ax python3 || echo "no python3"
systemctl --user start at-spi-dbus-bus.service >/dev/null 2>&1
systemctl --user start pipewire wireplumber >/dev/null 2>&1

echo "### restart shell"
systemctl --user stop screenlab-shell 2>/dev/null; systemctl --user reset-failed screenlab-shell 2>/dev/null
sleep 2
systemd-run --user --unit=screenlab-shell --collect --setenv=NO_AT_BRIDGE=0 \
  --property=StandardError=file:/tmp/screenlab-shell.err \
  -- gnome-shell --headless --virtual-monitor 1920x1080 --wayland-display=screenlab-0 >/dev/null 2>&1
sleep 9
printf "shell=%s\n" "$(systemctl --user is-active screenlab-shell)"

echo "### one clean client (no blink)"
python3 /tmp/e2-client.py --secs 60 > /tmp/a1w-client.log 2>&1 &
sleep 5
sed -n '1,4p' /tmp/a1w-client.log

echo "### a11y"
python3 /tmp/e4-atspi.py > /tmp/a1w-atspi.log 2>&1
grep -E "FOUND|CENTER|NOT-FOUND" /tmp/a1w-atspi.log
CX=$(awk '/^CENTER/{print $2}' /tmp/a1w-atspi.log)
CY=$(awk '/^CENTER/{print $3}' /tmp/a1w-atspi.log)

echo "### frame"
python3 /tmp/screencast-mon.py 35 > /tmp/a1w-hold.log 2>&1 &
H=$!
sleep 6
NODE=$(wpctl status 2>&1 | awk '/^Video/{p=1} p&&/^ *[0-9]+\./{gsub(/\./,"",$1); print $1; exit}')
echo "node=$NODE center=$CX,$CY"
rm -f /tmp/a1w.png
timeout 15 gst-launch-1.0 -q pipewiresrc path="$NODE" num-buffers=1 ! videoconvert ! pngenc ! filesink location=/tmp/a1w.png >/dev/null 2>&1
python3 - "$CX" "$CY" <<'PY'
import sys, os
from PIL import Image
cx, cy = int(sys.argv[1]), int(sys.argv[2])
p = '/tmp/a1w.png'
if not (os.path.exists(p) and os.path.getsize(p) > 0):
    print("NO-FRAME"); sys.exit(0)
im = Image.open(p).convert('RGB')
W, H = im.size
print("frame", im.size, "pixel@center:", im.getpixel((cx, cy)))
# coarse bbox of non-background (bg sampled at 5,5)
bg = im.getpixel((5, 5))
xs = []; ys = []
for y in range(0, H, 8):
    for x in range(0, W, 8):
        px = im.getpixel((x, y))
        if abs(px[0]-bg[0]) + abs(px[1]-bg[1]) + abs(px[2]-bg[2]) > 40:
            xs.append(x); ys.append(y)
if xs:
    print("non-bg bbox x:[%d,%d] y:[%d,%d] bg=%s" % (min(xs), max(xs), min(ys), max(ys), bg))
else:
    print("all background? bg=", bg)
im.crop((max(0,cx-250), max(0,cy-200), min(W,cx+250), min(H,cy+200))).save('/tmp/a1w-crop.png')
PY
kill $H 2>/dev/null
echo "### DONE-A1w"
