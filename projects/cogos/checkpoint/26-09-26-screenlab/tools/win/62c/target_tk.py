"""Ground-truth target window for the Windows loop (Slice 3).

Runs inside assist's INTERACTIVE session. Makes this process per-monitor DPI
aware (so Tk coordinates and Win32 rects are physical px, matching DXGI capture
and SendInput), then opens a topmost borderless 400x300 window at +700+400.

Writes target.marker (JSON, atomic) with its measured screen rect + center:
  {"state": "READY"|"HIT"|"TIMEOUT"|"CLOSED", "rect":[l,t,r,b],
   "center":[cx,cy], "screen":[w,h], ...}
A left click anywhere on the window flips it to "HIT" (and turns green) then
closes shortly after, so the selftest can confirm the injected click landed.
Auto-closes after TIMEOUT_S with state "TIMEOUT" so it never orphans.
"""
import ctypes
import ctypes.wintypes as wt
import json
import os
import time

DIR = os.path.dirname(os.path.abspath(__file__))
MARK = os.path.join(DIR, "target.marker")
TIMEOUT_S = 30.0
POS = (700, 400)
SIZE = (400, 300)


def _dpi_aware() -> None:
    try:
        fn = ctypes.WinDLL("user32").SetProcessDpiAwarenessContext
        fn.argtypes = [ctypes.c_void_p]
        fn.restype = wt.BOOL
        if fn(ctypes.c_void_p(-4)):  # PER_MONITOR_AWARE_V2
            return
    except Exception:  # noqa: BLE001
        pass
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except Exception:  # noqa: BLE001
        pass


_dpi_aware()

import tkinter as tk  # noqa: E402  (must be after DPI awareness)

state = {"state": "INIT"}


def write() -> None:
    tmp = MARK + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(state, fh)
    os.replace(tmp, MARK)


root = tk.Tk()
root.overrideredirect(True)
root.attributes("-topmost", True)
root.geometry("%dx%d+%d+%d" % (SIZE[0], SIZE[1], POS[0], POS[1]))
canvas = tk.Canvas(root, width=SIZE[0], height=SIZE[1], bg="#cc0000",
                   highlightthickness=0)
canvas.pack(fill="both", expand=True)
root.update_idletasks()
root.update()
root.lift()

user32 = ctypes.WinDLL("user32", use_last_error=True)
hwnd = root.winfo_id()
top = user32.GetAncestor(hwnd, 2)  # GA_ROOT
rc = wt.RECT()
if top and user32.GetWindowRect(top, ctypes.byref(rc)):
    rect = [rc.left, rc.top, rc.right, rc.bottom]
else:  # fallback: Tk client-area screen coords
    rect = [root.winfo_rootx(), root.winfo_rooty(),
            root.winfo_rootx() + root.winfo_width(),
            root.winfo_rooty() + root.winfo_height()]
cx = (rect[0] + rect[2]) // 2
cy = (rect[1] + rect[3]) // 2
state.update({"state": "READY", "rect": rect, "center": [cx, cy],
              "screen": [user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)],
              "hwnd": int(top or hwnd)})
write()

_start = time.time()
_done = {"v": False}


def on_click(event) -> None:
    if _done["v"]:
        return
    _done["v"] = True
    canvas.config(bg="#00cc00")
    state.update({"state": "HIT", "click": [event.x_root, event.y_root]})
    write()
    root.after(400, root.destroy)


def tick() -> None:
    if _done["v"]:
        return
    if time.time() - _start >= TIMEOUT_S:
        _done["v"] = True
        state.update({"state": "TIMEOUT"})
        write()
        root.destroy()
        return
    root.after(200, tick)


canvas.bind("<Button-1>", on_click)
root.after(200, tick)
root.mainloop()

if state["state"] not in ("HIT", "TIMEOUT"):
    state.update({"state": "CLOSED"})
    write()
