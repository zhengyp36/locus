"""62c probe: SetWinEventHook as a change trigger.

Out-of-context hook over the whole desktop; counts EVENT_OBJECT_* /
EVENT_SYSTEM_* while a load generator changes the screen. Run in the
interactive session.
"""
import ctypes
import ctypes.wintypes as wt
import json
import sys
import time

DURATION = float(sys.argv[1]) if len(sys.argv) > 1 else 8.0

WINEVENT_OUTOFCONTEXT = 0x0000
WINEVENT_SKIPOWNPROCESS = 0x0002

EVENT_NAMES = {
    0x0001: "SYSTEM_SOUND", 0x0002: "SYSTEM_ALERT", 0x0003: "SYSTEM_FOREGROUND",
    0x0004: "SYSTEM_MENUSTART", 0x0005: "SYSTEM_MENUEND",
    0x000A: "SYSTEM_MOVESIZESTART", 0x000B: "SYSTEM_MOVESIZEEND",
    0x000C: "SYSTEM_CONTEXTHELPSTART", 0x000D: "SYSTEM_CONTEXTHELPEND",
    0x0010: "SYSTEM_DIALOGSTART", 0x0011: "SYSTEM_DIALOGEND",
    0x0014: "SYSTEM_CAPTURESTART", 0x0015: "SYSTEM_CAPTUREEND",
    0x0016: "SYSTEM_MINIMIZESTART", 0x0017: "SYSTEM_MINIMIZEEND",
    0x8000: "OBJECT_CREATE", 0x8001: "OBJECT_DESTROY", 0x8002: "OBJECT_SHOW",
    0x8003: "OBJECT_HIDE", 0x8004: "OBJECT_LOCATIONCHANGE",
    0x8005: "OBJECT_NAMECHANGE", 0x8006: "OBJECT_FOCUS",
    0x8007: "OBJECT_SELECTION", 0x8008: "OBJECT_SELECTIONADD",
    0x8009: "OBJECT_SELECTIONREMOVE", 0x800A: "OBJECT_SELECTIONWITHIN",
    0x800B: "OBJECT_STATECHANGE", 0x800C: "OBJECT_LOCATIONCHANGE?",
    0x800D: "OBJECT_VALUECHANGE?", 0x800E: "OBJECT_VALUECHANGE",
    0x800F: "OBJECT_REORDER", 0x8010: "OBJECT_CONTENTSCROLLED",
    0x8020: "OBJECT_DESKTOPSWITCH", 0x8021: "OBJECT_END",
}

PROC = ctypes.WINFUNCTYPE(None, ctypes.c_void_p, wt.DWORD, ctypes.c_void_p,
                          ctypes.c_long, ctypes.c_long, wt.DWORD, wt.DWORD)
user = ctypes.WinDLL("user32")
user.SetWinEventHook.restype = ctypes.c_void_p
user.SetWinEventHook.argtypes = [wt.DWORD, wt.DWORD, ctypes.c_void_p, PROC,
                                 wt.DWORD, wt.DWORD, wt.DWORD]


class MSG(ctypes.Structure):
    _fields_ = [("hwnd", ctypes.c_void_p), ("message", wt.UINT),
                ("wParam", ctypes.c_void_p), ("lParam", ctypes.c_void_p),
                ("time", wt.DWORD), ("pt", wt.POINT)]


counts = {}
total = 0
last = None
examples = []


def cb(hook, event, hwnd, idobj, idchild, tid, t):
    global total, last
    total += 1
    counts[event] = counts.get(event, 0) + 1
    now = time.time()
    last = now
    if len(examples) < 8:
        examples.append({"event": hex(event), "name": EVENT_NAMES.get(event, "?"),
                         "idObject": idobj, "idChild": idchild, "thread": tid, "t": round(t)})


cb_ref = PROC(cb)
hooks = []
for lo, hi in [(0x0001, 0x7FFF), (0x8000, 0x8FFF)]:
    h = user.SetWinEventHook(lo, hi, None, cb_ref, 0, 0,
                             WINEVENT_OUTOFCONTEXT | WINEVENT_SKIPOWNPROCESS)
    hooks.append(h)


def cpu_times():
    k32 = ctypes.WinDLL("kernel32")
    k32.GetProcessTimes.restype = wt.BOOL
    k32.GetProcessTimes.argtypes = [ctypes.c_void_p] + [ctypes.POINTER(ctypes.c_longlong)] * 4
    c = ctypes.c_longlong(); e = ctypes.c_longlong()
    k = ctypes.c_longlong(); u = ctypes.c_longlong()
    k32.GetProcessTimes(ctypes.c_void_p(-1), ctypes.byref(c), ctypes.byref(e),
                        ctypes.byref(k), ctypes.byref(u))
    return (k.value + u.value) / 1e7


cpu0 = cpu_times()
wall0 = time.time()
deadline = wall0 + DURATION
msg = MSG()
PM_REMOVE = 0x0001
while time.time() < deadline:
    if user.PeekMessageW(ctypes.byref(msg), None, 0, 0, PM_REMOVE):
        user.TranslateMessage(ctypes.byref(msg))
        user.DispatchMessageW(ctypes.byref(msg))
    else:
        time.sleep(0.002)

wall = time.time() - wall0
cpu = cpu_times() - cpu0
for h in hooks:
    user.UnhookWinEvent(ctypes.c_void_p(h))
report = {
    "probe": "setwineventhook", "duration_s": round(wall, 3),
    "total_events": total,
    "events_per_sec": round(total / wall, 1) if wall else None,
    "hooks_ok": [bool(h) for h in hooks],
    "cpu_s": round(cpu, 4),
    "cpu_pct": round(100.0 * cpu / wall, 2) if wall else None,
    "breakdown": [{"event": hex(k), "name": EVENT_NAMES.get(k, "?"), "n": v}
                  for k, v in sorted(counts.items(), key=lambda kv: -kv[1])],
    "examples": examples,
}
print(json.dumps(report, indent=2))
