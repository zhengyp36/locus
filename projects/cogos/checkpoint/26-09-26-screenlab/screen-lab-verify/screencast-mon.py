import sys
import time
import gi

gi.require_version('Gio', '2.0')
from gi.repository import Gio, GLib

SC = 'org.gnome.Mutter.ScreenCast'
SC_PATH = '/org/gnome/Mutter/ScreenCast'
DC = 'org.gnome.Mutter.DisplayConfig'
DC_PATH = '/org/gnome/Mutter/DisplayConfig'
bus = Gio.bus_get_sync(Gio.BusType.SESSION, None)


def call(dest, path, iface, method, params=None, timeout=10000):
    try:
        r = bus.call_sync(dest, path, iface, method, params, None,
                          Gio.DBusCallFlags.NONE, timeout, None)
        return r.unpack()
    except GLib.Error as e:
        print("ERR %s.%s: %s" % (iface, method, e.message), flush=True)
        return None


state = call(DC, DC_PATH, DC, 'GetCurrentState')
connector = None
if state:
    for mon in state[1]:
        connector = mon[0][0]
        print("monitor connector:", connector, flush=True)
        break

r = call(SC, SC_PATH, SC, 'CreateSession', GLib.Variant('(a{sv})', ({},)))
session = r[0]
print("session:", session, flush=True)

node = {'id': None}
r = call(SC, session, SC + '.Session', 'RecordMonitor',
         GLib.Variant('(sa{sv})', (connector, {})))
print("RecordMonitor ->", r, flush=True)
if r:
    stream_path = r[0]
    bus.signal_subscribe(SC, SC + '.Stream', 'PipeWireStreamAdded', stream_path, None,
                         Gio.DBusSignalFlags.NONE,
                         lambda *a: node.__setitem__('id', a[5].unpack()[0]))
print("Session.Start ->", call(SC, session, SC + '.Session', 'Start'), flush=True)
for _ in range(50):
    if node['id'] is not None:
        break
    time.sleep(0.1)
print("NODE=%s" % node['id'], flush=True)
time.sleep(int(sys.argv[1]) if len(sys.argv) > 1 else 20)
call(SC, session, SC + '.Session', 'Stop')
