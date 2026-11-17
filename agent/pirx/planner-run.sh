#!/usr/bin/env bash
# Planner: one run on pirx that turns the owner's roadmap into the next issues, as the `agent` user.
# Started detached by start-claude-run.sh when nothing is ready for the agents.
#   planner-run.sh <model> <decision.json>     (decision from agent/planner.py --json)
# PLAN:          Claude creates one issue per chosen story (agent/planner-prompt.md); it can only create
#                issues (agent/pirx/planner-settings.json: no edits, no pushes, no PRs).
# NEED_ROADMAP:  no model call. One `owner:todo` issue asks for projects/<project>/ROADMAP.md (once).
# Afterwards this script counts the issues that now carry a `Story:` line for the chosen ids; the
# cooldown only starts when at least one was created, so a failed run is retried at the next dispatch.
set -uo pipefail
source "$(dirname "$0")/common.sh"

model="${1:-sonnet}"; decision="${2:?decision json}"
action="$(json_get "$decision" action)"
export AUTOMATED_RUN_PID=$$

if [[ "$action" == NEED_ROADMAP ]]; then
  title="Roadmap needed: write projects/<project>/ROADMAP.md so the planner can queue work"
  if [[ -z "$(gh issue list --state open --label owner:todo --search 'in:title "Roadmap needed"' --json number --jq '.[0].number')" ]]; then
    gh issue create --title "$title" --label owner:todo --body "The agent queue is empty and the planner has no roadmap to plan from.

Add \`projects/<project>/ROADMAP.md\` with milestone headings and story lines:

\`\`\`
## M1 First product features
- US-1.1: Artist registration
- US-1.2: Public artist page (depends: US-1.1)
\`\`\`

The planner turns unplanned stories into issues when fewer than 2 tasks are queued (at most 4 per run, earliest milestone first). It never adds scope that is not in the roadmap. Close this issue when the file is on \`main\`.
<!-- automated:planner-need-roadmap -->" >/dev/null && status_update "Planner: no roadmap, asked the owner (owner:todo issue)"
  fi
  exit 0
fi
[[ "$action" == PLAN ]] || exit 0

bash "$LOCK" acquire >/dev/null || { log "planner: no free slot"; exit 0; }
trap 'bash "$LOCK" release >/dev/null' EXIT
bash "$LOCK" claim "planner" >/dev/null || { log "planner: already claimed"; exit 0; }

project="$(json_get "$decision" project)"; ms="$(json_get "$decision" milestone)"; mtitle="$(json_get "$decision" milestone_title)"
ids="$(python3 "$RUNNER_DIR/agent/planner.py" --format-stories "$decision" --ids)"
ms_name="$ms${mtitle:+ $mtitle}"

# The milestone is created by this script, not by the model (the model has no `gh api`).
if [[ -z "$(gh api "repos/$GH_REPO/milestones?state=all&per_page=100" --jq ".[] | select(.title | startswith(\"$ms \") or . == \"$ms\") | .title" | head -1)" ]]; then
  gh api "repos/$GH_REPO/milestones" -f title="$ms_name" >/dev/null || { log "planner: could not create milestone $ms_name"; exit 0; }
fi
ms_name="$(gh api "repos/$GH_REPO/milestones?state=all&per_page=100" --jq ".[] | select(.title | startswith(\"$ms \") or . == \"$ms\") | .title" | head -1)"

stories="$(python3 "$RUNNER_DIR/agent/planner.py" --format-stories "$decision")"
[[ -n "$stories" ]] || { log "planner: no stories in $decision, not calling the model"; status_update "Planner: empty story list, nothing sent to the model (bug)"; exit 0; }
prompt="$(cat "$RUNNER_DIR/agent/planner-prompt.md")

## This run
- Project: $project. Milestone for the new issues: \"$ms_name\" (it exists). The repository is checked out at the runner directory: \`$RUNNER_DIR\` (read \`projects/$project/ROADMAP.md\`, README and CLAUDE.md there).
- Stories to plan, in this order:
$stories
- Model for this run: $model. Scratch files are not allowed; you only create issues."
runlog="$RUNTIME/logs/planner-$(date -u +%Y%m%dT%H%M%SZ).jsonl"
before="$(gh issue list --state all --limit 500 --json body --jq '[.[] | select(.body | test("(?i)story:"))] | length')"
log "planner: $model plans $ids for $project ($ms_name)"
beat planner
(cd "$RUNNER_DIR" && claude -p "$prompt" --model "$model" --output-format stream-json --verbose \
  --settings "$RUNNER_DIR/agent/pirx/planner-settings.json" > "$runlog" 2>&1)

after="$(gh issue list --state all --limit 500 --json body --jq '[.[] | select(.body | test("(?i)story:"))] | length')"
created=$(( after - before ))
if (( created > 0 )); then
  python3 "$RUNNER_DIR/agent/planner.py" --mark-planned
  log "planner: created $created issue(s) for $ids"
  status_update "Planner ($model) queued $created issue(s) for $project $ms: $ids"
else
  log "planner: no issues created (log $runlog)"
  status_update "Planner ($model) created no issues for $project $ms; will retry next dispatch"
fi
exit 0
