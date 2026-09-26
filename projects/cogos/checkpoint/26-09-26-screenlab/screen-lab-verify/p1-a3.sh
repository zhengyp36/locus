#!/bin/bash
set -u
source /tmp/p1-env

echo "### A3 run 1 (before move)"
TARGET=A4-BUTTON python3 /tmp/p1-a3.py > /tmp/p1-a3-run1.out 2>&1
cat /tmp/p1-a3-run1.out
C=$(sed -n 's/^CENTER //p' /tmp/p1-a3-run1.out)
X=$(echo "$C" | cut -d' ' -f1); Y=$(echo "$C" | cut -d' ' -f2)
if [ -z "$X" ]; then echo "NO-CENTER"; exit 1; fi
echo "click at ($X,$Y)"
xdotool mousemove "$X" "$Y" click 1
sleep 1

WID=$(xdotool search --name "A4 Ground Truth" | head -1)
echo "### move window $WID +250+120"
xdotool windowmove "$WID" 250 120
sleep 1

echo "### A3 run 2 (after move)"
TARGET=A4-BUTTON python3 /tmp/p1-a3.py > /tmp/p1-a3-run2.out 2>&1
cat /tmp/p1-a3-run2.out
C2=$(sed -n 's/^CENTER //p' /tmp/p1-a3-run2.out)
X2=$(echo "$C2" | cut -d' ' -f1); Y2=$(echo "$C2" | cut -d' ' -f2)
if [ -z "$X2" ]; then echo "NO-CENTER-2"; exit 1; fi
echo "click at ($X2,$Y2)"
xdotool mousemove "$X2" "$Y2" click 1
sleep 1

echo "### hits"
if [ -s /tmp/a4t-hits.log ]; then tail -6 /tmp/a4t-hits.log; else echo "(no hits)"; fi
echo "### DONE-A3"
