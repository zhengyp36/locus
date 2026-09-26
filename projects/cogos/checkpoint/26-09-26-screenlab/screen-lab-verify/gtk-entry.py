import sys
import time

import gi

gi.require_version("Gtk", "3.0")
gi.require_version("Atspi", "2.0")
from gi.repository import Gtk, GLib, Atspi

MODE = sys.argv[1] if len(sys.argv) > 1 else "client"

if MODE == "client":
    w = Gtk.Window(title="EDITWIN")
    e = Gtk.Entry()
    try:
        e.get_accessible().set_name("EDIT-ME")
    except Exception as ex:
        print("set_accessible_name ERR", ex, flush=True)
    e.set_text("seed")
    w.add(e)
    w.connect("destroy", Gtk.main_quit)
    w.show_all()
    GLib.timeout_add_seconds(60, Gtk.main_quit)
    print("CLIENT-UP", flush=True)
    Gtk.main()
    sys.exit(0)

Atspi.init()
desktop = Atspi.get_desktop(0)
found = []
t0 = time.time()


def walk(node):
    if time.time() - t0 > 20:
        return
    try:
        cnt = node.get_child_count()
    except Exception:
        return
    for i in range(cnt):
        try:
            ch = node.get_child_at_index(i)
        except Exception:
            continue
        if ch is None:
            continue
        try:
            nm = ch.get_name()
        except Exception:
            nm = None
        if nm == "EDIT-ME":
            found.append(ch)
        walk(ch)


for i in range(desktop.get_child_count()):
    walk(desktop.get_child_at_index(i))

print("FOUND", len(found), flush=True)
for ch in found[:1]:
    et = ch.get_editable_text_iface()
    print("get_editable_text_iface ->", "OBJ" if et else None, flush=True)
    try:
        print("Text.get_text ->", repr(Atspi.Text.get_text(ch, 0, -1)), flush=True)
    except Exception as ex:
        print("Text.get_text ERR", ex, flush=True)
    try:
        r = Atspi.EditableText.set_text_contents(ch, "GTK-EDIT")
        print("EditableText.set_text_contents ->", r, flush=True)
    except Exception as ex:
        print("EditableText ERR", type(ex).__name__, ex, flush=True)
    time.sleep(1)
    try:
        print("Text.get_text after ->", repr(Atspi.Text.get_text(ch, 0, -1)), flush=True)
    except Exception as ex:
        print("read-after ERR", ex, flush=True)
print("DONE", flush=True)
