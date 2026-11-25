#!/usr/bin/env bash
# One AI review run on pirx for one PR, as the `agent` user. Started detached by start-claude-run.sh.
#   review-run.sh <pr> <model>
# The reviewer model only writes a verdict (.agent/REVIEW.json); this script acts on it:
#   approve + CI green (or no CI) + mergeable + not protected -> merge-ready.sh: merged against the current main
#   approve + protected (automation money/permission rules) -> comment, the owner merges with one tap
#   changes  -> comment with the points, issue back to agent:todo; after 3 rounds one rescue round
#               (Opus, larger budget, agent/rescue-prompt.md); if that is sent back too: agent:blocked
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
read -r sha branch issue ci rounds prot auto money <<<"$(python3 - "$info" "$RUNNER_DIR/agent" <<'EOF'
import json, sys
sys.path.insert(0, sys.argv[2])
import review_queue as rq
pr = json.load(open(sys.argv[1]))
a = rq.assess(pr, set())
print(a["sha"], a["branch"], a["issue"] or 0, a["ci"], a["rounds"], "yes" if a["protected"] else "no",
      "yes" if a["automation"] else "no", "yes" if a["money"] else "no")
EOF
)"
mark="<!-- automated:review:$sha -->"
back_to_builder() {  # back_to_builder "<why>"
  [[ "$issue" -gt 0 ]] || return 0
  if [[ "$rounds" -ge 2 ]] && ! rescue_used "$issue"; then
    rescue_round "$1"
  elif [[ "$rounds" -ge 2 ]]; then
    gh issue edit "$issue" --remove-label agent:review --add-label agent:blocked >/dev/null
    gh issue comment "$issue" --body "🛑 Blocked after $((rounds + 1)) review rounds without approval, including the rescue round ($1). PR #$pr needs your decision." >/dev/null
  else
    gh issue edit "$issue" --remove-label agent:review --add-label agent:todo >/dev/null
    gh issue comment "$issue" --body "↩️ Back to the builder: $1. See the review on PR #$pr." >/dev/null
    escalate_on_changes
  fi
}
rescue_round() {  # rescue_round "<why>": one more build on Opus with agent/rescue-prompt.md, then the owner
  local cur
  cur="$(gh issue view "$issue" --json labels -q '[.labels[].name | select(startswith("model:"))] | join(" ")' 2>/dev/null)"
  for l in $cur; do [[ "$l" != model:opus ]] && gh issue edit "$issue" --remove-label "$l" >/dev/null 2>&1; done
  gh issue edit "$issue" --remove-label agent:review --add-label agent:todo --add-label model:opus >/dev/null
  gh issue comment "$issue" --body "🚑 Rescue round after $((rounds + 1)) review rounds without approval ($1): one more build on Opus with a larger budget and a fresh analysis of every review point (agent/rescue-prompt.md). If its review asks for changes again, the task comes to you. See PR #$pr. $RESCUE_MARK" >/dev/null
  log "review #$pr: issue #$issue gets its rescue round after $((rounds + 1)) round(s)"
}
escalate_on_changes() {  # Sonnet first: the next build runs on Opus after 1 round with changes (security) or 2 (others)
  local labels cur need=2
  labels="$(gh issue view "$issue" --json labels -q '[.labels[].name] | join(" ")' 2>/dev/null)"
  cur="$(grep -o 'model:[a-z]*' <<<"$labels" | head -1)"
  [[ "$cur" == model:opus || "$cur" == model:pirx ]] && return 0
  [[ " $labels " == *" area:security "* ]] && need=1
  if (( rounds + 1 >= need )); then
    [[ -n "$cur" ]] && gh issue edit "$issue" --remove-label "$cur" >/dev/null 2>&1
    gh issue edit "$issue" --add-label model:opus >/dev/null
    gh issue comment "$issue" --body "⬆️ Next build on Opus: $((rounds + 1)) review round(s) with changes on ${cur#model:}." >/dev/null
    log "review #$pr: issue #$issue escalated to Opus after $((rounds + 1)) round(s)"
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
# Diff policy (agent/review_queue.py): deleted tests, new skips, changed CI or test settings.
# A step that cannot run becomes a flag the reviewer cannot judge "ok", so the policy never fails open.
files_json="$RUNTIME/state/review-$pr-files.json"; flags="$RUNTIME/state/review-$pr-flags.txt"
if gh api --paginate "repos/$GH_REPO/pulls/$pr/files?per_page=100" --jq '.[]' 2>/dev/null \
    | python3 -c 'import json,sys; json.dump([json.loads(l) for l in sys.stdin if l.strip()], sys.stdout)' > "$files_json" 2>/dev/null; then
  (cd "$RUNNER_DIR" && python3 agent/review_queue.py --policy "$files_json") > "$flags" 2>/dev/null \
    || echo "diff policy could not run: the policy check failed" > "$flags"
else
  echo "diff policy could not run: the PR's file list could not be fetched" > "$flags"
fi
min_criteria="$( [[ "$issue" -gt 0 ]] && gh issue view "$issue" --json body -q .body 2>/dev/null | (cd "$RUNNER_DIR" && python3 agent/review_queue.py --criteria-count) || echo 0)"

prompt="$(cat "$RUNNER_DIR/agent/review-prompt.md")

## This review
- PR #$pr ($(json_get "$info" title)), head ${sha:0:7}, branch $branch
- Linked issue: #$issue
- CI: $ci$([[ "$prot" == yes ]] && echo "; this PR touches the automation's money or permission rules, so be strict: the owner merges it only on your approval")$([[ "$auto" == yes && "$prot" == no ]] && echo "; this PR changes the automation itself and is merged on your approval, so be strict: it must not weaken a budget gate, a permission or a check, and must keep the automation running")
- Review round: $((rounds + 1)) of 3$( (( rounds >= 3 )) && echo " (after the builder's rescue round: if you ask for changes now, the task goes to the owner, so list every remaining point)")
- You run on: $model$([[ -s "$flags" ]] && printf '\n\n## Diff-policy flags (judge each one in `policy`, copying the flag text exactly)\n%s' "$(sed 's/^/- /' "$flags")")"

runlog="$RUNTIME/logs/review-$pr-$(date -u +%Y%m%dT%H%M%SZ).jsonl"
log "review #$pr: starts ($model, ${sha:0:7}, protected $prot)"
(cd "$work" && claude -p "$prompt" --model "$model" --output-format stream-json --verbose \
   --max-budget-usd "$(run_budget review "$model")" \
   --settings "$RUNNER_DIR/agent/pirx/claude-settings.json") > "$runlog" 2>&1

beat review
verdict_file="$work/.agent/REVIEW.json"
if [[ ! -s "$verdict_file" ]]; then   # fallback: the ```json block at the end of the reviewer's final reply
  python3 - "$runlog" > "$verdict_file.tmp" <<'PYEOF' && mv "$verdict_file.tmp" "$verdict_file"
import json, re, sys
result = ""
for line in open(sys.argv[1], errors="replace"):
    try:
        d = json.loads(line)
    except ValueError:
        continue
    if d.get("type") == "result":
        result = d.get("result") or ""
blocks = re.findall(r"```json\s*(.*?)```", result, re.S)
if not blocks:
    sys.exit(1)
print(json.dumps(json.loads(blocks[-1].strip())))
PYEOF
  rm -f "$verdict_file.tmp"
fi
if ! python3 -c 'import json,sys; d=json.load(open(sys.argv[1])); assert d["verdict"] in ("approve","changes","blocked")' "$verdict_file" 2>/dev/null; then
  log "review #$pr: no valid verdict"; status_update "Review of PR #$pr ended without a verdict (log $runlog)"; exit 0
fi
before="$(json_get "$verdict_file" verdict)"
verdict="$(cd "$RUNNER_DIR" && python3 agent/review_queue.py --enforce "$verdict_file" "$flags" "${min_criteria:-0}")"
[[ "$verdict" =~ ^(approve|changes|blocked)$ ]] || { verdict=changes; log "review #$pr: enforce gave no verdict, treated as changes"; }
[[ "$before" != "$verdict" ]] && log "review #$pr: approval turned into $verdict (missing evidence or unjudged flags)"
body="$(python3 - "$verdict_file" "$model" "${sha:0:7}" <<'EOF'
import json, sys
d = json.load(open(sys.argv[1])); model, sha = sys.argv[2], sys.argv[3]
icon = {"approve": "✅ approved", "changes": "🔁 changes requested", "blocked": "🛑 blocked"}[d["verdict"]]
out = [f"🔎 **AI review ({model}, `{sha}`): {icon}**", "", d.get("summary", "")]
if d.get("points"):
    out += ["", "**Must change:**"] + [f"{i}. {('`'+p['file']+'`: ') if p.get('file') else ''}{p.get('issue','')} → {p.get('fix','')}" for i, p in enumerate(d["points"], 1)]
if d.get("notes"):
    out += ["", "**Notes:**"] + [f"- {n}" for n in d["notes"]]
if d.get("criteria"):
    out += ["", "**Acceptance criteria:**"] + [f"- {'✅' if c.get('met') else '❌'} {c.get('criterion','')}: {c.get('evidence','')}" for c in d["criteria"]]
if d.get("policy"):
    out += ["", "**Diff policy:**"] + [f"- {'✅' if p.get('ok') else '❌'} {p.get('flag','')}: {p.get('why','')}" for p in d["policy"]]
if d.get("checked"):
    out += ["", "**Checked:** " + "; ".join(d["checked"])]
print("\n".join(out))
EOF
)"

case "$verdict" in
  approve)
    now="$(gh pr view "$pr" --json headRefOid,mergeable -q '.headRefOid + " " + .mergeable')"
    if [[ "$now" == "$sha CONFLICTING" ]]; then   # before the protected check: the owner cannot merge a conflict either
      gh pr comment "$pr" --body "$body

Not merged yet: the branch conflicts with \`main\`. The conflict resolver merges \`main\` into it next, then the new commit is reviewed again (this does not use a review round). $mark" >/dev/null
      log "review #$pr: approved but conflicting, to the conflict resolver"; status_update "PR #$pr approved but conflicts with main; the conflict resolver takes it"
    elif [[ "$prot" == yes ]]; then
      gh pr comment "$pr" --body "$body

This PR touches the automation's money or permission rules, so it is not merged automatically: **owner, merge it with one tap.** $mark <!-- automated:needs-owner-merge -->" >/dev/null
      if [[ "$money" == yes ]]; then   # spending rules change: the one kind of PR the owner hears about
        gh issue create --label owner:money --title "💰 Merge PR #$pr: it changes the spending limits" \
          --body "PR #$pr changes \`agent/budget.py\` or \`agent/openrouter_budget.py\` (how much of the Claude plan or OpenRouter money the automation spends). The AI review approved it. Merge it if you agree, or close it; then close this issue." >/dev/null
      fi
      status_update "PR #$pr approved by AI review; waits for the owner's merge (money or permission rules)"
    elif [[ "$now" != "$sha MERGEABLE" ]]; then
      gh pr comment "$pr" --body "$body

Not merged: the PR changed or is not mergeable now ($now). It will be reviewed again. $mark" >/dev/null
    else   # merge-ready.sh merges it only against the current main and while main is green
      approve_record "$pr" "$sha"
      gh pr comment "$pr" --body "$body $mark <!-- automated:approved:$sha -->" >/dev/null
      log "review #$pr: approved ($model)"; status_update "PR #$pr approved by AI review ($model)"
      bash "$RUNNER_DIR/agent/pirx/merge-ready.sh" "$pr"
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
