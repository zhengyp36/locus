set -u
export XDG_RUNTIME_DIR=/run/user/1001
export DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1001/bus
export WAYLAND_DISPLAY=screenlab-0
AUTH=$(ls /run/user/1001/.mutter-Xwaylandauth.* 2>/dev/null | head -1)
export XAUTHORITY="$AUTH"
export DISPLAY=:1
export GDK_BACKEND=wayland
unset NO_AT_BRIDGE

echo "### at-spi bus"
systemctl --user start at-spi-dbus-bus.service 2>&1 | tail -1
printf "at-spi-dbus-bus: %s\n" "$(systemctl --user is-active at-spi-dbus-bus.service)"
echo "### tools"
command -v xdotool || echo "NO xdotool"

echo "### start client (background)"
rm -f /tmp/e4-client.log
python3 /tmp/e2-client.py --secs 40 > /tmp/e4-client.log 2>&1 &
CPID=$!
sleep 5
echo "--- client log ---"
sed -n '1,40p' /tmp/e4-client.log

echo "### a11y tree"
python3 /tmp/e4-atspi.py > /tmp/e4-atspi.log 2>&1
echo "atspi rc=$?"
sed -n '1,80p' /tmp/e4-atspi.log

CX=$(awk '/^CENTER/{print $2}' /tmp/e4-atspi.log)
CY=$(awk '/^CENTER/{print $3}' /tmp/e4-atspi.log)
echo "### click at ${CX:-none} ${CY:-none}"
if [ -n "${CX:-}" ] && command -v xdotool >/dev/null; then
  timeout 8 xdotool mousemove "$CX" "$CY"
  timeout 8 xdotool click 1
  echo "xdotool rc=$?"
fi
sleep 2
echo "### client log after click"
sed -n '1,40p' /tmp/e4-client.log
kill "$CPID" 2>/dev/null
echo "### DONE-E4"
