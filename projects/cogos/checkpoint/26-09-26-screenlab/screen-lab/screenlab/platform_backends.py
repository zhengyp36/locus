"""Pick the platform adapter.

X11    -> Pillow/ImageMagick capture + xdotool injection
win32  -> Pillow (GDI) capture + SendInput injection
android-> adb screencap + adb `input` injection (daemon runs on the host)
"""
from __future__ import annotations

import sys
from typing import Optional


def pick(display=None, xauth=None, backend: Optional[str] = None, adb_serial: Optional[str] = None):
    """Return (capture, act, list_displays_fn)."""
    if backend is None:
        backend = "win32" if sys.platform == "win32" else "x11"

    if backend == "android":
        from . import backends_android as android

        return android.pick(adb_serial)

    if backend == "win32":
        from . import backends_win as win

        return win.PillowCaptureWin(), win.SendInputAct(), win.list_displays

    from . import backends as x11

    env = x11._env(display, xauth)
    return (
        x11.pick_capture(display, xauth),
        x11.XdotoolAct(display, xauth),
        lambda: x11.list_displays(env),
    )
