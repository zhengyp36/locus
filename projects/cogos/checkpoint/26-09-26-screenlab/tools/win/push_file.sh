#!/usr/bin/env bash
# Push one changed file into the RUNNING install (no reinstall / venv rebuild).
#   tools/win/push_file.sh service/daemon.py
set -euo pipefail
source "$(dirname "$0")/../env.sh"
rel="${1:?usage: push_file.sh <path-relative-to-screenlab>}"
scp -q "$SL_COGOS/screenlab/$rel" \
    "$SL_WIN_SSH:C:/Users/assist/AppData/Local/screenlab/screenlab/$rel"
echo "pushed screenlab/$rel -> installed copy"
