#!/bin/bash
# Launch chrome as an X11/Xwayland client inside the headless screenlab session.
#
#   screenlab-chrome.sh [url]
#
# Env:
#   PROFILE  user-data-dir (default /tmp/screenlab-chrome)
#   EXTRA    extra chrome flags   (default --force-renderer-accessibility)
#   X11_ENV  pre-baked env file from a prior probe (optional)
#
# Deliberately does NOT pass --ozone-platform=wayland: the default X11 backend is
# what gives us global a11y coordinates and XTEST input (see screen-exp-log B1).
set -u

SELF_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
URL="${1:-about:blank}"
PROFILE="${PROFILE:-/tmp/screenlab-chrome}"
EXTRA="${EXTRA:---force-renderer-accessibility}"

if [ -n "${X11_ENV:-}" ] && [ -f "$X11_ENV" ]; then
  # shellcheck disable=SC1090
  . "$X11_ENV"
else
  # shellcheck source=/dev/null
  . "$SELF_DIR/screenlab-x11.sh" || { echo "screenlab-chrome: no X display" >&2; exit 1; }
fi

mkdir -p "$PROFILE"
exec google-chrome --no-sandbox --disable-gpu --disable-dev-shm-usage --no-first-run \
  --no-default-browser-check --password-store=basic \
  --user-data-dir="$PROFILE" --window-size=1200,900 $EXTRA "$URL"
