set -u
export XDG_RUNTIME_DIR=/run/user/1001
export DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1001/bus

echo "### start session services"
systemctl --user start at-spi-dbus-bus.service 2>&1 | tail -2
systemctl --user start pipewire pipewire-pulse wireplumber 2>&1 | tail -4

echo "### compositor as persistent user unit"
systemctl --user stop wl 2>/dev/null; systemctl --user reset-failed wl 2>/dev/null
systemd-run --user --unit=wl --collect --setenv=NO_AT_BRIDGE=0 -- \
  mutter --headless --virtual-monitor 1280x720 --wayland-display=wl 2>&1 | tail -2
sleep 6

echo "### states"
for u in wl pipewire pipewire-pulse wireplumber at-spi-dbus-bus.service; do
  printf "%-24s %s\n" "$u" "$(systemctl --user is-active "$u" 2>&1)"
done
echo "### procs"
pgrep -ax mutter; pgrep -ax pipewire | head -3; pgrep -ax wireplumber | head -2
echo "### active VT (A5)"
cat /sys/class/tty/tty0/active
echo "### mutter gpu lines (A6/A5)"
grep -E "renderD128|surfaceless|card0|mode setting|virtual monitor|X11 display" /tmp/wl-p0-mutter.log 2>/dev/null || \
  journalctl --user -u wl -n 0 2>/dev/null || true
echo "### DisplayConfig monitors"
timeout 10 gdbus call --session --dest org.gnome.Mutter.DisplayConfig \
  --object-path /org/gnome/Mutter/DisplayConfig \
  --method org.gnome.Mutter.DisplayConfig.GetCurrentState 2>&1 | head -c 3000
echo
echo "### DONE-SETUP"
