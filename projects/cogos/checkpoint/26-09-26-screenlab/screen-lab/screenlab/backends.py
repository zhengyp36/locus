"""Platform backends: capture (see) and injection (act).

The only platform implemented here is Linux/X11 (Pillow or ImageMagick for
capture, xdotool for injection). Platform differences are supposed to sink
into adapters; this module is the X11 adapter.
"""
from __future__ import annotations

import io
import os
import shutil
import struct
import subprocess
from typing import Dict, List, Optional, Tuple

Region = Optional[Tuple[int, int, int, int]]  # (x, y, w, h)


class BackendError(Exception):
    pass


def _env(display: Optional[str], xauth: Optional[str]) -> Dict[str, str]:
    env = dict(os.environ)
    if display:
        env["DISPLAY"] = display
    if xauth and os.path.exists(xauth):
        env["XAUTHORITY"] = xauth
    return env


def _png_size(data: bytes) -> Tuple[int, int]:
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise BackendError("not a PNG payload")
    w, h = struct.unpack(">II", data[16:24])
    return w, h


class CaptureBackend:
    name = "null"

    def grab(self, region: Region = None, max_dim: Optional[int] = None) -> Tuple[bytes, Tuple[int, int]]:
        raise NotImplementedError


class PillowCapture(CaptureBackend):
    name = "pillow"

    def __init__(self, display: Optional[str], xauth: Optional[str]):
        from PIL import ImageGrab  # noqa: WPS433

        self._ImageGrab = ImageGrab
        self._display = display

    def grab(self, region: Region = None, max_dim: Optional[int] = None):
        bbox = None
        if region:
            x, y, w, h = region
            bbox = (x, y, x + w, y + h)
        img = self._ImageGrab.grab(xdisplay=self._display, bbox=bbox)
        if max_dim:
            longest = max(img.size)
            if longest > max_dim:
                ratio = float(max_dim) / float(longest)
                img = img.resize((max(1, int(img.width * ratio)), max(1, int(img.height * ratio))))
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return buf.getvalue(), (img.width, img.height)


class ImportCapture(CaptureBackend):
    """ImageMagick `import` fallback (no Pillow required)."""

    name = "import"

    def __init__(self, display: Optional[str], xauth: Optional[str]):
        if not shutil.which("import"):
            raise BackendError("ImageMagick `import` not found")
        self._env = _env(display, xauth)

    def grab(self, region: Region = None, max_dim: Optional[int] = None):
        cmd = ["import", "-window", "root"]
        if region:
            x, y, w, h = region
            cmd += ["-crop", "%dx%d+%d+%d" % (w, h, x, y)]
        cmd += ["png:-"]
        proc = subprocess.run(cmd, env=self._env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if proc.returncode != 0:
            raise BackendError("import failed: %s" % proc.stderr.decode("utf-8", "replace").strip())
        data = proc.stdout
        return data, _png_size(data)


def pick_capture(display: Optional[str], xauth: Optional[str]) -> CaptureBackend:
    try:
        return PillowCapture(display, xauth)
    except Exception:
        return ImportCapture(display, xauth)


class XdotoolAct:
    """Injection backend via xdotool (XTEST)."""

    name = "xdotool"

    def __init__(self, display: Optional[str], xauth: Optional[str]):
        if not shutil.which("xdotool"):
            raise BackendError("xdotool not found")
        self._env = _env(display, xauth)

    def _run(self, args: List[str]) -> str:
        proc = subprocess.run(["xdotool"] + args, env=self._env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if proc.returncode != 0:
            raise BackendError("xdotool %s failed: %s" % (args, proc.stderr.decode("utf-8", "replace").strip()))
        return proc.stdout.decode("utf-8", "replace").strip()

    def pointer(self, x: int, y: int, button: int = 1, clicks: int = 1) -> Dict:
        self._run(["mousemove", "--sync", str(x), str(y)])
        if clicks <= 0:
            return {"x": x, "y": y, "moved_only": True}
        for _ in range(clicks):
            self._run(["click", str(button)])
        return {"x": x, "y": y, "button": button, "clicks": clicks}

    def key(self, combo: str) -> Dict:
        self._run(["key", "--clearmodifiers", combo])
        return {"key": combo}

    def type_text(self, text: str, delay: int = 40) -> Dict:
        self._run(["type", "--clearmodifiers", "--delay", str(delay), text])
        return {"text_length": len(text)}

    def scroll(self, dy: int, x: Optional[int] = None, y: Optional[int] = None) -> Dict:
        if x is not None and y is not None:
            self._run(["mousemove", "--sync", str(x), str(y)])
        button = "4" if dy > 0 else "5"
        for _ in range(max(1, abs(int(dy)))):
            self._run(["click", button])
        return {"dy": dy}

    def focus_window(self, window_id: str) -> Dict:
        self._run(["windowactivate", "--sync", str(window_id)])
        return {"window_id": window_id}

    def active_window(self) -> Optional[Dict[str, str]]:
        try:
            wid = self._run(["getactivewindow"])
        except BackendError:
            return None
        title = ""
        try:
            title = self._run(["getwindowname", wid])
        except BackendError:
            pass
        return {"window_id": wid, "title": title}

    def pointer_pos(self) -> Optional[Dict[str, int]]:
        try:
            out = self._run(["getmouselocation", "--shell"])
        except BackendError:
            return None
        vals = {}
        for line in out.splitlines():
            if "=" in line:
                k, v = line.split("=", 1)
                vals[k.strip()] = v.strip()
        try:
            return {"x": int(vals.get("X", 0)), "y": int(vals.get("Y", 0))}
        except ValueError:
            return None


def list_displays(env: Dict[str, str]) -> List[Dict]:
    """Parse `xrandr --current`; fall back to an empty list."""
    if not shutil.which("xrandr"):
        return []
    proc = subprocess.run(["xrandr", "--current"], env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if proc.returncode != 0:
        return []
    out = []  # type: List[Dict]
    for line in proc.stdout.decode("utf-8", "replace").splitlines():
        if " connected" not in line:
            continue
        parts = line.split()
        name = parts[0]
        primary = "primary" in line
        geometry = None
        for tok in parts:
            if "x" in tok and "+" in tok:
                try:
                    size, xoff, yoff = tok.split("+")
                    w, h = size.split("x")
                    geometry = [int(w), int(h), int(xoff), int(yoff)]
                except ValueError:
                    pass
                break
        out.append({"id": name, "name": name, "primary": primary, "geometry": geometry})
    return out
