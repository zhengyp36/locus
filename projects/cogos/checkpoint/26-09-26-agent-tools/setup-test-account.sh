#!/usr/bin/env bash
#
# setup-test-account.sh - create/remove a throwaway Linux account that acts as
# BOTH a local account and a "remote" account (ssh to localhost with password).
#
# Account layout:
#   home           : /home/<user>
#   machine root   : /home/<user>/machine   (seeded with readme.txt)
#
# Typical use:
#   ./setup-test-account.sh create          # user cogtest / password cogtest123
#   ./setup-test-account.sh check           # account + sshd readiness
#   ./setup-test-account.sh su              # login shell as cogtest (local role)
#   ./setup-test-account.sh ssh             # password ssh to localhost (remote role)
#   ./setup-test-account.sh clean           # kill processes, delete user + home
#
set -euo pipefail

DEFAULT_USER="cogtest"
DEFAULT_PASS="cogtest123"
MACHINE_SUBDIR="machine"
HOST="localhost"

if [[ "${EUID}" -eq 0 ]]; then
  SUDO=""
else
  SUDO="sudo"
fi

usage() {
  cat <<'EOF'
Usage: setup-test-account.sh <command> [user] [password]

Commands:
  create [user] [pass]   Create the account (default: cogtest / cogtest123)
  check  [user]          Show account info and sshd readiness for password login
  su     [user]          Open a login shell as the account (simulates local role)
  ssh    [user] [pass]   Password ssh to localhost as the account (remote role)
  clean  [user]          Kill the account's processes, delete user + home
  help                   Show this message

Notes:
  - Requires sudo (or root); user creation/deletion is a system change.
  - The "remote" role is simulated by ssh to localhost. sshd must be running
    with PasswordAuthentication enabled; 'check' reports both.
  - To automate the ssh login install sshpass; otherwise ssh prompts manually.
EOF
}

die() { echo "error: $*" >&2; exit 1; }

as_root() {
  if [[ -n "${SUDO}" ]]; then "${SUDO}" "$@"; else "$@"; fi
}

run_as() {
  local u="$1"; shift
  if [[ -n "${SUDO}" ]]; then "${SUDO}" -H -u "$u" "$@"; else runuser -u "$u" -- "$@"; fi
}

user_exists() { id -u "$1" >/dev/null 2>&1; }

home_of() { getent passwd "$1" | cut -d: -f6; }

cmd_create() {
  local user="${1:-$DEFAULT_USER}" pass="${2:-$DEFAULT_PASS}"
  if user_exists "$user"; then
    echo "user already exists: $user (run 'clean $user' first)"
    return 0
  fi
  as_root useradd -m -s /bin/bash "$user"
  printf '%s:%s\n' "$user" "$pass" | as_root chpasswd
  as_root chage -E -1 -M -1 "$user" 2>/dev/null || true

  local home; home="$(home_of "$user")"
  run_as "$user" mkdir -p "${home}/${MACHINE_SUBDIR}"
  printf 'hello from %s\n' "$user" \
    | run_as "$user" tee "${home}/${MACHINE_SUBDIR}/readme.txt" >/dev/null

  echo "created : $user"
  echo "password: $pass"
  echo "home    : $home"
  echo "machine : ${home}/${MACHINE_SUBDIR}"
  cmd_check "$user"
}

cmd_check() {
  local user="${1:-$DEFAULT_USER}"
  user_exists "$user" || { echo "no such user: $user"; return 1; }

  local home; home="$(home_of "$user")"
  echo "user      : $user"
  echo "uid/gid   : $(id -u "$user")/$(id -g "$user")"
  echo "home      : $home"
  echo "shell     : $(getent passwd "$user" | cut -d: -f7)"
  echo "machine   : ${home}/${MACHINE_SUBDIR}"
  if [[ -d "${home}/${MACHINE_SUBDIR}" ]]; then
    ls -la "${home}/${MACHINE_SUBDIR}"
  fi

  echo "--- sshd ---"
  if ! command -v sshd >/dev/null 2>&1; then
    echo "sshd not installed (e.g. apt install openssh-server)"
  fi
  local pas
  pas="$(as_root sshd -T 2>/dev/null \
    | awk 'tolower($1)=="passwordauthentication"{print $2}' || true)"
  if [[ -n "${pas}" ]]; then
    echo "PasswordAuthentication: ${pas}"
    if [[ "${pas}" == "no" ]]; then
      echo "  -> set 'PasswordAuthentication yes' in /etc/ssh/sshd_config and restart sshd"
    fi
  fi
  if (exec 3<>/dev/tcp/127.0.0.1/22) 2>/dev/null; then
    echo "port 22 : reachable on 127.0.0.1"
  else
    echo "port 22 : NOT reachable (start sshd: systemctl start ssh/sshd)"
  fi
}

cmd_su() {
  local user="${1:-$DEFAULT_USER}"
  user_exists "$user" || die "no such user: $user"
  run_as "$user" "${SHELL:-/bin/bash}" -l
}

cmd_ssh() {
  local user="${1:-$DEFAULT_USER}" pass="${2:-$DEFAULT_PASS}" cmd="${3:-}"
  user_exists "$user" || die "no such user: $user"

  local -a opts=(
    -o StrictHostKeyChecking=no
    -o UserKnownHostsFile=/dev/null
    -o PreferredAuthentications=password
    -o PubkeyAuthentication=no
    -o ConnectTimeout=5
  )
  local target="${user}@${HOST}"

  if command -v sshpass >/dev/null 2>&1; then
    if [[ -n "${cmd}" ]]; then
      sshpass -p "$pass" ssh "${opts[@]}" "$target" "$cmd"
    else
      sshpass -p "$pass" ssh "${opts[@]}" "$target"
    fi
  else
    echo "sshpass not installed; ssh will prompt. password: $pass"
    if [[ -n "${cmd}" ]]; then
      ssh "${opts[@]}" "$target" "$cmd"
    else
      ssh "${opts[@]}" "$target"
    fi
  fi
}

cmd_clean() {
  local user="${1:-$DEFAULT_USER}"
  if ! user_exists "$user"; then
    echo "no such user: $user"
    return 0
  fi
  local home; home="$(home_of "$user")"

  if command -v pkill >/dev/null 2>&1; then
    as_root pkill -KILL -u "$user" 2>/dev/null || true
    sleep 1
  fi
  if ! as_root userdel -r "$user" 2>/dev/null; then
    as_root userdel "$user" 2>/dev/null || true
    if [[ -n "${home}" && "${home}" != "/" ]]; then
      as_root rm -rf "${home}"
    fi
  fi
  echo "removed : $user"
}

main() {
  local cmd="${1:-help}"; shift || true
  case "$cmd" in
    create) cmd_create "$@" ;;
    check)  cmd_check "$@" ;;
    su)     cmd_su "$@" ;;
    ssh)    cmd_ssh "$@" ;;
    clean)  cmd_clean "$@" ;;
    help|-h|--help) usage ;;
    *) usage; exit 2 ;;
  esac
}

main "$@"
