#!/usr/bin/env python3
"""handoff - start a new Kilo session and confirm it is actually running.

Wraps `kilo run` (no -s/-c => new session) with the given title and first
sentence, launched fire-and-forget, then polls the server until the new session
shows up as running (busy) or a timeout elapses.

Usage:
    handoff <title> "first sentence" [--dir DIR]
    handoff <title> --file first.txt [--dir DIR]
    echo "first sentence" | handoff <title> [--dir DIR]

Output:
    handoff: starting "<title>" (dir=..., pid=...)
    handoff: running <session-id> "<title>"        # exit 0
    handoff: FAILED ...                            # exit 1

Defaults: --dir = cwd, --attach = http://127.0.0.1:4097, user/pass = kilo/kilo
(env KILO_ATTACH / KILO_SERVER_USERNAME / KILO_SERVER_PASSWORD override).
"""
import argparse
import base64
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request


def http_json(url, user, password, path):
    req = urllib.request.Request(url.rstrip("/") + path)
    token = base64.b64encode(f"{user}:{password}".encode()).decode()
    req.add_header("Authorization", "Basic " + token)
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.loads(r.read().decode())


def first_sentence(args):
    if args.file:
        text = open(args.file, encoding="utf-8").read()
    elif args.message is not None:
        text = args.message
    elif not sys.stdin.isatty():
        text = sys.stdin.read()
    else:
        return ""
    return text.strip()


def main():
    p = argparse.ArgumentParser(description="start a new Kilo session and confirm it is running")
    p.add_argument("title", help="session title")
    p.add_argument("message", nargs="?", default=None, help="first sentence (else --file or stdin)")
    p.add_argument("-f", "--file", help="read the first sentence from a file")
    p.add_argument("--dir", help="directory to run in (default: cwd)")
    p.add_argument("--attach", default=os.environ.get("KILO_ATTACH", "http://127.0.0.1:4097"))
    p.add_argument("-u", "--username", default=os.environ.get("KILO_SERVER_USERNAME", "kilo"))
    p.add_argument("-p", "--password", default=os.environ.get("KILO_SERVER_PASSWORD", "kilo"))
    p.add_argument("--timeout", type=int, default=120, help="seconds to wait for the session to start")
    args = p.parse_args()

    sentence = first_sentence(args)
    if not sentence:
        p.error("no first sentence: pass it as an argument, --file, or stdin")

    directory = args.dir or os.getcwd()
    query = urllib.parse.urlencode({"directory": directory})

    def running_ids():
        try:
            data = http_json(args.attach, args.username, args.password, f"/session/status?{query}")
            return set(data.keys()) if isinstance(data, dict) else set()
        except Exception:
            return set()

    before = running_ids()

    logdir = os.path.expanduser("~/.local/state/locus-handoff")
    os.makedirs(logdir, exist_ok=True)
    log = os.path.join(logdir, f"handoff-{int(time.time())}.log")
    cmd = [
        "kilo", "run", "--attach", args.attach,
        "-u", args.username, "-p", args.password,
        "--dir", directory, "--title", args.title, sentence,
    ]
    with open(log, "w", encoding="utf-8") as lf:
        proc = subprocess.Popen(cmd, stdin=subprocess.DEVNULL, stdout=lf, stderr=lf, start_new_session=True)

    print(f'handoff: starting "{args.title}" (dir={directory}, pid={proc.pid})')

    deadline = time.time() + args.timeout
    while time.time() < deadline:
        started = running_ids() - before
        if started:
            print(f'handoff: running {sorted(started)[0]} "{args.title}"')
            return 0
        rc = proc.poll()
        if rc is not None:
            if rc == 0:
                print(f'handoff: finished "{args.title}" (kilo run exited 0)')
                return 0
            print(f'handoff: FAILED "{args.title}" (kilo run exited {rc}); log: {log}')
            return 1
        time.sleep(2)

    print(f'handoff: FAILED to start "{args.title}" within {args.timeout}s (pid {proc.pid}); log: {log}')
    return 1


if __name__ == "__main__":
    sys.exit(main())
