#!/usr/bin/env bash
# Healer on pirx, as the `agent` user. Every 30 minutes (automated-heal.timer) and whenever another
# automated unit fails (OnFailure=). It reads only local state and GitHub labels, never issue text, and
# applies fixed fixes without a model:
#   1. unit files match the runner, timers are enabled, failed units are reset
#   2. tasks stuck in agent:doing with no live run go back to the queue (twice, then blocked)
#   3. leftover review/conflict/heal worktrees are removed, the runner is on its ref (no run active)
#   4. old logs are deleted; above 85% disk use podman and the uv cache are pruned
#   5. the health page is refreshed when stale
#   6. with the root helper installed (agent/pirx/root/): the owner's services (not phone-farm) and the
#      system services in its list are restarted when down, and the agent firewall is reloaded
#   7. OpenRouter keys close to their limit open an `owner:money` issue: the only alert sent to the
#      owner's phone (agent/pirx/owner/money-notify.sh)
#   8. a project's CI failing on main opens one priority:high fix task (label red-main); merge-ready.sh
#      holds that project's other PRs meanwhile and merges approved PRs that are ready
# A problem that survives 3 runs in a row goes to a model: heal-diagnose.sh (Sonnet, once per 6 h each).
set -uo pipefail
source "$(dirname "$0")/common.sh"

st="$RUNTIME/state"; details="$st/heal-detail"; mkdir -p "$details"
ROOT_HELPER=/usr/local/sbin/automated-root
problems=(); fixes=()
problem() {  # problem <fingerprint> <detail>
  problems+=("$1"); printf '%s\n' "$2" > "$details/$(echo "$1" | tr -c 'a-zA-Z0-9._-' '_').txt"
}
fixed() { fixes+=("$1"); log "heal: $1"; }
held="$(bash "$LOCK" status | grep -c ': held' || true)"
beat heal

# 1. Units and timers.
units="$HOME/.config/systemd/user"; changed=false
mkdir -p "$units"
for f in "$RUNNER_DIR"/agent/pirx/systemd/automated-*; do
  b="$(basename "$f")"
  [[ "$b" == automated-report-send.* ]] && continue   # the owner's side
  cmp -s "$f" "$units/$b" || { install -m 644 "$f" "$units/"; changed=true; }
done
if $changed; then systemctl --user daemon-reload; fixed "unit files updated from the runner"; fi
for t in dispatch opencode health report heal retro; do
  if ! systemctl --user is-active -q "automated-$t.timer"; then
    if systemctl --user enable --now "automated-$t.timer" >/dev/null 2>&1; then fixed "timer automated-$t re-enabled"
    else problem "timer:$t" "systemctl --user enable --now automated-$t.timer failed"; fi
  fi
done
for u in $(systemctl --user list-units --failed --no-legend --plain 2>/dev/null | awk '{print $1}' | grep '^automated-'); do
  problem "unit:${u%%.service}" "$(systemctl --user status "$u" --no-pager -n 40 2>&1 | tail -40)"
  systemctl --user reset-failed "$u" && fixed "reset failed unit $u"
done

# 2. Tasks stuck in agent:doing with no live run.
claims="$(bash "$LOCK" claimed | paste -sd, -)"
if gh api "repos/$GH_REPO/issues?labels=agent:doing&state=open&per_page=50" > "$st/heal-doing.json" 2>/dev/null; then
  for n in $(python3 "$RUNNER_DIR/agent/heal.py" stuck "$st/heal-doing.json" "$claims"); do
    systemctl --user is-active -q "automated-claude-$n" && continue
    times="$(gh api "repos/$GH_REPO/issues/$n/comments?per_page=100" --jq '[.[] | select(.body | contains("<!-- automated:healed:stuck -->"))] | length')"
    if [[ "${times:-0}" -ge 2 ]]; then
      gh issue edit "$n" --remove-label agent:doing --add-label agent:blocked >/dev/null
      gh issue comment "$n" --body "🛑 Healer: this task got stuck 3 times with no run working on it (runs time out or crash). Blocked; see the run logs on pirx in \`$RUNTIME/logs\`." >/dev/null
      fixed "#$n stuck 3 times: blocked"
    else
      gh issue edit "$n" --remove-label agent:doing --add-label agent:todo >/dev/null
      gh issue comment "$n" --body "🩹 Healer: no run has worked on this task for over an hour, so it goes back to the queue. <!-- automated:healed:stuck -->" >/dev/null
      fixed "#$n was stuck in doing: back to todo"
    fi
  done
else
  problem "github" "gh api failed: GitHub unreachable or the token expired ($(gh auth status 2>&1 | tail -2 | paste -sd' ' -))"
fi

# 3. Worktrees and the runner (only when no run is active).
if [[ "$held" -eq 0 ]]; then
  git -C "$REPO_ROOT" worktree prune
  for d in "$(dirname "$RUNNER_DIR")"/{review,conflict,heal,retro}-*; do
    [[ -d "$d" ]] || continue
    git -C "$REPO_ROOT" worktree remove --force "$d" >/dev/null 2>&1 && fixed "removed leftover worktree $(basename "$d")"
  done
  if git -C "$REPO_ROOT" fetch -q origin 2>/dev/null; then
    want="$(git -C "$REPO_ROOT" rev-parse "$RUNNER_REF" 2>/dev/null)"
    if [[ -n "$want" && "$want" != "$(git -C "$RUNNER_DIR" rev-parse HEAD)" ]]; then
      git -C "$RUNNER_DIR" checkout -q --detach "$RUNNER_REF" && fixed "runner moved to $RUNNER_REF (${want:0:7})"
    fi
  else
    problem "git" "git fetch from GitHub failed"
  fi
fi

# 4. Disk and logs.
find "$RUNTIME/logs" -type f -mtime +30 -delete 2>/dev/null
disk() { df --output=pcent / | tail -1 | tr -dc 0-9; }
if (( $(disk) > 85 )); then
  before="$(disk)"
  podman system prune -f >/dev/null 2>&1; uv cache prune >/dev/null 2>&1
  find "$RUNTIME/logs" -type f -mtime +7 -delete 2>/dev/null
  fixed "disk at $before%: pruned podman, the uv cache and logs older than 7 days (now $(disk)%)"
  (( $(disk) > 85 )) && problem "disk" "disk use $(disk)% after pruning; biggest: $(du -xsh "$HOME"/* 2>/dev/null | sort -rh | head -5 | paste -sd' ' -)"
fi
(( $(free_mb) < 300 )) && problem "memory" "MemAvailable $(free_mb) MB; top: $(ps -eo user,rss,comm --sort=-rss | head -6 | paste -sd' ' -)"

# 5. Health page.
if [[ ! -f "$st/beat-health" ]] || (( $(date +%s) - $(cat "$st/beat-health") > 5400 )); then
  if AUTOMATED_LOCK_SCRIPT="$LOCK" python3 "$RUNNER_DIR/agent/health.py" >/dev/null 2>"$st/heal-health.err"; then
    fixed "health page refreshed (it was stale)"
  else
    problem "health" "health.py fails: $(tail -5 "$st/heal-health.err")"
  fi
fi

# 6. Root side: the owner's services and the agent firewall (only with the root helper installed).
if sudo -n "$ROOT_HELPER" ping >/dev/null 2>&1; then
  sudo -n "$ROOT_HELPER" status > "$st/heal-root.txt" 2>&1
  while read -r kind unit state; do
    case "$kind" in
      system|owner)
        [[ "$state" =~ ^(active|activating|reloading)$ ]] && continue
        if sudo -n "$ROOT_HELPER" "restart-$kind" "$unit" >/dev/null 2>&1; then fixed "restarted $kind service $unit (was $state)"
        else problem "svc:$unit" "restart of $kind service $unit failed (state $state)"; fi ;;
      firewall)
        [[ "$state" == active ]] && continue
        if sudo -n "$ROOT_HELPER" reload-firewall >/dev/null 2>&1; then fixed "agent firewall reloaded (was $state)"
        else problem "firewall" "agent firewall is $state and the reload failed"; fi ;;
    esac
  done < "$st/heal-root.txt"
fi

# 7. Money: OpenRouter keys close to their limit -> one owner:money issue per key.
check_key() {  # check_key <name> <key>
  [[ -n "$2" ]] || return 0
  local info alert
  info="$(printf 'Authorization: Bearer %s\n' "$2" | curl -s -m 20 -H @- https://openrouter.ai/api/v1/key)" || return 0
  alert="$(python3 "$RUNNER_DIR/agent/heal.py" money "$1" <<<"$info" 2>/dev/null)"
  [[ -n "$alert" ]] || return 0
  if [[ -z "$(gh issue list --label owner:money --state open --search "OpenRouter key '$1'" --json number -q '.[0].number')" ]]; then
    gh issue create --label owner:money --title "💰 $alert" --body "The automation will stop using this key when it runs out.

**What to do:** on openrouter.ai, add credits or raise this key's limit (Settings → API keys → '$1'). Close this issue when done; the healer opens a new one if it runs low again." >/dev/null \
      && fixed "money alert opened: $alert"
  fi
}
check_key opencode "$(cat "$CONF_DIR/openrouter-opencode.key" 2>/dev/null)"
check_key app "$(sed -n 's/^OPENROUTER_API_KEY=//p' "$CONF_DIR/secrets.env" 2>/dev/null | tr -d '"'"'"' ')"

# 8. Red main: one priority:high fix task per project whose CI fails on main; then merge what is ready.
for wf in "$RUNNER_DIR"/.github/workflows/*-ci.yml; do
  p="$(basename "$wf" -ci.yml)"
  [[ -d "$RUNNER_DIR/projects/$p" ]] || continue
  read -r concl sha url <<<"$(gh run list --branch main --workflow "$(basename "$wf")" --status completed --limit 1 \
    --json conclusion,headSha,url -q '.[0] | "\(.conclusion) \(.headSha) \(.url)"' 2>/dev/null)"
  [[ "$concl" == failure ]] || continue
  # Only when main has not moved since: after a fix is merged, its CI is still running and the last finished
  # run is the old failure; a task then would be a duplicate.
  [[ "$sha" == "$(gh api "repos/$GH_REPO/commits/main" --jq .sha 2>/dev/null)" ]] || continue
  [[ -n "$(gh issue list --label red-main --label "project:$p" --state open --json number -q '.[0].number' 2>/dev/null)" ]] && continue
  gh label create red-main --color B60205 --description "CI is red on main; fix first" >/dev/null 2>&1
  subject="$(gh api "repos/$GH_REPO/commits/$sha" --jq '.commit.message' 2>/dev/null | head -1)"
  if gh issue create --title "Fix red main: $p CI fails on ${sha:0:7}" \
      --label agent:todo --label priority:high --label red-main --label "project:$p" --label model:opus \
      --body "**Project:** $p

**Goal:** the project's CI is red on \`main\` since \`${sha:0:7}\` ($subject). Make it green again. Other PRs of this project are held (not merged) until it is.

**Failed run:** $url

**Acceptance criteria**
- Given the fix is merged, when CI runs on \`main\`, then every job of \`$(basename "$wf")\` passes.
- No test is deleted, skipped or weakened to get there; if a test is wrong, say why in the PR.
- The PR explains the cause (which merged change broke it, or which flaky step) in 2-3 lines." >/dev/null; then
    fixed "main is red for $p (${sha:0:7}): fix task opened"
  else
    problem "red-main:$p" "CI is red on main for $p ($url) and the fix issue could not be created"
  fi
done
bash "$RUNNER_DIR/agent/pirx/merge-ready.sh"

# Repeating problems go to a model; new ones and fixes go to the health page.
out="$(python3 "$RUNNER_DIR/agent/heal.py" track "$st/heal-state.json" "${problems[@]}")"
new="$(python3 -c 'import json,sys; print("; ".join(json.loads(sys.argv[1])["new"]))' "$out")"
next="$(python3 -c 'import json,sys; d=json.loads(sys.argv[1])["diagnose"]; print(d[0] if d else "")' "$out")"
[[ ${#fixes[@]} -gt 0 ]] && status_update "Healer fixed: $(printf '%s; ' "${fixes[@]}" | sed 's/; $//')"
[[ -n "$new" ]] && status_update "Healer found a problem: $new"
if [[ -n "$next" ]] && ! systemctl --user is-active -q automated-heal-diagnose; then
  python3 "$RUNNER_DIR/agent/heal.py" mark "$st/heal-state.json" "$next"
  systemd-run --user --quiet --collect --unit automated-heal-diagnose -p RuntimeMaxSec=3600 -p Nice=5 \
    --setenv=HOME="$HOME" /bin/bash "$RUNNER_DIR/agent/pirx/heal-diagnose.sh" "$next"
  log "heal: diagnosis started for $next"
fi
exit 0
