#!/usr/bin/env bash
# external-clone.sh — clone one external project on demand into the workspace (../<name>)
# Usage (run from locus root inside a workspace): tools/external-clone.sh <name>
set -euo pipefail

NAME="${1:-}"
if [ -z "$NAME" ]; then
  echo "usage: $0 <name>" >&2
  exit 1
fi

if [ ! -f workspace.json ]; then
  echo "error: workspace.json not found (run from locus root inside a workspace)" >&2
  exit 1
fi

REMOTE=$(python3 - "$NAME" <<'PY'
import json, sys
name = sys.argv[1]
cfg = json.load(open("workspace.json"))
remote = cfg["external"].get(name)
if remote is None:
    print(f"error: '{name}' not in workspace.json external list", file=sys.stderr)
    sys.exit(1)
print(remote)
PY
)

DST="../$NAME"
if [ -d "$DST" ]; then
  echo "skip $NAME: already exists at $DST"
  exit 0
fi

echo "clone $NAME -> $DST"
git clone "$REMOTE" "$DST"
