import ctypes
import ctypes.wintypes as wt
import json

class GUID(ctypes.Structure):
    _fields_ = [("Data1", ctypes.c_ulong), ("Data2", ctypes.c_ushort),
                ("Data3", ctypes.c_ushort), ("Data4", ctypes.c_ubyte * 8)]

def guid(s):
    g = GUID(); ctypes.windll.ole32.CLSIDFromString(ctypes.c_wchar_p(s), ctypes.byref(g)); return g

IID_IDXGIFactory1 = guid("{770aae78-f26f-4dba-a829-253c83d1b387}")
IID_IDXGIOutput1 = guid("{00cddea8-939b-4b83-a340-a685226666cc}")

def com(ptr, index, restype, *argtypes):
    vt = ctypes.cast(ptr, ctypes.POINTER(ctypes.POINTER(ctypes.c_void_p))).contents
    proto = ctypes.WINFUNCTYPE(restype, ctypes.c_void_p, *argtypes)
    return proto(vt[index])

out = {}
dxgi = ctypes.WinDLL("dxgi")
C = dxgi.CreateDXGIFactory1
C.restype = ctypes.c_long
C.argtypes = [ctypes.POINTER(GUID), ctypes.POINTER(ctypes.c_void_p)]
f = ctypes.c_void_p()
out["create_hr"] = "0x%08X" % (C(ctypes.byref(IID_IDXGIFactory1), ctypes.byref(f)) & 0xFFFFFFFF)
out["factory"] = repr(f)
ea = com(f, 12, ctypes.c_long, ctypes.c_uint, ctypes.POINTER(ctypes.c_void_p))
a = ctypes.c_void_p()
out["enum_adapters_hr"] = "0x%08X" % (ea(f, 0, ctypes.byref(a)) & 0xFFFFFFFF)
out["adapter"] = repr(a)
eo = com(a, 7, ctypes.c_long, ctypes.c_uint, ctypes.POINTER(ctypes.c_void_p))
o = ctypes.c_void_p()
out["enum_outputs_hr"] = "0x%08X" % (eo(a, 0, ctypes.byref(o)) & 0xFFFFFFFF)
out["output"] = repr(o)
qi = com(o, 0, ctypes.c_long, ctypes.POINTER(GUID), ctypes.POINTER(ctypes.c_void_p))
o1 = ctypes.c_void_p()
out["qi_hr"] = "0x%08X" % (qi(o, ctypes.byref(IID_IDXGIOutput1), ctypes.byref(o1)) & 0xFFFFFFFF)
out["out1"] = repr(o1)

class RECT(ctypes.Structure):
    _fields_ = [("left", ctypes.c_long), ("top", ctypes.c_long), ("right", ctypes.c_long), ("bottom", ctypes.c_long)]
class OUTPUT_DESC(ctypes.Structure):
    _fields_ = [("DeviceName", ctypes.c_wchar * 32), ("DesktopCoordinates", RECT),
                ("AttachedToDesktop", wt.BOOL), ("Rotation", ctypes.c_uint), ("Monitor", ctypes.c_void_p)]

for label, iface in [("output_getdesc", o), ("out1_getdesc", o1)]:
    try:
        gd = com(iface, 8, ctypes.c_long, ctypes.POINTER(OUTPUT_DESC))
        d = OUTPUT_DESC()
        hr = gd(iface, ctypes.byref(d))
        out[label] = {"hr": "0x%08X" % (hr & 0xFFFFFFFF), "attached": d.AttachedToDesktop,
                      "rect": [d.DesktopCoordinates.left, d.DesktopCoordinates.top,
                               d.DesktopCoordinates.right, d.DesktopCoordinates.bottom]}
    except Exception as e:
        out[label] = "EXC:" + repr(e)

try:
    wfv = com(o, 11, ctypes.c_long)
    out["wait_for_vblank"] = "0x%08X" % (wfv(o) & 0xFFFFFFFF)
except Exception as e:
    out["wait_for_vblank"] = "EXC:" + repr(e)

try:
    gp = com(o, 6, ctypes.c_long, ctypes.POINTER(GUID), ctypes.POINTER(ctypes.c_void_p))
    par = ctypes.c_void_p()
    out["get_parent"] = {"hr": "0x%08X" % (gp(o, ctypes.byref(IID_IDXGIFactory1), ctypes.byref(par)) & 0xFFFFFFFF),
                         "ptr": repr(par)}
except Exception as e:
    out["get_parent"] = "EXC:" + repr(e)

try:
    gd0 = com(o, 8, ctypes.c_long, ctypes.c_void_p)
    out["getdesc_null"] = "0x%08X" % (gd0(o, ctypes.c_void_p(0)) & 0xFFFFFFFF)
except Exception as e:
    out["getdesc_null"] = "EXC:" + repr(e)

print(json.dumps(out, indent=2))
