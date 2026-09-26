#!/bin/bash
# Probe a usable Xwayland display in the headless screenlab session and export
# DISPLAY / XAUTHORITY. Source this file (or run it) before X11 clients.
#
#   source /path/screenlab-x11.sh && google-chrome <url>
#
# Note: the headless shell spawns several Xwayland instances; :2/:3 are usually
# good, :0/:1 belong to other sessions, :4/:5 are stale. Always probe.

screenlab_x11_probe() {
  export XDG_RUNTIME_DIR="${XDG_RUNTIME_DIR:-/run/user/1001}"
  export DBUS_SESSION_BUS_ADDRESS="${DBUS_SESSION_BUS_ADDRESS:-unix:path=/run/user/1001/bus}"
  export WAYLAND_DISPLAY="${WAYLAND_DISPLAY:-screenlab-0}"
  unset NO_AT_BRIDGE
  local d f out
  for d in :2 :3 :1 :0; do
    for f in $(ls -t "$XDG_RUNTIME_DIR"/.mutter-Xwaylandauth.* 2>/dev/null); do
      out=$(DISPLAY="$d" XAUTHORITY="$f" timeout 4 xdotool getdisplaygeometry 2>/dev/null)
      if echo "$out" | grep -qE '^[0-9]+ [0-9]+$'; then
        export DISPLAY="$d"
        export XAUTHORITY="$f"
        echo "screenlab-x11: DISPLAY=$d auth=$(basename "$f") geom=$out" >&2
        if [ -n "${SCREENLAB_X11_ENV:-}" ]; then
          {
            echo "export XDG_RUNTIME_DIR=$XDG_RUNTIME_DIR"
            echo "export DBUS_SESSION_BUS_ADDRESS=$DBUS_SESSION_BUS_ADDRESS"
            echo "export WAYLAND_DISPLAY=$WAYLAND_DISPLAY"
            echo "export DISPLAY=$DISPLAY"
            echo "export XAUTHORITY=$XAUTHORITY"
          } > "$SCREENLAB_X11_ENV"
        fi
        return 0
      fi
    done
  done
  echo "screenlab-x11: no usable Xwayland" >&2
  return 1
}

screenlab_x11_probe
