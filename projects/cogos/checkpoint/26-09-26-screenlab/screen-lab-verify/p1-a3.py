import os
import sys
import time

import gi

gi.require_version("Atspi", "2.0")
from gi.repository import Atspi

TARGET = os.environ.get("TARGET", "A4-BUTTON")
DEADLINE_MS = float(os.environ.get("DEADLINE_MS", "200"))

Atspi.init()
desktop = Atspi.get_desktop(0)


def chrome_app():
    for i in range(desktop.get_child_count()):
        app = desktop.get_child_at_index(i)
        try:
            nm = app.get_name() or ""
        except Exception:
            continue
        if "chrom" in nm.lower():
            return app
    return None


def walk(root, deadline_ms, want):
    t0 = time.time()
    budget = deadline_ms / 1000.0
    nodes = 0
    hits = []
    aborted = False
    stack = [root]
    while stack:
        if time.time() - t0 > budget:
            aborted = True
            break
        node = stack.pop()
        try:
            cnt = node.get_child_count()
        except Exception:
            continue
        for i in range(cnt):
            if time.time() - t0 > budget:
                aborted = True
                break
            try:
                ch = node.get_child_at_index(i)
            except Exception:
                continue
            if ch is None:
                continue
            nodes += 1
            try:
                nm = ch.get_name()
            except Exception:
                nm = None
            if want and nm == want:
                hits.append(ch)
            stack.append(ch)
        if aborted:
            break
    return nodes, hits, aborted, (time.time() - t0) * 1000.0


chrome = chrome_app()
print("CHROME=%s" % (chrome.get_name() if chrome else None))

n_full, hit_full, ab_full, ms_full = walk(desktop, 60000, TARGET)
print("FULL   nodes=%d ms=%.1f found=%d aborted=%s" % (n_full, ms_full, len(hit_full), ab_full))

n_sub, hit_sub, ab_sub, ms_sub = walk(chrome, 60000, TARGET)
print("SUB    nodes=%d ms=%.1f found=%d aborted=%s" % (n_sub, ms_sub, len(hit_sub), ab_sub))

for dl in (200, 20):
    n, h, ab, ms = walk(chrome, dl, TARGET)
    print("DEADLINE %dms nodes=%d ms=%.1f found=%d aborted=%s" % (dl, n, ms, len(h), ab))

if not hit_sub:
    print("NOTFOUND")
    sys.exit(3)

ch = hit_sub[-1]
ext = ch.get_extents(Atspi.CoordType.SCREEN)
print("EXT x=%d y=%d w=%d h=%d" % (ext.x, ext.y, ext.width, ext.height))
print("CENTER %d %d" % (ext.x + ext.width // 2, ext.y + ext.height // 2))
