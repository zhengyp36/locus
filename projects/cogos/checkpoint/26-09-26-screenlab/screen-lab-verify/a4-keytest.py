import sys

import gi

gi.require_version("Atspi", "2.0")
from gi.repository import Atspi

target = sys.argv[1] if len(sys.argv) > 1 else "A4-TEXT"
Atspi.init()
desktop = Atspi.get_desktop(0)
res = []


def walk(node):
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
        if nm == target:
            res.append(ch)
        walk(ch)


for i in range(desktop.get_child_count()):
    app = desktop.get_child_at_index(i)
    try:
        an = app.get_name() or ""
    except Exception:
        continue
    if "chrom" in an.lower():
        walk(app)

if not res:
    print("NOTFOUND")
    sys.exit(3)

ch = res[-1]
ext = ch.get_extents(Atspi.CoordType.SCREEN)
print("EXT x=%d y=%d w=%d h=%d" % (ext.x, ext.y, ext.width, ext.height))
try:
    gf = ch.get_component_iface().grab_focus()
    print("GRAB %s" % gf)
except Exception as e:
    print("GRAB-ERR %s" % e)
print("CENTER %d %d" % (ext.x + ext.width // 2, ext.y + ext.height // 2))
