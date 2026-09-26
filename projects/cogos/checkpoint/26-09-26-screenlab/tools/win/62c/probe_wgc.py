import ctypes
import ctypes.wintypes as wt
import json
import sys
import threading
import time

DUR = float(sys.argv[1]) if len(sys.argv) > 1 else 5.0

out = {"probe": "windows_graphics_capture"}
try:
    from windows_capture import WindowsCapture
    out["import"] = "ok"
except Exception as e:
    out["import"] = "exc:" + repr(e)
    print(json.dumps(out, indent=2))
    sys.exit(0)


def cpu_times():
    k32 = ctypes.WinDLL("kernel32")
    k32.GetProcessTimes.restype = wt.BOOL
    k32.GetProcessTimes.argtypes = [ctypes.c_void_p] + [ctypes.POINTER(ctypes.c_longlong)] * 4
    c = ctypes.c_longlong(); e = ctypes.c_longlong()
    k = ctypes.c_longlong(); u = ctypes.c_longlong()
    k32.GetProcessTimes(ctypes.c_void_p(-1), ctypes.byref(c), ctypes.byref(e),
                        ctypes.byref(k), ctypes.byref(u))
    return (k.value + u.value) / 1e7


try:
    cap = WindowsCapture(cursor_capture=False, draw_border=False, monitor_index=1)
except Exception as e:
    out["create"] = "exc:" + repr(e)
    print(json.dumps(out, indent=2))
    sys.exit(0)

state = {"n": 0, "t0": None, "shapes": set(), "ivs": [], "last": None, "err": None}
ctl = {"c": None}
stop_flag = {"v": False}


@cap.event
def on_frame_arrived(frame, capture_control):
    now = time.time()
    if state["t0"] is None:
        state["t0"] = now
    state["n"] += 1
    if state["last"] is not None:
        state["ivs"].append((now - state["last"]) * 1000.0)
    state["last"] = now
    try:
        buf = frame.frame_buffer
        if buf is not None and len(buf) > 0:
            state["shapes"].add((len(buf),))
    except Exception:
        pass
    ctl["c"] = capture_control
    if now - state["t0"] >= DUR:
        stop_flag["v"] = True
        try:
            capture_control.stop()
        except Exception:
            pass


@cap.event
def on_closed():
    pass


cpu0 = cpu_times()
wall0 = time.time()


def watchdog():
    time.sleep(DUR + 2.0)
    if not stop_flag["v"] and ctl["c"] is not None:
        try:
            ctl["c"].stop()
        except Exception:
            pass


threading.Thread(target=watchdog, daemon=True).start()

try:
    cap.start()
except Exception as e:
    state["err"] = repr(e)

wall = time.time() - wall0
cpu = cpu_times() - cpu0
out["frames"] = state["n"]
out["wall_s"] = round(wall, 2)
out["fps"] = round(state["n"] / wall, 2) if wall else None
out["cpu_pct"] = round(100.0 * cpu / wall, 2) if wall else None
if state["ivs"]:
    out["frame_interval_ms"] = {"min": round(min(state["ivs"]), 2),
                                "max": round(max(state["ivs"]), 2),
                                "avg": round(sum(state["ivs"]) / len(state["ivs"]), 2)}
out["buffer_shapes"] = [list(s) for s in state["shapes"]]
out["start_exc"] = state["err"]
print(json.dumps(out, indent=2))
