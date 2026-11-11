#!/usr/bin/env bash
# Hourly OpenCode worker on pirx (systemd user timer, as the `agent` user): one `model:pirx` task per run.
# Gates: memory, OpenRouter budget (agent/openrouter_budget.py), a free slot, a ready task.
# OpenCode only edits and commits (agent/pirx/opencode.json denies push, gh and leaving the working copy);
# this script does the labels, the push and the PR, and watches the spend while OpenCode runs.
# Two failed OpenCode runs on an issue -> it moves to model:sonnet (a Claude run).
set -uo pipefail
source "$(dirname "$0")/common.sh"

export AUTOMATED_RUN_PID=$$
keyfile="${OPENROUTER_KEY_FILE:-$CONF_DIR/openrouter-opencode.key}"
model="${OPENCODE_MODEL:-openrouter/deepseek/deepseek-v4.1-flash-1017}"
keyinfo="$RUNTIME/state/openrouter-key.json"
budget="$RUNTIME/state/openrouter-budget.json"

memory_ok || exit 0
[[ -s "$keyfile" ]] || { log "opencode: no key file ($keyfile)"; exit 0; }

key_info() { sed 's/^/Authorization: Bearer /' "$keyfile" | curl -s -m 20 -H @- https://openrouter.ai/api/v1/key; }
usage_now() { key_info | python3 -c 'import json,sys; print(json.load(sys.stdin)["data"]["usage_monthly"])' 2>/dev/null || echo ""; }

key_info > "$keyinfo"
python3 "$RUNNER_DIR/agent/openrouter_budget.py" < "$keyinfo" > "$budget"
if [[ "$(json_get "$budget" decision)" != "RUN" ]]; then log "opencode: $(json_get "$budget" reason)"; exit 0; fi
task_budget="$(json_get "$budget" task_budget_usd)"

bash "$LOCK" acquire >/dev/null || { log "opencode: no free slot"; exit 0; }
trap 'bash "$LOCK" release >/dev/null' EXIT

next="$RUNTIME/state/opencode-next.json"
(cd "$RUNNER_DIR" && AUTOMATED_LOCK_SCRIPT="$LOCK" python3 agent/pick_task.py --next-json --executor opencode) > "$next" \
  || { log "opencode: nothing ready"; exit 0; }
num="$(json_get "$next" number)"; title="$(json_get "$next" title)"
bash "$LOCK" claim "$num" >/dev/null || { log "opencode: #$num already claimed"; exit 0; }

gh issue edit "$num" --remove-label agent:todo --add-label agent:doing >/dev/null 2>&1
gh issue comment "$num" --body "🔧 OpenCode (\`${model#openrouter/}\`) started on pirx. Budget for this task: \$$task_budget." >/dev/null

slug="$(echo "$title" | tr '[:upper:]' '[:lower:]' | tr -cs 'a-z0-9' '-' | cut -c1-40 | sed 's/^-//; s/-$//')"
work="$(bash "$RUNNER_DIR/scripts/task-worktree.sh" "$num" "$slug")" || { log "opencode: worktree failed for #$num"; exit 1; }
branch="agent/$num-$slug"
mkdir -p "$work/.agent"; rm -f "$work/.agent/PR_BODY.md"
base="$(git -C "$work" rev-parse HEAD)"

prompt="$(cat "$RUNNER_DIR/agent/opencode-prompt.md")

## The issue
#$num $title

$(gh issue view "$num" --json body -q .body)"

runlog="$RUNTIME/logs/opencode-$num-$(date -u +%Y%m%dT%H%M%SZ).log"
start_usage="$(usage_now)"
log "opencode: #$num starts ($model, budget \$$task_budget)"
( cd "$work" && OPENROUTER_API_KEY="$(cat "$keyfile")" OPENCODE_CONFIG="$RUNNER_DIR/agent/pirx/opencode.json" \
    timeout "${OPENCODE_TIMEOUT_MIN:-40}m" opencode run --standalone --auto --model "$model" "$prompt" ) > "$runlog" 2>&1 &
pid=$!
killed=""
while kill -0 "$pid" 2>/dev/null; do
  sleep 60
  now="$(usage_now)"
  if [[ -n "$now" && -n "$start_usage" ]] && python3 -c "import sys; sys.exit(0 if float('$now')-float('$start_usage') > float('$task_budget') else 1)"; then
    killed="budget"; pkill -TERM -P "$pid" 2>/dev/null; kill -TERM "$pid" 2>/dev/null; break
  fi
done
wait "$pid" 2>/dev/null; rc=$?
spent="$(python3 -c "print(round(float('$(usage_now)' or 0)-float('${start_usage:-0}' or 0),3))" 2>/dev/null || echo "?")"

commits="$(git -C "$work" rev-list --count "$base..HEAD" 2>/dev/null || echo 0)"
body_file="$work/.agent/PR_BODY.md"
if [[ "$commits" -gt 0 && -s "$body_file" ]] && ! head -1 "$body_file" | grep -q '^INCOMPLETE:'; then
  if git -C "$work" push -q -u origin "$branch" 2>>"$runlog"; then
    pr_body="$(cat "$body_file")

Built by OpenCode (\`${model#openrouter/}\`) on pirx, about \$$spent of OpenRouter.

Closes #$num"
    url="$(gh pr create --head "$branch" --title "$title" --body "$pr_body" 2>>"$runlog" || gh pr view "$branch" --json url -q .url 2>/dev/null)"
    gh issue edit "$num" --remove-label agent:doing --add-label agent:review >/dev/null
    gh issue comment "$num" --body "✅ PR ready: $url (OpenCode, \$$spent)." >/dev/null
    log "opencode: #$num PR $url (\$$spent)"
    status_update "OpenCode opened a PR for #$num (\$$spent)"
    exit 0
  fi
fi

why="exit $rc"; [[ -n "$killed" ]] && why="stopped at the task budget (\$$task_budget)"
[[ "$commits" -eq 0 ]] && why="$why, no commits"
[[ -s "$body_file" ]] && head -1 "$body_file" | grep -q '^INCOMPLETE:' && why="$why, $(head -1 "$body_file" | cut -c1-200)"
[[ "$commits" -gt 0 ]] && git -C "$work" push -q -u origin "$branch" 2>>"$runlog"   # keep partial work for the next run
gh issue comment "$num" --body "❌ OpenCode run failed: $why (about \$$spent). Log on pirx: \`$runlog\`. <!-- automated:fail:pirx -->" >/dev/null
fails="$(fail_count "$num" pirx)"
if [[ "$fails" -ge 2 ]]; then
  gh issue edit "$num" --remove-label model:pirx >/dev/null 2>&1
  gh issue edit "$num" --add-label model:sonnet >/dev/null
  gh issue comment "$num" --body "⬆️ Moved to Sonnet (a Claude run) after $fails failed OpenCode runs." >/dev/null
fi
gh issue edit "$num" --remove-label agent:doing --add-label agent:todo >/dev/null
status_update "OpenCode failed on #$num ($why)"
exit 0
