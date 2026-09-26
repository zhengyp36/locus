#!/usr/bin/env python3.11
"""Slice 1 acceptance for the X11 live loop: look -> mark -> coord -> act.

Ground truth: the throwaway surface is Xvfb 1280x800 with an openbox-centered
zenity dialog; its OK button is at normalized (0.567, 0.572) => device (726,458).
The loop is accepted only if the model-facing chain (imgctx look/mark/coord/act)
clicks that spot: coord px == expected px, pointer == device px, and the zenity
window disappears (1 -> 0). The zoom step re-marks inside a sub-window to prove
the @原图 mapping survives an unregistered crop (Slice 0 covered static zoom).

Every imgctx call is a separate process (state persistence + id continuity real).
The device surface is (re)started by this script, so it is self-contained.
Exit 0 = all pass.
"""
from __future__ import annotations

import json
import subprocess
import tempfile
from pathlib import Path

PY = "/usr/bin/python3.11"
TOOLS = Path(__file__).resolve().parent
CLI = TOOLS / "imgctx.py"
X11 = TOOLS / "x11.sh"

SCREEN = (1280, 800)
OK_NORM = (0.567, 0.572)                 # known truth on the 1280x800 surface
OK_PX = (round(OK_NORM[0] * SCREEN[0]), round(OK_NORM[1] * SCREEN[1]))  # (726,458)
PX_TOL = 3                               # click target is ~90px wide; 3px is tight

BASE = Path(tempfile.mkdtemp(prefix="x11-selftest-"))
ROOT = BASE / "dom"
STATE = "s1.json"

FAIL: list[str] = []


def check(name: str, cond: bool, detail="") -> None:
    print(("PASS " if cond else "FAIL ") + name + ("" if cond else f"  :: {detail}"))
    if not cond:
        FAIL.append(name)


def run(*a: str) -> dict:
    r = subprocess.run([PY, str(CLI), "--root", str(ROOT), "--state", STATE, *a],
                       capture_output=True, text=True, timeout=180)
    try:
        out = json.loads(r.stdout.strip().splitlines()[-1])
    except Exception:
        out = {"ok": False, "raw": r.stdout, "err": r.stderr, "rc": r.returncode}
    print("$ imgctx", " ".join(a))
    print("  ->", json.dumps(out, ensure_ascii=False)[:400])
    return out


def x11(*a: str) -> str:
    r = subprocess.run([str(X11), *a], capture_output=True, text=True, timeout=180)
    lines = [ln for ln in r.stdout.splitlines() if ln.strip()]
    print("$ x11.sh", " ".join(a), "->", lines[-1] if lines else r.stderr.strip()[:200])
    return lines[-1] if lines else ""


def fig_of(block: dict) -> str:
    return block.get("text", "").split("|")[0].split(":")[1].strip()


def last_anno(block: dict) -> str:
    toks = [t for t in block.get("text", "").split() if t.startswith("ANNO:")]
    return toks[-1] if toks else "?"


def near(a, b, tol=PX_TOL) -> bool:
    return abs(a[0] - b[0]) <= tol and abs(a[1] - b[1]) <= tol


def parse_px(text: str) -> tuple[int, int]:
    # "... | 像素 (726,458)" or "... | 像素 中心 (726,458) ..."
    i = text.find("像素")
    seg = text[i:]
    open_ = seg.find("(")
    a, b = seg[open_ + 1:seg.find(")", open_)].split(",")
    return int(a), int(b)


def main() -> int:
    x11("start")
    geo = tuple(int(v) for v in x11("geometry").split()[-2:])
    check("surface 1280x800", geo == SCREEN, geo)
    before = int(x11("zenity").split()[-1])
    check("zenity target visible (1 window)", before == 1, before)

    o = run("look")
    check("look ok", o.get("ok") is True, o)
    check("look orig is 1280x800", "（1280×800）" in o.get("text", ""), o.get("text"))
    check("look render 800x500 (max_dim 800)", o.get("image_size") == [800, 500], o.get("image_size"))
    fig0 = fig_of(o)
    check("look mints FIG", bool(fig0) and fig0.isdigit(), fig0)

    m = run("mark", "--ref", f"FIG:{fig0}", "--kind", "cross",
            "--center", f"{OK_NORM[0]},{OK_NORM[1]}")
    check("mark ok", m.get("ok") is True, m)
    c = run("coord", "--ref", f"FIG:{fig0}", "--anno", last_anno(m))
    check("coord px == device truth", near(parse_px(c.get("text", "")), OK_PX), c.get("text"))
    check("coord norm == (0.567,0.572)",
          f"({OK_NORM[0]:.3f},{OK_NORM[1]:.3f})" in c.get("text", ""), c.get("text"))

    z = run("see", "--ref", f"FIG:{fig0}", "--center", f"{OK_NORM[0]},{OK_NORM[1]}",
            "--size", "0.2,0.2")
    check("zoom window 256x160", z.get("image_size") == [256, 160], z.get("image_size"))
    fig1 = fig_of(z)
    m2 = run("mark", "--ref", f"FIG:{fig1}", "--kind", "cross", "--center", "0.5,0.5")
    c2 = run("coord", "--ref", f"FIG:{fig1}", "--anno", last_anno(m2))
    check("zoom->orig px still device truth",
          near(parse_px(c2.get("text", "")), OK_PX), c2.get("text"))

    a = run("act", "--ref", f"FIG:{fig1}", "--anno", last_anno(m2))
    check("act ok", a.get("ok") is True, a)
    check("act device == truth", near(tuple(a.get("device", ())), OK_PX), a.get("device"))
    check("act screen 1280x800", a.get("screen") == list(SCREEN), a.get("screen"))
    check("act returns landing FIG", str(a.get("landing_fig", "")).isdigit()
          and a.get("landing_fig") != fig1, a.get("landing_fig"))
    ptr = a.get("pointer", "")
    dev = a.get("device", [])
    check("pointer == device px",
          f"X={dev[0]}" in ptr and f"Y={dev[1]}" in ptr, ptr)
    after = int(x11("zenity").split()[-1])
    check("zenity closed (1 -> 0)", after == 0, f"before={before} after={after}")

    print(f"\nstate dir: {BASE}")
    print("RESULT: FAIL " + str(FAIL) if FAIL else "RESULT: ALL PASS")
    return 1 if FAIL else 0


if __name__ == "__main__":
    raise SystemExit(main())
