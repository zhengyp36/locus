#!/usr/bin/env python3.11
"""imgctx — thin CLI adapter over cogos/image_ctx (screenlab Slice 0/1).

argv -> image_ctx function + flock'd state file + structured JSON output.
Model-facing ops: see / mark / adjust-mark / unmark / coord (Slice 0); look / act
(device loop via a mechanical backend: tools/x11.sh for X11, tools/android.sh for
Android, tools/windows.sh for Windows). `--backend` / SL_SCREEN_BACKEND selects
it (default x11).
State: <root>/<state> (default tools/.imgctx/default.json); fig/anno ids persist
across invocations via Domain.save/load (design decisions 3-8).

Output is one JSON line: {"ok":true,"text":...,"image":<abs png path>,"image_size":[w,h],...}.
Read the PNG path as an attachment; the text carries FIG/ANNO ids + meta.
"""

from __future__ import annotations

import argparse
import fcntl
import json
import os
import sys
import time
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parent
COGOS = os.environ.get("SL_COGOS", "/home/zhengyp/work/A/cogos")
if COGOS not in sys.path:
    sys.path.insert(0, COGOS)

from PIL import Image  # noqa: E402

from cogos.agent.impl.graphics import (  # noqa: E402
    GraphicsUnavailable,
    ScreenChannel,
)
from cogos.agent.impl.terminal import SshTarget  # noqa: E402
from cogos.image_ctx import (  # noqa: E402
    Domain,
    RefError,
    adjust_mark,
    anno_to_src,
    coord,
    find_fig,
    mark,
    resolve_anno,
    see,
    source_of_fig,
    unmark,
)
from screenlab.proto.client import ClientError  # noqa: E402
from screenlab.service.change import diff_bbox  # noqa: E402

DEFAULT_ROOT = Path(os.environ.get("IMGCTX_ROOT", TOOLS_DIR / ".imgctx"))

# Device endpoints: the product ``screen/1`` service (no more ad-hoc backend
# scripts for look/act). ``backend`` only selects the default endpoint/key/tunnel;
# ``--endpoint`` / ``--key`` / ``--ssh`` override (screenlab-rules.md: tools use
# the product governance — snapshot/generation/consent/lifecycle).
_ENDPOINTS = {
    "x11": os.environ.get("SL_X11_ENDPOINT", "unix:/run/user/1002/screenlab.sock"),
    "android": os.environ.get("SL_ANDROID_ENDPOINT", "tcp:%s:%s" % (
        os.environ.get("SL_ANDROID_HOST", "192.168.1.175"),
        os.environ.get("SL_ANDROID_SVC_PORT", "8901"))),
    "win": os.environ.get("SL_WIN_ENDPOINT", "tcp:127.0.0.1:%s" % (
        os.environ.get("SL_WIN_PORT", "9911"))),
}
# ssh tunnel target per backend ("" = direct). Required where the service binds
# loopback on a remote box (Windows daemon) or a unix socket on the target (X11).
_SSH_TARGETS = {
    "x11": os.environ.get("SL_SCREEN_SSH", os.environ.get("SL_SSH", "")),
    "android": os.environ.get("SL_ANDROID_SSH", ""),
    "win": os.environ.get("SL_WIN_SSH", "assist@100.112.50.115"),
}


class ScreenDrift(RuntimeError):
    """The region the model saw moved before act; acting there would be wrong."""


def _ssh_target(spec: str):
    if not spec:
        return None
    user, _, hostport = spec.partition("@")
    if not hostport:
        user, hostport = None, spec
    host, _, port = hostport.partition(":")
    return SshTarget(host=host, user=user or None, port=int(port) if port else None)


def _channel(args) -> ScreenChannel:
    endpoint = args.endpoint or _ENDPOINTS[args.backend]
    key = args.key
    if key is None and not endpoint.startswith("unix:"):
        # TCP endpoints are the assist/auth path: an agent key is required.
        key = os.environ.get("SL_AGENT_KEY")
        if key and not Path(key).is_file():
            key = None
    ssh_spec = args.ssh if args.ssh is not None else _SSH_TARGETS[args.backend]
    return ScreenChannel(
        endpoint, key_path=key, ssh=_ssh_target(ssh_spec),
        blob_root=Path(args.root) / "frames",
    )


def _frame_path(root, tag: str) -> Path:
    """Every capture gets a unique path (image_ctx ``add_src`` dedups by path)."""
    out = Path(root) / "frames"
    out.mkdir(parents=True, exist_ok=True)
    return out / ("frame-%s-%d-%d.png" % (tag, os.getpid(), time.time_ns()))


def _capture_to(client: ScreenChannel, path) -> dict:
    """Capture the whole screen (native) and save its blob locally."""
    header = client.capture(since_hash="")
    image = header.get("image")
    if not image:
        raise RuntimeError("capture returned no image")
    client.save_frame(image["blob_sha"], path)
    return header


def _capture_settled(client: ScreenChannel, path, prev_path,
                     timeout: float = 5.0, interval: float = 0.4) -> dict:
    """Capture until the frame differs from ``prev_path`` (bounded), so the
    post-act confirmation shows the effect rather than the pre-render instant."""
    if not prev_path or not Path(prev_path).is_file():
        return _capture_to(client, path)
    deadline = time.time() + timeout
    while True:
        header = _capture_to(client, path)
        if _drift_bbox(prev_path, path) is not None or time.time() >= deadline:
            return header
        time.sleep(interval)


def _drift_bbox(a_path, b_path):
    """Coarse block diff between the model's frame and the fresh one (may be None)."""
    if not a_path or not Path(a_path).is_file():
        return None
    with Image.open(a_path) as a, Image.open(b_path) as b:
        return diff_bbox(a.convert("RGB"), b.convert("RGB"))


def _inside(bbox, pt) -> bool:
    x, y, w, h = bbox
    return x <= pt[0] <= x + w and y <= pt[1] <= y + h


def _fig_of(ref: str) -> str:
    return ref.split(":", 1)[1].strip()


def _pair(text: str) -> list[float]:
    a, b = text.split(",")
    return [float(a), float(b)]


def _resolve(args) -> tuple[Path, Path]:
    root = Path(args.root)
    sp = Path(args.state)
    if not sp.is_absolute():
        sp = root / sp
    return root, sp


def _dispatch(args):
    dom = Domain.open(args.root, state=args.state)
    cmd = args.command
    extra: dict = {}
    if cmd == "see":
        block = see(dom, args.ref, args.center, args.size, remark=args.remark)
    elif cmd == "mark":
        block = mark(dom, args.ref, args.kind, args.center, args.size, remark=args.remark)
    elif cmd == "adjust-mark":
        block = adjust_mark(dom, args.ref, args.anno, args.center, args.size, remark=args.remark)
    elif cmd == "unmark":
        block = unmark(dom, args.ref, args.anno)
    elif cmd == "coord":
        block = coord(dom, args.ref, args.anno)
    elif cmd == "look":
        client = _channel(args)
        try:
            frame = _frame_path(args.root, "look")
            header = _capture_to(client, frame)
        finally:
            client.close()
        block = see(dom, f"PATH:{frame}", remark=args.remark)
        extra = {"frame": str(frame), "backend": args.backend,
                 "snapshot_id": header.get("snapshot_id"),
                 "frame_hash": header.get("frame_hash"),
                 "capture_backend": header.get("capture_backend")}
    elif cmd == "act":
        fig = find_fig(dom, _fig_of(args.ref))
        if fig is None:
            raise RefError(f"unknown FIG: {_fig_of(args.ref)}")
        anno = resolve_anno(fig, args.anno)
        # #61 fix: act in the frame's own normalized space (@原图 = whole screen).
        norm, _px = anno_to_src(fig, anno)
        src = source_of_fig(dom, fig.fig_id)
        look_path = Path(src.path) if src is not None else None
        client = _channel(args)
        try:
            # Bind to the frame the model saw: capture fresh (mints this
            # connection's snapshot_id), refuse only if the region under the
            # target itself moved. The daemon still expiry-checks the token.
            fresh = _frame_path(args.root, "act")
            header = _capture_to(client, fresh)
            w, h = header["image"]["w"], header["image"]["h"]
            device = [round(norm[0] * w), round(norm[1] * h)]
            drift = _drift_bbox(look_path, fresh)
            if drift is not None and _inside(drift, device):
                raise ScreenDrift(
                    "target region changed since look (%s); re-look before act"
                    % (list(drift),))
            acted = client.act("pointer", x=norm[0], y=norm[1]).get("acted") or {}
            post = _frame_path(args.root, "post")
            _capture_settled(client, post, look_path)
        finally:
            client.close()
        fresh_block = see(dom, f"PATH:{post}")
        landing_fig = fresh_block.text.split("|")[0].split(":")[1].strip()
        block = mark(dom, f"FIG:{landing_fig}", "cross", [norm[0], norm[1]])
        dev = [acted.get("x", device[0]), acted.get("y", device[1])]
        extra = {"screen": [w, h], "norm": [norm[0], norm[1]],
                 "device": dev, "pointer": "X=%s Y=%s" % (dev[0], dev[1]),
                 "frame": str(post), "landing_fig": landing_fig,
                 "backend": args.backend, "stale": drift is not None}
    else:
        raise ValueError(f"unknown command: {cmd}")
    dom.save()
    return block, extra


def _add_common_ref(sp):
    sp.add_argument("--ref", required=True,
                    help="PATH:<file> | FIG:<id>")


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="imgctx", description=__doc__)
    p.add_argument("--root", default=str(DEFAULT_ROOT), help="domain root (images/cache/state)")
    p.add_argument("--state", default="default.json", help="state file name, relative to --root")
    p.add_argument("--backend", default=os.environ.get("SL_SCREEN_BACKEND", "x11"),
                   choices=("x11", "android", "win"),
                   help="device backend for look/act (default x11; env SL_SCREEN_BACKEND)")
    p.add_argument("--endpoint", default=None,
                   help="screen/1 endpoint (unix:/path | tcp:host:port); overrides --backend default")
    p.add_argument("--key", default=None,
                   help="agent private key for a TCP endpoint (default $SL_AGENT_KEY)")
    p.add_argument("--ssh", default=None,
                   help="ssh tunnel target [user@]host[:port] for a remote/loopback endpoint")
    sub = p.add_subparsers(dest="command", required=True)

    ps = sub.add_parser("see", help="open a PATH or re-view a FIG")
    _add_common_ref(ps)
    ps.add_argument("--center", type=_pair, help="cx,cy window center (0..1)")
    ps.add_argument("--size", type=_pair, help="wx,wy window size (0..1)")
    ps.add_argument("--remark", default="")

    pm = sub.add_parser("mark", help="add cross/rect annotation")
    _add_common_ref(pm)
    pm.add_argument("--kind", required=True, choices=("cross", "rect"))
    pm.add_argument("--center", type=_pair, required=True, help="cx,cy on the FIG (0..1)")
    pm.add_argument("--size", type=_pair, help="wx,wy (rect only)")
    pm.add_argument("--remark", default="")

    pa = sub.add_parser("adjust-mark", help="move/resize an existing annotation")
    _add_common_ref(pa)
    pa.add_argument("--anno", required=True, help="ANNO:<n>")
    pa.add_argument("--center", type=_pair, required=True)
    pa.add_argument("--size", type=_pair)
    pa.add_argument("--remark", default="")

    pu = sub.add_parser("unmark", help="delete one annotation or all")
    _add_common_ref(pu)
    pu.add_argument("--anno", required=True, help="ANNO:<n> | all")

    pc = sub.add_parser("coord", help="read @原图 coordinate of an annotation")
    _add_common_ref(pc)
    pc.add_argument("--anno", required=True, help="ANNO:<n>")

    pl = sub.add_parser("look", help="capture the backend screen into image_ctx (new FIG)")
    pl.add_argument("--remark", default="")

    pt = sub.add_parser("act", help="tap an annotation's @原图 coord; return screen + landing mark")
    _add_common_ref(pt)
    pt.add_argument("--anno", required=True, help="ANNO:<n> on the FIG whose frame was acted on")

    return p


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    _, sp = _resolve(args)
    sp.parent.mkdir(parents=True, exist_ok=True)
    lock = open(str(sp) + ".lock", "w")
    fcntl.flock(lock, fcntl.LOCK_EX)
    try:
        block, extra = _dispatch(args)
        if block.image and not Path(block.image).exists():
            raise FileNotFoundError(f"rendered png missing: {block.image}")
    except (RefError, ValueError, FileNotFoundError, RuntimeError, KeyError,
            GraphicsUnavailable, ClientError, OSError) as exc:
        print(json.dumps({"ok": False, "error": f"{type(exc).__name__}: {exc}"},
                         ensure_ascii=False))
        return 1
    finally:
        fcntl.flock(lock, fcntl.LOCK_UN)
        lock.close()

    out = {
        "ok": True,
        "command": args.command,
        "text": block.text,
        "image": block.image,
        "image_size": list(block.image_size),
    }
    out.update(extra)
    print(json.dumps(out, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
