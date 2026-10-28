#!/usr/bin/env bash
# Rewrite the pinned "Agent status" issue: limits, reset times, budget
# decision, queue and last run. Reads budget.py's JSON output on stdin.
# Usage: agent/budget.py < usage.json | scripts/update-status.sh "<what happened this run>"
set -euo pipefail
cd "$(dirname "$0")/.."

note="${1:-}"
budget="$(cat)"
tz="${AGENT_TZ:-Europe/Warsaw}"

local_time() { TZ="$tz" python3 -c "import sys,datetime as d;print(d.datetime.fromisoformat(sys.argv[1].replace('Z','+00:00')).astimezone().strftime('%a %d %b %H:%M'))" "$1"; }
field() { jq -r ".$1 // \"?\"" <<<"$budget"; }

five_reset="$(field five_hour_resets_at)"; weekly_reset="$(field weekly_resets_at)"
[[ "$five_reset" != "?" ]] && five_reset="$(local_time "$five_reset")"
[[ "$weekly_reset" != "?" ]] && weekly_reset="$(local_time "$weekly_reset")"

queue_line() {
  gh issue list --label "agent:$1" --state open --limit 50 --json number,title \
    --jq 'if length == 0 then "_none_" else map("#\(.number) \(.title)") | join("<br>") end'
}

body="## 🤖 Agent status
_Updated $(TZ="$tz" date '+%a %d %b %H:%M') ($tz)_

### Limits
| Window | Used | Agent cap | Resets |
|---|---|---|---|
| 5-hour | **$(field five_hour_used)%** | $(field five_hour_cap)% | $five_reset |
| Weekly | **$(field weekly_used)%** | $(field weekly_allowed_now)% allowed now · $(field weekly_cap)% max | $weekly_reset |

**Last decision:** $(field decision) — $(field reason)
**Last run:** ${note:-_no note_}
**Worker slots:** $(bash "${AUTOMATED_LOCK_SCRIPT:-$HOME/.config/automated/worker-lock.sh}" status 2>/dev/null | paste -sd ';' - | sed 's/;/ · /g' || echo '?')

### Queue
| State | Issues |
|---|---|
| 🟡 doing | $(queue_line doing) |
| 🔴 blocked | $(queue_line blocked) |
| 🟢 todo | $(queue_line todo) |
| 🔵 review | $(queue_line review) |
"

# REST lookup, not `gh issue list`: search can lag and would create a duplicate.
num="$(gh api "repos/{owner}/{repo}/issues?labels=agent:status&state=open&per_page=1" --jq '.[0].number // empty')"
if [[ -z "$num" ]]; then
  url="$(gh issue create --title "🤖 Agent status" --label agent:status --body "$body")"
  num="${url##*/}"
  gh issue pin "$num" >/dev/null 2>&1 || true
else
  gh issue edit "$num" --body "$body" >/dev/null
fi
echo "status issue: #$num"
