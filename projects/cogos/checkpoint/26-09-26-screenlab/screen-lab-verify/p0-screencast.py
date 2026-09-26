import sys, subprocess
import gi
gi.require_version('Gio', '2.0')
from gi.repository import Gio, GLib

SC = 'org.gnome.Mutter.ScreenCast'
SC_PATH = '/org/gnome/Mutter/ScreenCast'
MON = '/org/gnome/Mutter/DisplayConfig/Meta-0'

bus = Gio.bus_get_sync(Gio.BusType.SESSION, None)


def call(dest, path, iface, method, params=None, timeout=10000):
    try:
        r = bus.call_sync(dest, path, iface, method, params, None,
                          Gio.DBusCallFlags.NONE, timeout, None)
        return r.unpack()
    except GLib.Error as e:
        print("ERR %s.%s: %s" % (iface, method, e.message))
        return None


r = call(SC, SC_PATH, SC, 'CreateSession', GLib.Variant('(a{sv})', ({},)))
if not r:
    sys.exit(1)
session = r[0]
print("session:", session)

stream = None
r = call(SC, session, SC + '.Session', 'RecordVirtual', GLib.Variant('(a{sv})', ({},)))
if r:
    stream = r[0]
    print("stream(virtual):", stream)
else:
    r = call(SC, session, SC + '.Session', 'RecordMonitor',
             GLib.Variant('(oa{sv})', (MON, {})))
    if r:
        stream = r[0]
        print("stream(monitor):", stream)
if not stream:
    print("NO-STREAM")
    sys.exit(1)

loop = GLib.MainLoop()
node = {'id': None}


def on_sig(conn, sender, path, iface, signal, params):
    print("SIGNAL", signal, params.unpack())
    if signal == 'PipeWireStreamAdded':
        node['id'] = params.unpack()[0]
        GLib.timeout_add(100, loop.quit)


bus.signal_subscribe(SC, SC + '.Stream', 'PipeWireStreamAdded', stream, None,
                     Gio.DBusSignalFlags.NONE, on_sig)

print("Stream.Start ->", call(SC, stream, SC + '.Stream', 'Start'))
print("Session.Start ->", call(SC, session, SC + '.Session', 'Start'))
GLib.timeout_add_seconds(8, loop.quit)
loop.run()
print("node:", node['id'])

if node['id'] is None:
    print("NO-NODE")
    sys.exit(1)

out = '/tmp/p0-frame.png'
try:
    subprocess.run(['rm', '-f', out], check=False)
except Exception:
    pass
cmd = ['gst-launch-1.0', '-q', 'pipewiresrc', 'path=%d' % node['id'],
       'num-buffers=1', '!', 'videoconvert', '!', 'pngenc',
       '!', 'filesink', 'location=' + out]
print("gst:", ' '.join(cmd))
try:
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=40)
    print("gst rc", p.returncode)
    if p.stderr:
        print("gst stderr tail:", p.stderr[-600:])
except Exception as e:
    print("gst exception:", e)

import os
if os.path.exists(out):
    print("FRAME-OK", out, os.path.getsize(out), "bytes")
    from PIL import Image
    im = Image.open(out)
    print("frame size:", im.size, im.mode)
else:
    print("FRAME-MISSING")
