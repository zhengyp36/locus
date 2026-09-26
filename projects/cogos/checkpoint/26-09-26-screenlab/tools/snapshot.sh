#!/usr/bin/env bash
# Machine-readable session snapshot: local repo state + live target status.
# This is the "one command to get oriented" entry for a new session; it replaces
# re-reading a long handoff to reconstruct the world. Writes tools/state.json too.
#
#   tools/snapshot.sh          # JSON to stdout (and tools/state.json)
set -uo pipefail
. "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/env.sh"

LOCAL_JSON=$("$SL_PY" - "$SL_COGOS" <<'PY'
import json, subprocess, sys
repo = sys.argv[1]
def g(*a):
    return subprocess.run(["git", "-C", repo, *a], capture_output=True, text=True).stdout.strip()
dirty = [l.split(None, 1)[1] for l in g("status", "--short").splitlines() if l.strip()]
tag = g("describe", "--tags", "--exact-match") or None
print(json.dumps({"branch": g("rev-parse", "--abbrev-ref", "HEAD"),
                  "head": g("rev-parse", "--short", "HEAD"),
                  "tag": tag, "dirty": dirty}))
PY
)

TARGET_JSON=$("$SL_TOOLS/status.sh" --json 2>/dev/null || echo '{"error":"unreachable"}')

"$SL_PY" - "$LOCAL_JSON" "$TARGET_JSON" "$SL_TOOLS/state.json" <<'PY'
import json, sys, time
local, target, out = json.loads(sys.argv[1]), json.loads(sys.argv[2]), sys.argv[3]
snap = {"generated": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "cogos": local, "target": target}
open(out, "w").write(json.dumps(snap, ensure_ascii=False, indent=2) + "\n")
print(json.dumps(snap, ensure_ascii=False, indent=2))
PY
