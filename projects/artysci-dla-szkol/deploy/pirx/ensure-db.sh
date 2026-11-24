#!/usr/bin/env bash
# Make sure PostgreSQL of the pirx dev instance is reachable on 127.0.0.1:$POSTGRES_PORT.
#
# Why: rootless podman publishes the port through a forwarder process. If that process dies
# (seen on 2026-11-23: container "Up", `podman ps` shows 127.0.0.1:54320->5432, but nothing
# listens), `podman compose up -d` is a no-op because the containers are running, so the app
# gets "connection refused" until the stack is recreated. This script detects that and
# recreates the lite stack (data lives in a bind mount, so nothing is lost).
#
# Run by ads-lite.service (ExecStartPost), `make deploy-pirx` / `rollback-pirx` and
# redeploy.sh (every timer run, so a dead forwarder heals within 10 minutes).
# Env: POSTGRES_PORT [54320], COMPOSE [podman compose], ENSURE_DB_WAIT [60 s].
set -uo pipefail

PORT="${POSTGRES_PORT:-54320}"
COMPOSE="${COMPOSE:-podman compose}"
WAIT="${ENSURE_DB_WAIT:-60}"

reachable() { (exec 3<>"/dev/tcp/127.0.0.1/$PORT") 2>/dev/null; }

wait_reachable() {
    local i
    for ((i = 0; i < WAIT; i++)); do
        reachable && return 0
        sleep 1
    done
    return 1
}

if wait_reachable; then
    exit 0
fi

echo "ensure-db: nothing listens on 127.0.0.1:$PORT, recreating the lite stack" >&2
$COMPOSE --profile lite down >&2 || true
$COMPOSE --profile lite up -d >&2 || true
if wait_reachable; then
    echo "ensure-db: PostgreSQL reachable again on 127.0.0.1:$PORT" >&2
    exit 0
fi
echo "ensure-db: FAILED, 127.0.0.1:$PORT still unreachable after recreating the stack" >&2
exit 1
