#!/usr/bin/env bash
# Entry point for the Mac dispatcher: decide whether a Claude run may start on pirx, and start it detached.
#   ssh user@pirx 'bash ~/Projects/automated-work/runner/agent/pirx/start-claude-run.sh' < usage.json
# stdin: the plan usage JSON from the desktop get_usage tool (only the Mac can read it).
# Gates, in order: Claude plan budget (agent/budget.py), memory on pirx, a free slot, a ready task,
# and Opus headroom when the task needs Opus. Prints one line saying what happened; always exits 0
# unless the input is broken, so the dispatcher stays a single cheap call.
set -uo pipefail
source "$(dirname "$0")/common.sh"

usage="$RUNTIME/state/claude-usage.json"
budget="$RUNTIME/state/claude-budget.json"
cat > "$usage"
[[ -s "$usage" ]] || { echo "ERROR: no usage JSON on stdin"; exit 2; }
beat dispatcher

free_slots() { bash "$LOCK" status | grep -c ': free$' || true; }
held_slots() { bash "$LOCK" status | grep -c ': held' || true; }

# Keep the tooling current, but never under a running script.
if [[ "$(held_slots)" -eq 0 ]]; then
  git -C "$REPO_ROOT" fetch -q origin && git -C "$RUNNER_DIR" checkout -q --detach "$RUNNER_REF"
fi

slot=$(( $(held_slots) + 1 ))
AGENT_SLOT=$slot python3 "$RUNNER_DIR/agent/budget.py" < "$usage" > "$budget"
decision="$(json_get "$budget" decision)"; reason="$(json_get "$budget" reason)"
if [[ "$decision" != "RUN" ]]; then
  status_update "Claude skipped: $reason"; echo "WAIT: $reason"; exit 0
fi
if ! memory_ok; then
  status_update "Claude skipped: pirx memory ($(free_mb) MB available)"; echo "WAIT: memory on pirx"; exit 0
fi
if [[ "$(free_slots)" -eq 0 ]]; then
  echo "BUSY: every pirx slot is taken"; exit 0
fi

# Reviews come first: a reviewed PR is merged work, and waiting PRs hold back the queue (review limit).
rev="$RUNTIME/state/review-next.json"
if (cd "$RUNNER_DIR" && python3 agent/review_queue.py --next-json) > "$rev" 2>/dev/null; then
  pr="$(json_get "$rev" pr)"; rmodel="$(json_get "$rev" model)"; fallback="$(json_get "$rev" fallback)"
  if [[ "$rmodel" == "opus" ]]; then
    AGENT_SLOT=$slot AGENT_MODEL=opus python3 "$RUNNER_DIR/agent/budget.py" < "$usage" > "$budget.opus"
    [[ "$(json_get "$budget.opus" decision)" == "RUN" ]] || rmodel="$fallback"
  fi
  if [[ -n "$rmodel" ]]; then
    unit="automated-review-$pr"
    if ! systemctl --user is-active -q "$unit"; then
      systemd-run --user --quiet --collect --unit "$unit" -p RuntimeMaxSec=3600 -p Nice=5 --setenv=HOME="$HOME" \
        /bin/bash "$RUNNER_DIR/agent/pirx/review-run.sh" "$pr" "$rmodel"
      log "started $unit (model $rmodel, slot $slot)"
      echo "STARTED: review of PR #$pr with $rmodel on pirx (unit $unit)"; exit 0
    fi
  else
    log "review of PR #$pr waits for Opus headroom (security)"
  fi
fi

spill=(); [[ "$(json_get "$budget" spillover_ok)" == "true" ]] && spill=(--spillover)
task="$RUNTIME/state/claude-next.json"
if ! (cd "$RUNNER_DIR" && AUTOMATED_LOCK_SCRIPT="$LOCK" python3 agent/pick_task.py --next-json --executor claude "${spill[@]}") > "$task"; then
  queue="$(cd "$RUNNER_DIR" && AUTOMATED_LOCK_SCRIPT="$LOCK" python3 agent/pick_task.py | head -5 | paste -sd ';' -)"
  status_update "Nothing ready for Claude: ${queue:-queue empty}"; echo "IDLE: nothing ready"; exit 0
fi
num="$(json_get "$task" number)"; model="$(json_get "$task" model)"
if [[ "$model" == "opus" ]]; then
  AGENT_SLOT=$slot AGENT_MODEL=opus python3 "$RUNNER_DIR/agent/budget.py" < "$usage" > "$budget.opus"
  if [[ "$(json_get "$budget.opus" decision)" != "RUN" ]]; then
    r="$(json_get "$budget.opus" reason)"
    status_update "Claude waits: #$num needs Opus ($r)"; echo "WAIT: #$num needs Opus ($r)"; exit 0
  fi
fi

unit="automated-claude-$num"
if systemctl --user is-active -q "$unit"; then echo "BUSY: $unit is already running"; exit 0; fi
systemd-run --user --quiet --collect --unit "$unit" \
  -p RuntimeMaxSec="$(( ${CLAUDE_MAX_RUN_H:-3} * 3600 ))" -p Nice=5 \
  --setenv=HOME="$HOME" \
  /bin/bash "$RUNNER_DIR/agent/pirx/claude-run.sh" "$num" "$model" "$(json_get "$task" spillover)"
log "started $unit (model $model, slot $slot)"
echo "STARTED: #$num with $model on pirx (unit $unit, slot $slot); $(json_get "$budget" reason)"
