"""screen/1 CLI (prototype).

Unix socket (Linux) or loopback TCP (Windows; OpenSSH cannot forward AF_UNIX).

Usage:
  python -m screenlab.cli daemon --display :0 [--xauth PATH] [--socket S]
  python -m screenlab.cli --tcp 127.0.0.1:9911 daemon
  python -m screenlab.cli [--socket S | --tcp HOST:PORT] ping|caps|displays
  python -m screenlab.cli [opts] state [--frame]
  python -m screenlab.cli [opts] see [--region x,y,w,h] [--max-dim N]
                                        [--since-hash H] [--wait-stable SEC] [--out PATH]
  python -m screenlab.cli [opts] act pointer --x N --y N [--button 1] [--clicks 1] --snapshot SID
  python -m screenlab.cli [opts] act key --key ctrl+l --snapshot SID
  python -m screenlab.cli [opts] act type --text "..." [--delay 40] --snapshot SID
  python -m screenlab.cli [opts] act scroll --dy -1 [--x X --y Y] --snapshot SID
  python -m screenlab.cli [opts] act focus --window-id WID --snapshot SID
  python -m screenlab.cli [opts] blob-get --sha SHA --out PATH
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any, Dict

from .client import ClientError, ScreenClient
from .daemon import serve, serve_tcp

DEFAULT_SOCKET = os.environ.get("SCREEN_SOCKET", "/tmp/kilo/screen-lab/run/screen.sock")
DEFAULT_BLOB_DIR = os.environ.get("SCREEN_BLOB_DIR", "/tmp/kilo/screen-lab/blobs")


def _print(obj: Dict[str, Any]) -> None:
    print(json.dumps(obj, ensure_ascii=False, indent=2))


def _parse_region(text):
    return [int(v) for v in text.split(",")]


def _endpoint(args):
    if getattr(args, "tcp", None):
        host, port = args.tcp.rsplit(":", 1)
        return {"host": host, "port": int(port)}
    return {"sock_path": args.socket}


def cmd_daemon(args) -> int:
    if args.tcp:
        host, port = args.tcp.rsplit(":", 1)
        serve_tcp(host, int(port), args.blob_dir, display=args.display, xauth=args.xauth,
                  backend=args.backend, adb_serial=args.adb_serial)
    else:
        if not args.display and args.backend != "android":
            raise SystemExit("daemon needs --display (unix socket) or --tcp HOST:PORT "
                             "(or --backend android)")
        serve(args.display, args.xauth, args.socket, args.blob_dir,
              backend=args.backend, adb_serial=args.adb_serial)
    return 0


def cmd_simple(op):
    def run(args):
        with ScreenClient(**_endpoint(args)) as c:
            header, _ = c.call(op)
        _print(header)
        return 0
    return run


def cmd_state(args) -> int:
    with ScreenClient(**_endpoint(args)) as c:
        header, _ = c.call("state", frame=bool(args.frame))
    _print(header)
    return 0


def cmd_see(args) -> int:
    params = {"mode": args.mode}
    if args.region:
        params["region"] = _parse_region(args.region)
    if args.max_dim:
        params["max_dim"] = args.max_dim
    if args.since_hash:
        params["since_hash"] = args.since_hash
    if args.wait_stable:
        params["wait_stable"] = args.wait_stable
    with ScreenClient(**_endpoint(args)) as c:
        header, _ = c.call("see", **params)
        if args.out and header.get("blobs"):
            sha = header["blobs"][0]
            _, payload = c.call("blob_get", sha=sha)
            with open(args.out, "wb") as fh:
                fh.write(payload)
            header["saved_to"] = args.out
    _print(header)
    return 0


def cmd_act(args) -> int:
    params: Dict[str, Any] = {"kind": args.kind, "snapshot_id": args.snapshot}
    if args.kind == "pointer":
        params.update({"x": args.x, "y": args.y, "button": args.button, "clicks": args.clicks})
    elif args.kind == "key":
        params["key"] = args.key
    elif args.kind == "type":
        params.update({"text": args.text, "delay": args.delay})
    elif args.kind == "scroll":
        params["dy"] = args.dy
        if args.x is not None:
            params["x"] = args.x
        if args.y is not None:
            params["y"] = args.y
    elif args.kind == "focus":
        params["window_id"] = args.window_id
    elif args.kind == "paste":
        params["key"] = "ctrl+v"
    with ScreenClient(**_endpoint(args)) as c:
        header, _ = c.call("act", **params)
    _print(header)
    return 0 if header.get("ok") else 1


def cmd_blob_get(args) -> int:
    with ScreenClient(**_endpoint(args)) as c:
        header, payload = c.call("blob_get", sha=args.sha)
    if args.out:
        with open(args.out, "wb") as fh:
            fh.write(payload)
        header["saved_to"] = args.out
        header["bytes"] = len(payload)
    _print(header)
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="screenlab")
    src = p.add_mutually_exclusive_group()
    src.add_argument("--socket", default=DEFAULT_SOCKET)
    src.add_argument("--tcp", default=None, help="HOST:PORT (Windows)")
    p.add_argument("--backend", default=None, choices=["x11", "win32", "android"],
                   help="platform adapter for the daemon (default: auto by host OS)")
    p.add_argument("--adb-serial", default=None, help="adb device serial (android backend)")
    sub = p.add_subparsers(dest="cmd", required=True)

    d = sub.add_parser("daemon")
    d.add_argument("--display", default=None)
    d.add_argument("--xauth", default=None)
    d.add_argument("--socket", default=DEFAULT_SOCKET)
    d.add_argument("--blob-dir", default=DEFAULT_BLOB_DIR)
    d.set_defaults(func=cmd_daemon)

    for op in ("ping", "caps", "displays"):
        s = sub.add_parser(op)
        s.set_defaults(func=cmd_simple(op))

    s = sub.add_parser("state")
    s.add_argument("--frame", action="store_true")
    s.set_defaults(func=cmd_state)

    s = sub.add_parser("see")
    s.add_argument("--mode", default="auto", choices=["auto", "pixels", "tree"])
    s.add_argument("--region", default=None, help="x,y,w,h")
    s.add_argument("--max-dim", type=int, default=None)
    s.add_argument("--since-hash", default=None)
    s.add_argument("--wait-stable", type=float, default=None)
    s.add_argument("--out", default=None, help="save first blob to this path")
    s.set_defaults(func=cmd_see)

    a = sub.add_parser("act")
    a.add_argument("kind", choices=["pointer", "key", "type", "scroll", "paste", "focus"])
    a.add_argument("--snapshot", required=True)
    a.add_argument("--x", type=int)
    a.add_argument("--y", type=int)
    a.add_argument("--button", type=int, default=1)
    a.add_argument("--clicks", type=int, default=1)
    a.add_argument("--key")
    a.add_argument("--text")
    a.add_argument("--delay", type=int, default=40)
    a.add_argument("--dy", type=int, default=-1)
    a.add_argument("--window-id")
    a.set_defaults(func=cmd_act)

    b = sub.add_parser("blob-get")
    b.add_argument("--sha", required=True)
    b.add_argument("--out", default=None)
    b.set_defaults(func=cmd_blob_get)

    return p


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.func(args)
    except ClientError as exc:
        _print({"ok": False, "error": "client_error", "detail": str(exc)})
        return 1
    except (FileNotFoundError, ConnectionRefusedError, ConnectionError) as exc:
        _print({"ok": False, "error": "connect_failed", "detail": str(exc)})
        return 1


if __name__ == "__main__":
    sys.exit(main())
