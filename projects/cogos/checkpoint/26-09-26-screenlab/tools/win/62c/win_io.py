"""Product-backend I/O worker for the Windows loop (Slice 3).

Runs inside assist's INTERACTIVE session via tools/win/62c/launch_probe.ps1.
Reads a one-shot JSON request (win_io.req) and writes a JSON result
(win_io.result), both next to this file. Uses the *product* backend
(screenlab.service.platform_backends) so the loop exercises the real
DXGI/dxcam capture + SendInput path.

Request:  {"op": "capture"|"tap"|"info", "args": {...}}
  capture: {"path": "<png out>", "max_dim": <int|omit>}
  tap:     {"x": <px>, "y": <px>}
"""
import hashlib
import json
import os
import sys

DIR = os.path.dirname(os.path.abspath(__file__))
PREFIX = r"C:\Users\assist\AppData\Local\screenlab"
REQ = os.path.join(DIR, "win_io.req")
RES = os.path.join(DIR, "win_io.result")
if PREFIX not in sys.path:
    sys.path.insert(0, PREFIX)


def write_result(obj: dict) -> None:
    tmp = RES + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(obj, fh)
    os.replace(tmp, RES)


def main() -> None:
    with open(REQ, encoding="utf-8") as fh:
        req = json.load(fh)
    op = req.get("op")
    args = req.get("args") or {}

    from screenlab.service import platform_backends

    capture, act, displays = platform_backends.pick(backend="win32")
    act_name = getattr(act, "name", None)

    if op == "capture":
        data, size = capture.grab(max_dim=args.get("max_dim"))
        path = args.get("path") or os.path.join(DIR, "win_io.png")
        with open(path, "wb") as fh:
            fh.write(data)
        obj = {"ok": True, "op": op, "backend": capture.name,
               "size": list(size), "png_bytes": len(data),
               "sha256": hashlib.sha256(data).hexdigest(), "path": path}
    elif op == "tap":
        res = act.pointer(int(args["x"]), int(args["y"]))
        obj = {"ok": True, "op": op, "act": act_name, "result": res}
    elif op == "info":
        obj = {"ok": True, "op": op, "backend": capture.name, "act": act_name,
               "displays": displays(), "active": act.active_window()}
    else:
        obj = {"ok": False, "error": "unknown op: %r" % (op,)}

    write_result(obj)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # noqa: BLE001
        import traceback

        write_result({"ok": False, "error": repr(exc),
                      "traceback": traceback.format_exc()})
