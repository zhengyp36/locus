set -u
export XDG_RUNTIME_DIR=/run/user/1001
export DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1001/bus
systemctl --user start at-spi-dbus-bus.service
systemctl --user stop wl-slice 2>/dev/null
systemctl --user reset-failed wl-slice 2>/dev/null
systemd-run --user --unit=wl-slice --collect \
  --setenv=NO_AT_BRIDGE=0 \
  -- mutter --headless --virtual-monitor 1280x720 --wayland-display=wl-slice
sleep 6
echo "unit: $(systemctl --user is-active wl-slice)"
echo "=== mutter procs ==="; pgrep -ax mutter
echo "=== screencast/remote names ==="; busctl --user list 2>/dev/null | grep -i -E "ScreenCast|RemoteDesktop"
echo "=== introspect ScreenCast ==="
gdbus introspect --session --dest org.gnome.Mutter.ScreenCast \
  --object-path /org/gnome/Mutter/ScreenCast 2>&1 | head -40
