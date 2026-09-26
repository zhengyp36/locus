import sys, os, json, ctypes, importlib, shutil, subprocess
from ctypes import wintypes

out = {}
out["python"] = sys.version
out["exe"] = sys.executable
out["cwd"] = os.getcwd()

for m in ["PIL", "numpy", "comtypes", "dxcam", "windows_capture", "winrt",
          "winsdk", "win32gui", "pywintypes", "screenlab"]:
    try:
        mod = importlib.import_module(m)
        out["pkg:" + m] = getattr(mod, "__version__", "OK")
    except Exception as e:
        out["pkg:" + m] = "NO:" + type(e).__name__

k32 = ctypes.WinDLL("kernel32", use_last_error=True)
u32 = ctypes.WinDLL("user32", use_last_error=True)
pid = k32.GetCurrentProcessId()
sid = wintypes.DWORD()
k32.ProcessIdToSessionId(pid, ctypes.byref(sid))
out["pid"] = pid
out["session_id"] = sid.value

def uo_name(h):
    need = wintypes.DWORD()
    u32.GetUserObjectInformationW(h, 2, None, 0, ctypes.byref(need))
    buf = ctypes.create_unicode_buffer(need.value)
    u32.GetUserObjectInformationW(h, 2, buf, need.value, ctypes.byref(need))
    return buf.value

h = u32.GetProcessWindowStation()
hd = u32.GetThreadDesktop(k32.GetCurrentThreadId())
out["winsta"] = uo_name(h) if h else None
out["desktop"] = uo_name(hd) if hd else None

out["SM_CXSCREEN"] = u32.GetSystemMetrics(0)
out["SM_CYSCREEN"] = u32.GetSystemMetrics(1)
out["SM_CMONITORS"] = u32.GetSystemMetrics(80)
out["SM_CXVIRTUALSCREEN"] = u32.GetSystemMetrics(78)
out["SM_CYVIRTUALSCREEN"] = u32.GetSystemMetrics(79)
try:
    out["dpi_system"] = u32.GetDpiForSystem()
except Exception:
    pass

for dll in ["dxgi.dll", "d3d11.dll", "d3d12.dll", "gdi32.dll", "user32.dll",
            "dwmapi.dll", "windows.graphics.capture.dll"]:
    try:
        ctypes.WinDLL(dll)
        out["dll:" + dll] = "OK"
    except Exception as e:
        out["dll:" + dll] = "NO:" + type(e).__name__

for exe in ["csc", "dotnet", "py"]:
    out["which:" + exe] = shutil.which(exe)
if shutil.which("dotnet"):
    try:
        out["dotnet_sdks"] = subprocess.run(
            ["dotnet", "--list-sdks"], capture_output=True, text=True,
            timeout=20).stdout.strip()
    except Exception as e:
        out["dotnet_sdks"] = "ERR:" + type(e).__name__

print(json.dumps(out, indent=2, ensure_ascii=False))
