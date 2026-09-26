set -u
export XDG_RUNTIME_DIR=/run/user/1001
export DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1001/bus
AUTH=$(ls /run/user/1001/.mutter-Xwaylandauth.* 2>/dev/null | head -1)
export DISPLAY=:1
export XAUTHORITY="$AUTH"
unset NO_AT_BRIDGE
export GTK_MODULES=gail:atk-bridge

echo "### start client as X11 (Xwayland) client"
rm -f /tmp/e5b-client.log
GDK_BACKEND=x11 python3 /tmp/e2-client.py --secs 40 > /tmp/e5b-client.log 2>&1 &
CPID=$!
sleep 4
echo "--- client head ---"
sed -n '1,10p' /tmp/e5b-client.log

echo "### locate target via AT-SPI"
python3 /tmp/e4-atspi.py > /tmp/e5b-atspi.log 2>&1
echo "atspi rc=$?"
grep -E "FOUND|CENTER|NOT-FOUND" /tmp/e5b-atspi.log
CX=$(awk '/^CENTER/{print $2}' /tmp/e5b-atspi.log)
CY=$(awk '/^CENTER/{print $3}' /tmp/e5b-atspi.log)

echo "### XTEST click at $CX,$CY"
timeout 8 xdotool mousemove "$CX" "$CY"
timeout 8 xdotool click 1
echo "xdotool rc=$?"
sleep 2
echo "### client result"
grep -E "BTN-ENTER|BTN-PRESS|BTN-CLICKED" /tmp/e5b-client.log || echo "NO-EVENTS"
kill "$CPID" 2>/dev/null
echo "### DONE-E5b"
