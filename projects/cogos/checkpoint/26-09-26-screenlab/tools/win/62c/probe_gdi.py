"""62c probe: GDI BitBlt baseline + pixel-fingerprint change detection.

Measures raw capture cost and three change signals on the captured pixels:
  - sha256 of raw BGRA bytes
  - sha256 of a downsampled (x8) grayscale frame
  - per-tile (64px) diff count + bbox
Also measures PNG-encode + sha256 (the current daemon frame_hash approach).
"""
import ctypes
import ctypes.wintypes as wt
import hashlib
import io
import json
import sys
import time

DURATION = float(sys.argv[1]) if len(sys.argv) > 1 else 8.0
INTERVAL = float(sys.argv[2]) if len(sys.argv) > 2 else 0.05
TILE = 64

try:
    import numpy as np
    HAVE_NP = True
except Exception:
    HAVE_NP = False


class BITMAPINFOHEADER(ctypes.Structure):
    _fields_ = [("biSize", wt.DWORD), ("biWidth", ctypes.c_long),
                ("biHeight", ctypes.c_long), ("biPlanes", wt.WORD),
                ("biBitCount", wt.WORD), ("biCompression", wt.DWORD),
                ("biSizeImage", wt.DWORD), ("biXPelsPerMeter", ctypes.c_long),
                ("biYPelsPerMeter", ctypes.c_long), ("biClrUsed", wt.DWORD),
                ("biClrImportant", wt.DWORD)]


class BITMAPINFO(ctypes.Structure):
    _fields_ = [("bmiHeader", BITMAPINFOHEADER), ("bmiColors", wt.DWORD * 3)]


gdi = ctypes.WinDLL("gdi32")
user = ctypes.WinDLL("user32")
for fn, rt in [("GetDC", ctypes.c_void_p), ("CreateCompatibleDC", ctypes.c_void_p),
               ("CreateCompatibleBitmap", ctypes.c_void_p), ("SelectObject", ctypes.c_void_p),
               ("DeleteDC", wt.BOOL), ("DeleteObject", wt.BOOL),
               ("BitBlt", wt.BOOL), ("GetDIBits", ctypes.c_int)]:
    f = getattr(gdi, fn, None) or getattr(user, fn)
    f.restype = rt
user.GetDC.argtypes = [ctypes.c_void_p]
gdi.CreateCompatibleDC.argtypes = [ctypes.c_void_p]
gdi.CreateCompatibleBitmap.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int]
gdi.SelectObject.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
gdi.BitBlt.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.c_int,
                       ctypes.c_int, ctypes.c_void_p, ctypes.c_int, ctypes.c_int, wt.DWORD]
gdi.GetDIBits.argtypes = [ctypes.c_void_p, ctypes.c_void_p, wt.UINT, wt.UINT,
                          ctypes.c_void_p, ctypes.POINTER(BITMAPINFO), wt.UINT]
gdi.DeleteDC.argtypes = [ctypes.c_void_p]
gdi.DeleteObject.argtypes = [ctypes.c_void_p]
user.ReleaseDC.argtypes = [ctypes.c_void_p, ctypes.c_void_p]

W = user.GetSystemMetrics(0)
H = user.GetSystemMetrics(1)
SRCCOPY = 0x00CC0020

screen = user.GetDC(None)
mem = gdi.CreateCompatibleDC(screen)
bmp = gdi.CreateCompatibleBitmap(screen, W, H)
old = gdi.SelectObject(mem, bmp)

bi = BITMAPINFO()
bi.bmiHeader.biSize = ctypes.sizeof(BITMAPINFOHEADER)
bi.bmiHeader.biWidth = W
bi.bmiHeader.biHeight = -H
bi.bmiHeader.biPlanes = 1
bi.bmiHeader.biBitCount = 32
bi.bmiHeader.biCompression = 0
buf = ctypes.create_string_buffer(W * H * 4)


def grab():
    gdi.BitBlt(mem, 0, 0, W, H, screen, 0, 0, SRCCOPY)
    gdi.GetDIBits(mem, bmp, 0, H, buf, ctypes.byref(bi), 0)
    return bytes(buf.raw)


def cpu_times():
    k32 = ctypes.WinDLL("kernel32")
    k32.GetProcessTimes.restype = wt.BOOL
    k32.GetProcessTimes.argtypes = [ctypes.c_void_p] + [ctypes.POINTER(ctypes.c_longlong)] * 4
    c = ctypes.c_longlong(); e = ctypes.c_longlong()
    k = ctypes.c_longlong(); u = ctypes.c_longlong()
    k32.GetProcessTimes(ctypes.c_void_p(-1), ctypes.byref(c), ctypes.byref(e),
                        ctypes.byref(k), ctypes.byref(u))
    return (k.value + u.value) / 1e7


def tile_stats(a, b):
    if not HAVE_NP:
        return None
    ta = np.frombuffer(a, np.uint8).reshape(H, W, 4)
    tb = np.frombuffer(b, np.uint8).reshape(H, W, 4)
    d = np.abs(ta.astype(np.int16) - tb.astype(np.int16)).max(axis=2)
    changed = d > 8
    if not changed.any():
        return {"tiles": 0, "bbox": None}
    ys, xs = np.nonzero(changed)
    bbox = (int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1)
    th, tw = (H + TILE - 1) // TILE, (W + TILE - 1) // TILE
    pad_h, pad_w = th * TILE - H, tw * TILE - W
    if pad_h or pad_w:
        changed = np.pad(changed, ((0, pad_h), (0, pad_w)), constant_values=False)
    tile_changed = changed.reshape(th, TILE, tw, TILE).any(axis=(1, 3))
    return {"tiles": int(tile_changed.sum()), "bbox": bbox}


def downsample_digest(raw):
    if not HAVE_NP:
        return hashlib.sha256(raw[::8]).hexdigest()
    a = np.frombuffer(raw, np.uint8).reshape(H, W, 4)[::8, ::8, :3]
    return hashlib.sha256(a.tobytes()).hexdigest()


report = {"probe": "gdi_bitblt", "screen": [W, H], "duration_s": DURATION,
          "interval_s": INTERVAL, "numpy": HAVE_NP, "tile": TILE}

cpu0 = cpu_times()
wall0 = time.time()
deadline = wall0 + DURATION
prev = None
prev_raw = None
prev_digest = None
grab_ms = []
encode_ms = []
digest_ms = []
rawsha_ms = []
tile_ms = []
changed_raw = 0
changed_digest = 0
changed_png = 0
tile_counts = []
bboxes = []
frames = 0
png_hashes = {}
while time.time() < deadline:
    t0 = time.perf_counter()
    raw = grab()
    t1 = time.perf_counter()
    h_raw = hashlib.sha256(raw).hexdigest()
    t2 = time.perf_counter()
    dg = downsample_digest(raw)
    t3 = time.perf_counter()
    ts = tile_stats(prev_raw, raw) if prev_raw is not None else None
    t4 = time.perf_counter()
    # PNG encode + sha (current daemon frame_hash equivalent)
    from PIL import Image
    img = Image.frombytes("RGB", (W, H), raw, "raw", "BGRX")
    bio = io.BytesIO()
    img.save(bio, "PNG")
    png = bio.getvalue()
    h_png = hashlib.sha256(png).hexdigest()
    t5 = time.perf_counter()
    frames += 1
    grab_ms.append((t1 - t0) * 1000)
    rawsha_ms.append((t2 - t1) * 1000)
    digest_ms.append((t3 - t2) * 1000)
    tile_ms.append((t4 - t3) * 1000)
    encode_ms.append((t5 - t4) * 1000)
    if prev is not None:
        if h_raw != prev[0]:
            changed_raw += 1
        if dg != prev_digest:
            changed_digest += 1
        if h_png != prev[1]:
            changed_png += 1
        if ts:
            tile_counts.append(ts["tiles"])
            if ts["bbox"]:
                bboxes.append(ts["bbox"])
    prev = (h_raw, h_png)
    prev_raw = raw
    prev_digest = dg
    png_hashes[h_png] = png_hashes.get(h_png, 0) + 1
    slack = INTERVAL - (time.perf_counter() - t0)
    if slack > 0:
        time.sleep(slack)


def stat(xs):
    if not xs:
        return None
    return {"min": round(min(xs), 3), "max": round(max(xs), 3),
            "avg": round(sum(xs) / len(xs), 3)}


wall = time.time() - wall0
cpu = cpu_times() - cpu0
report["frames"] = frames
report["grab_ms"] = stat(grab_ms)
report["sha256_raw_ms"] = stat(rawsha_ms)
report["digest_downsample_ms"] = stat(digest_ms)
report["tile_diff_ms"] = stat(tile_ms)
report["png_encode_sha_ms"] = stat(encode_ms)
report["changed_raw_hash"] = changed_raw
report["changed_downsample_hash"] = changed_digest
report["changed_png_hash"] = changed_png
report["tile_changed_frames"] = len(tile_counts)
report["tile_count"] = stat(tile_counts)
report["tile_max"] = max(tile_counts) if tile_counts else 0
report["bbox_examples"] = bboxes[:6]
report["wall_s"] = round(wall, 3)
report["cpu_s"] = round(cpu, 4)
report["cpu_pct"] = round(100.0 * cpu / wall, 2) if wall else None
print(json.dumps(report, indent=2))

gdi.SelectObject(mem, old)
gdi.DeleteObject(bmp)
gdi.DeleteDC(mem)
user.ReleaseDC(None, screen)
