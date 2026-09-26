set -u
export XDG_RUNTIME_DIR=/run/user/1001
export DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1001/bus
export WAYLAND_DISPLAY=screenlab-0
export GDK_BACKEND=wayland
unset NO_AT_BRIDGE

echo "### start client"
rm -f /tmp/e5-client.log
python3 /tmp/e2-client.py --secs 40 > /tmp/e5-client.log 2>&1 &
CPID=$!
sleep 4

echo "### locate target via AT-SPI"
python3 /tmp/e4-atspi.py > /tmp/e5-atspi.log 2>&1
echo "atspi rc=$?"
tail -3 /tmp/e5-atspi.log
CX=$(awk '/^CENTER/{print $2}' /tmp/e5-atspi.log)
CY=$(awk '/^CENTER/{print $3}' /tmp/e5-atspi.log)

echo "### inject via Mutter RemoteDesktop ($CX,$CY)"
python3 /tmp/e5-rd-inject.py "$CX" "$CY" 2>&1

sleep 2
echo "### client log"
grep -E "BTN-CLICKED|client exited" /tmp/e5-client.log || echo "NO-CLICK-SEEN"
kill "$CPID" 2>/dev/null
echo "### DONE-E5"
