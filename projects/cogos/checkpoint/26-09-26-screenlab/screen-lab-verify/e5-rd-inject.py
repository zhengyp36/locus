import sys
import gi

gi.require_version('Gio', '2.0')
from gi.repository import Gio, GLib

cx = float(sys.argv[1])
cy = float(sys.argv[2])

RD = 'org.gnome.Mutter.RemoteDesktop'
OBJ = '/org/gnome/Mutter/RemoteDesktop'
S = 'org.gnome.Mutter.RemoteDesktop.Session'

conn = Gio.bus_get_sync(Gio.BusType.SESSION, None)

res = conn.call_sync(RD, OBJ, RD, 'CreateSession', None,
                     GLib.VariantType.new('(o)'),
                     Gio.DBusCallFlags.NONE, -1, None)
sp = res.unpack()[0]
print("session:", sp, flush=True)


def call(method, params=None, reply=None):
    return conn.call_sync(RD, sp, S, method, params, reply,
                          Gio.DBusCallFlags.NONE, -1, None)


call('Start')
print("started", flush=True)

call('NotifyPointerMotionRelative', GLib.Variant('(dd)', (-10000.0, -10000.0)))
print("moved to corner", flush=True)
call('NotifyPointerMotionRelative', GLib.Variant('(dd)', (cx, cy)))
print("moved to %.0f,%.0f" % (cx, cy), flush=True)

call('NotifyPointerButton', GLib.Variant('(ib)', (1, True)))
GLib.usleep(80000)
call('NotifyPointerButton', GLib.Variant('(ib)', (1, False)))
print("clicked", flush=True)

GLib.usleep(200000)
call('Stop')
print("stopped", flush=True)
