import sys
import time

import gi

gi.require_version("Atspi", "2.0")
from gi.repository import Atspi

Atspi.init()
desktop = Atspi.get_desktop(0)


def walk(node, out):
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
        if nm and nm.startswith("A4-"):
            try:
                ext = ch.get_extents(Atspi.CoordType.SCREEN)
                out.append((nm, ch.get_role_name(),
                            ext.x, ext.y, ext.width, ext.height))
            except Exception as e:
                out.append((nm, "?", -1, -1, -1, -1))
        walk(ch, out)


out = []
for i in range(desktop.get_child_count()):
    app = desktop.get_child_at_index(i)
    try:
        an = app.get_name() or ""
    except Exception:
        continue
    if "chrom" in an.lower():
        walk(app, out)

for nm, role, x, y, w, h in sorted(out):
    print("EXT %-14s role=%-16s x=%-6d y=%-6d w=%-6d h=%-6d" % (nm, role, x, y, w, h))
print("N=%d" % len(out))
