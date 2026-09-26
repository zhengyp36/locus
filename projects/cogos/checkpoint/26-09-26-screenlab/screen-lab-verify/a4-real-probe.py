import sys
import time

import gi

gi.require_version("Atspi", "2.0")
from gi.repository import Atspi

DEADLINE = 120.0
INTERACTIVE = {
    "push button", "link", "check box", "radio button", "entry", "slider",
    "combo box", "toggle button", "menu item", "tab", "image", "menu",
}

Atspi.init()
desktop = Atspi.get_desktop(0)

state = {"nodes": 0, "t0": time.time()}
roles = {}
actions = []
samples = []


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
            rn = ch.get_role_name()
        except Exception:
            rn = "?"
        roles[rn] = roles.get(rn, 0) + 1
        if rn in INTERACTIVE:
            try:
                na = ch.get_n_actions()
            except Exception:
                na = 0
            names = []
            for k in range(na):
                try:
                    names.append(ch.get_action_name(k))
                except Exception:
                    names.append("?")
            if na > 0:
                try:
                    nm = ch.get_name()
                except Exception:
                    nm = None
                actions.append((rn, nm, names))
                if len(samples) < 25:
                    samples.append("SAMPLE role=%-14s name=%-40s actions=%s"
                                   % (rn, (nm or "")[:40], ",".join(names)))
        walk(ch)


def scan():
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
        if "chrom" in (an or "").lower():
            walk(app)
    return apps, time.time() - state["t0"]


ATTEMPTS = int(sys.argv[sys.argv.index("--attempts") + 1]) if "--attempts" in sys.argv else 4
for attempt in range(1, ATTEMPTS + 1):
    roles.clear()
    actions.clear()
    apps, elapsed = scan()
    print("ATTEMPT %d apps=%s nodes=%d elapsed=%.1fs interactive_with_action=%d"
          % (attempt, apps, state["nodes"], elapsed, len(actions)), flush=True)
    print("  roles=%s" % (dict(sorted(roles.items(), key=lambda x: -x[1])),), flush=True)
    if state["nodes"] > 50:
        break
    time.sleep(4)

print("--- SAMPLE INTERACTIVE ---", flush=True)
for s in samples:
    print(s, flush=True)
print("WALK_DONE", flush=True)
