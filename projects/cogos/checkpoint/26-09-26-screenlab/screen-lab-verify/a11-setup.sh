#!/bin/bash
set -u
export XDG_RUNTIME_DIR=/run/user/1001
export DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1001/bus

mkdir -p "$HOME/.config/systemd/user"
cat > "$HOME/.config/systemd/user/screenlab-shell.service" <<'EOF'
[Unit]
Description=screenlab headless gnome-shell (M2 graphical desktop)
After=dbus.service

[Service]
Type=simple
Environment=NO_AT_BRIDGE=0
ExecStart=/usr/bin/gnome-shell --headless --virtual-monitor 1920x1080 --wayland-display=screenlab-0
StandardError=append:/tmp/screenlab-shell.err
Restart=on-failure
RestartSec=3

[Install]
WantedBy=default.target
EOF

systemctl --user daemon-reload
echo "### stop transient screenlab-shell"
systemctl --user stop screenlab-shell 2>&1
sleep 2
echo "### enable + start persistent unit"
systemctl --user enable screenlab-shell.service 2>&1
systemctl --user start screenlab-shell.service 2>&1
sleep 7
echo "active=$(systemctl --user is-active screenlab-shell) enabled=$(systemctl --user is-enabled screenlab-shell)"
echo "### default.target wants"
systemctl --user show default.target -p Wants --no-pager 2>&1
echo "### sockets"
ls -la /run/user/1001/screenlab-0 2>&1
ls -la /tmp/.X11-unix/ 2>&1 | grep tangyu
echo "### shell err tail"
tail -4 /tmp/screenlab-shell.err 2>&1
echo "### DONE-A11-SETUP"
