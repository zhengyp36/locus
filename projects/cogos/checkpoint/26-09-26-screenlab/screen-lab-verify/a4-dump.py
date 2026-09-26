import sys
import time

import gi

gi.require_version("Atspi", "2.0")
from gi.repository import Atspi

LIMIT = 200
if "--limit" in sys.argv:
    LIMIT = int(sys.argv[sys.argv.index("--limit") + 1])

Atspi.init()
desktop = Atspi.get_desktop(0)

apps = []
for i in range(desktop.get_child_count()):
    a = desktop.get_child_at_index(i)
    try:
        apps.append(a.get_name())
    except Exception:
        apps.append("?")
print("APPS:", apps, flush=True)

target = None
for i in range(desktop.get_child_count()):
    a = desktop.get_child_at_index(i)
    try:
        nm = a.get_name() or ""
    except Exception:
        nm = ""
    if "chrom" in nm.lower():
        target = a
        break
if target is None:
    print("NO-CHROME", flush=True)
    sys.exit(3)

print("CHROME APP NAME:", target.get_name(), flush=True)

t0 = time.time()
n = [0]


def walk(node, depth):
    if depth > 40 or n[0] >= LIMIT:
        return
    try:
        cnt = node.get_child_count()
    except Exception:
        return
    for i in range(cnt):
        if n[0] >= LIMIT:
            return
        try:
            ch = node.get_child_at_index(i)
        except Exception:
            continue
        if ch is None:
            continue
        n[0] += 1
        try:
            nm = ch.get_name()
        except Exception:
            nm = None
        try:
            role = ch.get_role_name()
        except Exception:
            role = "?"
        try:
            na = ch.get_n_actions()
        except Exception:
            na = 0
        acts = []
        for k in range(na):
            try:
                acts.append(str(ch.get_action_name(k)))
            except Exception:
                acts.append("?")
        print("%s[%d] role=%-18s n_act=%d %s name=%r"
              % ("  " * depth, i, role, na, ",".join(acts), nm), flush=True)
        walk(ch, depth + 1)


walk(target, 0)
print("DUMP nodes=%d elapsed=%.2fs" % (n[0], time.time() - t0), flush=True)
