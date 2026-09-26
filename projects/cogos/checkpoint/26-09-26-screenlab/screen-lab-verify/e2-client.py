import sys
import gi

gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
from gi.repository import Gtk, Gdk, GLib

secs = 6
for i, a in enumerate(sys.argv):
    if a == '--secs' and i + 1 < len(sys.argv):
        secs = int(sys.argv[i + 1])

try:
    Gtk.init([])
except Exception as e:
    print("Gtk init FAILED:", e, flush=True)
    sys.exit(2)

d = Gdk.Display.get_default()
print("display:", d, "type:", type(d).__name__ if d else None, flush=True)
if d:
    n = d.get_n_monitors()
    print("n_monitors:", n, flush=True)
    for i in range(n):
        m = d.get_monitor(i)
        g = m.get_geometry()
        print(
            "monitor[%d] model=%r manuf=%r geom=%dx%d+%d+%d scale=%d refresh=%d primary=%s"
            % (i, m.get_model(), m.get_manufacturer(), g.width, g.height,
               g.x, g.y, m.get_scale_factor(), m.get_refresh_rate(), m.is_primary()),
            flush=True,
        )

win = Gtk.Window(title="SCREENLAB-WINDOW")
win.set_default_size(400, 300)
btn = Gtk.Button(label="CLICK-ME")
btn.connect("clicked", lambda *_: print("BTN-CLICKED", flush=True))
win.add(btn)
win.add_events(
    Gdk.EventMask.POINTER_MOTION_MASK
    | Gdk.EventMask.ENTER_NOTIFY_MASK
    | Gdk.EventMask.LEAVE_NOTIFY_MASK
    | Gdk.EventMask.BUTTON_PRESS_MASK
)


def on_event(name):
    def handler(widget, event):
        print("%s %.0f,%.0f" % (name, getattr(event, 'x', -1), getattr(event, 'y', -1)), flush=True)
        return False
    return handler


btn.connect("enter-notify-event", on_event("BTN-ENTER"))
btn.connect("leave-notify-event", on_event("BTN-LEAVE"))
btn.connect("button-press-event", on_event("BTN-PRESS"))
win.connect("destroy", lambda *_: Gtk.main_quit())
win.show_all()


def report():
    gdkwin = win.get_window()
    if gdkwin:
        print("toplevel gdk size: %dx%d" % (gdkwin.get_width(), gdkwin.get_height()), flush=True)
    scr = Gdk.Screen.get_default()
    if scr:
        print("screen size: %dx%d" % (scr.get_width(), scr.get_height()), flush=True)
    return False


blink = '--blink' in sys.argv
if blink:
    state = {'n': 0}

    def tick():
        state['n'] += 1
        try:
            win.get_child().set_label("CLICK-ME %d" % state['n'])
        except Exception:
            pass
        return True

    GLib.timeout_add(300, tick)

GLib.timeout_add(1500, report)
GLib.timeout_add(secs * 1000, Gtk.main_quit)
Gtk.main()
print("client exited", flush=True)
