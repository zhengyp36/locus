#!/usr/bin/env bash
# workspace-clone.sh — clone a temporary workspace: locus + external projects + checkpoint
# Usage: tools/workspace-clone.sh <name> [workspace-root]
set -euo pipefail

LOCUS_REMOTE="${LOCUS_REMOTE:-git@github.com:zhengyp36/locus.git}"
NAME="${1:-}"
WS_ROOT="${2:-$HOME/work}"

if [ -z "$NAME" ]; then
  echo "usage: $0 <name> [workspace-root]" >&2
  exit 1
fi

WS="$WS_ROOT/$NAME"
mkdir -p "$WS"

echo "== clone locus -> $WS/locus"
git clone "$LOCUS_REMOTE" "$WS/locus"

echo "== clone external projects (from workspace.json)"
python3 - "$WS" <<'PY'
import json, os, subprocess, sys
ws = sys.argv[1]
cfg = json.load(open(os.path.join(ws, "locus", "workspace.json")))
for name, remote in cfg["external"].items():
    dst = os.path.join(ws, name)
    if os.path.isdir(dst):
        print(f"skip {name}: already exists")
        continue
    print(f"clone {name} -> {dst}")
    subprocess.run(["git", "clone", remote, dst], check=True)
PY

mkdir -p "$WS/checkpoint"
echo "== ready: $WS"
echo "   cd $WS/locus"
