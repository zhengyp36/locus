#!/usr/bin/env bash
# Push ../cogos to the target, (re)install to /opt/screenlab, restart the attach daemon.
# Encapsulates the rsync + install-machine + systemctl dance. Usage: tools/deploy.sh
set -euo pipefail
. "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/env.sh"

echo "== rsync $SL_COGOS -> $SL_SSH:/tmp/cogos-src/ =="
rsync -a --exclude __pycache__ -e "ssh -o BatchMode=yes" "$SL_COGOS/" "$SL_SSH:/tmp/cogos-src/"

echo "== install-machine (--desktop-user $SL_USER) =="
sl_root "bash /tmp/cogos-src/screenlab/install/screenlab install-machine --prefix /opt/screenlab --desktop-user $SL_USER"

echo "== restart screenlab-attach =="
sl_root_script <<EOS
set -uo pipefail
$(sl_remote_vars)
run systemctl --user restart screenlab-attach.service
sleep 2
echo -n "attach: "; run systemctl --user is-active screenlab-attach.service
echo -n "8911:   "; ss -ltn 2>/dev/null | grep -c ":$SL_PORT "
echo -n "code:   "; grep -c note_injection /opt/screenlab/screenlab/service/presence.py
EOS
