#!/usr/bin/env bash
# Send today's daily report to WhatsApp through Hermes. Runs as the owner's user on pirx (not as `agent`),
# from a systemd user timer at 08:00 Europe/Warsaw. Installed to ~/.local/bin/automated-report-send.sh.
# It reads the newest comment on the "📋 Daily report" issue (label agent:report), takes the part between
# <!-- whatsapp:start --> and <!-- whatsapp:end -->, adds the link, and calls `hermes send` (no AI call).
# If there is no report from today, it sends a short warning instead, so a broken pipeline is noticed.
set -uo pipefail
export PATH="$HOME/.local/bin:$HOME/.local/node/bin:$PATH"
REPO="${AUTOMATED_GH_REPO:-thobho/automated}"
TARGET="${REPORT_TARGET:-whatsapp}"
today="$(TZ=Europe/Warsaw date +%F)"

issue="$(gh api "repos/$REPO/issues?labels=agent:report&state=open&per_page=1" --jq '.[0].number // empty')"
if [[ -n "$issue" ]]; then
  latest="$(gh api "repos/$REPO/issues/$issue/comments?per_page=100" --jq 'last // empty | @json')"
fi
if [[ -z "${issue:-}" || -z "${latest:-}" ]]; then
  hermes send -t "$TARGET" "📋 automated: no daily report found. Check the agent timer on pirx (systemctl --user status automated-report as agent)." >/dev/null
  exit 0
fi
created="$(jq -r '.created_at' <<<"$latest" | python3 -c 'import sys,datetime,zoneinfo; print(datetime.datetime.fromisoformat(sys.stdin.read().strip().replace("Z","+00:00")).astimezone(zoneinfo.ZoneInfo("Europe/Warsaw")).date())')"
url="$(jq -r '.html_url' <<<"$latest")"
if [[ "$created" != "$today" ]]; then
  hermes send -t "$TARGET" "📋 automated: today's report is missing (last one: $created). $url" >/dev/null
  exit 0
fi
short="$(jq -r '.body' <<<"$latest" | sed -n '/<!-- whatsapp:start -->/,/<!-- whatsapp:end -->/p' | sed '1d;$d')"
# Watchdog: if the health page has not been refreshed for 2 hours, pirx's side is down.
h_upd="$(gh api "repos/$REPO/issues?labels=agent:status&state=open&per_page=1" --jq '.[0].updated_at // empty')"
if [[ -n "$h_upd" ]] && (( $(date +%s) - $(date -d "$h_upd" +%s) > 7200 )); then
  short="⚠️ The health page has not updated since $h_upd: the automation on pirx may be down.
$short"
fi
[[ -n "$short" ]] || short="📋 automated: report ready."
printf '%s\nFull report: %s\n' "$short" "$url" | hermes send -t "$TARGET" -f - >/dev/null
