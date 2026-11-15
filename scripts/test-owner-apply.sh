#!/usr/bin/env bash
# Tests for scripts/sudo-request.sh and scripts/owner-apply.sh in a throwaway queue (no real root needed).
# Usage: scripts/test-owner-apply.sh
set -uo pipefail

DIR="$(cd "$(dirname "$0")" && pwd)"
tmp=$(mktemp -d); trap 'rm -rf "$tmp"' EXIT
export SUDO_QUEUE_DIR=$tmp/queue SUDO_STATE_DIR=$tmp/state OWNER_APPLY_TEST=1 AUTOMATED_AGENT_USER=$(id -un)
fails=0
check() { local name=$1 want=$2; shift 2; local out; out=$("$@" 2>&1); local got=$?
  if [[ $got == "$want" ]]; then echo "ok   $name"; else echo "FAIL $name (exit $got, want $want): $out"; fails=$((fails + 1)); fi; }
apply() { OWNER_APPLY_ANSWER=$1 bash "$DIR/owner-apply.sh" "${@:2}"; }

echo 'echo hello > '"$tmp"'/marker' > "$tmp/a.sh"
echo 'exit 3' > "$tmp/fail.sh"

check "bad id refused"            1 bash "$DIR/sudo-request.sh" "Bad Id" "$tmp/a.sh" why
check "missing file refused"      1 bash "$DIR/sudo-request.sh" ok-id "$tmp/none.sh" why
check "request queued"            0 bash "$DIR/sudo-request.sh" t1-marker "$tmp/a.sh" "write a marker"
check "duplicate pending refused" 1 bash "$DIR/sudo-request.sh" t1-marker "$tmp/a.sh" "again"

check "--list runs nothing"       0 apply y --list
check "marker not created by list" 1 test -e "$tmp/marker"
check "skip leaves it pending"    0 apply s
check "still pending after skip"  0 test -f "$SUDO_QUEUE_DIR/pending/t1-marker.sh"
check "reject runs nothing"       0 apply n
check "marker not created by reject" 1 test -e "$tmp/marker"
check "rejected is recorded"      0 test -f "$SUDO_STATE_DIR/rejected/t1-marker.sh"
check "pending emptied"           1 test -e "$SUDO_QUEUE_DIR/pending/t1-marker.sh"
check "rejected id cannot be reused" 1 bash "$DIR/sudo-request.sh" t1-marker "$tmp/a.sh" "again"

check "queue second"              0 bash "$DIR/sudo-request.sh" t2-marker "$tmp/a.sh" "write a marker"
check "approve runs it"           0 apply y
check "marker created"            0 test -f "$tmp/marker"
check "status recorded exit 0"    0 grep -q '^exit=0$' "$SUDO_STATE_DIR/done/t2-marker.status"

check "queue failing script"      0 bash "$DIR/sudo-request.sh" t3-fail "$tmp/fail.sh" "fails"
check "approve runs failing one"  0 apply y
check "failing exit is recorded"  0 grep -q '^exit=3$' "$SUDO_STATE_DIR/done/t3-fail.status"

# The copy that runs is a snapshot: a symlink or a foreign owner is skipped, not run.
mkdir -p "$SUDO_QUEUE_DIR/pending"; ln -s "$tmp/a.sh" "$SUDO_QUEUE_DIR/pending/t4-link.sh"
rm -f "$tmp/marker"
check "symlink request is skipped" 0 apply y
check "symlink was not run"       1 test -e "$tmp/marker"
rm -f "$SUDO_QUEUE_DIR/pending/t4-link.sh"
check "empty queue is fine"       0 apply y

echo; [[ $fails == 0 ]] && echo "all passed" || { echo "$fails failed"; exit 1; }
