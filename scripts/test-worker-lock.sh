#!/usr/bin/env bash
# Tests for scripts/worker-lock.sh, using throwaway `sleep` processes as fake worker runs.
# Usage: scripts/test-worker-lock.sh
set -uo pipefail

LOCK="$(cd "$(dirname "$0")" && pwd)/worker-lock.sh"
export AUTOMATED_STATE_DIR="$(mktemp -d)"
export AUTOMATED_SLOTS=2
fails=0; pids=()

run() { sleep 300 >/dev/null 2>&1 & pids+=($!); eval "$1=$!"; }   # start a fake run, store its pid in $1
as() { local pid=$1; shift; AUTOMATED_RUN_PID=$pid bash "$LOCK" "$@"; }
check() {  # check <name> <expected exit> <command...>
  local name=$1 want=$2; shift 2
  local out; out=$("$@" 2>&1); local got=$?
  if [[ $got == "$want" ]]; then echo "ok   $name"; else echo "FAIL $name (exit $got, want $want): $out"; fails=$((fails + 1)); fi
}
cleanup() { { kill "${pids[@]}"; wait; } 2>/dev/null; rm -rf "$AUTOMATED_STATE_DIR"; }
trap cleanup EXIT

run a; run b; run c
check "run A takes slot 1"           0 as "$a" acquire
check "run A acquiring again is OK"  0 as "$a" acquire
check "run B takes slot 2"           0 as "$b" acquire
check "run C is BUSY"                1 as "$c" acquire

check "A claims #6"                  0 as "$a" claim 6
check "B cannot claim #6"            1 as "$b" claim 6
check "B claims #12"                 0 as "$b" claim 12
check "claimed lists 6 and 12"       0 test "$(bash "$LOCK" claimed | sort -n | tr '\n' ' ')" == "6 12 "

check "B unclaims #12"               0 as "$b" unclaim 12
check "claimed lists only 6"         0 test "$(bash "$LOCK" claimed | tr '\n' ' ')" == "6 "
as "$b" unclaim 6 >/dev/null
check "B's unclaim leaves A's claim" 0 test "$(bash "$LOCK" claimed | tr '\n' ' ')" == "6 "

check "A releases"                   0 as "$a" release
check "release dropped A's claims"   0 test -z "$(bash "$LOCK" claimed)"
check "C takes the freed slot"       0 as "$c" acquire

kill "$b"; wait "$b" 2>/dev/null
run d
check "D takes dead B's stale slot"  0 as "$d" acquire
as "$d" claim 13 >/dev/null; kill "$d"; wait "$d" 2>/dev/null
check "dead run's claim is not listed" 0 test -z "$(bash "$LOCK" claimed)"
check "C can take a dead run's claim"  0 as "$c" claim 13

run e
echo "$c|$(LC_ALL=C TZ=UTC ps -o lstart= -p "$c" | sed 's/^ *//; s/ *$//')|$(( $(date +%s) - 11 * 3600 ))" > "$AUTOMATED_STATE_DIR/slots/1"
check "entry older than 10h is stale" 0 as "$e" acquire

run f; run g
rm -rf "$AUTOMATED_STATE_DIR"/slots/*
LANG=pl_PL.UTF-8 LC_ALL=pl_PL.UTF-8 TZ=Europe/Warsaw AUTOMATED_RUN_PID=$f bash "$LOCK" acquire >/dev/null
LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8 TZ=America/New_York AUTOMATED_RUN_PID=$g bash "$LOCK" acquire >/dev/null
run h
check "Polish/English locale entries both count as live" 1 \
  env LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8 AUTOMATED_RUN_PID=$h bash "$LOCK" acquire

check "one slot by default"          1 env -u AUTOMATED_SLOTS AUTOMATED_RUN_PID=$h bash "$LOCK" acquire
echo 3 > "$AUTOMATED_STATE_DIR/slots.conf"
check "slots.conf sets the count"    0 env -u AUTOMATED_SLOTS AUTOMATED_RUN_PID=$h bash "$LOCK" acquire

echo; [[ $fails == 0 ]] && echo "all passed" || { echo "$fails failed"; exit 1; }
