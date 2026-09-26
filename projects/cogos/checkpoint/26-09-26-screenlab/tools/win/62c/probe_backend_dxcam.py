"""Prove the product Windows capture backend (DXGI/dxcam, GDI fallback) inside
the interactive session: instantiate via platform_backends.pick, grab a frame,
and cross-check geometry / content against a GDI grab.

Run with tools/win/62c/launch_probe.ps1. Prints JSON metadata only (no pixels).
"""
import hashlib
import json
import os
import sys

PREFIX = r"C:\Users\assist\AppData\Local\screenlab"
OUT = r"C:\Users\assist\screenlab-62c"
sys.path.insert(0, PREFIX)

sys.argv_backend = os.environ.get("SCREENLAB_CAPTURE", "")
report = {"probe": "product_capture_backend", "forced": sys.argv_backend}
try:
    from screenlab.service import platform_backends

    capture, act, displays = platform_backends.pick(backend="win32")
    report["backend_name"] = capture.name
    report["act_name"] = getattr(act, "name", None)
    report["displays"] = displays()

    data, size = capture.grab()
    png_path = os.path.join(OUT, "dxcam_capture.png")
    with open(png_path, "wb") as fh:
        fh.write(data)
    report["full"] = {
        "size": list(size),
        "png_bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
        "path": png_path,
    }

    # region crop: (x, y, w, h) relative to the full screen
    rdata, rsize = capture.grab(region=(0, 0, 200, 100))
    report["region_0_0_200_100"] = {"size": list(rsize), "png_bytes": len(rdata)}

    # max_dim scaling
    mdata, msize = capture.grab(max_dim=320)
    report["max_dim_320"] = {"size": list(msize), "png_bytes": len(mdata)}

    # content cross-check vs GDI (same desktop, same instant)
    from screenlab.service.backends_win import PillowCaptureWin
    from PIL import Image
    import io

    gdata, gsize = PillowCaptureWin().grab()
    a = Image.open(io.BytesIO(data)).convert("RGB")
    g = Image.open(io.BytesIO(gdata)).convert("RGB")
    report["gdi"] = {"size": list(gsize), "png_bytes": len(gdata),
                     "same_size": list(gsize) == list(size)}
    if g.size == a.size:
        w, h = a.size
        pts = [(w // 2, h // 2), (w // 4, h // 3), (3 * w // 4, 2 * h // 3)]
        diffs = []
        for x, y in pts:
            pa = a.getpixel((x, y))
            pg = g.getpixel((x, y))
            diffs.append({"at": [x, y], "dxgi": list(pa), "gdi": list(pg),
                          "delta": [abs(pa[i] - pg[i]) for i in range(3)]})
        report["pixel_crosscheck"] = diffs
        report["pixel_max_delta"] = max(max(d["delta"]) for d in diffs)
except Exception as exc:  # noqa: BLE001
    import traceback
    report["error"] = repr(exc)
    report["traceback"] = traceback.format_exc()

print(json.dumps(report, indent=2))
