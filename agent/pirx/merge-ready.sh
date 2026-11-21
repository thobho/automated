#!/usr/bin/env bash
# Merge approved PRs safely, without a model (see "Merge safety" in agent/review_queue.py).
#   merge-ready.sh [<pr>]     all PRs that are ready, or only this one
# Run by dispatch.sh and heal.sh, and by review-run.sh right after an approval. For each approved PR:
#   CI red (after main was merged in)  -> back to the builder: it clashes with work merged meanwhile
#   the project's CI is red on main    -> held, unless the PR is the red-main fix itself
#   head does not contain current main -> GitHub "update branch", wait for CI on the new head (max 3 times)
#   otherwise                          -> squash-merge with --match-head-commit
set -uo pipefail
source "$(dirname "$0")/common.sh"

only="${1:-}"
list="$RUNTIME/state/merge-ready.json"
(cd "$RUNNER_DIR" && python3 agent/review_queue.py --merge-ready-json) > "$list" 2>/dev/null || exit 0
python3 - "$list" "$only" <<'PYEOF' |
import json, sys
for t in json.load(open(sys.argv[1])):
    if sys.argv[2] and str(t["pr"]) != sys.argv[2]:
        continue
    print(t["pr"], t["sha"], t["ci"], t["project"] or "-", t["issue"] or 0, t["updates"], t["max_updates"],
          "yes" if t["red_main_fix"] else "no", "yes" if t["update_of_approved"] else "no")
PYEOF
while read -r pr sha ci project issue updates max fix updated; do
  if [[ "$ci" == red ]]; then   # once per commit (merge-red mark), with or without a linked issue
    if [[ "$updated" == yes ]]; then why="after \`main\` was merged into this approved PR: it clashes with work merged meanwhile"
    else why="on the approved commit itself"; fi
    gh pr comment "$pr" --body "🔁 CI is red on \`${sha:0:7}\` $why. Not merged; back to the builder. <!-- automated:merge-red:$sha --> <!-- automated:review:$sha --> <!-- automated:review-changes -->" >/dev/null
    if [[ "$issue" -gt 0 ]]; then
      gh issue edit "$issue" --remove-label agent:review --add-label agent:todo >/dev/null
      gh issue comment "$issue" --body "↩️ Back to the builder: PR #$pr was approved, but CI is red $why. Merge \`main\`, fix it, push." >/dev/null
    fi
    log "merge #$pr: CI red ($why), back to builder"; status_update "PR #$pr: CI red after approval, back to the builder"; continue
  fi
  if [[ "$fix" != yes ]] && main_red "$project"; then
    log "merge #$pr: held, $project CI is red on main"; continue
  fi
  behind="$(behind_main "$sha")"
  if [[ -z "$behind" ]]; then log "merge #$pr: could not compare with main, skipped this time"; continue; fi
  if (( behind > 0 && updates < max )); then
    approve_record "$pr" "$sha"   # the update commit is trusted only as GitHub's merge of this approved commit
    if gh api -X PUT "repos/$GH_REPO/pulls/$pr/update-branch" -f expected_head_sha="$sha" >/dev/null 2>&1; then
      gh pr comment "$pr" --body "⤵️ Approved, but \`main\` moved ($behind new commits). Merged \`main\` into the branch; this PR is merged when CI is green on the updated commit (update $((updates + 1)) of $max, no new review). <!-- automated:approved:$sha --> <!-- automated:updated -->" >/dev/null
      log "merge #$pr: updated with main ($behind behind), waiting for CI"
    else
      log "merge #$pr: update-branch failed (conflict?), the conflict resolver takes it"
    fi
    continue
  fi
  if (( behind > 0 )); then
    gh pr comment "$pr" --body "⚠️ \`main\` moved again after $max updates; merging on CI of the last update (${behind} commits behind). <!-- automated:max-updates:$sha -->" >/dev/null
    log "merge #$pr: $max updates used, merging $behind behind main"
  fi
  if gh pr merge "$pr" --squash --delete-branch --match-head-commit "$sha" >/dev/null 2>>"$RUNTIME/logs/runner.log"; then
    [[ "$issue" -gt 0 ]] && gh issue edit "$issue" --remove-label agent:review --add-label agent:done >/dev/null 2>&1
    log "merge #$pr: merged (${sha:0:7})"; status_update "PR #$pr merged (approved, CI green on the latest main)"
  else
    log "merge #$pr: merge failed"
  fi
done
exit 0
