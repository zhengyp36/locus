#!/bin/bash
export XDG_RUNTIME_DIR=/run/user/1001
export DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1001/bus
setsid python3 /tmp/a4-serve.py >/tmp/a4-serve.log 2>&1 </dev/null &
sleep 1
echo "listening:"
ss -tlnp 2>/dev/null | grep 8765 || echo "(not listening)"
echo -n "self-test: "
curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8765/
