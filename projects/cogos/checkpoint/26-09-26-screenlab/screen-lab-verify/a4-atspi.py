import sys
import time

import gi

gi.require_version("Atspi", "2.0")
from gi.repository import Atspi

ACT = "--act" in sys.argv
ATTEMPTS = 3
DEADLINE = 90.0
PREFER = ("click", "activate", "press", "jump", "toggle", "expand")


def argval(flag, default):
    if flag in sys.argv:
        i = sys.argv.index(flag)
        if i + 1 < len(sys.argv):
            return int(sys.argv[i + 1])
    return default


ATTEMPTS = argval("--attempts", ATTEMPTS)
DEADLINE = float(argval("--deadline", int(DEADLINE)))

Atspi.init()
desktop = Atspi.get_desktop(0)

state = {"nodes": 0, "t0": 0.0}


def role_name(n):
    try:
        return n.get_role_name()
    except Exception:
        return "?"


def walk(node):
    if time.time() - state["t0"] > DEADLINE:
        return
    try:
        cnt = node.get_child_count()
    except Exception:
        return
    for i in range(cnt):
        if time.time() - state["t0"] > DEADLINE:
            return
        try:
            ch = node.get_child_at_index(i)
        except Exception:
            continue
        if ch is None:
            continue
        state["nodes"] += 1
        try:
            nm = ch.get_name()
        except Exception:
            nm = None
        if nm and nm.startswith("A4-"):
            try:
                na = ch.get_n_actions()
            except Exception:
                na = 0
            found.append((nm, role_name(ch), na, ch))
        walk(ch)


def scan():
    global found
    found = []
    state["nodes"] = 0
    state["t0"] = time.time()
    apps = []
    for i in range(desktop.get_child_count()):
        app = desktop.get_child_at_index(i)
        try:
            an = app.get_name()
        except Exception:
            an = "?"
        apps.append(an)
        if "chrom" in (an or "").lower() or "chrome" in (an or "").lower():
            walk(app)
    return apps, time.time() - state["t0"]


for attempt in range(1, ATTEMPTS + 1):
    apps, elapsed = scan()
    print("ATTEMPT %d apps=%s nodes=%d elapsed=%.2fs found=%d"
          % (attempt, apps, state["nodes"], elapsed, len(found)), flush=True)
    if found:
        break
    time.sleep(4)

if not found:
    print("NO-A4-NODES", flush=True)
    sys.exit(3)

by_role = {}
for nm, role, na, ch in found:
    names = []
    for k in range(na):
        try:
            names.append(ch.get_action_name(k))
        except Exception:
            names.append("?")
    print("NODE %-14s role=%-18s n_actions=%d actions=%s"
          % (nm, role, na, ",".join(names)), flush=True)
    by_role.setdefault(role, []).append(nm)

print("SUMMARY found=%d roles=%s" % (len(found), {k: len(v) for k, v in by_role.items()}),
      flush=True)

if ACT:
    print("--- DO-ACTION ---", flush=True)
    for nm, role, na, ch in found:
        if na <= 0:
            print("ACT %-14s SKIP no-action-iface" % nm, flush=True)
            continue
        idx = 0
        try:
            for k in range(na):
                if str(ch.get_action_name(k)).lower() in PREFER:
                    idx = k
                    break
        except Exception:
            pass
        try:
            ch.do_action(idx)
            print("ACT %-14s called action[%d]=%s"
                  % (nm, idx, ch.get_action_name(idx)), flush=True)
        except Exception as e:
            print("ACT %-14s ERROR %s" % (nm, e), flush=True)
        time.sleep(0.3)

print("WALK_DONE", flush=True)
