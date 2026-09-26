import sys
import time

import gi

gi.require_version("Atspi", "2.0")
from gi.repository import Atspi

TARGETS = ("A4-TEXT", "A4-SELECT")
Atspi.init()
desktop = Atspi.get_desktop(0)
found = []
t0 = time.time()


def walk(node, depth=0):
    if time.time() - t0 > 40:
        return
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
            rl = ch.get_role_name()
        except Exception:
            nm, rl = None, "?"
        if nm in TARGETS:
            found.append((nm, rl, ch))
        if rl in ("menu item", "list item", "option", "check box", "radio button") and depth < 40:
            found.append(("MENUITEM:%s" % (nm or rl), rl, ch))
        walk(ch, depth + 1)


for i in range(desktop.get_child_count()):
    app = desktop.get_child_at_index(i)
    try:
        an = app.get_name()
    except Exception:
        an = "?"
    if "chrom" in (an or "").lower():
        walk(app)

print("FOUND", [(n, r) for n, r, _ in found], flush=True)

targets = {n: (r, c) for n, r, c in found}
if "A4-TEXT" in targets:
    rl, ch = targets["A4-TEXT"]
    comp = ch.get_component_iface()
    try:
        print("grab_focus ->", comp.grab_focus(), flush=True)
    except Exception as e:
        print("grab_focus ERR", e, flush=True)
    time.sleep(1)
    ok = 0
    for ks in ("h", "i", "!"):
        try:
            r = Atspi.generate_keyboard_event(0, ks, 0)
            print("key %r -> %s" % (ks, r), flush=True)
            ok += 1
        except Exception as e:
            print("key %r ERR %s" % (ks, e), flush=True)
    print("keys_sent=%d" % ok, flush=True)
    time.sleep(1)

if "A4-SELECT" in targets:
    rl, ch = targets["A4-SELECT"]
    a = ch.get_action_iface()
    for k in range(a.get_n_actions()):
        if "open" in (a.get_action_name(k) or "").lower():
            a.do_action(k)
            break
    time.sleep(2)
    found.clear()
    t0 = time.time()
    for i in range(desktop.get_child_count()):
        app = desktop.get_child_at_index(i)
        try:
            an = app.get_name()
        except Exception:
            an = "?"
        if "chrom" in (an or "").lower():
            walk(app)
    items = [(n, r, c) for n, r, c in found if n.startswith("MENUITEM")]
    print("AFTER-OPEN items=%d" % len(items), flush=True)
    for n, r, c in items[:6]:
        a2 = c.get_action_iface()
        names = []
        try:
            names = [a2.get_action_name(k) for k in range(a2.get_n_actions())]
        except Exception:
            pass
        print("  item %r role=%s actions=%s" % (n, r, names), flush=True)
        for k, an2 in enumerate(names):
            if "click" in (an2 or "").lower() or "press" in (an2 or "").lower() or "select" in (an2 or "").lower():
                try:
                    c.do_action(k)
                    print("    -> did %s" % an2, flush=True)
                except Exception as e:
                    print("    do ERR %s" % e, flush=True)
                break
print("DONE2", flush=True)
