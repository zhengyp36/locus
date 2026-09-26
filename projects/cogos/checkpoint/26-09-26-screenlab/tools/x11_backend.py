#!/usr/bin/env python3.11
"""Mechanical X11 backend for Slice 1: capture root -> PNG, inject clicks, read pointer.

Pure mechanical I/O; no semantics. Used by imgctx.py `look`/`act`. Works against any
X display (local Xvfb now, surface-centos-9 later) given DISPLAY.
"""
from __future__ import annotations

import os
import subprocess
from pathlib import Path

from PIL import ImageGrab


def _env(display: str) -> dict:
    return {**os.environ, "DISPLAY": display}


def capture(display: str, out_path) -> tuple[int, int]:
    """Grab the full root window natively -> PNG. Returns (w, h)."""
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    img = ImageGrab.grab(xdisplay=display).convert("RGB")
    img.save(out, format="PNG")
    return img.size


def pointer(display: str) -> tuple[int, int]:
    r = subprocess.run(["xdotool", "getmouselocation", "--shell"],
                       env=_env(display), capture_output=True, text=True, check=True)
    d = dict(l.split("=", 1) for l in r.stdout.splitlines() if "=" in l)
    return int(d["X"]), int(d["Y"])


def click(display: str, x: int, y: int, button: int = 1) -> None:
    subprocess.run(["xdotool", "mousemove", "--sync", str(int(x)), str(int(y)),
                    "click", str(int(button))],
                   env=_env(display), capture_output=True, check=True)
