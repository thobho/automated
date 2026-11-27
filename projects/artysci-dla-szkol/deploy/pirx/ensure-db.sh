#!/usr/bin/env bash
# Make sure PostgreSQL of the pirx dev instance is reachable on 127.0.0.1:$POSTGRES_PORT.
#
# Handles every way the db has been lost so far: the podman port forwarder died while the
# container stayed "Up" (#177), and the container was stopped or removed (#216).
#
# Two modes:
#   * Default (redeploy.sh, `make deploy-pirx` / `rollback-pirx`, by hand): repair by
#     restarting ads-lite.service. Containers must be started by that unit: rootless podman leaves
#     conmon and the port forwarder in the cgroup of whoever ran `podman compose up`, and systemd
#     kills a oneshot's cgroup when it ends. Started from ads-redeploy.service they died with it
#     (#216: Postgres got a shutdown request the moment the redeploy run finished).
#   * ENSURE_DB_IN_UNIT=1 (ExecStartPost of ads-lite.service): recreate the lite stack in place
#     (`down` + `up -d`; data lives in a bind mount, so nothing is lost). Refuses to start when
#     ARTYSCI_STATE_DIR is unset: compose would mount /postgres, and `down` would already have
#     removed the working container (#216: `Error: statfs /postgres`).
#
# Env: POSTGRES_PORT [54320], ENSURE_DB_WAIT [60 s], COMPOSE [podman compose],
#      SYSTEMCTL [systemctl --user], LITE_UNIT [ads-lite.service], ENSURE_DB_IN_UNIT [unset].
set -uo pipefail

PORT="${POSTGRES_PORT:-54320}"
WAIT="${ENSURE_DB_WAIT:-60}"
COMPOSE="${COMPOSE:-podman compose}"
SYSTEMCTL="${SYSTEMCTL:-systemctl --user}"
LITE_UNIT="${LITE_UNIT:-ads-lite.service}"

say() { echo "ensure-db: $*" >&2; }

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

if [ "${ENSURE_DB_IN_UNIT:-}" != 1 ]; then
    say "nothing listens on 127.0.0.1:$PORT, restarting $LITE_UNIT"
    if $SYSTEMCTL restart "$LITE_UNIT" >&2 && wait_reachable; then
        say "PostgreSQL reachable again on 127.0.0.1:$PORT"
        exit 0
    fi
    say "FAILED, 127.0.0.1:$PORT still unreachable after restarting $LITE_UNIT" \
        "(see: systemctl --user status $LITE_UNIT; podman ps -a)"
    exit 1
fi

if [ -z "${ARTYSCI_STATE_DIR:-}" ]; then
    say "FAILED, ARTYSCI_STATE_DIR is not set (pirx.env not loaded?); not touching the stack"
    exit 1
fi
say "nothing listens on 127.0.0.1:$PORT, recreating the lite stack"
$COMPOSE --profile lite down >&2 || true
$COMPOSE --profile lite up -d >&2 || true
if wait_reachable; then
    say "PostgreSQL reachable again on 127.0.0.1:$PORT"
    exit 0
fi
say "FAILED, 127.0.0.1:$PORT still unreachable after recreating the stack"
exit 1
