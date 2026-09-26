#!/usr/bin/env bash
# Desktop / tray operations on the human's real XFCE session (:0).
#
#   tools/desktop.sh coords          # print configured UI coords + live tray count
#   tools/desktop.sh tray            # crop the panel tray to a PNG, print count + path
#   tools/desktop.sh shot [NAME]     # full-screen ground-truth PNG, print local path
#   tools/desktop.sh dblclick        # double-click the "启动协助" desktop icon, print verdict
#   tools/desktop.sh reset           # stop consent_app + attach (clean slate)
#
# All clicks are XTEST (synthetic); they prove wiring, not real-mouse feel.
set -uo pipefail
. "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/env.sh"

xy() { printf '%s %s' "${1%,*}" "${1#*,}"; }
IFS=, read -r _x1 _y1 _x2 _y2 <<<"$SL_TRAY_CROP"
GEO="$((_x2 - _x1))x$((_y2 - _y1))+${_x1}+${_y1}"

case "${1:-}" in
  coords)
    sl_root_script <<EOS
$(sl_remote_vars)
echo "launcher_xy=$SL_LAUNCHER_XY tray_lock_xy=$SL_TRAY_LOCK_XY tray_crop=$SL_TRAY_CROP"
echo -n "tray_windows="; run bash -c 'xdotool search --onlyvisible --name consent_app 2>/dev/null | wc -l'
EOS
    ;;
  tray)
    sl_root_script <<EOS
$(sl_remote_vars)
run import -window root -crop $GEO +repage /tmp/sl-tray.png && chmod 644 /tmp/sl-tray.png
echo -n "tray_windows="; run bash -c 'xdotool search --onlyvisible --name consent_app 2>/dev/null | wc -l'
EOS
    sl_pull /tmp/sl-tray.png tray.png
    ;;
  shot)
    sl_root_script <<EOS
$(sl_remote_vars)
run import -window root /tmp/sl-shot.png && chmod 644 /tmp/sl-shot.png
EOS
    sl_pull /tmp/sl-shot.png "${2:-shot.png}"
    ;;
  dblclick)
    sl_root_script <<EOS
$(sl_remote_vars)
run xdotool mousemove $(xy "$SL_LAUNCHER_XY") click --repeat 2 --delay 130 1
sleep 4
attn=\$(run bash -c 'xdotool search --name Attention 2>/dev/null | wc -l')
procs=\$(pgrep -fc 'screenlab.service.consent_app' 2>/dev/null || true)
tray=\$(run bash -c 'xdotool search --onlyvisible --name consent_app 2>/dev/null | wc -l')
attach=\$(run systemctl --user is-active screenlab-attach.service 2>/dev/null | head -n1)
echo "attention=\$attn consent_app=\$procs tray=\$tray attach=\$attach"
EOS
    ;;
  reset)
    sl_root_script <<EOS
set +e
$(sl_remote_vars)
pkill -f 'screenlab.service.consent_app' 2>/dev/null
run systemctl --user stop screenlab-attach.service 2>/dev/null
sleep 1
echo -n "consent_app="; pgrep -fc 'screenlab.service.consent_app' || echo 0
EOS
    ;;
  *)
    sed -n '2,12p' "$0"
    ;;
esac
