"""62c probe: DXGI Desktop Duplication dirty/move rects.

Runs inside the interactive session (WinSta0\\Default). Pure ctypes COM, no
third-party deps. Reports signal granularity, per-frame cost, reliability.
"""
import ctypes
import ctypes.wintypes as wt
import json
import sys
import time

try:
    ctypes.WinDLL("user32").SetProcessDPIAware()
except Exception:
    pass

DURATION = float(sys.argv[1]) if len(sys.argv) > 1 else 8.0
TIMEOUT_MS = 100

DXGI_ERROR_WAIT_TIMEOUT = 0x887A0027
DXGI_ERROR_ACCESS_LOST = 0x887A0026
DXGI_ERROR_NOT_CURRENTLY_AVAILABLE = 0x887A0022
DXGI_ERROR_MORE_DATA = 0x887A002B

S_OK = 0


class GUID(ctypes.Structure):
    _fields_ = [("Data1", ctypes.c_ulong), ("Data2", ctypes.c_ushort),
                ("Data3", ctypes.c_ushort), ("Data4", ctypes.c_ubyte * 8)]


def guid(s):
    g = GUID()
    ctypes.windll.ole32.CLSIDFromString(ctypes.c_wchar_p(s), ctypes.byref(g))
    return g


IID_IDXGIFactory1 = guid("{770aae78-f26f-4dba-a829-253c83d1b387}")
IID_IDXGIOutput1 = guid("{00cddea8-939b-4b83-a340-a685226666cc}")


class LARGE_INTEGER(ctypes.Structure):
    _fields_ = [("QuadPart", ctypes.c_longlong)]


class POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]


class POINTER_POSITION(ctypes.Structure):
    _fields_ = [("Position", POINT), ("Visible", wt.BOOL)]


class FRAME_INFO(ctypes.Structure):
    _fields_ = [
        ("LastPresentTime", LARGE_INTEGER),
        ("LastMouseUpdateTime", LARGE_INTEGER),
        ("AccumulatedFrames", ctypes.c_uint),
        ("RectsCoalesced", wt.BOOL),
        ("ProtectedContentMaskedOut", wt.BOOL),
        ("PointerPosition", POINTER_POSITION),
        ("TotalMetadataBufferSize", ctypes.c_uint),
        ("PointerShapeBufferSize", ctypes.c_uint),
    ]


class RECT(ctypes.Structure):
    _fields_ = [("left", ctypes.c_long), ("top", ctypes.c_long),
                ("right", ctypes.c_long), ("bottom", ctypes.c_long)]


def com(ptr, index, restype, *argtypes):
    vtbl = ctypes.cast(ptr, ctypes.POINTER(ctypes.POINTER(ctypes.c_void_p))).contents
    proto = ctypes.WINFUNCTYPE(restype, ctypes.c_void_p, *argtypes)
    return proto(vtbl[index])


def ok(hr, what):
    if hr < 0:
        raise OSError("%s hr=0x%08X" % (what, hr & 0xFFFFFFFF))
    return hr


def default_desktop_name():
    u32 = ctypes.WinDLL("user32")
    h = ctypes.c_void_p()
    u32.GetThreadDesktop.restype = ctypes.c_void_p
    k32 = ctypes.WinDLL("kernel32")
    k32.GetCurrentThreadId.restype = wt.DWORD
    h = u32.GetThreadDesktop(k32.GetCurrentThreadId())
    need = wt.DWORD()
    u32.GetUserObjectInformationW(ctypes.c_void_p(h), 2, None, 0, ctypes.byref(need))
    buf = ctypes.create_unicode_buffer(need.value)
    u32.GetUserObjectInformationW(ctypes.c_void_p(h), 2, buf, need.value, ctypes.byref(need))
    return buf.value


def cpu_times():
    k32 = ctypes.WinDLL("kernel32")
    k32.GetCurrentProcess.restype = ctypes.c_void_p
    h = k32.GetCurrentProcess()
    c = LARGE_INTEGER()
    e = LARGE_INTEGER()
    k = LARGE_INTEGER()
    u = LARGE_INTEGER()
    k32.GetProcessTimes(ctypes.c_void_p(h), ctypes.byref(c), ctypes.byref(e),
                        ctypes.byref(k), ctypes.byref(u))
    return (k.QuadPart + u.QuadPart) / 1e7


report = {"probe": "dxgi_desktop_duplication", "duration_s": DURATION,
          "desktop": default_desktop_name()}

dxgi = ctypes.WinDLL("dxgi")
CreateDXGIFactory1 = dxgi.CreateDXGIFactory1
CreateDXGIFactory1.restype = ctypes.c_long
CreateDXGIFactory1.argtypes = [ctypes.POINTER(GUID), ctypes.POINTER(ctypes.c_void_p)]

factory = ctypes.c_void_p()
hr = CreateDXGIFactory1(ctypes.byref(IID_IDXGIFactory1), ctypes.byref(factory))
if hr < 0:
    report["error"] = "CreateDXGIFactory1 hr=0x%08X" % (hr & 0xFFFFFFFF)
    print(json.dumps(report, indent=2))
    sys.exit(0)

enum_adapters1 = com(factory, 12, ctypes.c_long, ctypes.c_uint, ctypes.POINTER(ctypes.c_void_p))
adapter = ctypes.c_void_p()
hr = enum_adapters1(factory, 0, ctypes.byref(adapter))
report["enum_adapters1_hr"] = "0x%08X" % (hr & 0xFFFFFFFF)
if hr < 0 or not adapter:
    report["error"] = "no adapter"
    print(json.dumps(report, indent=2))
    sys.exit(0)

enum_outputs = com(adapter, 7, ctypes.c_long, ctypes.c_uint, ctypes.POINTER(ctypes.c_void_p))
output = ctypes.c_void_p()
hr = enum_outputs(adapter, 0, ctypes.byref(output))
report["enum_outputs_hr"] = "0x%08X" % (hr & 0xFFFFFFFF)
if hr < 0 or not output:
    report["error"] = "no output"
    print(json.dumps(report, indent=2))
    sys.exit(0)

qi = com(output, 0, ctypes.c_long, ctypes.POINTER(GUID), ctypes.POINTER(ctypes.c_void_p))
out1 = ctypes.c_void_p()
hr = qi(output, ctypes.byref(IID_IDXGIOutput1), ctypes.byref(out1))
report["qi_output1_hr"] = "0x%08X" % (hr & 0xFFFFFFFF)
if hr < 0:
    report["error"] = "no IDXGIOutput1"
    print(json.dumps(report, indent=2))
    sys.exit(0)

d3d11 = ctypes.WinDLL("d3d11")
D3D11CreateDevice = d3d11.D3D11CreateDevice
D3D11CreateDevice.restype = ctypes.c_long
D3D11CreateDevice.argtypes = [
    ctypes.c_void_p, ctypes.c_uint, ctypes.c_void_p, ctypes.c_uint,
    ctypes.c_void_p, ctypes.c_uint, ctypes.c_uint,
    ctypes.POINTER(ctypes.c_void_p), ctypes.POINTER(ctypes.c_uint),
    ctypes.POINTER(ctypes.c_void_p)]
device = ctypes.c_void_p()
ctx = ctypes.c_void_p()
level = ctypes.c_uint()
D3D11_CREATE_DEVICE_BGRA_SUPPORT = 0x0
hr = D3D11CreateDevice(adapter, 0, None, D3D11_CREATE_DEVICE_BGRA_SUPPORT,
                       None, 0, 7, ctypes.byref(device), ctypes.byref(level),
                       ctypes.byref(ctx))
report["d3d11_create_device_hr"] = "0x%08X" % (hr & 0xFFFFFFFF)
if hr < 0:
    report["error"] = "no D3D11 device"
    print(json.dumps(report, indent=2))
    sys.exit(0)

duplicate = com(out1, 22, ctypes.c_long, ctypes.c_void_p, ctypes.POINTER(ctypes.c_void_p))


class OUTPUT_DESC(ctypes.Structure):
    _fields_ = [("DeviceName", ctypes.c_wchar * 32), ("DesktopCoordinates", RECT),
                ("AttachedToDesktop", wt.BOOL), ("Rotation", ctypes.c_uint),
                ("Monitor", ctypes.c_void_p)]


_getdesc = com(out1, 7, ctypes.c_long, ctypes.POINTER(OUTPUT_DESC))
_d = OUTPUT_DESC()
_hr = _getdesc(out1, ctypes.byref(_d))
report["output_desc_hr"] = "0x%08X" % (_hr & 0xFFFFFFFF)
report["output_name"] = _d.DeviceName
report["output_rect"] = [_d.DesktopCoordinates.left, _d.DesktopCoordinates.top,
                         _d.DesktopCoordinates.right, _d.DesktopCoordinates.bottom]
report["output_attached"] = bool(_d.AttachedToDesktop)
dupl = ctypes.c_void_p()
hr = duplicate(out1, device, ctypes.byref(dupl))
report["duplicate_output_hr"] = "0x%08X" % (hr & 0xFFFFFFFF)
if hr < 0:
    report["error"] = "DuplicateOutput failed (0x887A0022 = NOT_CURRENTLY_AVAILABLE)"
    print(json.dumps(report, indent=2))
    sys.exit(0)

acquire = com(dupl, 8, ctypes.c_long, ctypes.c_uint, ctypes.POINTER(FRAME_INFO), ctypes.POINTER(ctypes.c_void_p))
get_dirty = com(dupl, 9, ctypes.c_long, ctypes.c_uint, ctypes.c_void_p, ctypes.POINTER(ctypes.c_uint))
get_move = com(dupl, 10, ctypes.c_long, ctypes.c_uint, ctypes.c_void_p, ctypes.POINTER(ctypes.c_uint))
release_frame = com(dupl, 14, ctypes.c_long)
release_com = com(dupl, 2, ctypes.c_ulong)

BUFSZ = 1 << 20
buf_d = ctypes.create_string_buffer(BUFSZ)
buf_m = ctypes.create_string_buffer(BUFSZ)


def rects_from(buf, nbytes):
    n = nbytes // ctypes.sizeof(RECT)
    out = []
    if n:
        arr = ctypes.cast(buf, ctypes.POINTER(RECT))
        for i in range(n):
            out.append((arr[i].left, arr[i].top, arr[i].right, arr[i].bottom))
    return out


cpu0 = cpu_times()
wall0 = time.time()
deadline = wall0 + DURATION

stats = {"acquired": 0, "timeout": 0, "access_lost": 0, "other": 0,
         "frames_with_dirty": 0, "dirty_total": 0, "dirty_min": None,
         "dirty_max": 0, "move_frames": 0, "move_total": 0,
         "move_min": None, "move_max": 0, "coalesced": 0,
         "protected": 0, "accumulated_sum": 0, "ptr_frames": 0,
         "examples_dirty": [], "examples_move": [],
         "frame_intervals_ms": []}
last_ts = None
while time.time() < deadline:
    fi = FRAME_INFO()
    res = ctypes.c_void_p()
    hr = acquire(dupl, TIMEOUT_MS, ctypes.byref(fi), ctypes.byref(res))
    hsigned = hr & 0xFFFFFFFF
    if hsigned == DXGI_ERROR_WAIT_TIMEOUT:
        stats["timeout"] += 1
        continue
    if hsigned == DXGI_ERROR_ACCESS_LOST:
        stats["access_lost"] += 1
        break
    if hr < 0:
        stats["other"] += 1
        if len(stats["examples_dirty"]) < 1:
            pass
        break
    now = time.time()
    if last_ts is not None:
        stats["frame_intervals_ms"].append((now - last_ts) * 1000.0)
    last_ts = now
    stats["acquired"] += 1
    stats["accumulated_sum"] += fi.AccumulatedFrames
    if fi.RectsCoalesced:
        stats["coalesced"] += 1
    if fi.ProtectedContentMaskedOut:
        stats["protected"] += 1
    if fi.PointerPosition.Visible:
        stats["ptr_frames"] += 1

    need = ctypes.c_uint(0)
    hrd = get_dirty(dupl, BUFSZ, ctypes.cast(buf_d, ctypes.c_void_p), ctypes.byref(need))
    if hrd >= 0:
        dr = rects_from(buf_d, need.value)
        c = len(dr)
        if c:
            stats["frames_with_dirty"] += 1
            stats["dirty_total"] += c
            stats["dirty_max"] = max(stats["dirty_max"], c)
            stats["dirty_min"] = c if stats["dirty_min"] is None else min(stats["dirty_min"], c)
            if len(stats["examples_dirty"]) < 6:
                stats["examples_dirty"].append({"n": c, "rects": dr[:6]})
    need2 = ctypes.c_uint(0)
    hrm = get_move(dupl, BUFSZ, ctypes.cast(buf_m, ctypes.c_void_p), ctypes.byref(need2))
    if hrm >= 0:
        mr = rects_from(buf_m, need2.value)
        c = len(mr)
        if c:
            stats["move_frames"] += 1
            stats["move_total"] += c
            stats["move_max"] = max(stats["move_max"], c)
            stats["move_min"] = c if stats["move_min"] is None else min(stats["move_min"], c)
            if len(stats["examples_move"]) < 6:
                stats["examples_move"].append({"n": c, "rects": mr[:6]})

    if res:
        release_com(res)
    release_frame(dupl)

wall = time.time() - wall0
cpu = cpu_times() - cpu0
report["stats"] = stats
report["wall_s"] = round(wall, 3)
report["cpu_s"] = round(cpu, 4)
report["cpu_pct"] = round(100.0 * cpu / wall, 2) if wall else None
iv = stats.pop("frame_intervals_ms")
if iv:
    report["frame_interval_ms"] = {"min": round(min(iv), 2), "max": round(max(iv), 2),
                                   "avg": round(sum(iv) / len(iv), 2)}
print(json.dumps(report, indent=2))
