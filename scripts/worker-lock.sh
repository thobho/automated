#!/usr/bin/env bash
# Slots and task claims for the automated worker, so runs never overlap on one task.
#
#   worker-lock.sh acquire        take a free slot for this run (exit 1 = BUSY: every slot is taken)
#   worker-lock.sh release        free this run's slot and all its claims
#   worker-lock.sh claim <n>      claim issue <n> for this run (exit 1 = a live run already has it)
#   worker-lock.sh unclaim <n>    drop this run's claim on issue <n>
#   worker-lock.sh claimed        print the issue numbers claimed by live runs, one per line
#   worker-lock.sh status         show slots and claims
#
# A holder is the Claude run process that owns the calling shell (nearest ancestor). Entries free themselves
# when that process dies. State lives outside the repo: ~/.config/automated/state (AUTOMATED_STATE_DIR).
# Number of slots: AUTOMATED_SLOTS, else the number in $STATE/slots.conf, else 1.
set -uo pipefail

STATE="${AUTOMATED_STATE_DIR:-$HOME/.config/automated/state}"
SLOTS="${AUTOMATED_SLOTS:-$(cat "$STATE/slots.conf" 2>/dev/null || echo 1)}"
MAX_AGE_H="${AUTOMATED_LOCK_MAX_AGE_H:-10}"   # an entry older than this is treated as stale (hung run)
mkdir -p "$STATE/slots" "$STATE/claims"

run_pid() {  # nearest ancestor that is a Claude Code run process
  local p=$$ cmd
  while [[ -n "$p" && "$p" -gt 1 ]]; do
    cmd=$(ps -o command= -p "$p" 2>/dev/null || true)
    if [[ "$cmd" == *claude* && "$cmd" == *--output-format* ]]; then echo "$p"; return 0; fi
    p=$(ps -o ppid= -p "$p" 2>/dev/null | tr -d ' ')
  done
  return 1
}
# Fixed locale and zone, so every shell writes and compares the same text.
started() { LC_ALL=C TZ=UTC ps -o lstart= -p "$1" 2>/dev/null | sed 's/^ *//; s/ *$//'; }
entry_pid() { cut -d'|' -f1 "$1" 2>/dev/null; }
entry_live() {  # $1 = entry file: its process is still the same one, and it is not older than MAX_AGE_H
  [[ -f "$1" ]] || return 1
  local pid start epoch
  IFS='|' read -r pid start epoch < "$1"
  [[ -n "$pid" && "$(started "$pid")" == "$start" ]] || return 1
  (( $(date +%s) - ${epoch:-0} < MAX_AGE_H * 3600 ))
}
write_entry() { echo "$2|$(started "$2")|$(date +%s)" > "$1"; }

me="${AUTOMATED_RUN_PID:-$(run_pid || true)}"
if [[ -z "$me" && "${1:-}" != "status" && "${1:-}" != "claimed" ]]; then
  echo "WARNING: could not identify this run's process; continuing without a lock" >&2; exit 0
fi

mutex="$STATE/.mutex"
lock() { for _ in $(seq 1 40); do mkdir "$mutex" 2>/dev/null && { trap 'rmdir "$mutex" 2>/dev/null' EXIT; return 0; }; sleep 0.25; done; return 0; }

case "${1:-}" in
  acquire)
    lock
    for i in $(seq 1 "$SLOTS"); do   # already hold one?
      f="$STATE/slots/$i"
      if [[ -f "$f" && "$(entry_pid "$f")" == "$me" ]] && entry_live "$f"; then echo "OK: slot $i"; exit 0; fi
    done
    for i in $(seq 1 "$SLOTS"); do
      f="$STATE/slots/$i"
      if ! entry_live "$f"; then write_entry "$f" "$me"; echo "OK: slot $i"; exit 0; fi
    done
    echo "BUSY: all $SLOTS worker slot(s) are taken by live runs. End this run now."; exit 1 ;;
  release)
    lock
    for f in "$STATE"/slots/* "$STATE"/claims/*; do [[ -f "$f" && "$(entry_pid "$f")" == "$me" ]] && rm -f "$f"; done
    echo "released" ;;
  claim)
    n="${2:?issue number}"; lock; f="$STATE/claims/$n"
    if entry_live "$f" && [[ "$(entry_pid "$f")" != "$me" ]]; then echo "CLAIMED: issue #$n is being worked on by pid $(entry_pid "$f")"; exit 1; fi
    write_entry "$f" "$me"; echo "OK: claimed #$n" ;;
  unclaim)
    n="${2:?issue number}"; lock; f="$STATE/claims/$n"
    [[ -f "$f" && "$(entry_pid "$f")" == "$me" ]] && rm -f "$f"; echo "unclaimed #$n" ;;
  claimed)
    for f in "$STATE"/claims/*; do [[ -f "$f" ]] && entry_live "$f" && basename "$f"; done; exit 0 ;;
  status)
    for i in $(seq 1 "$SLOTS"); do
      f="$STATE/slots/$i"
      if entry_live "$f"; then echo "slot $i: held by pid $(entry_pid "$f")"; else echo "slot $i: free"; fi
    done
    for f in "$STATE"/claims/*; do
      [[ -f "$f" ]] || continue
      if entry_live "$f"; then echo "claim #$(basename "$f"): pid $(entry_pid "$f")"; else echo "claim #$(basename "$f"): stale"; fi
    done ;;
  *) echo "usage: $0 acquire|release|claim <n>|unclaim <n>|claimed|status" >&2; exit 64 ;;
esac
