#!/usr/bin/env bash
# Owner side on pirx (run as the owner's user, not as agent; no sudo):
#   bash agent/pirx/owner/install.sh
# Installs the money alert (owner:money issues -> WhatsApp via Hermes, every 15 minutes) and stops the
# daily WhatsApp report: the report stays on GitHub.
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
install -D -m 755 "$here/money-notify.sh" "$HOME/.local/bin/automated-money-notify.sh"
mkdir -p "$HOME/.config/systemd/user"
install -m 644 "$here/automated-money-notify.service" "$here/automated-money-notify.timer" "$HOME/.config/systemd/user/"
systemctl --user daemon-reload
systemctl --user enable --now automated-money-notify.timer >/dev/null
systemctl --user disable --now automated-report-send.timer >/dev/null 2>&1 || true
systemctl --user list-timers 'automated-*' --no-pager
