set -u
export XDG_RUNTIME_DIR=/run/user/1001
export DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1001/bus
export WAYLAND_DISPLAY=screenlab-0
unset NO_AT_BRIDGE

echo "### cleanup + shell"
pkill -x python3 2>/dev/null; sleep 1
systemctl --user start at-spi-dbus-bus.service >/dev/null 2>&1
systemctl --user start pipewire wireplumber >/dev/null 2>&1
systemctl --user stop screenlab-shell 2>/dev/null; systemctl --user reset-failed screenlab-shell 2>/dev/null
sleep 2
systemd-run --user --unit=screenlab-shell --collect --setenv=NO_AT_BRIDGE=0 \
  --property=StandardError=file:/tmp/screenlab-shell.err \
  -- gnome-shell --headless --virtual-monitor 1920x1080 --wayland-display=screenlab-0 >/dev/null 2>&1
sleep 9
printf "shell=%s\n" "$(systemctl --user is-active screenlab-shell)"

XDN=$(grep -oP 'Using public X11 display :\K[0-9]+' /tmp/screenlab-shell.err | head -1)
export DISPLAY=":1"
export XAUTHORITY="$(ls /run/user/1001/.mutter-Xwaylandauth.* 2>/dev/null | head -1)"
export GTK_MODULES=gail:atk-bridge
echo "DISPLAY=$DISPLAY XAUTHORITY=$XAUTHORITY"
timeout 8 xdotool getdisplaygeometry 2>&1

echo "### X11 client"
GDK_BACKEND=x11 python3 /tmp/e2-client.py --secs 60 > /tmp/a1x-client.log 2>&1 &
sleep 5
sed -n '1,5p' /tmp/a1x-client.log

echo "### a11y"
python3 /tmp/e4-atspi.py > /tmp/a1x-atspi.log 2>&1
grep -E "FOUND|CENTER|NOT-FOUND" /tmp/a1x-atspi.log
CX=$(awk '/^CENTER/{print $2}' /tmp/a1x-atspi.log)
CY=$(awk '/^CENTER/{print $3}' /tmp/a1x-atspi.log)

echo "### frame"
python3 /tmp/screencast-mon.py 35 > /tmp/a1x-hold.log 2>&1 &
H=$!
sleep 6
NODE=$(wpctl status 2>&1 | awk '/^Video/{p=1} p&&/^ *[0-9]+\./{gsub(/\./,"",$1); print $1; exit}')
echo "node=$NODE center=$CX,$CY"
rm -f /tmp/a1x.png
timeout 15 gst-launch-1.0 -q pipewiresrc path="$NODE" num-buffers=1 ! videoconvert ! pngenc ! filesink location=/tmp/a1x.png >/dev/null 2>&1
python3 - "$CX" "$CY" <<'PY'
import sys, os
from PIL import Image
cx, cy = int(sys.argv[1]), int(sys.argv[2])
p = '/tmp/a1x.png'
if not (os.path.exists(p) and os.path.getsize(p) > 0):
    print("NO-FRAME"); sys.exit(0)
im = Image.open(p).convert('RGB')
print("frame", im.size, "pixel@a11y-center(%d,%d):" % (cx, cy), im.getpixel((cx, cy)))
PY
kill $H 2>/dev/null
echo "### DONE-A1x"
