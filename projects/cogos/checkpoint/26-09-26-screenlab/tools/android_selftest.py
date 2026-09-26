#!/usr/bin/env python3.11
"""Slice 2 acceptance for the Android live loop: look -> mark -> coord -> zoom -> act.

Ground truth: the phone's home screen, where the launcher itself reports the Chrome
dock icon's bounds via uiautomator. Its center is the device px the whole chain must
land on. The loop is accepted only if the model-facing chain (imgctx look/mark/coord/
act, --backend android) taps that icon's center AND Chrome actually comes to the
foreground: coord px == icon center, act device == coord, the post-tap frame differs
from the pre-tap frame, and mResumedActivity becomes com.android.chrome.

This is the #61 coordinate-chain fix made verifiable: act takes its device pixel size
from the FIG's own frame (the image the model saw), not a separately-queried geometry.

Every imgctx call is a separate process (state persistence + id continuity real).
Exit 0 = all pass.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import tempfile
from pathlib import Path

PY = "/usr/bin/python3.11"
TOOLS = Path(__file__).resolve().parent
CLI = TOOLS / "imgctx.py"
AND = TOOLS / "android.sh"

# The loop now goes through the product ``screen/1`` service (the assist app on
# LAN 8901), not the ad-hoc adb backend: auth = agent key, consent = dev auto.
ENDPOINT = os.environ.get("SL_ANDROID_ENDPOINT", "tcp:192.168.1.175:8901")
KEY = os.environ.get("SL_ANDROID_AGENT_KEY", str(TOOLS / "keys" / "android_agent.key"))

PX_TOL = 3                 # normalization/rounding slack
TARGET_LABEL = "Chrome"    # launcher dock icon, located via uiautomator bounds
TARGET_PKG = "com.android.chrome"

BASE = Path(tempfile.mkdtemp(prefix="android-selftest-"))
ROOT = BASE / "dom"
STATE = "s2.json"

FAIL: list[str] = []


def check(name: str, cond: bool, detail="") -> None:
    print(("PASS " if cond else "FAIL ") + name + ("" if cond else f"  :: {detail}"))
    if not cond:
        FAIL.append(name)


def andr(*a: str) -> str:
    r = subprocess.run([str(AND), *a], capture_output=True, text=True, timeout=180)
    lines = [ln for ln in r.stdout.splitlines() if ln.strip()]
    out = lines[-1] if lines else ""
    print("$ android.sh", " ".join(a), "->", out)
    return out


def sd(*a: str) -> dict:
    r = subprocess.run([PY, str(TOOLS / "screendiff.py"), *a],
                       capture_output=True, text=True, timeout=60)
    lines = [ln for ln in r.stdout.splitlines() if ln.strip()]
    try:
        out = json.loads(lines[-1])
    except Exception:
        out = {"ok": False, "raw": r.stdout, "err": r.stderr, "rc": r.returncode}
    print("$ screendiff", " ".join(a), "->", json.dumps(out, ensure_ascii=False)[:200])
    return out


def run(*a: str) -> dict:
    r = subprocess.run([PY, str(CLI), "--root", str(ROOT), "--state", STATE,
                        "--backend", "android", "--endpoint", ENDPOINT,
                        "--key", KEY, *a],
                       capture_output=True, text=True, timeout=180)
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


def near(a, b, tol=PX_TOL) -> bool:
    return abs(a[0] - b[0]) <= tol and abs(a[1] - b[1]) <= tol


def parse_px(text: str) -> tuple[int, int]:
    i = text.find("像素")
    seg = text[i:]
    open_ = seg.find("(")
    a, b = seg[open_ + 1:seg.find(")", open_)].split(",")
    return int(a), int(b)


def sha(path: str) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def wait_foreground(pkg: str, tries: int = 8) -> str:
    fg = ""
    for _ in range(tries):
        fg = andr("foreground")
        if fg.startswith(pkg):
            return fg
        subprocess.run(["sleep", "0.6"])
    return fg


def main() -> int:
    andr("consent-auto")  # dev: the app approves the agent key without a human
    andr("key", "KEYCODE_WAKEUP")
    andr("key", "KEYCODE_HOME")
    subprocess.run(["sleep", "1.0"])
    geo = tuple(int(v) for v in andr("geometry").split("x"))
    check("device is 1080x2312", geo == (1080, 2312), geo)
    W, H = geo

    truth = andr("ui-bounds", TARGET_LABEL)
    parts = truth.split("\t")
    check(f"uiautomator found {TARGET_LABEL} bounds", len(parts) == 3, truth)
    if len(parts) != 3:
        print("\nRESULT: FAIL", FAIL)
        return 1
    tx, ty = (int(v) for v in parts[1].split(","))
    truth_px = (tx, ty)
    norm = (tx / W, ty / H)
    print(f"ground truth {TARGET_LABEL} center px={truth_px} norm=({norm[0]:.4f},{norm[1]:.4f})")

    home = andr("foreground")
    check("home screen on top before look", "launcher" in home.lower(), home)

    o = run("look")
    check("look ok", o.get("ok") is True, o)
    check("look orig is 1080x2312", "（1080×2312）" in o.get("text", ""), o.get("text"))
    fig0 = fig_of(o)
    pre_frame = o.get("frame", "")
    check("look mints FIG", bool(fig0) and fig0.isdigit(), fig0)
    check("look produced a frame png", Path(pre_frame).is_file(), pre_frame)

    # Fingerprint (global hash) can differ on sub-block noise (e.g. clock seconds);
    # the meaningful stability signal is the block diff finding no changed cell.
    home2 = andr("capture")
    d0 = sd(pre_frame, home2)
    check("home screen stable (no changed block)", d0.get("bbox") is None, d0)

    m = run("mark", "--ref", f"FIG:{fig0}", "--kind", "cross",
            "--center", f"{norm[0]},{norm[1]}")
    check("mark ok", m.get("ok") is True, m)
    c = run("coord", "--ref", f"FIG:{fig0}", "--anno", last_anno(m))
    check("coord px == icon center", near(parse_px(c.get("text", "")), truth_px), c.get("text"))

    # 0.15 window (not 0.2): the dock icon sits at y=0.919, so a 0.2-tall window
    # would clamp against the bottom and break the center==target identity.
    z = run("see", "--ref", f"FIG:{fig0}", "--center", f"{norm[0]},{norm[1]}",
            "--size", "0.15,0.15")
    check("zoom ok", z.get("ok") is True, z)
    check("zoom window did not clamp", "clamp" not in z.get("text", ""), z.get("text"))
    fig1 = fig_of(z)
    check("zoom mints a new FIG", fig1.isdigit() and fig1 != fig0, fig1)
    m2 = run("mark", "--ref", f"FIG:{fig1}", "--kind", "cross", "--center", "0.5,0.5")
    c2 = run("coord", "--ref", f"FIG:{fig1}", "--anno", last_anno(m2))
    check("zoom->orig px still icon center", near(parse_px(c2.get("text", "")), truth_px),
          c2.get("text"))

    a = run("act", "--ref", f"FIG:{fig1}", "--anno", last_anno(m2))
    check("act ok", a.get("ok") is True, a)
    check("act device == icon center", near(tuple(a.get("device", ())), truth_px), a.get("device"))
    check("act screen 1080x2312", a.get("screen") == list(geo), a.get("screen"))
    check("act returns landing FIG", str(a.get("landing_fig", "")).isdigit()
          and a.get("landing_fig") != fig1, a.get("landing_fig"))
    ptr = a.get("pointer", "")
    dev = a.get("device", [])
    check("pointer echoes device px", f"{dev[0]}" in ptr and f"{dev[1]}" in ptr, ptr)
    post_frame = a.get("frame", "")
    check("screen changed after act (frame hash differs)",
          bool(pre_frame) and bool(post_frame) and sha(pre_frame) != sha(post_frame),
          f"{pre_frame} vs {post_frame}")
    d1 = sd(pre_frame, post_frame)
    bbox = d1.get("bbox")
    check("self-computed diff detects change", d1.get("same") is False and bbox is not None, d1)
    if bbox:
        bx, by, bw, bh = bbox
        check("change bbox contains tap point",
              bx <= truth_px[0] <= bx + bw and by <= truth_px[1] <= by + bh, bbox)

    fg = wait_foreground(TARGET_PKG)
    check(f"{TARGET_PKG} is foreground after act", fg.startswith(TARGET_PKG), fg)

    andr("key", "KEYCODE_HOME")
    print(f"\nstate dir: {BASE}")
    print("RESULT: FAIL " + str(FAIL) if FAIL else "RESULT: ALL PASS")
    return 1 if FAIL else 0


if __name__ == "__main__":
    raise SystemExit(main())
