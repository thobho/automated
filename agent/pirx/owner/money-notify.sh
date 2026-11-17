#!/usr/bin/env bash
# The only message the automation sends to the owner's phone: something needs money.
# Runs as the owner's user on pirx (Hermes lives there), every 15 minutes (automated-money-notify.timer).
# It lists open issues labelled owner:money and sends each one once to WhatsApp through Hermes (no AI
# call). Sent issue numbers are remembered in ~/.local/state/automated/money-notified.
# The daily report stays on GitHub (the 📋 Daily report issue) and is no longer sent to WhatsApp.
set -uo pipefail
export PATH="$HOME/.local/bin:$HOME/.local/node/bin:$PATH"
REPO="${AUTOMATED_GH_REPO:-thobho/automated}"
TARGET="${REPORT_TARGET:-whatsapp}"
state="$HOME/.local/state/automated/money-notified"
mkdir -p "$(dirname "$state")"; touch "$state"

gh api "repos/$REPO/issues?labels=owner:money&state=open&per_page=20" \
   --jq '.[] | select(.pull_request | not) | "\(.number)\t\(.title)\t\(.html_url)"' |
while IFS=$'\t' read -r n title url; do
  grep -qx "$n" "$state" && continue
  if printf '💰 automated needs money: %s\n%s\n' "$title" "$url" | hermes send -t "$TARGET" -f - >/dev/null; then
    echo "$n" >> "$state"
  fi
done
