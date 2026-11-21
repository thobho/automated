#!/bin/bash
# Install (or update) the automation's root helper on pirx. Run by the owner, once and after each change,
# from a checkout the owner owns (never the agent's runner checkout), using merged main. umask 022:
# Ubuntu's default 002 checks files out group-writable, which the check below refuses.
#   (umask 022; d=$(mktemp -d) && git -C ~/Projects/automated fetch -q && git -C ~/Projects/automated worktree add --detach "$d/ah" origin/main && sudo bash "$d/ah/agent/pirx/root/install-root-helper.sh"; git -C ~/Projects/automated worktree remove --force "$d/ah"; rmdir "$d")
# It installs /usr/local/sbin/automated-root (root-owned copy), writes /etc/automated/root-helper.conf on
# the first run (edit it to change the lists; it is kept on updates), and two sudoers rules:
#   agent ALL=(root) NOPASSWD: /usr/local/sbin/automated-root
#   <owner> ALL=(root) NOPASSWD: /usr/local/sbin/automated-owner-apply   (sudo-queue approvals from Claude on pirx)
# That is the agent's only root access: the fixed verbs of the helper. Nothing else changes.
#
# Safety: root must never install a file the agent can write between review and install. So:
#   1. this script refuses to run from a file whose directory, or any directory above it, can be changed by
#      anyone but root or the owner (the agent's runner checkout and a fixed, pre-creatable /tmp path are
#      refused; mktemp -d makes a private 0700 directory; a sticky root-owned /tmp itself is accepted);
#   2. the helper is NOT read from the working tree: it is copied out of git (`git show <ref>:path`, the
#      reviewed, merged content, default ref origin/main) into a root-owned temp directory, and that copy
#      is installed. Override the checkout with AUTOMATED_REPO and the ref with AUTOMATED_REF.
set -euo pipefail
[[ "$(id -u)" == 0 ]] || { echo "run with sudo"; exit 1; }
here="$(cd "$(dirname "$0")" && pwd)"
owner="${OWNER_USER:-${SUDO_USER:-user}}"
repo="${AUTOMATED_REPO:-$(getent passwd "$owner" | cut -d: -f6)/Projects/automated}"
ref="${AUTOMATED_REF:-origin/main}"

untrusted() {  # untrusted <path>: true when the path, or any directory above it, can be changed by someone else
  local p o m
  p="$(readlink -f "$1")"
  while :; do
    o="$(stat -L -c %U "$p")"; m="$(stat -L -c %a "$p")"
    [[ "$o" != root && "$o" != "$owner" ]] && return 0
    if (( (8#$m & 8#022) != 0 )); then
      # A sticky root-owned directory (/tmp) is fine: nobody can rename or replace another user's entries in it.
      [[ -d "$p" && "$o" == root ]] && (( (8#$m & 8#1000) != 0 )) || return 0
    fi
    [[ "$p" == / ]] && return 1
    p="$(dirname "$p")"
  done
}
for path in "$0" "$here"; do
  if untrusted "$path"; then
    echo "refusing: $path, or a directory above it, is writable by someone other than root or $owner (run it from a checkout you own in a private directory, not the agent's runner checkout or a fixed /tmp path)"; exit 1
  fi
done
git -c safe.directory="$repo" -C "$repo" rev-parse --verify -q "$ref^{commit}" >/dev/null \
  || { echo "refusing: $repo has no $ref (git fetch there first)"; exit 1; }
tmp="$(mktemp -d)"; trap 'rm -rf "$tmp"' EXIT
chmod 0700 "$tmp"
git -c safe.directory="$repo" -C "$repo" show "$ref:agent/pirx/root/automated-root" > "$tmp/automated-root"
echo "installing agent/pirx/root/automated-root from $ref ($(git -c safe.directory="$repo" -C "$repo" rev-parse --short "$ref"), sha256 $(sha256sum "$tmp/automated-root" | cut -c1-16))"

install -o root -g root -m 0755 "$tmp/automated-root" /usr/local/sbin/automated-root
install -d -o root -g root -m 0755 /etc/automated
if [[ ! -f /etc/automated/root-helper.conf ]]; then
  cat > /etc/automated/root-helper.conf <<CONF
# Lists for /usr/local/sbin/automated-root. Root-owned; the agent cannot change it.
# Phone-farm stays out of every list.
SYSTEM_SERVICES="tailscaled.service chrony.service"
OWNER_USER="$owner"
OWNER_SERVICES="hermes-gateway.service hermes-session.service gallery.service claude-session.service opencode.service"
PACKAGES="podman podman-compose buildah make just jq sqlite3 postgresql-client build-essential pkg-config libpq-dev python3-dev ffmpeg imagemagick unzip libatk1.0-0t64 libatk-bridge2.0-0t64 libatspi2.0-0t64 libxcomposite1 libxdamage1 fonts-liberation fonts-noto-color-emoji"
FIREWALL_UNIT="agent-netguard.service"
CONF
  chmod 0644 /etc/automated/root-helper.conf
fi
rule=/etc/sudoers.d/automated-root
echo 'agent ALL=(root) NOPASSWD: /usr/local/sbin/automated-root' > "$rule.tmp"
chmod 0440 "$rule.tmp"
visudo -cf "$rule.tmp" >/dev/null && mv "$rule.tmp" "$rule" || { rm -f "$rule.tmp"; echo "sudoers check failed"; exit 1; }
touch /var/log/automated-root.log; chmod 0640 /var/log/automated-root.log

# Owner approvals of the sudo queue from the Claude session on pirx: a root-owned copy of scripts/owner-apply.sh
# (from git, like the helper) that the owner, and only the owner, may run without a password. It runs a queued
# script only with `--approve <id> <sha256>` naming exactly the content shown by `--list`. Re-run this installer
# after a change to scripts/owner-apply.sh.
if [[ "$owner" != agent && "$owner" != root ]]; then
  git -c safe.directory="$repo" -C "$repo" show "$ref:scripts/owner-apply.sh" > "$tmp/owner-apply"
  install -o root -g root -m 0755 "$tmp/owner-apply" /usr/local/sbin/automated-owner-apply
  orule=/etc/sudoers.d/automated-owner-apply
  echo "$owner ALL=(root) NOPASSWD: /usr/local/sbin/automated-owner-apply" > "$orule.tmp"
  chmod 0440 "$orule.tmp"
  visudo -cf "$orule.tmp" >/dev/null && mv "$orule.tmp" "$orule" || { rm -f "$orule.tmp"; echo "sudoers check failed (owner apply)"; exit 1; }
  echo "installed owner approvals: as $owner, sudo -n /usr/local/sbin/automated-owner-apply --list"
fi
echo "installed. Check as agent: sudo -n /usr/local/sbin/automated-root status"
sudo -u agent sudo -n /usr/local/sbin/automated-root status
