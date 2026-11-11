# Shared settings and helpers for the agent runners on pirx. Source it; do not run it.
# Machine settings live outside the repo in ~/.config/automated/pirx.env (see setup.sh).

CONF_DIR="$HOME/.config/automated"
_ref_override="${AUTOMATED_RUNNER_REF:-}"
[[ -f "$CONF_DIR/pirx.env" ]] && source "$CONF_DIR/pirx.env"
[[ -n "$_ref_override" ]] && AUTOMATED_RUNNER_REF="$_ref_override"

export PATH="$HOME/.local/bin:$HOME/.opencode/bin:$HOME/.local/node/bin:$PATH"   # systemd units get no login PATH
REPO_ROOT="${AUTOMATED_REPO_ROOT:-$HOME/Projects/automated}"        # shared checkout: never switch its branch
RUNNER_DIR="${AUTOMATED_RUNNER_DIR:-$HOME/Projects/automated-work/runner}"  # this tooling, pinned to RUNNER_REF
RUNNER_REF="${AUTOMATED_RUNNER_REF:-origin/main}"
RUNTIME="${AUTOMATED_RUNTIME:-$HOME/runtime/automated}"             # logs and state, outside ~/Projects
LOCK="$CONF_DIR/worker-lock.sh"
PIRX_MIN_FREE_MB="${PIRX_MIN_FREE_MB:-1000}"
GH_REPO="${AUTOMATED_GH_REPO:-thobho/automated}"
export GH_REPO
mkdir -p "$RUNTIME/logs" "$RUNTIME/state"

log() { echo "[$(date -u +%FT%TZ)] $*" | tee -a "$RUNTIME/logs/runner.log" >&2; }

free_mb() { awk '/^MemAvailable:/ {print int($2/1024)}' /proc/meminfo; }

# Memory gate: pirx also runs Hermes, the gallery and other services, so a run starts only with room to spare.
memory_ok() {
  local free; free="$(free_mb)"
  if (( free < PIRX_MIN_FREE_MB )); then
    log "memory gate: ${free} MB available, need ${PIRX_MIN_FREE_MB} MB"; return 1
  fi
}

json_get() {  # json_get <file> <key>  -> value of a top-level key ("" if missing)
  python3 -c 'import json,sys; v=json.load(open(sys.argv[1])).get(sys.argv[2]); print("" if v is None else (str(v).lower() if isinstance(v,bool) else v))' "$1" "$2"
}

# Fail markers: hidden comments the runners leave on an issue, counted for escalation.
fail_count() {  # fail_count <issue> <executor-or-model>
  gh api "repos/$GH_REPO/issues/$1/comments?per_page=100" --jq "[.[] | select(.body | contains(\"<!-- automated:fail:$2 -->\"))] | length"
}

beat() {  # beat <component>: record that a component ran just now (read by agent/health.py)
  date +%s > "$RUNTIME/state/beat-$1"
}

status_update() {  # status_update "<note>": record the event and refresh the health page (pinned GitHub issue)
  echo "$(date -u +%FT%TZ)|$1" >> "$RUNTIME/state/events.log"
  tail -500 "$RUNTIME/state/events.log" > "$RUNTIME/state/events.tmp" && mv "$RUNTIME/state/events.tmp" "$RUNTIME/state/events.log"
  AUTOMATED_LOCK_SCRIPT="$LOCK" python3 "$RUNNER_DIR/agent/health.py" >/dev/null 2>>"$RUNTIME/logs/runner.log" || log "health page update failed"
}
