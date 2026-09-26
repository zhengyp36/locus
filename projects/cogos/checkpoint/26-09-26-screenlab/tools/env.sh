# screenlab dev/ops environment facts -- source this; never re-derive or re-type.
#
#   source ../checkpoint/tools/env.sh
#
# Everything here is an *environment fact* (re-discoverable, not a rule). Override by
# exporting SL_* before sourcing if the target/account changes.
# Rules & discipline stay in ../checkpoint/screenlab-rules.md.

TOOLS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export SL_TOOLS="$TOOLS_DIR"

# --- target VM (surface-centos-9) ------------------------------------
export SL_HOST="${SL_HOST:-100.100.137.78}"
export SL_LOGIN="${SL_LOGIN:-zhengyp}"                 # ssh login (key-based)
export SL_SSH="${SL_SSH:-$SL_LOGIN@$SL_HOST}"
export SL_SUDO_KEY="${SL_SUDO_KEY:-$HOME/.secrets/centos.key}"   # sudo -S stdin

# --- the human's real desktop session on the target ------------------
export SL_USER="${SL_USER:-human}"
export SL_UID="${SL_UID:-1002}"
export SL_DISPLAY="${SL_DISPLAY:-:0}"
export SL_RUNTIME="${SL_RUNTIME:-/run/user/$SL_UID}"
export SL_XAUTH="${SL_XAUTH:-$SL_RUNTIME/gdm/Xauthority}"
export SL_USER_HOME="${SL_USER_HOME:-/home/$SL_USER}"
export SL_REGISTRY="${SL_REGISTRY:-$SL_USER_HOME/.config/screenlab/registry}"
export SL_DESKTOP_ITEM="${SL_DESKTOP_ITEM:-$SL_USER_HOME/Desktop/screenlab-assist.desktop}"

# Cached UI coordinates (rediscover with `tools/desktop.sh coords` / `tray`).
export SL_LAUNCHER_XY="${SL_LAUNCHER_XY:-70,405}"      # "启动协助" desktop icon
export SL_TRAY_LOCK_XY="${SL_TRAY_LOCK_XY:-1692,18}"   # consent_app padlock in panel
export SL_TRAY_CROP="${SL_TRAY_CROP:-1494,0,1707,26}"
export SL_TAKEBACK_KEYS="${SL_TAKEBACK_KEYS:-Ctrl+Alt+Shift+Escape}"

# --- 3a endpoint + agent identity (test key, persisted across sessions) ---
export SL_PORT="${SL_PORT:-8911}"
export SL_ENDPOINT="${SL_ENDPOINT:-tcp:$SL_HOST:$SL_PORT}"
export SL_AGENT_KEY="${SL_AGENT_KEY:-$TOOLS_DIR/keys/agent.key}"
export SL_AGENT_ALIAS="${SL_AGENT_ALIAS:-kilocode}"
export SL_BLOB_ROOT="${SL_BLOB_ROOT:-$TOOLS_DIR/blobs}"

# --- Windows 3a target (the human's real Windows machine) -------------
# Daily ops as the standard account; admin ssh for account/OS-level steps.
export SL_WIN_HOST="${SL_WIN_HOST:-100.112.50.115}"
export SL_WIN_USER="${SL_WIN_USER:-assist}"
export SL_WIN_SSH="${SL_WIN_SSH:-$SL_WIN_USER@$SL_WIN_HOST}"
export SL_WIN_ADMIN_SSH="${SL_WIN_ADMIN_SSH:-zhengyp@$SL_WIN_HOST}"
export SL_WIN_PORT="${SL_WIN_PORT:-9911}"                 # screen/1 (loopback)
export SL_WIN_PREFIX="${SL_WIN_PREFIX:-C:\\Users\\$SL_WIN_USER\\AppData\\Local\\screenlab}"
export SL_WIN_REGISTRY="${SL_WIN_REGISTRY:-C:\\Users\\$SL_WIN_USER\\.config\\screenlab\\registry}"
export SL_AGENT_PUBKEY="${SL_AGENT_PUBKEY:-TsrTNVQgfSeKuFDFxp07O06ji5NKH+Cmc2qwLqOj4cE=}"

# --- Android target (nova 4e / EMUI 10, Android 10, SDK29) ------------
# wifi adb: Android 10 has no "wireless debugging" UI -> needs USB `adb tcpip 5555`
# first; adbd tcp mode is lost on reboot. The assist app listens on LAN 8901.
export SL_ANDROID_HOST="${SL_ANDROID_HOST:-192.168.1.175}"
export SL_ANDROID_DEV="${SL_ANDROID_DEV:-$SL_ANDROID_HOST:5555}"   # wifi adb serial
export SL_ANDROID_PKG="${SL_ANDROID_PKG:-com.screenlab.assist}"
export SL_ANDROID_SVC_PORT="${SL_ANDROID_SVC_PORT:-8901}"          # screen/1 on LAN
export SL_ANDROID_ENDPOINT="${SL_ANDROID_ENDPOINT:-tcp:$SL_ANDROID_HOST:$SL_ANDROID_SVC_PORT}"
export SL_ANDROID_AGENT_KEY="${SL_ANDROID_AGENT_KEY:-$TOOLS_DIR/keys/android_agent.key}"
export SL_ANDROID_A11Y="${SL_ANDROID_A11Y:-com.screenlab.assist/.InjectService}"
export SL_ANDROID_CMD="${SL_ANDROID_CMD:-com.screenlab.assist/.CmdReceiver}"
adb_dev() { adb -s "$SL_ANDROID_DEV" "$@"; }

# --- local repo / interpreter ----------------------------------------
export SL_COGOS="${SL_COGOS:-/home/zhengyp/work/A/cogos}"
export SL_PY="${SL_PY:-/usr/bin/python3.11}"
export SL_TARGET_PY="${SL_TARGET_PY:-/usr/bin/python3.11}"

# --- helpers ---------------------------------------------------------
sl_ssh() { ssh -o BatchMode=yes -o ConnectTimeout=6 "$SL_SSH" "$@"; }

# Windows target: daily ops as the assist account, admin for OS-level steps.
win_ssh()   { ssh -o BatchMode=yes -o ConnectTimeout=8 "$SL_WIN_SSH" "$@"; }
win_admin() { ssh -o BatchMode=yes -o ConnectTimeout=8 "$SL_WIN_ADMIN_SSH" "$@"; }

# Run a shell command as the target root (password piped to `sudo -S`).
sl_root() {  # sl_root '<shell command>'
  cat "$SL_SUDO_KEY" | ssh -o BatchMode=yes -o ConnectTimeout=6 "$SL_SSH" \
    "sudo -S -p '' bash -c $(printf '%q' "$1")"
}

# Run a multi-line script as target root. Feed the script on stdin:
#   sl_root_script <<'EOS'
#   ... rootshell ...
#   EOS
sl_root_script() { { cat "$SL_SUDO_KEY"; cat; } | ssh -o BatchMode=yes -o ConnectTimeout=6 "$SL_SSH" "sudo -S -p '' bash -s"; }

# Emits the remote-side preamble used by `sl_root_script` bodies: sets the
# human-session variables and a `run` wrapper. Values are baked in locally; the
# `$RID`-style references stay literal so the remote shell expands them.
sl_remote_vars() {
  cat <<VARS
U=$SL_USER; RID=$SL_RUNTIME; DISP=$SL_DISPLAY; XA=$SL_XAUTH
HENV="HOME=$SL_USER_HOME XDG_RUNTIME_DIR=\$RID DBUS_SESSION_BUS_ADDRESS=unix:path=\$RID/bus DISPLAY=\$DISP XAUTHORITY=\$XA"
run() { runuser -u "\$U" -- env \$HENV "\$@"; }
VARS
}

# Pull a file produced on the target into the local blob dir; prints local path.
sl_pull() {  # sl_pull <remote-path> [local-name]
  local src="$1" name="${2:-$(basename "$1")}"
  mkdir -p "$SL_BLOB_ROOT"
  ssh -o BatchMode=yes -o ConnectTimeout=6 "$SL_SSH" "chmod 644 '$src'" >/dev/null 2>&1 || true
  scp -q -o BatchMode=yes -o ConnectTimeout=6 "$SL_SSH:$src" "$SL_BLOB_ROOT/$name"
  printf '%s\n' "$SL_BLOB_ROOT/$name"
}
