import sys
import time
import gi

gi.require_version('Gio', '2.0')
from gi.repository import Gio, GLib

SC = 'org.gnome.Mutter.ScreenCast'
SC_PATH = '/org/gnome/Mutter/ScreenCast'
bus = Gio.bus_get_sync(Gio.BusType.SESSION, None)
node = {'id': None}


def call(dest, path, iface, method, params=None, timeout=10000):
    try:
        r = bus.call_sync(dest, path, iface, method, params, None,
                          Gio.DBusCallFlags.NONE, timeout, None)
        return r.unpack()
    except GLib.Error as e:
        print("ERR %s.%s: %s" % (iface, method, e.message), flush=True)
        return None


r = call(SC, SC_PATH, SC, 'CreateSession', GLib.Variant('(a{sv})', ({},)))
session = r[0]
print("session:", session, flush=True)
r = call(SC, session, SC + '.Session', 'RecordVirtual', GLib.Variant('(a{sv})', ({},)))
print("stream:", r[0] if r else None, flush=True)
stream_path = r[0] if r else None
bus.signal_subscribe(SC, SC + '.Stream', 'PipeWireStreamAdded', stream_path, None,
                     Gio.DBusSignalFlags.NONE,
                     lambda *a: node.__setitem__('id', a[5].unpack()[0]))
print("Session.Start ->", call(SC, session, SC + '.Session', 'Start'), flush=True)

for _ in range(50):
    if node['id'] is not None:
        break
    time.sleep(0.1)
print("NODE=%s" % node['id'], flush=True)
sys.stdout.flush()

secs = int(sys.argv[1]) if len(sys.argv) > 1 else 60
time.sleep(secs)
print("closing session", flush=True)
call(SC, session, SC + '.Session', 'Stop')
