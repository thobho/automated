#!/usr/bin/env bash
# Weekly retro on pirx (timer automated-retro, Monday 05:30 Warsaw), as the `agent` user.
# agent/retro.py collects the week's review findings (no model); with at least 2, Sonnet turns repeated ones
# into rules in projects/<p>/CLAUDE.md (retro-settings.json: it may edit only those files; rules for every
# builder in agent/worker-prompt.md stay a human or reviewed-PR decision). This script, not the model, commits, pushes agent-setup/retro-<date> and opens the PR,
# which the AI reviewer handles like any other.
# Gated like every Claude run: fresh plan usage, the budget, memory and a free slot.
set -uo pipefail
source "$(dirname "$0")/common.sh"

export AUTOMATED_RUN_PID=$$
beat retro
usage="$RUNTIME/state/claude-usage.json"
if [[ ! -s "$usage" ]] || (( $(date +%s) - $(stat -c %Y "$usage") > 7200 )); then
  log "retro: no fresh plan usage, skipped"; exit 0
fi
AGENT_SLOT=1 python3 "$RUNNER_DIR/agent/budget.py" < "$usage" > "$RUNTIME/state/retro-budget.json"
[[ "$(json_get "$RUNTIME/state/retro-budget.json" decision)" == "RUN" ]] || { log "retro: budget says wait"; exit 0; }
memory_ok || exit 0
digest="$RUNTIME/state/retro-digest.md"
(cd "$RUNNER_DIR" && python3 agent/retro.py --days 7) > "$digest" 2>>"$RUNTIME/logs/runner.log"; rc=$?
if (( rc == 1 )); then log "retro: fewer than 2 findings, nothing to learn"; exit 0; fi
if (( rc != 0 )); then log "retro: digest failed (exit $rc)"; status_update "Weekly retro failed: the digest could not read GitHub"; exit 0; fi
bash "$LOCK" acquire >/dev/null || { log "retro: no free slot"; exit 0; }
trap 'bash "$LOCK" release >/dev/null; [[ -n "${work:-}" ]] && git -C "$REPO_ROOT" worktree remove --force "$work" >/dev/null 2>&1' EXIT
bash "$LOCK" claim retro >/dev/null || exit 0

branch="agent-setup/retro-$(date -u +%Y-%m-%d-%H%M)"
git -C "$REPO_ROOT" fetch -q origin main
work="$(dirname "$RUNNER_DIR")/retro-work"
git -C "$REPO_ROOT" worktree remove --force "$work" >/dev/null 2>&1
git -C "$REPO_ROOT" worktree add -q -B "$branch" "$work" origin/main || exit 1
runlog="$RUNTIME/logs/retro-$(date -u +%Y%m%dT%H%M%SZ).jsonl"
prompt="$(cat "$RUNNER_DIR/agent/retro-prompt.md")

## Digest
$(head -c 40000 "$digest")"
log "retro: starts (sonnet)"
(cd "$work" && claude -p "$prompt" --model sonnet --output-format stream-json --verbose \
   --settings "$RUNNER_DIR/agent/pirx/retro-settings.json") > "$runlog" 2>&1

changed="$(git -C "$work" status --porcelain)"
if [[ -z "$changed" ]]; then log "retro: no rule changes"; status_update "Weekly retro: no new rules"; exit 0; fi
if grep -v -E '^ M projects/[^/]+/CLAUDE\.md$' <<<"$changed" | grep -q .; then
  log "retro: edits outside the allowed files, discarded"; status_update "Weekly retro: edits outside the allowed files were discarded"; exit 0
fi
reply="$(python3 - "$runlog" <<'PYEOF'
import json, sys
result = ""
for line in open(sys.argv[1], errors="replace"):
    try:
        d = json.loads(line)
    except ValueError:
        continue
    if d.get("type") == "result":
        result = d.get("result") or ""
print(result[:5000])
PYEOF
)"
# Nothing that looks like a credential leaves pirx: token formats, private keys, or any value from the
# automation's own secret files.
if ! { git -C "$work" diff; printf '%s\n' "$reply"; } | python3 "$RUNNER_DIR/agent/retro.py" --scan-secrets "$CONF_DIR"; then
  log "retro: possible credential in the edits or reply, discarded"; status_update "Weekly retro: discarded, its output looked like it contained a credential"; exit 0
fi
git -C "$work" add -A
git -C "$work" -c user.name="automated-retro" -c user.email="agent@pirx" commit -q -m "Weekly retro: rules from repeated review findings ($(date -u +%F))"
git -C "$work" push -q origin "$branch" 2>>"$runlog" || { log "retro: push failed"; exit 0; }
pr="$(gh pr create --base main --head "$branch" --title "Weekly retro: rules from repeated review findings ($(date -u +%F))" --body "Rules added by the weekly retro (agent/pirx/retro-run.sh) from findings that repeated in the last 7 days. The reviewer should check each rule against the digest: concrete, backed by at least two findings (or one security/data-loss finding), not a duplicate.

## What changed and why
$reply

<details><summary>Digest</summary>

$(head -c 30000 "$digest")
</details>" 2>>"$runlog")"
log "retro: opened $pr"; status_update "Weekly retro opened $pr"
exit 0
