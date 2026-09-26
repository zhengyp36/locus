import sys
import time

import gi

gi.require_version("Atspi", "2.0")
from gi.repository import Atspi

TARGETS = ("A4-TEXT", "A4-TEXTAREA", "A4-RANGE", "A4-SELECT")
DEADLINE = 60.0

Atspi.init()
desktop = Atspi.get_desktop(0)
found = []
t0 = time.time()


def walk(node):
    if time.time() - t0 > DEADLINE:
        return
    try:
        cnt = node.get_child_count()
    except Exception:
        return
    for i in range(cnt):
        if time.time() - t0 > DEADLINE:
            return
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
        if nm in TARGETS:
            found.append((nm, ch))
        walk(ch)


def scan():
    found.clear()
    for i in range(desktop.get_child_count()):
        app = desktop.get_child_at_index(i)
        try:
            an = app.get_name()
        except Exception:
            an = "?"
        if "chrom" in (an or "").lower():
            walk(app)


for attempt in range(1, 6):
    scan()
    print("ATTEMPT %d found=%d %s" % (attempt, len(found), [n for n, _ in found]), flush=True)
    if len(found) >= len(TARGETS):
        break
    time.sleep(4)

if not found:
    print("NO-NODES", flush=True)
    sys.exit(3)


def iface(node, name):
    for m in ("get_%s_iface" % name, "get_%s" % name):
        f = getattr(node, m, None)
        if f:
            try:
                return f()
            except Exception:
                pass
    return None


for nm, ch in found:
    print("--- %s role=%s" % (nm, ch.get_role_name()), flush=True)
    roles = []
    for cand in ("text", "editable_text", "value", "action", "component"):
        o = iface(ch, cand)
        roles.append("%s=%s" % (cand, "yes" if o else "no"))
    print("    ifaces:", " ".join(roles), flush=True)

    if nm in ("A4-TEXT", "A4-TEXTAREA"):
        done = False
        et = iface(ch, "editable_text")
        for m in ("set_text_contents", "set_contents"):
            f = getattr(et, m, None) if et else None
            if f:
                try:
                    f("set-by-atspi")
                    print("    set via editable_text.%s OK" % m, flush=True)
                    done = True
                    break
                except Exception as e:
                    print("    editable_text.%s ERR %s" % (m, e), flush=True)
        if not done and et is None:
            print("    no editable_text iface", flush=True)
    elif nm == "A4-RANGE":
        v = iface(ch, "value")
        if v:
            try:
                print("    value now=%s min=%s max=%s" % (v.get_current_value(), v.get_minimum_value(), v.get_maximum_value()), flush=True)
            except Exception as e:
                print("    read value ERR %s" % e, flush=True)
            for m in ("set_current_value",):
                f = getattr(v, m, None)
                if f:
                    try:
                        f(v.get_maximum_value() if v.get_maximum_value() > 1 else 80.0)
                        print("    set via value.%s OK" % m, flush=True)
                    except Exception as e:
                        print("    value.%s ERR %s" % (m, e), flush=True)
    elif nm == "A4-SELECT":
        a = iface(ch, "action")
        if a:
            try:
                n = a.get_n_actions()
                names = [a.get_action_name(k) for k in range(n)]
                print("    actions=%s" % names, flush=True)
                for k, an2 in enumerate(names):
                    if "open" in (an2 or "").lower() or "press" in (an2 or "").lower():
                        a.do_action(k)
                        print("    did action[%d]=%s" % (k, an2), flush=True)
                        break
                time.sleep(1)
            except Exception as e:
                print("    action ERR %s" % e, flush=True)

print("WALK_DONE", flush=True)
