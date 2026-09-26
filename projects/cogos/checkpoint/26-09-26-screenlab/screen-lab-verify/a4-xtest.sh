#!/bin/bash
set -u
export XDG_RUNTIME_DIR=/run/user/1001
export DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1001/bus
export WAYLAND_DISPLAY=screenlab-0

for d in :2 :3 :1 :0; do
  for f in $(ls -t /run/user/1001/.mutter-Xwaylandauth.* 2>/dev/null); do
    out=$(DISPLAY=$d XAUTHORITY=$f timeout 4 xdotool getdisplaygeometry 2>/dev/null)
    if echo "$out" | grep -qE '^[0-9]+ [0-9]+$'; then
      export DISPLAY="$d"; export XAUTHORITY="$f"
      echo "X-OK display=$d auth=$(basename "$f") geom=$out"
      break 2
    fi
  done
done
echo "DISPLAY=${DISPLAY:-NONE} XAUTHORITY=${XAUTHORITY:-NONE}"

rm -f /tmp/a4t-key.out
python3 /tmp/a4-keytest.py A4-TEXT > /tmp/a4t-key.out 2>&1
cat /tmp/a4t-key.out
CENTER=$(sed -n 's/^CENTER //p' /tmp/a4t-key.out)
X=$(echo "$CENTER" | cut -d' ' -f1)
Y=$(echo "$CENTER" | cut -d' ' -f2)
echo "CENTER=($X,$Y)"
if [ -z "$X" ]; then echo "NO-CENTER"; exit 1; fi

echo "### XTEST: mousemove + click + type"
DISPLAY="$DISPLAY" XAUTHORITY="$XAUTHORITY" xdotool mousemove "$X" "$Y" click 1
sleep 1
DISPLAY="$DISPLAY" XAUTHORITY="$XAUTHORITY" xdotool type --delay 80 'X11KEY'
sleep 1
DISPLAY="$DISPLAY" XAUTHORITY="$XAUTHORITY" xdotool key ctrl+a
sleep 1
echo "### hits"
if [ -s /tmp/a4t-hits.log ]; then tail -8 /tmp/a4t-hits.log; else echo "(no hits)"; fi
echo "### DONE-XTEST"
