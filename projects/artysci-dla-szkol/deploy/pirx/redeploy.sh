#!/usr/bin/env bash
# Redeploy the pirx dev instance when origin/main moved. Run by ads-redeploy.timer (every 10 min)
# from the dedicated deployment checkout; safe to run by hand (`systemctl --user start
# ads-redeploy.service`). Never two at once (flock). State and log live in ARTYSCI_STATE_DIR.
#
#   deployed.commit  last commit that deployed with a green smoke test
#   failed.commit    "<sha> <count>" consecutive failed deploys of one commit (cap: 3)
#   logs/redeploy.log
#
# Test hooks (env): MAKE, ARTYSCI_STATE_DIR, REDEPLOY_BRANCH, MAX_ATTEMPTS.
set -uo pipefail

PROJECT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
STATE_DIR="${ARTYSCI_STATE_DIR:-$HOME/runtime/artysci-dla-szkol}"
BRANCH="${REDEPLOY_BRANCH:-main}"
MAX_ATTEMPTS="${MAX_ATTEMPTS:-3}"
MAKE="${MAKE:-make}"

mkdir -p "$STATE_DIR/logs"
LOG="$STATE_DIR/logs/redeploy.log"
DEPLOYED="$STATE_DIR/deployed.commit"
FAILED="$STATE_DIR/failed.commit"

log() { printf '%s redeploy: %s\n' "$(date -Is)" "$*" >>"$LOG"; }

exec 9>"$STATE_DIR/redeploy.lock"
flock -n 9 || exit 0   # another deploy is running

cd "$PROJECT" || exit 1

if ! git fetch -q origin >>"$LOG" 2>&1; then
    log "git fetch failed, will try again next run"
    exit 1
fi
if [ -n "$(git status --porcelain --untracked-files=no)" ]; then
    log "deployment checkout has local changes, not deploying (clean it: git status in $PROJECT)"
    exit 1
fi
target="$(git rev-parse "origin/$BRANCH")" || exit 1
good="$(cat "$DEPLOYED" 2>/dev/null || true)"

[ "$target" = "$good" ] && exit 0

failed_sha="" failed_count=0
[ -f "$FAILED" ] && read -r failed_sha failed_count <"$FAILED"
if [ "$failed_sha" = "$target" ] && [ "${failed_count:-0}" -ge "$MAX_ATTEMPTS" ]; then
    exit 0   # already gave up on this commit (logged when the cap was hit)
fi

log "deploying ${target:0:12} (last good: ${good:0:12})"
if $MAKE deploy-pirx DEPLOY_REF="$BRANCH" >>"$LOG" 2>&1 && $MAKE smoke-pirx >>"$LOG" 2>&1; then
    deployed="$(git rev-parse HEAD)"   # what is really checked out and smoke-tested
    echo "$deployed" >"$DEPLOYED"
    rm -f "$FAILED"
    log "deployed ${deployed:0:12}, smoke test green"
    exit 0
fi

# Failed: count it, then put the last good commit back so the instance is never left broken.
[ "$failed_sha" = "$target" ] || failed_count=0
failed_count=$((failed_count + 1))
echo "$target $failed_count" >"$FAILED"
log "FAILED deploy of ${target:0:12} (attempt $failed_count of $MAX_ATTEMPTS), see output above"
if [ "$failed_count" -ge "$MAX_ATTEMPTS" ]; then
    log "GIVING UP on ${target:0:12} after $MAX_ATTEMPTS failures; waiting for a newer commit"
fi

if [ -n "$good" ]; then
    if $MAKE rollback-pirx ROLLBACK_REF="$good" >>"$LOG" 2>&1 && $MAKE smoke-pirx >>"$LOG" 2>&1; then
        log "rolled back to ${good:0:12}, smoke test green"
    else
        log "ROLLBACK to ${good:0:12} FAILED, instance needs the owner"
    fi
else
    log "no last good commit recorded, nothing to roll back to"
fi
exit 1
