#!/usr/bin/env bash
# Bring the installed systemd user units in line with deploy/pirx/ads-*.{service,timer}.
# Called by `make deploy-pirx` (after the checkout moved), so a merged unit change reaches pirx by
# itself. Idempotent: units whose rendered content is unchanged are neither rewritten nor restarted.
#
# Env (defaults in brackets; overridden by tests): PROJECT [checkout root], UV_BIN [command -v uv],
# PIRX_UNIT_DIR [~/.config/systemd/user], SYSTEMCTL [systemctl --user].
set -euo pipefail

PROJECT="${PROJECT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
UV_BIN="${UV_BIN:-$(command -v uv || true)}"
UNIT_DIR="${PIRX_UNIT_DIR:-$HOME/.config/systemd/user}"
SYSTEMCTL="${SYSTEMCTL:-systemctl --user}"

[ -n "$UV_BIN" ] || { echo "refresh-units: uv not found in PATH" >&2; exit 1; }
mkdir -p "$UNIT_DIR"

changed=()
for f in "$PROJECT"/deploy/pirx/ads-*.service "$PROJECT"/deploy/pirx/ads-*.timer; do
    [ -e "$f" ] || continue
    name="$(basename "$f")"
    rendered="$(sed -e "s|@PROJECT@|$PROJECT|g" -e "s|@UV@|$UV_BIN|g" "$f")"
    if [ ! -f "$UNIT_DIR/$name" ] || [ "$rendered" != "$(cat "$UNIT_DIR/$name")" ]; then
        printf '%s\n' "$rendered" >"$UNIT_DIR/$name"
        changed+=("$name")
    fi
done

if [ "${#changed[@]}" -eq 0 ]; then
    echo "refresh-units: unit files unchanged"
    exit 0
fi

echo "refresh-units: updated ${changed[*]}"
$SYSTEMCTL daemon-reload
for name in "${changed[@]}"; do
    case "$name" in
        *.timer)
            # enable is a no-op for an enabled timer; restart picks up a changed schedule
            $SYSTEMCTL enable "$name"
            $SYSTEMCTL restart "$name"
            ;;
        ads-lite.service)
            $SYSTEMCTL restart "$name"
            ;;
        # ads-web/worker/media are restarted by deploy-pirx right after; the oneshot services
        # (redeploy, logrotate) are picked up by their next run. Restarting redeploy would kill us.
    esac
done
