#!/usr/bin/env python3
"""Reusable agent-side driver for the 3a screenlab endpoint.

Replaces the throwaway /tmp/kilo/e4_*.py scripts. Every invocation with a fresh
connection triggers one consent request on the human's desktop (by design).

Coordinates for `act` are normalized (0..1) unless `--abs` is given.

    tools/agent.py probe
    tools/agent.py act 0.30 0.60 [--button 1] [--clicks 1] [--cap out.png]
    tools/agent.py key "ctrl+l"
    tools/agent.py hold  [--secs 180] [--x 0.30] [--y 0.60]
    tools/agent.py watch [--secs 180]

Env (see tools/env.sh): SL_ENDPOINT, SL_AGENT_KEY, SL_BLOB_ROOT.
"""
import argparse
import json
import os
import sys
import time

COGOS = os.environ.get("SL_COGOS", "/home/zhengyp/work/A/cogos")
sys.path.insert(0, COGOS)

from cogos.agent.impl.graphics import GraphicsUnavailable, ScreenChannel  # noqa: E402


def ts() -> str:
    return time.strftime("%H:%M:%S")


def make_channel(args) -> ScreenChannel:
    return ScreenChannel(
        args.endpoint,
        key_path=args.key,
        blob_root=args.blob_root,
        timeout=args.timeout,
    )


def role(st: dict) -> str:
    return (st.get("seat") or {}).get("role", "?")


def cmd_probe(ch: ScreenChannel, args) -> int:
    info = ch.info()
    print("server=%s backends=%s" % (info.get("protocol"), info.get("backends")), flush=True)
    d = ch.displays()
    print("displays=%s" % json.dumps(d.get("displays"), ensure_ascii=False), flush=True)
    st = ch.state()
    print("seat=%s gen=%s" % (role(st), (st.get("screen") or {}).get("generation")), flush=True)
    h = ch.capture()
    out = args.cap or os.path.join(args.blob_root, "probe-%d.png" % int(time.time()))
    os.makedirs(os.path.dirname(out), exist_ok=True)
    ch.save_frame(h["image"]["blob_sha"], out)
    print("capture hash=%s -> %s" % (h.get("frame_hash", "")[:12], out), flush=True)
    return 0


def cmd_act(ch: ScreenChannel, args) -> int:
    ch.capture()
    if args.op == "key":
        r = ch.act("key", key=args.keyseq)
    else:
        r = ch.act("pointer", x=args.x, y=args.y, button=args.button, clicks=args.clicks)
    st = ch.state()
    print("act=%s seat=%s gen=%s" % (json.dumps(r, ensure_ascii=False), role(st),
                                     (st.get("screen") or {}).get("generation")), flush=True)
    if args.cap:
        h = ch.capture()
        ch.save_frame(h["image"]["blob_sha"], args.cap)
        print("capture -> %s" % args.cap, flush=True)
    return 0


def cmd_hold(ch: ScreenChannel, args) -> int:
    ch.capture()
    r = ch.act("pointer", x=args.x, y=args.y, button=1, clicks=1)
    st = ch.state()
    print("%s act=%s seat=%s" % (ts(), r.get("ok", r), role(st)), flush=True)
    print("%s READY: agent holds input (real mouse -> PREEMPT, %s -> REVOKE)"
          % (ts(), os.environ.get("SL_TAKEBACK_KEYS", "Ctrl+Alt+Shift+Escape")), flush=True)
    t0 = time.time()
    while time.time() - t0 < args.secs:
        try:
            st = ch.state()
        except GraphicsUnavailable as exc:
            print("%s REVOKED after %.1fs: %s" % (ts(), time.time() - t0, exc), flush=True)
            return 0
        r = role(st)
        if r != "controller":
            print("%s PREEMPTED role=%s after %.1fs" % (ts(), r, time.time() - t0), flush=True)
            t1 = time.time()
            while time.time() - t1 < args.secs:
                try:
                    ch.state()
                except GraphicsUnavailable as exc:
                    print("%s REVOKED after %.1fs: %s" % (ts(), time.time() - t1, exc), flush=True)
                    return 0
                time.sleep(0.4)
            print("%s NO_REVOKE_TIMEOUT" % ts(), flush=True)
            return 1
        time.sleep(0.4)
    print("%s NO_PREEMPT_TIMEOUT" % ts(), flush=True)
    return 1


def cmd_watch(ch: ScreenChannel, args) -> int:
    ch.capture()
    print("%s connected; waiting up to %ss for revoke" % (ts(), args.secs), flush=True)
    t0 = time.time()
    while time.time() - t0 < args.secs:
        try:
            ch.state()
        except GraphicsUnavailable as exc:
            print("%s REVOKED after %.1fs: %s" % (ts(), time.time() - t0, exc), flush=True)
            return 0
        time.sleep(0.4)
    print("%s NO_REVOKE_TIMEOUT" % ts(), flush=True)
    return 1


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--endpoint", default=os.environ.get("SL_ENDPOINT", "tcp:100.100.137.78:8911"))
    p.add_argument("--key", default=os.environ.get("SL_AGENT_KEY",
                  "/home/zhengyp/work/A/checkpoint/tools/keys/agent.key"))
    p.add_argument("--blob-root", default=os.environ.get(
        "SL_BLOB_ROOT", "/home/zhengyp/work/A/checkpoint/tools/blobs"))
    p.add_argument("--timeout", type=int, default=300)
    sub = p.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("probe"); sp.add_argument("--cap"); sp.set_defaults(fn=cmd_probe)
    sa = sub.add_parser("act")
    sa.add_argument("x", nargs="?", type=float, default=0.5)
    sa.add_argument("y", nargs="?", type=float, default=0.5)
    sa.add_argument("--button", type=int, default=1)
    sa.add_argument("--clicks", type=int, default=1)
    sa.add_argument("--cap")
    sa.set_defaults(fn=cmd_act, op="pointer", keyseq=None)
    sk = sub.add_parser("key"); sk.add_argument("keyseq"); sk.add_argument("--cap")
    sk.set_defaults(fn=cmd_act, op="key", x=0.5, y=0.5, button=1, clicks=1)
    sh = sub.add_parser("hold")
    sh.add_argument("--secs", type=int, default=180)
    sh.add_argument("--x", type=float, default=0.30)
    sh.add_argument("--y", type=float, default=0.60)
    sh.set_defaults(fn=cmd_hold)
    sw = sub.add_parser("watch"); sw.add_argument("--secs", type=int, default=180)
    sw.set_defaults(fn=cmd_watch)

    args = p.parse_args()
    ch = make_channel(args)
    try:
        return args.fn(ch, args)
    except GraphicsUnavailable as exc:
        print("UNAVAILABLE: %s" % exc, file=sys.stderr)
        return 2
    finally:
        try:
            ch.close()
        except Exception:
            pass


if __name__ == "__main__":
    sys.exit(main())
