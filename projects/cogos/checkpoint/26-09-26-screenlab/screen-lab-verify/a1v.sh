set -u
export XDG_RUNTIME_DIR=/run/user/1001
export DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1001/bus
export WAYLAND_DISPLAY=screenlab-0
unset NO_AT_BRIDGE

echo "### restart shell"
systemctl --user reset-failed screenlab-shell 2>/dev/null
systemd-run --user --unit=screenlab-shell --collect --setenv=NO_AT_BRIDGE=0 \
  --property=StandardError=file:/tmp/screenlab-shell.err \
  -- gnome-shell --headless --virtual-monitor 1920x1080 --wayland-display=screenlab-0 >/dev/null 2>&1
sleep 9
printf "shell=%s\n" "$(systemctl --user is-active screenlab-shell)"

echo "### client"
systemctl --user start at-spi-dbus-bus.service >/dev/null 2>&1
printf "atspi=%s\n" "$(systemctl --user is-active at-spi-dbus-bus.service)"
python3 /tmp/e2-client.py --secs 70 --blink > /tmp/a1v-client.log 2>&1 &
sleep 5

echo "### a11y target"
python3 /tmp/e4-atspi.py > /tmp/a1v-atspi.log 2>&1
grep -E "FOUND|CENTER|NOT-FOUND" /tmp/a1v-atspi.log
CX=$(awk '/^CENTER/{print $2}' /tmp/a1v-atspi.log)
CY=$(awk '/^CENTER/{print $3}' /tmp/a1v-atspi.log)

echo "### screencast (RecordMonitor) + frame"
python3 /tmp/screencast-mon.py 40 > /tmp/a1v-hold.log 2>&1 &
H=$!
sleep 6
NODE=$(wpctl status 2>&1 | awk '/^Video/{p=1} p&&/^ *[0-9]+\./{gsub(/\./,"",$1); print $1; exit}')
echo "node=$NODE a11y_center=$CX,$CY"
rm -f /tmp/a1v.png
timeout 15 gst-launch-1.0 -q pipewiresrc path="$NODE" num-buffers=1 ! videoconvert ! pngenc ! filesink location=/tmp/a1v.png >/dev/null 2>&1
python3 - "$CX" "$CY" <<'PY'
import sys, os
from PIL import Image
cx, cy = int(sys.argv[1]), int(sys.argv[2])
p = '/tmp/a1v.png'
if not (os.path.exists(p) and os.path.getsize(p) > 0):
    print("NO-FRAME"); sys.exit(0)
im = Image.open(p).convert('RGB')
print("frame", im.size)
print("pixel at a11y center (%d,%d):" % (cx, cy), im.getpixel((cx, cy)))
x0, y0 = max(0, cx - 220), max(0, cy - 160)
im.crop((x0, y0, min(im.size[0], cx + 220), min(im.size[1], cy + 160))).save('/tmp/a1v-crop.png')
print("crop saved around a11y center")
PY
kill $H 2>/dev/null
echo "### DONE-A1v"
