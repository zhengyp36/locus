#!/usr/bin/env bash
# Push the current cogos screenlab package to the Windows staging dir and the
# one-shot shot.py into the install prefix. Re-run install.ps1 afterwards to
# rebuild the installed copy + venv (see tools/win/README.md).
set -euo pipefail
source "$(dirname "$0")/../env.sh"
SRC="$SL_COGOS/screenlab"
ssh "$SL_WIN_SSH" 'cmd /c rmdir /s /q C:\Users\assist\sl\screenlab' 2>/dev/null || true
scp -q -r "$SRC" "$SL_WIN_SSH:C:/Users/assist/sl/"
scp -q "$SL_TOOLS/win/shot.py" \
    "$SL_WIN_SSH:C:/Users/assist/AppData/Local/screenlab/shot.py"
echo "pushed package -> C:\\Users\\assist\\sl\\screenlab (re-run install.ps1)"
