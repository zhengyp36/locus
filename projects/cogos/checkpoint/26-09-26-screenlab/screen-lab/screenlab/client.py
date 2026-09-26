"""screen/1 client: thin transport wrapper, no platform logic."""
from __future__ import annotations

import socket
from typing import Any, Dict, Tuple

from .framing import Channel


class ClientError(Exception):
    pass


class ScreenClient:
    def __init__(self, sock_path: str = None, host: str = None, port: int = None, timeout: float = 60.0):
        self.sock_path = sock_path
        self.host = host
        self.port = port
        self.timeout = timeout
        self._sock = None
        self._chan = None

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, *exc):
        self.close()

    def connect(self) -> None:
        if self.host is not None:
            s = socket.create_connection((self.host, int(self.port)), timeout=self.timeout)
        else:
            s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            s.settimeout(self.timeout)
            s.connect(self.sock_path)
        self._sock = s
        self._chan = Channel(s.makefile("rb"), s.makefile("wb"))

    def close(self) -> None:
        if self._sock is not None:
            try:
                self._sock.close()
            finally:
                self._sock = None
                self._chan = None

    def call(self, op: str, **params: Any) -> Tuple[Dict[str, Any], bytes]:
        if self._chan is None:
            raise ClientError("not connected")
        req = {"op": op}
        req.update(params)
        self._chan.send(req)
        header, payload = self._chan.recv()
        if header.get("ok") is False and "error" in header:
            raise ClientError("%s: %s" % (header.get("error"), header.get("detail", "")))
        return header, payload
