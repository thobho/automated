#!/usr/bin/env bash
# One AI review run on pirx for one PR, as the `agent` user. Started detached by start-claude-run.sh.
#   review-run.sh <pr> <model>
# The reviewer model only writes a verdict (.agent/REVIEW.json); this script acts on it:
#   approve + CI green (or no CI) + mergeable + not protected -> squash-merge, delete the branch
#   approve + protected (changes the automation)            -> comment, the owner merges with one tap
#   changes  -> comment with the points, issue back to agent:todo (after 3 rounds: agent:blocked)
#   blocked  -> comment, issue to agent:blocked
# Red CI goes straight back to the builder, without a model call.
set -uo pipefail
source "$(dirname "$0")/common.sh"

pr="${1:?pr}"; model="${2:?model}"
export AUTOMATED_RUN_PID=$$
bash "$LOCK" acquire >/dev/null || { log "review #$pr: no free slot"; exit 0; }
trap 'bash "$LOCK" release >/dev/null; [[ -n "${work:-}" ]] && git -C "$REPO_ROOT" worktree remove --force "$work" >/dev/null 2>&1' EXIT
bash "$LOCK" claim "pr$pr" >/dev/null || { log "review #$pr: already claimed"; exit 0; }

info="$RUNTIME/state/review-$pr.json"
gh pr view "$pr" --json number,title,body,headRefName,headRefOid,mergeable,statusCheckRollup,files,comments > "$info"
read -r sha branch issue ci rounds prot <<<"$(python3 - "$info" "$RUNNER_DIR/agent" <<'EOF'
import json, sys
sys.path.insert(0, sys.argv[2])
import review_queue as rq
pr = json.load(open(sys.argv[1]))
a = rq.assess(pr, set())
print(a["sha"], a["branch"], a["issue"] or 0, a["ci"], a["rounds"], "yes" if a["protected"] else "no")
EOF
)"
mark="<!-- automated:review:$sha -->"
back_to_builder() {  # back_to_builder "<why>"
  [[ "$issue" -gt 0 ]] || return 0
  if [[ "$rounds" -ge 2 ]]; then
    gh issue edit "$issue" --remove-label agent:review --add-label agent:blocked >/dev/null
    gh issue comment "$issue" --body "🛑 Blocked after 3 review rounds without approval ($1). PR #$pr needs your decision." >/dev/null
  else
    gh issue edit "$issue" --remove-label agent:review --add-label agent:todo >/dev/null
    gh issue comment "$issue" --body "↩️ Back to the builder: $1. See the review on PR #$pr." >/dev/null
  fi
}

if [[ "$ci" == "red" ]]; then
  gh pr comment "$pr" --body "🔎 AI review skipped: CI is red on \`${sha:0:7}\`. Fix CI first. $mark <!-- automated:review-changes -->" >/dev/null
  back_to_builder "CI is red"
  log "review #$pr: CI red, back to builder"; status_update "Review of PR #$pr: CI red, back to the builder"; exit 0
fi

git -C "$REPO_ROOT" fetch -q origin "$branch"
work="$(dirname "$RUNNER_DIR")/review-$pr"
git -C "$REPO_ROOT" worktree remove --force "$work" >/dev/null 2>&1
git -C "$REPO_ROOT" worktree add -q --detach "$work" "$sha" || { log "review #$pr: checkout failed"; exit 1; }
mkdir -p "$work/.agent"

prompt="$(cat "$RUNNER_DIR/agent/review-prompt.md")

## This review
- PR #$pr ($(json_get "$info" title)), head ${sha:0:7}, branch $branch
- Linked issue: #$issue
- CI: $ci$([[ "$prot" == yes ]] && echo "; this PR changes the automation itself, so be strict: the owner will merge it only on your approval")
- Review round: $((rounds + 1)) of 3
- You run on: $model"

runlog="$RUNTIME/logs/review-$pr-$(date -u +%Y%m%dT%H%M%SZ).jsonl"
log "review #$pr: starts ($model, ${sha:0:7}, protected $prot)"
(cd "$work" && claude -p "$prompt" --model "$model" --output-format stream-json --verbose \
   --settings "$RUNNER_DIR/agent/pirx/claude-settings.json") > "$runlog" 2>&1

verdict_file="$work/.agent/REVIEW.json"
if ! python3 -c 'import json,sys; d=json.load(open(sys.argv[1])); assert d["verdict"] in ("approve","changes","blocked")' "$verdict_file" 2>/dev/null; then
  log "review #$pr: no valid verdict"; status_update "Review of PR #$pr ended without a verdict (log $runlog)"; exit 0
fi
verdict="$(json_get "$verdict_file" verdict)"
body="$(python3 - "$verdict_file" "$model" "${sha:0:7}" <<'EOF'
import json, sys
d = json.load(open(sys.argv[1])); model, sha = sys.argv[2], sys.argv[3]
icon = {"approve": "✅ approved", "changes": "🔁 changes requested", "blocked": "🛑 blocked"}[d["verdict"]]
out = [f"🔎 **AI review ({model}, `{sha}`): {icon}**", "", d.get("summary", "")]
if d.get("points"):
    out += ["", "**Must change:**"] + [f"{i}. {('`'+p['file']+'`: ') if p.get('file') else ''}{p.get('issue','')} → {p.get('fix','')}" for i, p in enumerate(d["points"], 1)]
if d.get("notes"):
    out += ["", "**Notes:**"] + [f"- {n}" for n in d["notes"]]
if d.get("checked"):
    out += ["", "**Checked:** " + "; ".join(d["checked"])]
print("\n".join(out))
EOF
)"

case "$verdict" in
  approve)
    now="$(gh pr view "$pr" --json headRefOid,mergeable -q '.headRefOid + " " + .mergeable')"
    if [[ "$prot" == yes ]]; then
      gh pr comment "$pr" --body "$body

This PR changes the automation itself, so it is not merged automatically: **owner, merge it with one tap.** $mark <!-- automated:needs-owner-merge -->" >/dev/null
      status_update "PR #$pr approved by AI review; waits for the owner's merge (automation change)"
    elif [[ "$now" != "$sha MERGEABLE" ]]; then
      gh pr comment "$pr" --body "$body

Not merged: the PR changed or is not mergeable now ($now). It will be reviewed again. $mark" >/dev/null
    else
      gh pr comment "$pr" --body "$body $mark" >/dev/null
      if gh pr merge "$pr" --squash --delete-branch --match-head-commit "$sha" >/dev/null 2>>"$runlog"; then
        [[ "$issue" -gt 0 ]] && gh issue edit "$issue" --remove-label agent:review --add-label agent:done >/dev/null 2>&1
        log "review #$pr: approved and merged"; status_update "PR #$pr approved by AI review ($model) and merged"
      else
        log "review #$pr: merge failed"; status_update "PR #$pr approved but the merge failed (log $runlog)"
      fi
    fi ;;
  changes)
    gh pr comment "$pr" --body "$body $mark <!-- automated:review-changes -->" >/dev/null
    back_to_builder "the AI review requested changes"
    status_update "PR #$pr: AI review requested changes" ;;
  blocked)
    gh pr comment "$pr" --body "$body $mark" >/dev/null
    [[ "$issue" -gt 0 ]] && gh issue edit "$issue" --remove-label agent:review --add-label agent:blocked >/dev/null
    [[ "$issue" -gt 0 ]] && gh issue comment "$issue" --body "🛑 The AI review of PR #$pr needs your decision: see its comment." >/dev/null
    status_update "PR #$pr: AI review blocked it (needs the owner)" ;;
esac
exit 0
