set -u
export XDG_RUNTIME_DIR=/run/user/1001
if [ -z "${DBUS_SESSION_BUS_ADDRESS:-}" ] && [ -S /run/user/1001/bus ]; then
  export DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1001/bus
fi
echo "### env"; echo "user=$(id -un) bus=${DBUS_SESSION_BUS_ADDRESS:-unset}"

echo "### atspi"
systemctl --user start at-spi-dbus-bus.service 2>&1 || true
echo "at-spi: $(systemctl --user is-active at-spi-dbus-bus.service)"

echo "### compositor: mutter --headless --virtual-monitor 1280x720"
pkill -x mutter 2>/dev/null; sleep 1
rm -f /tmp/wl2-mutter.log
setsid mutter --headless --virtual-monitor 1280x720 --wayland-display=wl-slice2 >/tmp/wl2-mutter.log 2>&1 &
sleep 6
XDISP=$(grep -oP 'Using public X11 display :\K[0-9]+' /tmp/wl2-mutter.log | head -1)
echo "xdisplay=:${XDISP:-MISSING}"
export DISPLAY=:${XDISP}
echo "xdotool geometry: $(xdotool getdisplaygeometry 2>&1)"
echo "grep virtual-monitor: $(grep -i -E 'virtual|monitor|renderD128|mode setting|card0' /tmp/wl2-mutter.log | head -8)"

echo "### gtk app"
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
echo "app: $(pgrep -af wl-slice-app.py | head -1)"

echo "### a11y tree"
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
            if name or role in ("push button", "frame", "application"):
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
echo "app log:"; tail -3 /tmp/wl-slice-app.log 2>&1

echo "### pixels"
python3 - <<'PY'
import os
from PIL import ImageGrab
im = ImageGrab.grab(xdisplay=os.environ["DISPLAY"])
print("capture size", im.size)
im.save("/tmp/wl-slice2.png")
print("saved /tmp/wl-slice2.png")
PY

echo "### cleanup"
pkill -x mutter 2>/dev/null; sleep 1
pkill -f wl-slice-app.py 2>/dev/null; sleep 1
echo "remaining mutter=$(pgrep -x mutter | wc -l) app=$(pgrep -f wl-slice-app.py | wc -l)"
echo "### DONE"
