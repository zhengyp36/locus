set -u
export XDG_RUNTIME_DIR=/run/user/1001
export DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1001/bus
export WAYLAND_DISPLAY=screenlab-0
unset NO_AT_BRIDGE

echo "### gst plugin"
gst-inspect-1.0 pipewire 2>&1 | head -3

echo "### ensure shell"
if [ "$(systemctl --user is-active screenlab-shell)" != "active" ]; then
  systemctl --user reset-failed screenlab-shell 2>/dev/null
  systemd-run --user --unit=screenlab-shell --collect --setenv=NO_AT_BRIDGE=0 \
    --property=StandardError=file:/tmp/screenlab-shell.err \
    -- gnome-shell --headless --virtual-monitor 1920x1080 --wayland-display=screenlab-0 >/dev/null 2>&1
  sleep 8
fi
printf "shell=%s\n" "$(systemctl --user is-active screenlab-shell)"

python3 /tmp/e2-client.py --secs 60 > /tmp/a1c-client.log 2>&1 &
sleep 4

echo "### hold screencast session"
python3 /tmp/screencast-hold.py 45 > /tmp/a1c-hold.log 2>&1 &
HOLD=$!
for i in $(seq 1 20); do
  NODE=$(awk '/^NODE=/{sub("NODE=","");print;exit}' /tmp/a1c-hold.log)
  [ -n "${NODE:-}" ] && [ "$NODE" != "None" ] && break
  sleep 0.5
done
echo "node=$NODE"
cat /tmp/a1c-hold.log

echo "### pipewire nodes"
pw-dump 2>/dev/null | grep -c '"type": "PipeWire:Interface:Node"' || echo "pw-dump failed"
pw-cli ls Node 2>&1 | head -20

echo "### gst verbose (timeout 15)"
timeout 15 gst-launch-1.0 -v pipewiresrc path="$NODE" num-buffers=1 ! videoconvert ! pngenc ! filesink location=/tmp/a1c-frame.png 2>&1 | tail -25
echo "gst rc=$?"
ls -l /tmp/a1c-frame.png 2>&1
kill "$HOLD" 2>/dev/null
echo "### DONE-A1c"
