#!/bin/bash
set -u
source /tmp/p1-env
export WAYLAND_DISPLAY=screenlab-0

systemctl --user start pipewire wireplumber >/dev/null 2>&1
sleep 2
echo "pipewire=$(systemctl --user is-active pipewire) wireplumber=$(systemctl --user is-active wireplumber)"

echo "### fan-out: 1 pipewiresrc -> N appsink"
python3 /tmp/p1-fanout.py "${N:-3}" "${DUR:-6}" > /tmp/p1-fanout.out 2>&1
echo "rc=$?"
cat /tmp/p1-fanout.out
echo "### DONE-FANOUT-SH"
