#!/usr/bin/env bash
# One-glance target status. Prints a compact key=value line + a JSON line.
# No consent required. Usage:
#   tools/status.sh            # summary + json
#   tools/status.sh --json     # json only
set -uo pipefail
. "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/env.sh"

REMOTE=$(cat <<REMOTE
$(sl_remote_vars)
attach=\$(run systemctl --user is-active screenlab-attach.service 2>/dev/null | head -n1)
port=\$(ss -ltn 2>/dev/null | grep -c ':$SL_PORT ')
procs=\$(pgrep -fc 'screenlab.service.consent_app' 2>/dev/null || true)
tray=\$(run bash -c 'xdotool search --onlyvisible --name consent_app 2>/dev/null | wc -l')
tcp=\$(grep -h SCREENLAB_TCP "$SL_USER_HOME/.config/screenlab/session.env" 2>/dev/null | cut -d= -f2-)
alias=\$(grep -o '"alias"[[:space:]]*:[[:space:]]*"[^"]*"' "$SL_REGISTRY/registry.json" 2>/dev/null | cut -d'"' -f4 | paste -sd, -)
lock=\$(run bash -c '[ -e "$SL_RUNTIME/screenlab-assist.lock" ] && echo present || echo none')
echo "attach=\$attach port=\$port consent_app=\$procs tray=\$tray tcp=\$tcp lock=\$lock alias=\$alias"
echo "JSON={\"attach\":\"\$attach\",\"port\":\$port,\"consent_app\":\$procs,\"tray\":\$tray,\"tcp\":\"\$tcp\",\"lock\":\"\$lock\",\"aliases\":\"\$alias\"}"
REMOTE
)

OUT=$({ cat "$SL_SUDO_KEY"; printf '%s\n' "$REMOTE"; } | \
  ssh -o BatchMode=yes -o ConnectTimeout=6 "$SL_SSH" "sudo -S -p '' bash -s" 2>/dev/null)

KEYVAL=$(printf '%s\n' "$OUT" | grep '^attach=' | head -1)
JSON=$(printf '%s\n' "$OUT" | grep '^JSON=' | sed 's/^JSON=//' | head -1)
[ -n "$KEYVAL" ] || KEYVAL="attach=unreachable"
[ -n "$JSON" ] || JSON='{"error":"unreachable"}'

if [ "${1:-}" = "--json" ]; then
  printf '%s\n' "$JSON"
else
  printf '%s\n' "$KEYVAL"
  printf '%s\n' "$JSON"
fi
