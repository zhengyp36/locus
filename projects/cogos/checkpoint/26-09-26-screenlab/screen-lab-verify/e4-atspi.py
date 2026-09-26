import sys
import time
import gi

gi.require_version('Atspi', '2.0')
from gi.repository import Atspi

want = "CLICK-ME"
Atspi.init()
desktop = Atspi.get_desktop(0)

nodes = [0]
found = []
t0 = time.time()


def walk(node, depth=0):
    if node is None or found:
        return
    try:
        count = node.get_child_count()
    except Exception:
        return
    for i in range(count):
        if found:
            return
        try:
            child = node.get_child_at_index(i)
        except Exception:
            continue
        if child is None:
            continue
        nodes[0] += 1
        try:
            name = child.get_name()
        except Exception:
            name = None
        if name and name.startswith(want):
            found.append(child)
            return
        if name:
            print("  " * depth + "%s" % name, flush=True)
        walk(child, depth + 1)


for i in range(desktop.get_child_count()):
    app = desktop.get_child_at_index(i)
    try:
        aname = app.get_name()
    except Exception:
        aname = "?"
    print("== app:", aname, flush=True)
    walk(app, 1)

elapsed = time.time() - t0
print("NODES %d ELAPSED %.3fs" % (nodes[0], elapsed), flush=True)

if not found:
    print("NOT-FOUND", flush=True)
    sys.exit(3)

target = found[0]
comp = None
for attr in ("get_component_iface", "query_component", "get_component"):
    if hasattr(target, attr):
        try:
            comp = getattr(target, attr)()
            if comp:
                break
        except Exception:
            pass

if comp is None:
    print("NO-COMPONENT", flush=True)
    sys.exit(4)

ext = comp.get_extents(Atspi.CoordType.SCREEN)
cx = ext.x + ext.width // 2
cy = ext.y + ext.height // 2
print("FOUND extents x=%d y=%d w=%d h=%d" % (ext.x, ext.y, ext.width, ext.height), flush=True)
print("CENTER %d %d" % (cx, cy), flush=True)
