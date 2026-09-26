#!/usr/bin/env python3.11
"""Slice 0 acceptance for imgctx CLI: known-truth PNG -> see/mark/coord.

Ground truth (800x600): red square center (600,150) => normalized (0.75,0.25);
green square center (200,450) => (0.25,0.75). Every CLI call is a separate
process, so state persistence + id continuity are exercised for real.
Exit 0 = all pass.
"""
from __future__ import annotations

import json
import subprocess
import tempfile
from pathlib import Path

from PIL import Image

PY = "/usr/bin/python3.11"
TOOLS = Path(__file__).resolve().parent
CLI = TOOLS / "imgctx.py"
BASE = Path(tempfile.mkdtemp(prefix="imgctx-selftest-"))
ROOT = BASE / "dom"
STATE = "s0.json"
IMG = BASE / "known.png"

FAIL: list[str] = []


def check(name: str, cond: bool, detail="") -> None:
    print(("PASS " if cond else "FAIL ") + name + ("" if cond else f"  :: {detail}"))
    if not cond:
        FAIL.append(name)


def run(*a: str) -> dict:
    r = subprocess.run([PY, str(CLI), "--root", str(ROOT), "--state", STATE, *a],
                       capture_output=True, text=True)
    try:
        out = json.loads(r.stdout.strip().splitlines()[-1])
    except Exception:
        out = {"ok": False, "raw": r.stdout, "err": r.stderr, "rc": r.returncode}
    print("$ imgctx", " ".join(a))
    print("  ->", json.dumps(out, ensure_ascii=False)[:400])
    return out


def fig_of(block: dict) -> str:
    return block.get("text", "").split("|")[0].split(":")[1].strip()


def last_anno(block: dict) -> str:
    toks = [t for t in block.get("text", "").split() if t.startswith("ANNO:")]
    return toks[-1] if toks else "?"


def main() -> int:
    im = Image.new("RGB", (800, 600), (20, 25, 35))
    for x in range(560, 640):
        for y in range(110, 190):
            im.putpixel((x, y), (220, 40, 40))
    for x in range(170, 230):
        for y in range(420, 480):
            im.putpixel((x, y), (40, 200, 80))
    im.save(IMG)

    o = run("see", "--ref", f"PATH:{IMG}")
    check("see whole ok", o.get("ok") is True, o)
    check("see whole size 800x600", o.get("image_size") == [800, 600], o.get("image_size"))
    fig0 = fig_of(o)
    check("whole fig == 1000", fig0 == "1000", fig0)

    m = run("mark", "--ref", f"FIG:{fig0}", "--kind", "cross", "--center", "0.75,0.25")
    check("mark cross ok", m.get("ok") is True, m)
    c = run("coord", "--ref", f"FIG:{fig0}", "--anno", last_anno(m))
    check("cross coord norm (0.750,0.250)", "(0.750,0.250)" in c.get("text", ""), c.get("text"))
    check("cross coord px (600,150)", "(600,150)" in c.get("text", ""), c.get("text"))

    z = run("see", "--ref", f"FIG:{fig0}", "--center", "0.75,0.25", "--size", "0.25,0.25")
    check("zoom size 200x150", z.get("image_size") == [200, 150], z.get("image_size"))
    fig1 = fig_of(z)
    check("zoom is new fig 1001", fig1 == "1001", fig1)

    m2 = run("mark", "--ref", f"FIG:{fig1}", "--kind", "cross", "--center", "0.5,0.5")
    c2 = run("coord", "--ref", f"FIG:{fig1}", "--anno", last_anno(m2))
    check("zoom->orig px (600,150)", "(600,150)" in c2.get("text", ""), c2.get("text"))

    m3 = run("mark", "--ref", f"FIG:{fig1}", "--kind", "rect", "--center", "0.5,0.5", "--size", "0.2,0.2")
    c3 = run("coord", "--ref", f"FIG:{fig1}", "--anno", last_anno(m3))
    t3 = c3.get("text", "")
    check("rect center px (600,150)", "(600,150)" in t3, t3)
    check("rect size px (40,30)", "(40,30)" in t3, t3)

    p = run("see", "--ref", f"PATH:{IMG}")
    check("persist dedup to FIG:1000", f"FIG:{fig0}" in p.get("text", ""), p.get("text"))

    q = run("see", "--ref", f"FIG:{fig0}", "--center=-0.2,0.5", "--size", "1.0,1.0")
    check("oob clamp flagged", "clamp:" in q.get("text", ""), q.get("text"))
    check("oob clamp effective 240x600", q.get("image_size") == [240, 600], q.get("image_size"))

    bad = run("coord", "--ref", "FIG:9999", "--anno", "ANNO:1")
    check("unknown fig errors", bad.get("ok") is False, bad)

    print(f"\nstate dir: {BASE}")
    print("RESULT: FAIL " + str(FAIL) if FAIL else "RESULT: ALL PASS")
    return 1 if FAIL else 0


if __name__ == "__main__":
    raise SystemExit(main())
