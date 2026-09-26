import sys

import gi

gi.require_version("Atspi", "2.0")
from gi.repository import Atspi

Atspi.init()
desktop = Atspi.get_desktop(0)

chrome = None
for i in range(desktop.get_child_count()):
    a = desktop.get_child_at_index(i)
    try:
        nm = a.get_name() or ""
    except Exception:
        nm = ""
    if "chrom" in nm.lower():
        chrome = a

if chrome is None:
    print("NO-CHROME")
    sys.exit(3)


def rn(n):
    try:
        return n.get_role_name()
    except Exception:
        return "?"


def nm_of(n):
    try:
        return n.get_name()
    except Exception:
        return None


frames = []
docs = []


def walk(n, depth=0):
    if depth > 60:
        return
    try:
        cnt = n.get_child_count()
    except Exception:
        return
    r = rn(n)
    if r == "frame":
        frames.append(n)
    if r in ("document web", "document frame", "document"):
        docs.append(n)
    for i in range(cnt):
        try:
            ch = n.get_child_at_index(i)
        except Exception:
            continue
        if ch:
            walk(ch, depth + 1)


walk(chrome)
print("FRAMES:", [nm_of(f) for f in frames])
for d in docs:
    try:
        cc = d.get_child_count()
    except Exception:
        cc = -1
    print("DOC role=%s name=%r children=%d" % (rn(d), nm_of(d), cc))
    for i in range(min(cc, 60)):
        try:
            ch = d.get_child_at_index(i)
            print("   [%d] role=%-16s name=%r" % (i, rn(ch), nm_of(ch)))
        except Exception as e:
            print("   [%d] ERR %s" % (i, e))
