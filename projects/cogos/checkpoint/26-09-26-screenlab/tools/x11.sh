#!/usr/bin/env bash
# Throwaway owned X11 surface on the target, for the screenlab visual loop (Slice 1).
#
# Not the product session form (`screenlab open`); a self-contained Xvfb + openbox
# on an unused display, so the coordinate loop can run without touching the human
# account's attach config and without any consent prompt. All launch goes through
# systemd-run (transient units) so ssh never holds a backgrounded child.
#
#   tools/x11.sh start            # Xvfb + openbox + a zenity click target
#   tools/x11.sh stop
#   tools/x11.sh geometry         # "W H" of the surface
#   tools/x11.sh capture [PNG]    # pull a full-screen PNG to a local path (default blob)
#   tools/x11.sh click X Y        # XTEST move+click (device px)
#   tools/x11.sh pointer          # actual pointer device px ("X Y")
#   tools/x11.sh windows [PATTERN]# visible window count (or matching PATTERN)
#   tools/x11.sh zenity           # visible zenity-class window count (1 = target up)
#   tools/x11.sh status           # unit states + window count
set -uo pipefail
. "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/env.sh"

DISP="${SL1_DISPLAY:-:101}"
GEOM="${SL1_GEOM:-1280x800}"
DIR="${SL1_DIR:-/tmp/sl1}"
XA="$DIR/xauth"
SHOT="$DIR/shot.png"

# remote preamble: run as the human user with our throwaway DISPLAY
pre() {
  cat <<VARS
$(sl_remote_vars)
D=$DISP; XA=$XA; G=$GEOM; DIR=$DIR
r() { run env DISPLAY="\$D" XAUTHORITY="\$XA" "\$@"; }
VARS
}

case "${1:-}" in
  start)
    sl_root_script <<EOS
$(pre)
mkdir -p "\$DIR"; chown "$SL_USER" "\$DIR"
: > "\$XA"; chown "$SL_USER" "\$XA"
systemctl stop sl1-zenity sl1-openbox sl1-xvfb 2>/dev/null
systemctl reset-failed sl1-zenity sl1-openbox sl1-xvfb 2>/dev/null
systemd-run --collect --unit=sl1-xvfb    --uid=$SL_USER --setenv=DISPLAY="\$D" --setenv=XAUTHORITY="\$XA" Xvfb "\$D" -screen 0 "\${G}x24" -ac -nolisten tcp
sleep 1.5
systemd-run --collect --unit=sl1-openbox --uid=$SL_USER --setenv=DISPLAY="\$D" --setenv=XAUTHORITY="\$XA" openbox
sleep 1
systemd-run --collect --unit=sl1-zenity  --uid=$SL_USER --setenv=DISPLAY="\$D" --setenv=XAUTHORITY="\$XA" zenity --info --text="screenlab slice1 click target"
sleep 1.5
echo -n "geometry="; r xdotool getdisplaygeometry
echo -n "windows="; r bash -c 'xdotool search --onlyvisible --name ".*" 2>/dev/null | wc -l'
EOS
    ;;
  stop)
    sl_root_script <<EOS
$(pre)
systemctl stop sl1-zenity sl1-openbox sl1-xvfb 2>/dev/null
systemctl reset-failed sl1-zenity sl1-openbox sl1-xvfb 2>/dev/null
echo stopped
EOS
    ;;
  geometry)
    sl_root_script <<EOS
$(pre)
r xdotool getdisplaygeometry
EOS
    ;;
  capture)
    NAME="frame-$(date +%Y%m%d-%H%M%S-%N).png"
    sl_root_script <<EOS
$(pre)
r import -window root "\$DIR/shot.png" && chmod 644 "\$DIR/shot.png"
EOS
    sl_pull "$SHOT" "$NAME" >/dev/null
    printf '%s\n' "$SL_BLOB_ROOT/$NAME"
    ;;
  click)
    X="$2"; Y="$3"
    sl_root_script <<EOS
$(pre)
r bash -c 'xdotool mousemove $X $Y; xdotool click 1'
echo -n "pointer="; r bash -c 'xdotool getmouselocation --shell | tr "\n" " "'
EOS
    ;;
  pointer)
    sl_root_script <<EOS
$(pre)
r bash -c 'xdotool getmouselocation --shell | tr "\n" " "'
EOS
    ;;
  windows)
    PAT="${2:-.*}"
    sl_root_script <<EOS
$(pre)
r bash -c 'xdotool search --onlyvisible --name "$PAT" 2>/dev/null | wc -l'
EOS
    ;;
  zenity)
    sl_root_script <<EOS
$(pre)
r bash -c 'xdotool search --onlyvisible --class zenity 2>/dev/null | wc -l'
EOS
    ;;
  status)
    sl_root_script <<EOS
$(pre)
for u in sl1-xvfb sl1-openbox sl1-zenity; do
  echo -n "\$u="; systemctl is-active "\$u" 2>/dev/null || true
  echo
done
echo -n "windows="; r bash -c 'xdotool search --onlyvisible --name ".*" 2>/dev/null | wc -l'
EOS
    ;;
  *)
    sed -n '2,17p' "$0"
    ;;
esac
