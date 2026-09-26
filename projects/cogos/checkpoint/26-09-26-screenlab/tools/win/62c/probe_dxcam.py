import json
import sys
import time

out = {"probe": "dxcam_independent_dxgi"}
try:
    import dxcam
    out["dxcam_version"] = getattr(dxcam, "__version__", "?")
except Exception as e:
    out["import"] = "exc:" + repr(e)
    print(json.dumps(out, indent=2))
    sys.exit(0)

cam = None
try:
    cam = dxcam.create(device_idx=0, output_idx=0, output_color="BGRA")
    out["create"] = "ok" if cam is not None else "none"
except Exception as e:
    out["create"] = "exc:" + repr(e)

if cam is None:
    print(json.dumps(out, indent=2))
    sys.exit(0)

DUR = float(sys.argv[1]) if len(sys.argv) > 1 else 5.0
try:
    n = 0
    times = []
    shapes = set()
    t0 = time.time()
    while time.time() - t0 < DUR:
        t = time.time()
        f = cam.grab()
        if f is not None:
            n += 1
            times.append((time.time() - t) * 1000)
            shapes.add(tuple(f.shape))
        time.sleep(0.03)
    out["grabs_nonnull"] = n
    out["shapes"] = [list(s) for s in shapes]
    if times:
        out["grab_ms"] = {"min": round(min(times), 2), "max": round(max(times), 2),
                          "avg": round(sum(times) / len(times), 2)}
        out["wall_s"] = round(time.time() - t0, 2)
except Exception as e:
    out["loop_exc"] = repr(e)

try:
    del cam
except Exception:
    pass
print(json.dumps(out, indent=2))
