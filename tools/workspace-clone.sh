#!/usr/bin/env bash
# workspace-clone.sh — clone a temporary workspace: locus + checkpoint
# External projects are cloned on demand via tools/external-clone.sh.
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

mkdir -p "$WS/checkpoint"
echo "== ready: $WS"
echo "   cd $WS/locus"
echo "   clone external projects on demand: tools/external-clone.sh <name>"
