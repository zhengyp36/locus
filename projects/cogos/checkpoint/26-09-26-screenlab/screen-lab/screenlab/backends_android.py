"""Android adapter via adb.

Unlike X11/Wayland/Windows, there is **no "daemon must live in the target
session" trap** here: the device only runs `adbd`, and the daemon runs on the
host, driving capture/injection through the `adb` client.

  capture: `adb exec-out screencap -p`   (PNG on stdout, no root)
  act:     `adb shell input tap/swipe/text/keyevent`
  coords:  screencap pixels == input coordinates == uiautomator bounds
           (verified on Android 10 / EMUI 10; no DPI offset like Windows)

Known limits: `input text` mangles spaces (encoded as `%s`) and cannot type
non-ASCII; rotation flips the screenshot/coordinate space and must be handled
by the caller (see `list_displays`).
"""
from __future__ import annotations

import io
import re
import shlex
import shutil
import subprocess
from typing import Dict, List, Optional, Tuple

from .backends import BackendError, CaptureBackend, Region, _png_size

# Common `input keyevent` names (xdotool-style names -> Android KEYCODE_*).
_KEYMAP = {
    "enter": "KEYCODE_ENTER", "return": "KEYCODE_ENTER",
    "escape": "KEYCODE_ESCAPE", "esc": "KEYCODE_ESCAPE",
    "back": "KEYCODE_BACK", "home": "KEYCODE_HOME",
    "menu": "KEYCODE_MENU", "tab": "KEYCODE_TAB", "space": "KEYCODE_SPACE",
    "delete": "KEYCODE_DEL", "backspace": "KEYCODE_DEL",
    "power": "KEYCODE_POWER", "wakeup": "KEYCODE_WAKEUP",
    "up": "KEYCODE_DPAD_UP", "down": "KEYCODE_DPAD_DOWN",
    "left": "KEYCODE_DPAD_LEFT", "right": "KEYCODE_DPAD_RIGHT",
    "center": "KEYCODE_DPAD_CENTER",
    "volume_up": "KEYCODE_VOLUME_UP", "volume_down": "KEYCODE_VOLUME_DOWN",
    "app_switch": "KEYCODE_APP_SWITCH", "recents": "KEYCODE_APP_SWITCH",
}


class Adb:
    """Thin `adb` wrapper bound to a device serial."""

    def __init__(self, serial: Optional[str] = None):
        if not shutil.which("adb"):
            raise BackendError("adb not found")
        self.serial = serial

    def _base(self) -> List[str]:
        cmd = ["adb"]
        if self.serial:
            cmd += ["-s", self.serial]
        return cmd

    def raw(self, args: List[str]) -> bytes:
        proc = subprocess.run(self._base() + args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if proc.returncode != 0:
            raise BackendError("adb %s failed: %s" % (args, proc.stderr.decode("utf-8", "replace").strip()))
        return proc.stdout

    def shell(self, command: str) -> str:
        return self.raw(["shell", command]).decode("utf-8", "replace")


class AdbCapture(CaptureBackend):
    name = "adb-screencap"

    def __init__(self, adb: Adb):
        self._adb = adb

    def grab(self, region: Region = None, max_dim: Optional[int] = None):
        data = self._adb.raw(["exec-out", "screencap", "-p"])
        if not data.startswith(b"\x89PNG"):
            raise BackendError("screencap did not return PNG")
        if region or max_dim:
            data, size = _crop_resize(data, region, max_dim)
        else:
            size = _png_size(data)
        return data, size


def _crop_resize(data: bytes, region: Region, max_dim: Optional[int]):
    from PIL import Image  # noqa: WPS433

    img = Image.open(io.BytesIO(data)).convert("RGB")
    if region:
        x, y, w, h = region
        img = img.crop((x, y, x + w, y + h))
    if max_dim:
        longest = max(img.size)
        if longest > max_dim:
            ratio = float(max_dim) / float(longest)
            img = img.resize((max(1, int(img.width * ratio)), max(1, int(img.height * ratio))))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue(), (img.width, img.height)


class AdbAct:
    name = "adb-input"

    def __init__(self, adb: Adb):
        self._adb = adb
        self._size = None  # cached (w, h)

    def _screen_size(self) -> Tuple[int, int]:
        if self._size is None:
            m = re.search(r"(\d+)x(\d+)", self._adb.shell("wm size"))
            self._size = (int(m.group(1)), int(m.group(2))) if m else (1080, 1920)
        return self._size

    def pointer(self, x: int, y: int, button: int = 1, clicks: int = 1) -> Dict:
        if clicks <= 0:
            return {"x": x, "y": y, "moved_only": True}
        for _ in range(clicks):
            self._adb.shell("input tap %d %d" % (int(x), int(y)))
        return {"x": x, "y": y, "button": button, "clicks": clicks}

    def key(self, combo: str) -> Dict:
        name = combo.strip().lower()
        code = _KEYMAP.get(name)
        if code is None:
            if name.startswith("keycode_") or name.isdigit():
                code = combo.strip()
            else:
                raise BackendError("unsupported key %r for android (use a KEYCODE name)" % combo)
        self._adb.shell("input keyevent %s" % code)
        return {"key": combo, "keycode": code}

    def type_text(self, text: str, delay: int = 40) -> Dict:
        # `input text` uses %s for spaces and cannot carry non-ASCII.
        escaped = text.replace(" ", "%s")
        self._adb.shell("input text %s" % shlex.quote(escaped))
        return {"text_length": len(text)}

    def scroll(self, dy: int, x: Optional[int] = None, y: Optional[int] = None) -> Dict:
        w, h = self._screen_size()
        cx = int(x) if x is not None else w // 2
        cy = int(y) if y is not None else h // 2
        dist = 400
        steps = max(1, min(abs(int(dy)), 5))
        for _ in range(steps):
            if dy > 0:  # finger up -> content scrolls down
                y1, y2 = cy + dist // 2, cy - dist // 2
            else:       # finger down -> content scrolls up
                y1, y2 = cy - dist // 2, cy + dist // 2
            self._adb.shell("input swipe %d %d %d %d 200" % (cx, y1, cx, y2))
        return {"dy": dy}

    def focus_window(self, window_id: str) -> Dict:
        raise BackendError("android has no focusable windows; use key/pointer")

    def active_window(self) -> Optional[Dict[str, str]]:
        out = self._adb.shell("dumpsys window | grep -m1 mCurrentFocus")
        m = re.search(r"mCurrentFocus=Window\{[^ ]+ [^ ]+ ([^}]+)\}", out)
        if not m:
            return None
        component = m.group(1).strip()
        return {"window_id": component, "title": component}

    def pointer_pos(self) -> Optional[Dict[str, int]]:
        return None  # touch devices have no cursor


def list_displays(adb: Adb) -> List[Dict]:
    size = None
    m = re.search(r"Physical size: (\d+)x(\d+)", adb.shell("wm size"))
    if m:
        size = [int(m.group(1)), int(m.group(2))]
    density = None
    m = re.search(r"Physical density: (\d+)", adb.shell("wm density"))
    if m:
        density = int(m.group(1))
    rotation = 0
    m = re.search(r"rotation (\d+)", adb.shell("dumpsys display | grep -m1 DisplayDeviceInfo"))
    if m:
        rotation = int(m.group(1))
    geom = [size[0], size[1], 0, 0] if size else None
    return [{
        "id": adb.serial or "device",
        "name": adb.serial or "device",
        "primary": True,
        "geometry": geom,
        "density": density,
        "rotation": rotation,
    }]


def pick(serial: Optional[str] = None):
    """Return (capture, act, list_displays_fn) for an adb-attached device."""
    adb = Adb(serial)
    return AdbCapture(adb), AdbAct(adb), (lambda: list_displays(adb))
