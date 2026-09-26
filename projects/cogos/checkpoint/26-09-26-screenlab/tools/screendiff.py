#!/usr/bin/env python3.11
"""screendiff — generic self-computed change signal between two captured frames.

Thin CLI over `screenlab.service.change`: an x8-downsampled fingerprint and a
coarse block-diff bbox. This is the universal fallback for platforms with no
native damage (Android over adb, plain X11): the mechanical layer reports *that*
and *where* pixels changed; the model decides what it means.

  screendiff.py fp A.png                 # {"ok":true,"fp":".."}
  screendiff.py A.png B.png              # {"ok":true,"same":bool,"bbox":[x,y,w,h]|null,...}
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

COGOS = os.environ.get("SL_COGOS", "/home/zhengyp/work/A/cogos")
if COGOS not in sys.path:
    sys.path.insert(0, COGOS)

from PIL import Image  # noqa: E402

from screenlab.service.change import diff_bbox, fingerprint  # noqa: E402


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="screendiff", description=__doc__)
    p.add_argument("files", nargs="+", help="fp <A> | <A> <B>")
    args = p.parse_args(argv)
    try:
        if len(args.files) == 1:
            with Image.open(args.files[0]) as im:
                out = {"ok": True, "fp": fingerprint(im)}
        elif len(args.files) == 2:
            with Image.open(args.files[0]) as a, Image.open(args.files[1]) as b:
                fa, fb = fingerprint(a), fingerprint(b)
                bbox = diff_bbox(a, b)
            out = {"ok": True, "fp_a": fa, "fp_b": fb, "same": fa == fb,
                   "bbox": list(bbox) if bbox else None}
        else:
            raise ValueError("expected 1 or 2 files")
    except (OSError, ValueError) as exc:
        print(json.dumps({"ok": False, "error": f"{type(exc).__name__}: {exc}"},
                         ensure_ascii=False))
        return 1
    print(json.dumps(out, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
