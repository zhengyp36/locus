set -u
export XDG_RUNTIME_DIR=/run/user/1001
export DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1001/bus
export WAYLAND_DISPLAY=screenlab-0
export GDK_BACKEND=wayland
unset NO_AT_BRIDGE

RD=org.gnome.Mutter.RemoteDesktop
OBJ=/org/gnome/Mutter/RemoteDesktop
M=org.gnome.Mutter.RemoteDesktop.Session

echo "### create+start RemoteDesktop session"
OUT=$(gdbus call --session --dest $RD --object-path $OBJ --method $RD.CreateSession 2>&1)
SP=$(echo "$OUT" | sed -n "s/.*'\(.*\)'.*/\1/p")
echo "session=$SP"
gdbus call --session --dest $RD --object-path "$SP" --method $M.Start 2>&1

echo "### start client"
rm -f /tmp/e4b-client.log
python3 /tmp/e2-client.py --secs 40 > /tmp/e4b-client.log 2>&1 &
CPID=$!
sleep 4

echo "### locate target"
python3 /tmp/e4-atspi.py > /tmp/e4b-atspi.log 2>&1
echo "atspi rc=$?"
tail -4 /tmp/e4b-atspi.log
CX=$(awk '/^CENTER/{print $2}' /tmp/e4b-atspi.log)
CY=$(awk '/^CENTER/{print $3}' /tmp/e4b-atspi.log)
echo "center=$CX,$CY"

echo "### inject: corner then absolute-ish move + click"
gdbus call --session --dest $RD --object-path "$SP" --method $M.NotifyPointerMotion -- -10000.0 -10000.0 2>&1
gdbus call --session --dest $RD --object-path "$SP" --method $M.NotifyPointerMotion "$CX.0" "$CY.0" 2>&1
gdbus call --session --dest $RD --object-path "$SP" --method $M.NotifyPointerButton 1 1 2>&1
sleep 1
gdbus call --session --dest $RD --object-path "$SP" --method $M.NotifyPointerButton 1 0 2>&1
sleep 2

echo "### client log after injection"
sed -n '1,40p' /tmp/e4b-client.log
gdbus call --session --dest $RD --object-path "$SP" --method $M.Stop 2>&1 | tail -1
kill "$CPID" 2>/dev/null
echo "### DONE-E4b"
