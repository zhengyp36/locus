import sys
import time

import gi

gi.require_version("Atspi", "2.0")
from gi.repository import Atspi, Gio, GLib

TARGETS = ("A4-TEXT", "A4-TEXTAREA")
Atspi.init()
desktop = Atspi.get_desktop(0)
found = []
t0 = time.time()


def walk(node):
    if time.time() - t0 > 30:
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

print("FOUND", [n for n, _ in found], flush=True)

for nm, ch in found:
    print("=== %s ===" % nm, flush=True)
    for mod, fn, args in (
        ("EditableText", "set_text_contents", ("ATSPI-EDIT",)),
        ("EditableText", "get_text", ()),
        ("Text", "get_text", (0, -1)),
        ("Text", "get_character_count", ()),
    ):
        obj = getattr(Atspi, mod, None)
        f = getattr(obj, fn, None) if obj else None
        if not f:
            print("  %s.%s: no such static fn" % (mod, fn), flush=True)
            continue
        try:
            r = f(ch, *args)
            print("  %s.%s(%s) -> %r" % (mod, fn, args, r), flush=True)
        except Exception as e:
            print("  %s.%s(%s) ERR %s: %s" % (mod, fn, args, type(e).__name__, e), flush=True)

# D-Bus introspection of the A4-TEXT accessible object
session = Gio.bus_get_sync(Gio.BusType.SESSION, None)
addr = session.call_sync("org.a11y.Bus", "/org/a11y/bus", "org.a11y.Bus",
                         "GetAddress", None, None, Gio.DBusCallFlags.NONE,
                         5000, None).unpack()[0]
conn = Gio.DBusConnection.new_for_address_sync(
    addr, Gio.DBusConnectionFlags.AUTHENTICATION_CLIENT |
    Gio.DBusConnectionFlags.MESSAGE_BUS_CONNECTION, None, None)

hits = []


def GetChildren(dest, path):
    try:
        r = conn.call_sync(dest, path, "org.a11y.atspi.Accessible", "GetChildren",
                           None, None, Gio.DBusCallFlags.NONE, 5000, None)
        return r.unpack()[0]
    except Exception as e:
        return []


def NameOf(dest, path):
    try:
        r = conn.call_sync(dest, path, "org.a11y.atspi.Accessible", "Name",
                           None, None, Gio.DBusCallFlags.NONE, 5000, None)
        return r.unpack()[0]
    except Exception:
        return None


def find(dest, path, depth=0):
    if depth > 25 or len(hits) > 3:
        return
    nm = NameOf(dest, path)
    if nm in TARGETS:
        hits.append((nm, dest, path))
        return
    for ref in GetChildren(dest, path):
        b, p = ref[0], ref[1]
        find(b or dest, p, depth + 1)


find("org.a11y.atspi.Registry", "/org/a11y/atspi/accessible/root")
print("DBUS-HITS", hits, flush=True)

for nm, dest, path in hits[:1]:
    try:
        xml = conn.call_sync(dest, path, "org.freedesktop.DBus.Introspectable",
                             "Introspect", None, None, Gio.DBusCallFlags.NONE,
                             5000, None).unpack()[0]
        ifaces = [ln.strip() for ln in xml.splitlines() if "<interface" in ln]
        print("IFACES of %s: %s" % (nm, ifaces), flush=True)
    except Exception as e:
        print("introspect ERR", e, flush=True)

print("DONE", flush=True)
