#!/bin/bash
# Install (or update) the automation's root helper on pirx. Run by the owner, once and after each change:
#   sudo bash ~/Projects/automated-work/runner/agent/pirx/root/install-root-helper.sh
# It installs /usr/local/sbin/automated-root (root-owned copy), writes /etc/automated/root-helper.conf on
# the first run (edit it to change the lists; it is kept on updates), and one sudoers rule:
#   agent ALL=(root) NOPASSWD: /usr/local/sbin/automated-root
# That is the agent's only root access: the fixed verbs of the helper. Nothing else changes.
set -euo pipefail
[[ "$(id -u)" == 0 ]] || { echo "run with sudo"; exit 1; }
here="$(cd "$(dirname "$0")" && pwd)"
owner="${OWNER_USER:-${SUDO_USER:-user}}"

install -o root -g root -m 0755 "$here/automated-root" /usr/local/sbin/automated-root
install -d -o root -g root -m 0755 /etc/automated
if [[ ! -f /etc/automated/root-helper.conf ]]; then
  cat > /etc/automated/root-helper.conf <<CONF
# Lists for /usr/local/sbin/automated-root. Root-owned; the agent cannot change it.
# Phone-farm stays out of every list.
SYSTEM_SERVICES="tailscaled.service chrony.service"
OWNER_USER="$owner"
OWNER_SERVICES="hermes-gateway.service hermes-session.service gallery.service claude-session.service opencode.service"
PACKAGES="podman podman-compose buildah make just jq sqlite3 postgresql-client build-essential pkg-config libpq-dev python3-dev ffmpeg imagemagick unzip"
FIREWALL_UNIT="agent-netguard.service"
CONF
  chmod 0644 /etc/automated/root-helper.conf
fi
rule=/etc/sudoers.d/automated-root
echo 'agent ALL=(root) NOPASSWD: /usr/local/sbin/automated-root' > "$rule.tmp"
chmod 0440 "$rule.tmp"
visudo -cf "$rule.tmp" >/dev/null && mv "$rule.tmp" "$rule" || { rm -f "$rule.tmp"; echo "sudoers check failed"; exit 1; }
touch /var/log/automated-root.log; chmod 0640 /var/log/automated-root.log
echo "installed. Check as agent: sudo -n /usr/local/sbin/automated-root status"
sudo -u agent sudo -n /usr/local/sbin/automated-root status
