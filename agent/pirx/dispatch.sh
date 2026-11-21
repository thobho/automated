#!/usr/bin/env bash
# Hourly dispatcher on pirx (systemd user timer `automated-dispatch`, as `agent`). Replaces the Mac's
# scheduled task: nothing in the agent runtime depends on the Mac any more.
# 1. agent/usage_probe.py reads the Claude plan limits from pirx's own Claude Code (the newest
#    rate_limit_event in the run logs, or one tiny Haiku probe call);
# 2. merge-ready.sh merges approved PRs whose CI is green on the latest main;
# 3. start-claude-run.sh applies the budget, memory, slot and task gates and starts a review or a build.
set -uo pipefail
source "$(dirname "$0")/common.sh"

usage="$RUNTIME/state/claude-usage-probe.json"
if ! AUTOMATED_RUNTIME="$RUNTIME" python3 "$RUNNER_DIR/agent/usage_probe.py" > "$usage"; then
  beat dispatcher
  status_update "Dispatcher: could not read the Claude plan limits on pirx (is the agent's Claude login valid?)"
  log "dispatch: usage unavailable"; exit 0
fi
bash "$RUNNER_DIR/agent/pirx/merge-ready.sh"   # approved PRs: no model, no budget needed
bash "$RUNNER_DIR/agent/pirx/start-claude-run.sh" < "$usage" | tee -a "$RUNTIME/logs/runner.log"
