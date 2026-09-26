import sys
import time

import gi

gi.require_version("Atspi", "2.0")
from gi.repository import Atspi, Gio, GLib

TARGETS = ("A4-TEXT", "A4-TEXTAREA", "A4-RANGE", "A4-SELECT")
Atspi.init()
desktop = Atspi.get_desktop(0)
found = []
t0 = time.time()


def walk(node):
    if time.time() - t0 > 40:
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
        if nm in TARGETS:
            found.append((nm, ch))
        walk(ch)


for i in range(desktop.get_child_count()):
    app = desktop.get_child_at_index(i)
    try:
        an = app.get_name()
    except Exception:
        an = "?"
    if "chrom" in (an or "").lower():
        walk(app)

if not found:
    print("NO-NODES", flush=True)
    sys.exit(3)

session = Gio.bus_get_sync(Gio.BusType.SESSION, None)
try:
    addr = session.call_sync("org.a11y.Bus", "/org/a11y/bus", "org.a11y.Bus",
                             "GetAddress", None, None, Gio.DBusCallFlags.NONE,
                             5000, None).unpack()[0]
except Exception as e:
    print("a11y bus addr ERR", e, flush=True)
    sys.exit(1)
print("a11y bus:", addr, flush=True)
conn = Gio.DBusConnection.new_for_address_sync(
    addr, Gio.DBusConnectionFlags.AUTHENTICATION_CLIENT |
    Gio.DBusConnectionFlags.MESSAGE_BUS_CONNECTION, None, None)

names = conn.call_sync("org.freedesktop.DBus", "/org/freedesktop/DBus",
                       "org.freedesktop.DBus", "ListNames", None, None,
                       Gio.DBusCallFlags.NONE, 5000, None).unpack()[0]
print("bus names:", [n for n in names if not n.startswith("org.freedesktop")][:20], flush=True)


def introspect(dest, path):
    try:
        xml = conn.call_sync(dest, path, "org.freedesktop.DBus.Introspectable",
                             "Introspect", None, None, Gio.DBusCallFlags.NONE,
                             5000, None).unpack()[0]
        return xml
    except Exception as e:
        return "ERR %s" % e


def node_refs(dest, path):
    try:
        r = conn.call_sync(dest, path, "org.a11y.atspi.Accessible",
                           "GetChildren", None, None, Gio.DBusCallFlags.NONE,
                           5000, None).unpack()[0]
        return r
    except Exception as e:
        return [("ERR", str(e))]


# probe the D-Bus expose of one found node via Atspi object path heuristics
for nm, ch in found:
    ifaces = " ".join(sorted(
        x for x in dir(Atspi) if "ditable" in x or x in ("Text", "Accessible")))
    print("--- %s" % nm, flush=True)
    for meth in ("get_editable_text_iface", "get_text_iface", "get_component_iface",
                 "get_action_iface", "get_value_iface"):
        f = getattr(ch, meth, None)
        try:
            o = f() if f else None
            print("   %s -> %s" % (meth, "OBJ" if o else None), flush=True)
        except Exception as e:
            print("   %s -> ERR %s" % (meth, e), flush=True)
    for meth in ("get_object_path", "get_bus_name", "get_accessible_id", "get_application"):
        f = getattr(ch, meth, None)
        if not f:
            continue
        try:
            print("   %s() -> %s" % (meth, f()), flush=True)
        except Exception as e:
            print("   %s() -> ERR %s" % (meth, e), flush=True)
    break

print("ATSPI-MODULE editable/text syms:", [x for x in dir(Atspi)
      if "ditable" in x or x == "Text"], flush=True)
print("DONE-PROBE", flush=True)
