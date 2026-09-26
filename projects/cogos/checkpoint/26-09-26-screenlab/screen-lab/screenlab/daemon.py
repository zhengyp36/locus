"""screen/1 daemon (prototype).

Must run *inside* the target session (see spec-screen-1 §5.1): capture and
injection both go through the session's X display / compositor.

Ops: caps, displays, state, see, act, blob_get, ping.
Transport: newline-delimited JSON over a Unix socket, optional binary tail.
"""
from __future__ import annotations

import hashlib
import json
import os
import socket
import sys
import threading
import time
from typing import Any, Dict, List, Optional

from . import backends, platform_backends
from .framing import Channel

PROTOCOL = "screen/1"


class ScreenDaemon:
    def __init__(self, display: Optional[str], xauth: Optional[str], blob_dir: str,
                 backend: Optional[str] = None, adb_serial: Optional[str] = None):
        self.display = display
        self.xauth = xauth
        self.blob_dir = blob_dir
        os.makedirs(blob_dir, exist_ok=True)
        self.capture, self.act_backend, self.displays_fn = platform_backends.pick(
            display, xauth, backend=backend, adb_serial=adb_serial
        )
        if backend is None:
            backend = "win32" if sys.platform == "win32" else "x11"
        self.platform = {"x11": "linux/x11", "win32": "win32", "android": "android"}.get(backend, backend)
        self.lock = threading.Lock()
        self.gen = 0
        self.current_snapshot = None  # type: Optional[str]
        self.last_frame_hash = None  # type: Optional[str]
        self.started_at = time.time()

    # -- blobs -------------------------------------------------------------
    def _blob_path(self, sha: str) -> str:
        return os.path.join(self.blob_dir, sha)

    def _store_blob(self, data: bytes) -> str:
        sha = hashlib.sha256(data).hexdigest()
        path = self._blob_path(sha)
        if not os.path.exists(path):
            tmp = path + ".part"
            with open(tmp, "wb") as fh:
                fh.write(data)
            os.rename(tmp, path)
        return sha

    # -- snapshots ---------------------------------------------------------
    def _issue_snapshot(self, frame_hash: str) -> str:
        self.gen += 1
        sid = "%d-%d" % (os.getpid(), self.gen)
        self.current_snapshot = sid
        self.last_frame_hash = frame_hash
        return sid

    # -- ops ---------------------------------------------------------------
    def op_caps(self, _req: Dict) -> Dict:
        return {
            "protocol": PROTOCOL,
            "platform": self.platform,
            "capture_backend": self.capture.name,
            "act_backend": self.act_backend.name,
            "display": self.display,
            "modes": ["pixels"],  # "tree" (a11y) not implemented yet
            "act_kinds": ["pointer", "key", "type", "scroll", "paste", "focus"],
            "pid": os.getpid(),
        }

    def op_ping(self, _req: Dict) -> Dict:
        return {"pong": True, "uptime": round(time.time() - self.started_at, 3)}

    def op_displays(self, _req: Dict) -> Dict:
        displays = self.displays_fn()
        if not displays:
            data, (w, h) = self.capture.grab()
            displays = [{"id": "screen", "name": "screen", "primary": True, "geometry": [w, h, 0, 0]}]
        return {"displays": displays, "display": self.display}

    def op_state(self, req: Dict) -> Dict:
        with self.lock:
            if req.get("frame"):
                data, _ = self.capture.grab()
                fh = hashlib.sha256(data).hexdigest()
                sid = self._issue_snapshot(fh)
                self._store_blob(data)
            else:
                fh = self.last_frame_hash
                sid = self.current_snapshot
            return {
                "display": self.display,
                "pointer": self.act_backend.pointer_pos(),
                "focus": self.act_backend.active_window(),
                "frame_hash": fh,
                "snapshot_id": sid,
            }

    def op_see(self, req: Dict) -> Dict:
        region = req.get("region")
        if region is not None:
            region = tuple(int(v) for v in region)
        max_dim = req.get("max_dim")
        if max_dim is not None:
            max_dim = int(max_dim)
        since_hash = req.get("since_hash")
        wait = req.get("wait_stable")
        with self.lock:
            if wait:
                data, size = self._grab_stable(region, max_dim, float(wait))
            else:
                data, size = self.capture.grab(region=region, max_dim=max_dim)
            fh = hashlib.sha256(data).hexdigest()
            if since_hash and since_hash == fh:
                self.last_frame_hash = fh
                return {
                    "unchanged": True,
                    "frame_hash": fh,
                    "snapshot_id": self.current_snapshot,
                    "size": list(size),
                    "blobs": [],
                    "capture_backend": self.capture.name,
                }
            sha = self._store_blob(data)
            sid = self._issue_snapshot(fh)
            return {
                "unchanged": False,
                "snapshot_id": sid,
                "frame_hash": fh,
                "size": list(size),
                "blobs": [sha],
                "capture_backend": self.capture.name,
            }

    def _grab_stable(self, region, max_dim, timeout: float):
        deadline = time.time() + timeout
        prev = None
        last = None
        while True:
            data, size = self.capture.grab(region=region, max_dim=max_dim)
            fh = hashlib.sha256(data).hexdigest()
            last = (data, size)
            if fh == prev:
                return data, size
            prev = fh
            if time.time() >= deadline:
                return last
            time.sleep(0.2)

    def op_act(self, req: Dict) -> Dict:
        snapshot_id = req.get("snapshot_id")
        kind = req.get("kind")
        with self.lock:
            if snapshot_id != self.current_snapshot:
                return {
                    "ok": False,
                    "error": "stale_snapshot",
                    "detail": "act must bind the snapshot_id returned by the latest see/state",
                    "current_snapshot_id": self.current_snapshot,
                }
            self.current_snapshot = None  # invalidate before acting
            result = self._dispatch_act(kind, req)
            # issue a fresh snapshot so the caller can immediately point again
            data, size = self.capture.grab()
            fh = hashlib.sha256(data).hexdigest()
            self._store_blob(data)
            sid = self._issue_snapshot(fh)
            result.update({"snapshot_id": sid, "frame_hash": fh, "size": list(size)})
            return result

    def _dispatch_act(self, kind: str, req: Dict) -> Dict:
        if kind == "pointer":
            r = self.act_backend.pointer(
                int(req["x"]), int(req["y"]),
                button=int(req.get("button", 1)), clicks=int(req.get("clicks", 1)),
            )
        elif kind == "key":
            r = self.act_backend.key(req["key"])
        elif kind == "type":
            r = self.act_backend.type_text(req["text"], delay=int(req.get("delay", 40)))
        elif kind == "scroll":
            r = self.act_backend.scroll(int(req.get("dy", -1)), req.get("x"), req.get("y"))
        elif kind == "paste":
            r = self.act_backend.key("ctrl+v")
        elif kind == "focus":
            r = self.act_backend.focus_window(str(req["window_id"]))
        else:
            raise backends.BackendError("unsupported act kind: %s" % kind)
        return {"ok": True, "kind": kind, "acted": r}

    def op_blob_get(self, req: Dict):
        sha = req["sha"]
        path = self._blob_path(sha)
        if not os.path.exists(path):
            return {"ok": False, "error": "not_found", "sha": sha}, b""
        with open(path, "rb") as fh:
            return {"ok": True, "sha": sha}, fh.read()

    # -- dispatch ----------------------------------------------------------
    def handle(self, req: Dict):
        op = req.get("op")
        handler = {
            "caps": self.op_caps,
            "ping": self.op_ping,
            "displays": self.op_displays,
            "state": self.op_state,
            "see": self.op_see,
            "act": self.op_act,
            "blob_get": self.op_blob_get,
        }.get(op)
        if handler is None:
            return {"ok": False, "error": "unknown_op", "op": op}, b""
        try:
            out = handler(req)
        except backends.BackendError as exc:
            return {"ok": False, "error": "backend_error", "detail": str(exc)}, b""
        except Exception as exc:  # noqa: BLE001
            return {"ok": False, "error": exc.__class__.__name__, "detail": str(exc)}, b""
        if isinstance(out, tuple):
            return out
        return out, b""


def _serve_conn(daemon: ScreenDaemon, conn: socket.socket) -> None:
    rfile = conn.makefile("rb")
    wfile = conn.makefile("wb")
    chan = Channel(rfile, wfile)
    try:
        while True:
            req, _ = chan.recv()
            resp, payload = daemon.handle(req)
            chan.send(resp, payload)
    except EOFError:
        pass
    except Exception:
        pass
    finally:
        try:
            conn.close()
        except Exception:
            pass


def _announce(daemon: ScreenDaemon, where: Dict) -> None:
    info = {
        "event": "listening",
        "display": daemon.display,
        "platform": daemon.platform,
        "capture_backend": daemon.capture.name,
        "act_backend": daemon.act_backend.name,
        "pid": os.getpid(),
    }
    info.update(where)
    print(json.dumps(info), flush=True)


def _accept_loop(srv: socket.socket, daemon: ScreenDaemon, cleanup) -> None:
    try:
        while True:
            conn, _ = srv.accept()
            threading.Thread(target=_serve_conn, args=(daemon, conn), daemon=True).start()
    except KeyboardInterrupt:
        pass
    finally:
        srv.close()
        if cleanup:
            cleanup()


def serve(display: Optional[str], xauth: Optional[str], sock_path: str, blob_dir: str,
          backend: Optional[str] = None, adb_serial: Optional[str] = None) -> None:
    daemon = ScreenDaemon(display, xauth, blob_dir, backend=backend, adb_serial=adb_serial)
    if os.path.exists(sock_path):
        os.unlink(sock_path)
    os.makedirs(os.path.dirname(sock_path), exist_ok=True)
    srv = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    srv.bind(sock_path)
    srv.listen(16)
    _announce(daemon, {"socket": sock_path})
    _accept_loop(srv, daemon, lambda: os.path.exists(sock_path) and os.unlink(sock_path))


def serve_tcp(host: str, port: int, blob_dir: str, display: Optional[str] = None,
              xauth: Optional[str] = None, backend: Optional[str] = None,
              adb_serial: Optional[str] = None) -> None:
    daemon = ScreenDaemon(display, xauth, blob_dir, backend=backend, adb_serial=adb_serial)
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind((host, port))
    srv.listen(16)
    _announce(daemon, {"tcp": "%s:%d" % (host, port)})
    _accept_loop(srv, daemon, None)
