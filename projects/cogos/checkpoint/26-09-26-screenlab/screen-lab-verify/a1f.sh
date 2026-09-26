set -u
export XDG_RUNTIME_DIR=/run/user/1001
export DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1001/bus
export WAYLAND_DISPLAY=screenlab-0
unset NO_AT_BRIDGE

echo "### restart shell"
systemctl --user stop screenlab-shell 2>/dev/null; systemctl --user reset-failed screenlab-shell 2>/dev/null
sleep 2
systemd-run --user --unit=screenlab-shell --collect --setenv=NO_AT_BRIDGE=0 \
  --property=StandardError=file:/tmp/screenlab-shell.err \
  -- gnome-shell --headless --virtual-monitor 1920x1080 --wayland-display=screenlab-0 >/dev/null 2>&1
sleep 8
printf "shell=%s\n" "$(systemctl --user is-active screenlab-shell)"
systemctl --user start pipewire wireplumber >/dev/null 2>&1

python3 /tmp/e2-client.py --secs 60 --blink > /tmp/a1f-client.log 2>&1 &
sleep 4

python3 /tmp/screencast-hold.py 45 > /tmp/a1f-hold.log 2>&1 &
H=$!
sleep 5
cat /tmp/a1f-hold.log
echo "### wpctl video streams"
wpctl status 2>&1 | sed -n '/Video/,/Settings/p'
NODE=$(awk -F= '/^NODE=/{print $2;exit}' /tmp/a1f-hold.log)
OUTNODE=$(wpctl status 2>&1 | awk '/Video/{v=1} v&&/output_/{gsub(/\./,"",$1);print $1; exit}')
echo "signal_node=$NODE wpctl_output=$OUTNODE"

for ID in "$NODE" "$OUTNODE"; do
  if [ -z "$ID" ] || [ "$ID" = "None" ]; then continue; fi
  echo "### gst id=$ID"
  GST_DEBUG=pipewire:3 timeout 12 gst-launch-1.0 -v pipewiresrc path="$ID" num-buffers=1 \
    ! videoconvert ! pngenc ! filesink location="/tmp/a1f-$ID.png" 2>&1 | tail -14
  ls -l "/tmp/a1f-$ID.png" 2>&1
done
kill $H 2>/dev/null
echo "### DONE-A1f"
