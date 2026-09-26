import sys

import gi

gi.require_version('Gio', '2.0')
gi.require_version('Gst', '1.0')
from gi.repository import Gio, GLib, Gst

N = int(sys.argv[1]) if len(sys.argv) > 1 else 3
DUR = float(sys.argv[2]) if len(sys.argv) > 2 else 6.0

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
        break
print("connector=%s" % connector, flush=True)

r = call(SC, SC_PATH, SC, 'CreateSession', GLib.Variant('(a{sv})', ({},)))
session = r[0]
node = {'id': None}
r = call(SC, session, SC + '.Session', 'RecordMonitor',
         GLib.Variant('(sa{sv})', (connector, {})))
stream_path = r[0]
bus.signal_subscribe(SC, SC + '.Stream', 'PipeWireStreamAdded', stream_path, None,
                     Gio.DBusSignalFlags.NONE,
                     lambda *a: node.__setitem__('id', a[5].unpack()[0]))
print("Session.Start ->", call(SC, session, SC + '.Session', 'Start'), flush=True)
import time
main = GLib.MainContext.default()
for _ in range(100):
    if node['id'] is not None:
        break
    while main.pending():
        main.iteration(False)
    time.sleep(0.05)
nid = node['id']
if nid is None:
    import subprocess
    try:
        out = subprocess.check_output(["wpctl", "status"], text=True)
        in_video = False
        for line in out.splitlines():
            if line.strip().startswith("Video"):
                in_video = True
                continue
            if in_video and line.strip() and line.strip()[0].isdigit():
                nid = int(line.strip().split(".")[0])
                break
    except Exception as e:
        print("wpctl fallback failed: %s" % e, flush=True)
print("NODE=%s" % nid, flush=True)
if nid is None:
    sys.exit(3)

Gst.init(None)
branches = " ".join(
    "t. ! queue ! videoconvert ! appsink name=sink%d emit-signals=true max-buffers=2 drop=true" % i
    for i in range(N))
desc = "pipewiresrc path=%d ! videoconvert ! tee name=t %s" % (nid, branches)
print("PIPELINE=%s" % desc, flush=True)
pipeline = Gst.parse_launch(desc)

stats = {}


def make_cb(i):
    def cb(sink):
        s = sink.emit("pull-sample")
        if s is None:
            return Gst.FlowReturn.OK
        buf = s.get_buffer()
        st = stats.setdefault(i, {"n": 0, "bytes": 0, "caps": None, "pts": None})
        st["n"] += 1
        st["bytes"] = buf.get_size()
        st["pts"] = buf.pts
        if st["caps"] is None:
            c = s.get_caps()
            st["caps"] = c.to_string() if c else None
        return Gst.FlowReturn.OK
    return cb


for i in range(N):
    sink = pipeline.get_by_name("sink%d" % i)
    sink.connect("new-sample", make_cb(i))

pipeline.set_state(Gst.State.PLAYING)
loop = GLib.MainLoop()
GLib.timeout_add(int(DUR * 1000), lambda: (loop.quit(), False)[1])
loop.run()
pipeline.set_state(Gst.State.NULL)

ok = 0
for i in range(N):
    st = stats.get(i, {"n": 0, "bytes": 0, "caps": None, "pts": None})
    if st["n"] > 0:
        ok += 1
    print("SUB %d frames=%d last_bytes=%d caps=%s last_pts=%s"
          % (i, st["n"], st["bytes"], st["caps"], st["pts"]), flush=True)
print("RESULT subscribers_with_frames=%d/%d" % (ok, N), flush=True)
print("DONE-FANOUT", flush=True)
