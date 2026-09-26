set -u
export XDG_RUNTIME_DIR=/run/user/1001
if [ -z "${DBUS_SESSION_BUS_ADDRESS:-}" ] && [ -S /run/user/1001/bus ]; then
  export DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1001/bus
fi
echo "### env"
echo "user=$(id -un) bus=${DBUS_SESSION_BUS_ADDRESS:-unset} runtime=$XDG_RUNTIME_DIR"

echo "### atspi (user unit, no root)"
systemctl --user start at-spi-dbus-bus.service 2>&1 || true
echo "at-spi state: $(systemctl --user is-active at-spi-dbus-bus.service)"
busctl --user list 2>/dev/null | grep -i "a11y" || echo "(no a11y name)"

echo "### compositor: mutter --headless"
pkill -x mutter 2>/dev/null
sleep 1
rm -f /tmp/wl-slice-mutter.log
setsid mutter --headless --wayland-display=wl-slice >/tmp/wl-slice-mutter.log 2>&1 &
sleep 6
echo "procs:"; pgrep -ax mutter; pgrep -ax Xwayland
echo "log:"; grep -E "renderD128|mode setting|No 3D|X11 display|Wayland display|Failed" /tmp/wl-slice-mutter.log | head -20

XDISP=$(grep -oP 'Using public X11 display :\K[0-9]+' /tmp/wl-slice-mutter.log | head -1)
echo "### xdisplay=:${XDISP:-MISSING}"
export DISPLAY=:${XDISP}
echo "xdotool geometry: $(xdotool getdisplaygeometry 2>&1)"

echo "### gtk app on the Xwayland display"
cat > /tmp/wl-slice-app.py <<'PY'
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

def on_click(*a):
    print("BTN-CLICKED", flush=True)

w = Gtk.Window(title="SliceApp")
w.set_default_size(420, 300)
box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
w.add(box)
box.pack_start(Gtk.Label(label="hello-slice"), False, False, 0)
btn = Gtk.Button(label="CLICK-ME")
btn.connect("clicked", on_click)
box.pack_start(btn, False, False, 0)
w.connect("destroy", Gtk.main_quit)
w.show_all()
Gtk.main()
PY
NO_AT_BRIDGE=0 GTK_MODULES=gail:atk-bridge setsid python3 /tmp/wl-slice-app.py >/tmp/wl-slice-app.log 2>&1 &
sleep 4
echo "app proc: $(pgrep -af wl-slice-app | head -1)"

echo "### a11y tree (Atspi via GI)"
python3 - <<'PY'
import gi
gi.require_version('Atspi', '2.0')
from gi.repository import Atspi
d = Atspi.get_desktop(0)
def walk(node, depth=0):
    try:
        n = node.get_child_count()
    except Exception:
        return
    for i in range(n):
        try:
            c = node.get_child_at_index(i)
        except Exception:
            continue
        try:
            name = c.get_name() or ""
            role = c.get_role_name() or ""
            ext = c.get_extents(Atspi.CoordType.SCREEN)
            interesting = name or role in ("push button", "frame", "label", "application")
            if interesting:
                print("%s%-16s name=%r ext=(%d,%d,%d,%d)" % (
                    "  " * depth, role, name, ext.x, ext.y, ext.width, ext.height))
            walk(c, depth + 1)
        except Exception:
            pass
walk(d)
PY

echo "### act: click CLICK-ME via a11y bounds"
python3 - <<'PY'
import gi, os, subprocess
gi.require_version('Atspi', '2.0')
from gi.repository import Atspi
d = Atspi.get_desktop(0)
def find(node):
    try:
        n = node.get_child_count()
    except Exception:
        return None
    for i in range(n):
        try:
            c = node.get_child_at_index(i)
        except Exception:
            continue
        if (c.get_name() or "") == "CLICK-ME":
            return c
        r = find(c)
        if r:
            return r
    return None
c = find(d)
if c is None:
    print("CLICK-ME NOT FOUND")
else:
    e = c.get_extents(Atspi.CoordType.SCREEN)
    cx, cy = e.x + e.width // 2, e.y + e.height // 2
    print("click at", cx, cy)
    subprocess.run(["xdotool", "mousemove", "--sync", str(cx), str(cy), "click", "1"],
                   env=dict(os.environ))
    print("xdotool click done")
PY
sleep 1
echo "app log: $(tail -2 /tmp/wl-slice-app.log 2>&1)"

echo "### pixels (PIL on Xwayland)"
python3 - <<'PY'
import os
from PIL import ImageGrab
im = ImageGrab.grab(xdisplay=os.environ["DISPLAY"])
print("capture size", im.size)
im.save("/tmp/wl-slice.png")
print("saved /tmp/wl-slice.png")
PY

echo "### cleanup"
pkill -x mutter 2>/dev/null; sleep 1
pkill -f wl-slice-app.py 2>/dev/null
sleep 1
echo "remaining mutter: $(pgrep -ax mutter | wc -l)  app: $(pgrep -f wl-slice-app.py | wc -l)"
echo "### DONE"
