"""Newline-delimited JSON framing with an optional trailing binary payload.

Request  = one JSON line.
Response = one JSON header line, then `bytes_len` raw bytes (if > 0).
"""
from __future__ import annotations

import json
from typing import Any, Dict, Optional, Tuple


def dumps(obj: Dict[str, Any]) -> bytes:
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":")).encode("utf-8") + b"\n"


class Channel:
    """Wraps a socket file object for this tiny protocol."""

    def __init__(self, rfile, wfile):
        self._rfile = rfile
        self._wfile = wfile

    def send(self, header: Dict[str, Any], payload: bytes = b"") -> None:
        h = dict(header)
        if payload:
            h["bytes_len"] = len(payload)
        self._wfile.write(dumps(h))
        if payload:
            self._wfile.write(payload)
        self._wfile.flush()

    def recv(self) -> Tuple[Dict[str, Any], bytes]:
        line = self._rfile.readline()
        if not line:
            raise EOFError("connection closed")
        header = json.loads(line.decode("utf-8"))
        n = int(header.get("bytes_len") or 0)
        payload = self._rfile.read(n) if n else b""
        return header, payload
