set -u
export XDG_RUNTIME_DIR=/run/user/1001
export DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1001/bus
PATH_OUT=$(gdbus call --session --dest org.gnome.Mutter.ScreenCast \
  --object-path /org/gnome/Mutter/ScreenCast \
  --method org.gnome.Mutter.ScreenCast.CreateSession '{}' 2>&1)
echo "CreateSession -> $PATH_OUT"
SP=$(echo "$PATH_OUT" | sed -n "s/.*'\(.*\)'.*/\1/p")
echo "session path = $SP"
if [ -n "$SP" ]; then
  echo "=== session interface ==="
  gdbus introspect --session --dest org.gnome.Mutter.ScreenCast --object-path "$SP" 2>&1 | sed -n '/org.gnome.Mutter.ScreenCast.Session/,/^  };/p'
fi
echo "=== RemoteDesktop interface ==="
gdbus introspect --session --dest org.gnome.Mutter.RemoteDesktop \
  --object-path /org/gnome/Mutter/RemoteDesktop 2>&1 | sed -n '/interface org.gnome.Mutter.RemoteDesktop /,/^  };/p'
