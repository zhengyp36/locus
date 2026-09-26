"""Windows adapter: capture via Pillow (GDI), injection via SendInput (ctypes).

Runs inside the target interactive session (see spec-screen-1 §5.1): a daemon in
Session 0 (sshd) sees no desktop.
"""
from __future__ import annotations

import ctypes
import ctypes.wintypes as wt
import io
import time
from typing import Dict, List, Optional, Tuple

from .backends import BackendError, Region

user32 = ctypes.WinDLL("user32", use_last_error=True)


def _enable_dpi_awareness() -> str:
    """Make this process per-monitor DPI aware.

    Without it, GetSystemMetrics/GetCursorPos return DPI-virtualized (logical)
    pixels while an `all_screens` GDI grab returns physical pixels -> the image
    coordinate space and the SendInput space differ (e.g. 1.5x at 150%).
    """
    try:
        fn = user32.SetProcessDpiAwarenessContext
        fn.argtypes = [ctypes.c_void_p]
        fn.restype = wt.BOOL
        if fn(ctypes.c_void_p(-4)):  # PER_MONITOR_AWARE_V2
            return "per-monitor-v2"
    except Exception:  # noqa: BLE001
        pass
    try:
        if ctypes.windll.shcore.SetProcessDpiAwareness(2) == 0:
            return "per-monitor"
    except Exception:  # noqa: BLE001
        pass
    try:
        if user32.SetProcessDPIAware():
            return "system"
    except Exception:  # noqa: BLE001
        pass
    return "none"


DPI_MODE = _enable_dpi_awareness()

ULONG_PTR = ctypes.c_ulonglong if ctypes.sizeof(ctypes.c_void_p) == 8 else ctypes.c_ulong

INPUT_MOUSE = 0
INPUT_KEYBOARD = 1

MOUSEEVENTF_MOVE = 0x0001
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
MOUSEEVENTF_RIGHTDOWN = 0x0008
MOUSEEVENTF_RIGHTUP = 0x0010
MOUSEEVENTF_MIDDLEDOWN = 0x0020
MOUSEEVENTF_MIDDLEUP = 0x0040
MOUSEEVENTF_WHEEL = 0x0800
MOUSEEVENTF_ABSOLUTE = 0x8000

KEYEVENTF_KEYUP = 0x0002
KEYEVENTF_UNICODE = 0x0004

SM_XVIRTUALSCREEN = 76
SM_YVIRTUALSCREEN = 77
SM_CXVIRTUALSCREEN = 78
SM_CYVIRTUALSCREEN = 79

SW_RESTORE = 9


class MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx", wt.LONG), ("dy", wt.LONG), ("mouseData", wt.DWORD),
        ("dwFlags", wt.DWORD), ("time", wt.DWORD), ("dwExtraInfo", ULONG_PTR),
    ]


class KEYBDINPUT(ctypes.Structure):
    _fields_ = [
        ("wVk", wt.WORD), ("wScan", wt.WORD), ("dwFlags", wt.DWORD),
        ("time", wt.DWORD), ("dwExtraInfo", ULONG_PTR),
    ]


class HARDWAREINPUT(ctypes.Structure):
    _fields_ = [("uMsg", wt.DWORD), ("wParamL", wt.WORD), ("wParamH", wt.WORD)]


class _INPUTUNION(ctypes.Union):
    _fields_ = [("mi", MOUSEINPUT), ("ki", KEYBDINPUT), ("hi", HARDWAREINPUT)]


class INPUT(ctypes.Structure):
    _fields_ = [("type", wt.DWORD), ("u", _INPUTUNION)]


def _send(*inputs: INPUT) -> None:
    n = len(inputs)
    arr = (INPUT * n)(*inputs)
    sent = user32.SendInput(n, ctypes.byref(arr), ctypes.sizeof(INPUT))
    if sent != n:
        raise BackendError("SendInput sent %d/%d (err=%d)" % (sent, n, ctypes.get_last_error()))


def _mouse_inp(dx: int, dy: int, data: int, flags: int) -> INPUT:
    return INPUT(type=INPUT_MOUSE, u=_INPUTUNION(mi=MOUSEINPUT(dx, dy, data, flags, 0, 0)))


def _key_inp(vk: int, scan: int, flags: int) -> INPUT:
    return INPUT(type=INPUT_KEYBOARD, u=_INPUTUNION(ki=KEYBDINPUT(vk, scan, flags, 0, 0)))


VK = {
    "return": 0x0D, "enter": 0x0D, "escape": 0x1B, "esc": 0x1B, "tab": 0x09,
    "backspace": 0x08, "space": 0x20, "delete": 0x2E, "insert": 0x2D,
    "left": 0x25, "up": 0x26, "right": 0x27, "down": 0x28,
    "home": 0x24, "end": 0x23, "pageup": 0x21, "pagedown": 0x22,
    "ctrl": 0x11, "control": 0x11, "alt": 0x12, "shift": 0x10,
    "super": 0x5B, "win": 0x5B, "meta": 0x5B, "cmd": 0x5B,
    "printscreen": 0x2C, "capslock": 0x14,
}
for _i in range(1, 25):
    VK["f%d" % _i] = 0x6F + _i

_MODS = {0x11, 0x12, 0x10, 0x5B}


def _resolve(name: str) -> int:
    n = name.strip().lower()
    if n in VK:
        return VK[n]
    if len(n) == 1:
        if n.isalpha():
            return ord(n.upper())
        if n.isdigit():
            return ord(n)
        vk = user32.VkKeyScanW(ord(n))
        if vk != -1:
            return vk & 0xFF
    raise BackendError("unknown key: %r" % name)


class PillowCaptureWin:
    name = "pillow"

    def __init__(self):
        try:
            from PIL import ImageGrab
        except Exception as exc:  # noqa: BLE001
            raise BackendError("Pillow not available: %s" % exc)
        self._grab = ImageGrab

    def grab(self, region: Region = None, max_dim: Optional[int] = None):
        bbox = None
        if region:
            x, y, w, h = region
            bbox = (x, y, x + w, y + h)
        img = self._grab.grab(bbox=bbox, all_screens=True)
        if max_dim:
            longest = max(img.size)
            if longest > max_dim:
                ratio = float(max_dim) / float(longest)
                img = img.resize((max(1, int(img.width * ratio)), max(1, int(img.height * ratio))))
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return buf.getvalue(), (img.width, img.height)


class SendInputAct:
    name = "sendinput"

    def _move(self, x: int, y: int) -> None:
        vx = user32.GetSystemMetrics(SM_XVIRTUALSCREEN)
        vy = user32.GetSystemMetrics(SM_YVIRTUALSCREEN)
        vw = max(1, user32.GetSystemMetrics(SM_CXVIRTUALSCREEN) - 1)
        vh = max(1, user32.GetSystemMetrics(SM_CYVIRTUALSCREEN) - 1)
        nx = int(round((int(x) - vx) * 65535.0 / vw))
        ny = int(round((int(y) - vy) * 65535.0 / vh))
        _send(_mouse_inp(nx, ny, 0, MOUSEEVENTF_MOVE | MOUSEEVENTF_ABSOLUTE))

    def pointer(self, x: int, y: int, button: int = 1, clicks: int = 1) -> Dict:
        self._move(x, y)
        if clicks <= 0:
            return {"x": x, "y": y, "moved_only": True}
        pairs = {
            1: (MOUSEEVENTF_LEFTDOWN, MOUSEEVENTF_LEFTUP),
            2: (MOUSEEVENTF_MIDDLEDOWN, MOUSEEVENTF_MIDDLEUP),
            3: (MOUSEEVENTF_RIGHTDOWN, MOUSEEVENTF_RIGHTUP),
        }
        if button not in pairs:
            raise BackendError("unsupported button: %s" % button)
        down, up = pairs[button]
        for _ in range(clicks):
            _send(_mouse_inp(0, 0, 0, down), _mouse_inp(0, 0, 0, up))
        return {"x": x, "y": y, "button": button, "clicks": clicks}

    def key(self, combo: str) -> Dict:
        parts = [p for p in combo.split("+") if p.strip()]
        if not parts:
            raise BackendError("empty key combo")
        mods, main = parts[:-1], parts[-1]
        mod_vks = [_resolve(m) for m in mods]
        for vk in mod_vks:
            _send(_key_inp(vk, 0, 0))
        vk = _resolve(main)
        _send(_key_inp(vk, 0, 0), _key_inp(vk, 0, KEYEVENTF_KEYUP))
        for vk in reversed(mod_vks):
            _send(_key_inp(vk, 0, KEYEVENTF_KEYUP))
        return {"key": combo}

    def type_text(self, text: str, delay: int = 40) -> Dict:
        for ch in text:
            if ch == "\n":
                self.key("Return")
            elif ch == "\t":
                self.key("Tab")
            else:
                code = ord(ch)
                units = [code]
                if code > 0xFFFF:
                    code -= 0x10000
                    units = [0xD800 + (code >> 10), 0xDC00 + (code & 0x3FF)]
                for u in units:
                    _send(_key_inp(0, u, KEYEVENTF_UNICODE),
                          _key_inp(0, u, KEYEVENTF_UNICODE | KEYEVENTF_KEYUP))
            if delay:
                time.sleep(delay / 1000.0)
        return {"text_length": len(text)}

    def scroll(self, dy: int, x: Optional[int] = None, y: Optional[int] = None) -> Dict:
        if x is not None and y is not None:
            self._move(int(x), int(y))
        delta = 120 if dy > 0 else -120
        data = delta & 0xFFFFFFFF
        for _ in range(max(1, abs(int(dy)))):
            _send(_mouse_inp(0, 0, data, MOUSEEVENTF_WHEEL))
        return {"dy": dy}

    def focus_window(self, window_id: str) -> Dict:
        hwnd = int(window_id)
        user32.ShowWindow(hwnd, SW_RESTORE)
        user32.SetForegroundWindow(hwnd)
        return {"window_id": str(window_id)}

    def active_window(self) -> Optional[Dict[str, str]]:
        hwnd = user32.GetForegroundWindow()
        if not hwnd:
            return None
        buf = ctypes.create_unicode_buffer(512)
        user32.GetWindowTextW(hwnd, buf, 512)
        return {"window_id": str(hwnd), "title": buf.value}

    def pointer_pos(self) -> Optional[Dict[str, int]]:
        pt = wt.POINT()
        if not user32.GetCursorPos(ctypes.byref(pt)):
            return None
        return {"x": pt.x, "y": pt.y}


def list_displays() -> List[Dict]:
    w = user32.GetSystemMetrics(0)
    h = user32.GetSystemMetrics(1)
    return [{"id": "primary", "name": "primary", "primary": True, "geometry": [w, h, 0, 0]}]
