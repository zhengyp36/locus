set -u
export XDG_RUNTIME_DIR=/run/user/1001
export DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1001/bus
export WAYLAND_DISPLAY=screenlab-0
unset NO_AT_BRIDGE

echo "### pipewire"
systemctl --user start pipewire pipewire-pulse wireplumber 2>&1 | tail -1
printf "pipewire=%s wireplumber=%s\n" \
  "$(systemctl --user is-active pipewire)" "$(systemctl --user is-active wireplumber)"

echo "### ensure shell"
if [ "$(systemctl --user is-active screenlab-shell)" != "active" ]; then
  systemctl --user reset-failed screenlab-shell 2>/dev/null
  systemd-run --user --unit=screenlab-shell --collect --setenv=NO_AT_BRIDGE=0 \
    --property=StandardError=file:/tmp/screenlab-shell.err \
    -- gnome-shell --headless --virtual-monitor 1920x1080 --virtual-monitor 1280x720 \
    --wayland-display=screenlab-0 >/dev/null 2>&1
  sleep 8
fi
printf "shell=%s\n" "$(systemctl --user is-active screenlab-shell)"

echo "### start client"
python3 /tmp/e2-client.py --secs 70 > /tmp/a1-client.log 2>&1 &
CPID=$!
sleep 4
grep -E "toplevel|screen size" /tmp/a1-client.log | head -2

echo "### a11y target"
python3 /tmp/e4-atspi.py > /tmp/a1-atspi.log 2>&1
grep -E "FOUND|CENTER|NOT-FOUND" /tmp/a1-atspi.log

echo "### screencast"
python3 /tmp/p0-screencast.py 2>&1 | tail -18

echo "### frame"
python3 - <<'PY'
import os
p = '/tmp/p0-frame.png'
print("exists", os.path.exists(p), os.path.getsize(p) if os.path.exists(p) else 0)
if os.path.exists(p) and os.path.getsize(p) > 0:
    from PIL import Image
    im = Image.open(p)
    print("frame", im.size, im.mode)
PY
kill "$CPID" 2>/dev/null
echo "### DONE-A1b"
