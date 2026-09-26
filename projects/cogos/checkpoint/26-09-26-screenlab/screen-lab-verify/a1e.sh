set -u
export XDG_RUNTIME_DIR=/run/user/1001
export DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1001/bus
export WAYLAND_DISPLAY=screenlab-0
unset NO_AT_BRIDGE

systemctl --user start pipewire wireplumber >/dev/null 2>&1
python3 /tmp/e2-client.py --secs 60 --blink > /tmp/a1e-client.log 2>&1 &
sleep 4
grep -E "toplevel" /tmp/a1e-client.log | head -1

python3 /tmp/screencast-hold.py 45 > /tmp/a1e-hold.log 2>&1 &
H=$!
sleep 5
echo "### hold log"; cat /tmp/a1e-hold.log
echo "### wpctl video streams"
wpctl status 2>&1 | sed -n '/Video/,/Settings/p'
NODE=$(awk -F= '/^NODE=/{print $2;exit}' /tmp/a1e-hold.log)
OUTNODE=$(wpctl status 2>&1 | awk '/Video/{v=1} v&&/output_/{gsub(/\./,"",$1);print $1; exit}')
echo "signal_node=$NODE wpctl_output=$OUTNODE"

for ID in "$NODE" "$OUTNODE"; do
  [ -z "$ID" ] || [ "$ID" = "None" ] && continue
  echo "### gst id=$ID"
  GST_DEBUG=pipewire:3 timeout 12 gst-launch-1.0 -v pipewiresrc path="$ID" num-buffers=1 \
    ! videoconvert ! pngenc ! filesink location="/tmp/a1e-$ID.png" 2>&1 | tail -12
  ls -l "/tmp/a1e-$ID.png" 2>&1
done
kill $H 2>/dev/null
echo "### DONE-A1e"
