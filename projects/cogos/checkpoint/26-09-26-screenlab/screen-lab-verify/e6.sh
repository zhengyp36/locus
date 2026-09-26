#!/bin/bash
set -u
export XDG_RUNTIME_DIR=/run/user/1001
export DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1001/bus
export WAYLAND_DISPLAY=screenlab-0
unset NO_AT_BRIDGE

for d in :2 :3 :1 :0; do
  for f in $(ls -t /run/user/1001/.mutter-Xwaylandauth.* 2>/dev/null); do
    out=$(DISPLAY=$d XAUTHORITY=$f timeout 4 xdotool getdisplaygeometry 2>/dev/null)
    if echo "$out" | grep -qE '^[0-9]+ [0-9]+$'; then
      export DISPLAY="$d"; export XAUTHORITY="$f"; break 2
    fi
  done
done
echo "X-OK display=${DISPLAY:-NONE} geom=$(DISPLAY=$DISPLAY XAUTHORITY=$XAUTHORITY xdotool getdisplaygeometry 2>/dev/null)"

systemctl --user start at-spi-dbus-bus.service >/dev/null 2>&1
gdbus call --session --dest org.a11y.Bus --object-path /org/a11y/bus \
  --method org.freedesktop.DBus.Properties.Set org.a11y.Status IsEnabled "<true>" >/dev/null 2>&1
gdbus call --session --dest org.a11y.Bus --object-path /org/a11y/bus \
  --method org.freedesktop.DBus.Properties.Set org.a11y.Status ScreenReaderEnabled "<true>" >/dev/null 2>&1

pkill -f "[e]6-serve.py" 2>/dev/null
sleep 1
rm -f /tmp/e6t-traj.log
nohup python3 /tmp/e6-serve.py >/tmp/e6t-serve.log 2>&1 &
sleep 1
curl -s -o /dev/null -w "server-http=%{http_code}\n" http://127.0.0.1:8767/e6-page.html

pkill -f "user-data-dir=/tmp/e6" 2>/dev/null
sleep 2
rm -rf /tmp/e6
setsid google-chrome --no-sandbox --disable-dev-shm-usage --no-first-run \
  --no-default-browser-check --password-store=basic --force-renderer-accessibility \
  --user-data-dir=/tmp/e6 --window-size=1200,900 "http://127.0.0.1:8767/e6-page.html" \
  >/tmp/e6-app.log 2>&1 < /dev/null &
sleep 11
echo "chrome=$(pgrep -c chrome)"

echo "### locate target via a11y"
python3 /tmp/a4-keytest.py E6-TARGET > /tmp/e6-target.out 2>&1
cat /tmp/e6-target.out
C=$(sed -n 's/^CENTER //p' /tmp/e6-target.out)
CX=$(echo "$C" | cut -d' ' -f1); CY=$(echo "$C" | cut -d' ' -f2)
if [ -z "$CX" ]; then echo "NO-TARGET"; exit 1; fi
SX=$((CX > 450 ? CX - 400 : 60)); SY=$((CY > 320 ? CY - 300 : 60))
echo "### human move from ($SX,$SY) to ($CX,$CY)"
python3 /tmp/e6-move.py "$SX" "$SY" "$CX" "$CY" 70 1.3
sleep 2

echo "### raw traj"
cat /tmp/e6t-traj.log
echo "### summary"
python3 - <<'PY'
import json, os, math
p = '/tmp/e6t-traj.log'
if not os.path.exists(p) or not os.path.getsize(p):
    print('NO-TRAJ'); raise SystemExit
d = json.loads(open(p).read().strip().split('\n')[-1].split('\t', 1)[1])
pts = d['pts']
print('kind=%s n=%d dur=%d' % (d['kind'], d['n'], d['dur']))
if len(pts) >= 2:
    L = sum(math.dist(pts[i][:2], pts[i + 1][:2]) for i in range(len(pts) - 1))
    dts = [pts[i + 1][2] - pts[i][2] for i in range(len(pts) - 1)]
    print('path_len=%.1f start=%s end=%s' % (L, pts[0][:2], pts[-1][:2]))
    print('dt min=%d max=%d avg=%.1f (ms)' % (min(dts), max(dts), sum(dts) / len(dts)))
PY
echo "### DONE-E6"
pkill -f "user-data-dir=/tmp/e6" 2>/dev/null
pkill -f "[e]6-serve.py" 2>/dev/null
