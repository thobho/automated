#!/usr/bin/env bash
# Diagnosis run of the healer: a problem the fixed fixes in heal.sh did not solve in an hour goes to
# Claude (Sonnet). Started by heal.sh, as the `agent` user.
#   heal-diagnose.sh <fingerprint>
# Gated like every Claude run: the plan budget (agent/budget.py, with the usage the dispatcher read last)
# and a free slot. Wide permissions inside the agent account (heal-settings.json) plus the root helper's
# fixed verbs. A fix to the automation's code becomes a PR (agent-setup/heal-...) that the AI review
# handles. The run's report is posted on the health issue.
set -uo pipefail
source "$(dirname "$0")/common.sh"

fp="${1:?fingerprint}"
export AUTOMATED_RUN_PID=$$
usage="$RUNTIME/state/claude-usage.json"
if [[ ! -s "$usage" ]] || (( $(date +%s) - $(stat -c %Y "$usage") > 7200 )); then
  log "heal-diagnose $fp: no fresh plan usage, skipped"; exit 0
fi
AGENT_SLOT=1 python3 "$RUNNER_DIR/agent/budget.py" < "$usage" > "$RUNTIME/state/heal-budget.json"
if [[ "$(json_get "$RUNTIME/state/heal-budget.json" decision)" != "RUN" ]]; then
  log "heal-diagnose $fp: budget says wait"; exit 0
fi
memory_ok || exit 0
bash "$LOCK" acquire >/dev/null || { log "heal-diagnose $fp: no free slot"; exit 0; }
trap 'bash "$LOCK" release >/dev/null; [[ -n "${work:-}" ]] && git -C "$REPO_ROOT" worktree remove --force "$work" >/dev/null 2>&1' EXIT
bash "$LOCK" claim heal >/dev/null || exit 0

git -C "$REPO_ROOT" fetch -q origin main
work="$(dirname "$RUNNER_DIR")/heal-work"
git -C "$REPO_ROOT" worktree remove --force "$work" >/dev/null 2>&1
git -C "$REPO_ROOT" worktree add -q --detach "$work" origin/main || exit 1
detail="$RUNTIME/state/heal-detail/$(echo "$fp" | tr -c 'a-zA-Z0-9._-' '_').txt"
runlog="$RUNTIME/logs/heal-$(date -u +%Y%m%dT%H%M%SZ).jsonl"
prompt="$(cat "$RUNNER_DIR/agent/heal-prompt.md")

## This problem
- Fingerprint: \`$fp\` (seen in 3 healer runs in a row, the fixed fixes did not help)
- Detail:
\`\`\`
$(head -c 6000 "$detail" 2>/dev/null)
\`\`\`
- Last events:
\`\`\`
$(tail -20 "$RUNTIME/state/events.log" 2>/dev/null)
\`\`\`
- Working copy of main: $work. Logs: $RUNTIME/logs. State: $RUNTIME/state. Runner (read only): $RUNNER_DIR."

log "heal-diagnose: $fp starts"
(cd "$work" && claude -p "$prompt" --model sonnet --output-format stream-json --verbose \
   --settings "$RUNNER_DIR/agent/pirx/heal-settings.json") > "$runlog" 2>&1
beat heal-diagnose

report="$(python3 - "$runlog" <<'PYEOF'
import json, sys
result = ""
for line in open(sys.argv[1], errors="replace"):
    try:
        d = json.loads(line)
    except ValueError:
        continue
    if d.get("type") == "result":
        result = d.get("result") or ""
print(result[:6000] or "(no report: see the log)")
PYEOF
)"
health="$(gh api "repos/$GH_REPO/issues?labels=agent:status&state=open&per_page=1" --jq '.[0].number // empty')"
[[ -n "$health" ]] && gh issue comment "$health" --body "🩹 **Healer diagnosis: \`$fp\`**

$report

Log on pirx: \`$runlog\`" >/dev/null
status_update "Healer diagnosis for $fp finished (report on the health issue)"
exit 0
