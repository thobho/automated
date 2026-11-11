#!/usr/bin/env bash
# One Claude Code run on pirx for one issue, as the unprivileged `agent` user.
# Started detached by start-claude-run.sh (systemd-run --user).
#   claude-run.sh <issue> <model> [spillover]
# Isolation: the agent user has no sudo and no access to /home/user or the LAN; on top of that Claude Code
# runs in `dontAsk` mode with a command allowlist (agent/pirx/claude-settings.json): file edits only inside
# the working copy, shell commands only from the list (git, gh issue/pr/run, uv, pytest, ruff, curl, ...),
# everything else is refused. (Claude Code's OS sandbox cannot start on Ubuntu 26.04 without relaxing its
# user-namespace restriction, which the owner chose not to do.)
# This script holds the slot and the claim, records the outcome and escalates:
# 3 failed sonnet/haiku runs -> model:opus; 3 failed opus runs -> agent:blocked.
# Runs stopped by a usage limit do not count as failures.
set -uo pipefail
source "$(dirname "$0")/common.sh"

num="${1:?issue}"; model="${2:?model}"; spillover="${3:-}"
export AUTOMATED_RUN_PID=$$
runlog="$RUNTIME/logs/claude-$num-$(date -u +%Y%m%dT%H%M%SZ).jsonl"
mkdir -p "$RUNTIME/scratch"

if ! bash "$LOCK" acquire >/dev/null; then log "#$num: no free slot"; exit 0; fi
trap 'bash "$LOCK" release >/dev/null' EXIT
if ! bash "$LOCK" claim "$num" >/dev/null; then log "#$num: already claimed"; exit 0; fi

title="$(gh issue view "$num" --json title -q .title)"
slug="$(echo "$title" | tr '[:upper:]' '[:lower:]' | tr -cs 'a-z0-9' '-' | cut -c1-40 | sed 's/^-//; s/-$//')"
work="$(bash "$RUNNER_DIR/scripts/task-worktree.sh" "$num" "$slug")" || { log "#$num: worktree failed"; exit 1; }

prompt="$(cat "$RUNNER_DIR/agent/worker-prompt.md")

## This run
- Issue: #$num ($title) in $GH_REPO
- Model: $model$([[ "$spillover" == "true" ]] && echo " (spillover: a simple OpenCode task, built by Claude)")
- Working copy: $work (branch agent/$num-$slug). Work only there; scratch files go to $RUNTIME/scratch.
- Machine: pirx (Linux, lean mode: 4 GB RAM). The slot and the claim are already held for you."

log "#$num: claude run starts (model $model, $work)"
(cd "$work" && claude -p "$prompt" --model "$model" --output-format stream-json --verbose \
   --settings "$RUNNER_DIR/agent/pirx/claude-settings.json") > "$runlog" 2>&1
rc=$?

state="$(gh issue view "$num" --json labels -q '[.labels[].name | select(startswith("agent:"))] | join(",")')"
limited=false
tail -5 "$runlog" | grep -qiE 'usage limit|rate limit|limit reached|overloaded' && limited=true
log "#$num: claude run ended (rc $rc, labels $state, usage-limited $limited)"

if [[ "$state" == *agent:review* || "$state" == *agent:blocked* ]]; then
  status_update "Claude ($model) finished #$num: $state"
elif [[ "$limited" == true ]]; then
  status_update "Claude ($model) paused on #$num by a usage limit; it resumes next run"
else
  gh issue comment "$num" --body "❌ Claude run ($model) ended without a PR (exit $rc). Log on pirx: \`$runlog\`. <!-- automated:fail:$model -->" >/dev/null
  fails="$(fail_count "$num" "$model")"
  if [[ "$spillover" != "true" && "$model" != "opus" && "$fails" -ge 3 ]]; then
    gh issue edit "$num" --remove-label "model:$model" >/dev/null 2>&1
    gh issue edit "$num" --add-label model:opus >/dev/null
    gh issue comment "$num" --body "⬆️ Escalated to Opus after $fails failed $model runs." >/dev/null
  elif [[ "$model" == "opus" && "$fails" -ge 3 ]]; then
    gh issue edit "$num" --remove-label agent:doing --add-label agent:blocked >/dev/null
    gh issue comment "$num" --body "🛑 Blocked after $fails failed Opus runs: this needs your look (see the ❌ comments)." >/dev/null
  fi
  status_update "Claude ($model) failed on #$num ($fails failed $model runs so far)"
fi

# Remove working copies of issues that are closed.
for dir in "$(dirname "$work")"/issue-*; do
  [[ -d "$dir" ]] || continue
  n="${dir##*-}"
  [[ "$(gh issue view "$n" --json state -q .state 2>/dev/null)" == "CLOSED" ]] && bash "$RUNNER_DIR/scripts/task-worktree.sh" --remove "$n" >/dev/null 2>&1
done
exit 0
