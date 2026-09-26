#!/usr/bin/env python3.11
"""Slice 3 acceptance for the Windows live loop: look -> mark -> coord -> zoom -> act.

Ground truth: a topmost Tk target window we launch inside assist's interactive
session, which measures and reports its own physical screen rect (DPI-aware) in
target.marker. Its center is the pixel the whole chain must land on. The loop is
accepted only if the model-facing chain (imgctx look/mark/coord/act, --backend
win) lands there AND the injected click actually reaches the target (marker
flips READY -> HIT): coord px == truth center, act device == coord, the post-act
frame differs, the self-computed diff bbox contains the point, and HIT appears.

The backend is the *product* path: DXGI/dxcam capture + SendInput injection,
run per-op in the interactive session (tools/windows.sh -> 62c harness).

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
WIN = TOOLS / "windows.sh"

# The loop goes through the product ``screen/1`` daemon in assist's interactive
# session (loopback TCP 19911, consent auto), reached over an ssh tunnel that
# imgctx builds from --ssh. The daemon is started/stopped via windows.sh.
ENDPOINT = os.environ.get("SL_WIN_ENDPOINT", "tcp:127.0.0.1:19911")
KEY = os.environ.get("SL_AGENT_KEY", str(TOOLS / "keys" / "agent.key"))
SSH = os.environ.get("SL_WIN_SSH", "assist@100.112.50.115")

PX_TOL = 3
BASE = Path(tempfile.mkdtemp(prefix="windows-selftest-"))
ROOT = BASE / "dom"
STATE = "s3.json"
FAIL: list[str] = []


def check(name: str, cond: bool, detail="") -> None:
    print(("PASS " if cond else "FAIL ") + name + ("" if cond else f"  :: {detail}"))
    if not cond:
        FAIL.append(name)


def win(*a: str, timeout: int = 180) -> str:
    r = subprocess.run([str(WIN), *a], capture_output=True, text=True, timeout=timeout)
    lines = [ln for ln in r.stdout.splitlines() if ln.strip()]
    out = lines[-1] if lines else ""
    print("$ windows.sh", " ".join(a), "->", out[:200])
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
                        "--backend", "win", "--endpoint", ENDPOINT,
                        "--key", KEY, "--ssh", SSH, *a],
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


def target_state() -> dict:
    out = win("target-state")
    try:
        return json.loads(out)
    except Exception:
        return {}


def wait_target(want: str, tries: int = 40) -> dict:
    st = {}
    for _ in range(tries):
        st = target_state()
        if st.get("state") == want:
            return st
        if st.get("state") in ("TIMEOUT", "HIT") and want == "READY":
            return st
        subprocess.run(["sleep", "0.5"])
    return st


def main() -> int:
    win("deploy")
    win("it-daemon", "start")
    subprocess.run(["sleep", "4"])
    win("target-start")
    st = wait_target("READY")
    check("target reaches READY", st.get("state") == "READY", st)
    if st.get("state") != "READY":
        win("it-daemon", "stop")
        print("\nRESULT: FAIL", FAIL)
        return 1
    truth_px = tuple(int(v) for v in st["center"])
    screen = tuple(int(v) for v in st["screen"])
    print(f"ground truth target center px={truth_px} screen={screen} rect={st.get('rect')}")
    W, H = screen
    norm = (truth_px[0] / W, truth_px[1] / H)

    o = run("look")
    check("look ok", o.get("ok") is True, o)
    check(f"look orig is {W}x{H}", f"（{W}×{H}）" in o.get("text", ""), o.get("text"))
    fig0 = fig_of(o)
    pre_frame = o.get("frame", "")
    check("look mints FIG", bool(fig0) and fig0.isdigit(), fig0)
    check("look produced a frame png", Path(pre_frame).is_file(), pre_frame)

    m = run("mark", "--ref", f"FIG:{fig0}", "--kind", "cross",
            "--center", f"{norm[0]},{norm[1]}")
    check("mark ok", m.get("ok") is True, m)
    c = run("coord", "--ref", f"FIG:{fig0}", "--anno", last_anno(m))
    check("coord px == target center", near(parse_px(c.get("text", "")), truth_px), c.get("text"))

    z = run("see", "--ref", f"FIG:{fig0}", "--center", f"{norm[0]},{norm[1]}",
            "--size", "0.3,0.3")
    check("zoom ok", z.get("ok") is True, z)
    check("zoom window did not clamp", "clamp" not in z.get("text", ""), z.get("text"))
    fig1 = fig_of(z)
    check("zoom mints a new FIG", fig1.isdigit() and fig1 != fig0, fig1)
    m2 = run("mark", "--ref", f"FIG:{fig1}", "--kind", "cross", "--center", "0.5,0.5")
    c2 = run("coord", "--ref", f"FIG:{fig1}", "--anno", last_anno(m2))
    check("zoom->orig px still target center", near(parse_px(c2.get("text", "")), truth_px),
          c2.get("text"))

    a = run("act", "--ref", f"FIG:{fig1}", "--anno", last_anno(m2))
    check("act ok", a.get("ok") is True, a)
    check("act device == target center", near(tuple(a.get("device", ())), truth_px), a.get("device"))
    check(f"act screen {W}x{H}", a.get("screen") == list(screen), a.get("screen"))
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
        check("change bbox contains click point",
              bx <= truth_px[0] <= bx + bw and by <= truth_px[1] <= by + bh, bbox)

    st2 = wait_target("HIT")
    check("target received the injected click (READY->HIT)", st2.get("state") == "HIT", st2)

    win("it-daemon", "stop")
    print(f"\nstate dir: {BASE}")
    print("RESULT: FAIL " + str(FAIL) if FAIL else "RESULT: ALL PASS")
    return 1 if FAIL else 0


if __name__ == "__main__":
    raise SystemExit(main())
