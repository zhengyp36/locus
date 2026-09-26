set -u
export XDG_RUNTIME_DIR=/run/user/1001
export DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1001/bus
export WAYLAND_DISPLAY=screenlab-0
unset NO_AT_BRIDGE

systemctl --user start pipewire wireplumber >/dev/null 2>&1
python3 /tmp/e2-client.py --secs 60 > /tmp/a1d-client.log 2>&1 &
sleep 4

python3 /tmp/screencast-hold.py 45 > /tmp/a1d-hold.log 2>&1 &
H=$!
sleep 4
cat /tmp/a1d-hold.log

echo "### wpctl video streams"
wpctl status 2>&1 | sed -n '/Video/,/Settings/p'
OUT=$(wpctl status 2>&1 | awk '/Video/{v=1} v&&/output_/{gsub(/\./,"",$1);print $1; exit}')
echo "out_node=$OUT"

echo "### gst with node $OUT (timeout 15)"
timeout 15 gst-launch-1.0 -v pipewiresrc path="$OUT" num-buffers=1 ! videoconvert ! pngenc ! filesink location=/tmp/a1d-frame.png 2>&1 | tail -20
ls -l /tmp/a1d-frame.png 2>&1
python3 - <<'PY'
import os
p='/tmp/a1d-frame.png'
print("size", os.path.getsize(p) if os.path.exists(p) else -1)
if os.path.exists(p) and os.path.getsize(p)>0:
    from PIL import Image
    im=Image.open(p); print("frame", im.size, im.mode); im.save('/tmp/a1d-frame.png')
PY
kill $H 2>/dev/null
echo "### DONE-A1d"
