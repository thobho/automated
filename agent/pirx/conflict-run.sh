#!/usr/bin/env bash
# Conflict resolver: one run on pirx for one PR that conflicts with main, as the `agent` user.
# Started detached by start-claude-run.sh before any review or build.
#   conflict-run.sh <pr> <model>
# 1. Merge origin/main into the PR branch. A clean merge is pushed with no model call.
# 2. Otherwise a Claude run resolves the conflicts, runs the project's checks and commits the merge.
#    It runs with wide permissions inside the agent account (agent/pirx/conflict-settings.json) but
#    cannot push: this script checks the result and pushes it.
# 3. Check: the merge is committed, origin/main is in the history, the old branch head is the first
#    parent (no rewritten history) and no conflict markers are left. Then a normal push (never forced).
# The new head commit then goes through the AI review as usual. Every attempt leaves a
# <!-- automated:conflict-attempt --> comment; after 2 failed attempts the task is blocked.
set -uo pipefail
source "$(dirname "$0")/common.sh"

pr="${1:?pr}"; model="${2:-sonnet}"
export AUTOMATED_RUN_PID=$$
bash "$LOCK" acquire >/dev/null || { log "conflict #$pr: no free slot"; exit 0; }
trap 'bash "$LOCK" release >/dev/null; [[ -n "${work:-}" ]] && git -C "$REPO_ROOT" worktree remove --force "$work" >/dev/null 2>&1' EXIT
bash "$LOCK" claim "conflict$pr" >/dev/null || { log "conflict #$pr: already claimed"; exit 0; }

info="$RUNTIME/state/conflict-$pr.json"
gh pr view "$pr" --json number,title,body,headRefName,headRefOid,isDraft,mergeable,statusCheckRollup,files,comments > "$info"
read -r sha branch issue attempts conflicting <<<"$(python3 - "$info" "$RUNNER_DIR/agent" <<'PYEOF'
import json, sys
sys.path.insert(0, sys.argv[2])
import review_queue as rq
a = rq.assess(json.load(open(sys.argv[1])), set())
print(a["sha"], a["branch"], a["issue"] or 0, a["conflict_attempts"], "yes" if a["conflicting"] else "no")
PYEOF
)"
[[ "$conflicting" == yes ]] || { log "conflict #$pr: no longer conflicting"; exit 0; }
mark="<!-- automated:conflict-attempt -->"
runlog="$RUNTIME/logs/conflict-$pr-$(date -u +%Y%m%dT%H%M%SZ).jsonl"

failed() {  # failed "<why>"
  local n=$((attempts + 1))
  if [[ "$n" -ge 2 ]]; then
    gh pr comment "$pr" --body "🔀 Conflict with \`main\` not resolved ($1), attempt $n of 2. Needs your look. Log on pirx: \`$runlog\`. $mark" >/dev/null
    [[ "$issue" -gt 0 ]] && gh issue edit "$issue" --remove-label agent:review --add-label agent:blocked >/dev/null 2>&1
    [[ "$issue" -gt 0 ]] && gh issue comment "$issue" --body "🛑 PR #$pr conflicts with \`main\` and two resolver runs could not fix it ($1)." >/dev/null
    status_update "PR #$pr: conflict with main not resolved after 2 attempts (blocked)"
  else
    gh pr comment "$pr" --body "🔀 Conflict with \`main\` not resolved ($1), attempt $n of 2; the next attempt runs on Opus. $mark" >/dev/null
    status_update "PR #$pr: conflict resolver attempt $n failed ($1)"
  fi
  log "conflict #$pr: failed ($1)"; exit 0
}

git -C "$REPO_ROOT" fetch -q origin main "$branch" || failed "fetch failed"
work="$(dirname "$RUNNER_DIR")/conflict-$pr"
git -C "$REPO_ROOT" worktree remove --force "$work" >/dev/null 2>&1
git -C "$REPO_ROOT" worktree add -q --detach "$work" "$sha" || failed "checkout failed"
cd "$work" || failed "no working copy"
git -c user.name=automated -c user.email=automated@pirx merge --no-edit origin/main >/dev/null 2>&1
how="a clean merge, no model needed"

if [[ -e "$(git rev-parse --git-path MERGE_HEAD)" ]]; then
  files="$(git diff --name-only --diff-filter=U | paste -sd ' ' -)"
  how="$model resolved: $files"
  prompt="$(cat "$RUNNER_DIR/agent/conflict-prompt.md")

## This run
- PR #$pr ($(json_get "$info" title)), branch $branch, head ${sha:0:7}; linked issue #$issue
- \`git merge origin/main\` stopped with conflicts in: $files
- Attempt $((attempts + 1)) of 2, on $model. Scratch files go to $RUNTIME/scratch."
  log "conflict #$pr: $model resolves $files"
  claude -p "$prompt" --model "$model" --output-format stream-json --verbose \
    --settings "$RUNNER_DIR/agent/pirx/conflict-settings.json" > "$runlog" 2>&1
fi
beat conflict

[[ -e "$(git rev-parse --git-path MERGE_HEAD)" ]] && failed "the merge was not committed"
[[ -z "$(git status --porcelain --untracked-files=no)" ]] || failed "uncommitted changes left"
git merge-base --is-ancestor origin/main HEAD || failed "main is not in the result"
git merge-base --is-ancestor "$sha" HEAD || failed "the branch history was rewritten"
git grep -qnE '^(<<<<<<<|>>>>>>>) ' HEAD && failed "conflict markers left"
git push -q origin "HEAD:refs/heads/$branch" 2>>"$runlog" || failed "push rejected (the branch moved?)"

new="$(git rev-parse --short HEAD)"
gh pr comment "$pr" --body "🔀 Merged \`main\` into this branch ($how). New head \`$new\`; the AI review looks at it next. $mark" >/dev/null
log "conflict #$pr: resolved ($new)"; status_update "PR #$pr: conflict with main resolved ($how)"
exit 0
