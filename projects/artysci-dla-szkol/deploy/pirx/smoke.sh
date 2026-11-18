#!/usr/bin/env bash
# Smoke test of the pirx dev instance. Run from the project folder with pirx.env loaded
# (`make smoke-pirx` does that). Waits up to 60 s for the web unit, then checks the pages and
# the background job path. Exits non-zero on the first failure.
set -euo pipefail

WEB="${SMOKE_WEB_URL:-http://127.0.0.1:8100}"

fail() { echo "SMOKE FAIL: $*" >&2; exit 1; }

code=000
for _ in $(seq 1 60); do
    code=$(curl -s -o /dev/null -w '%{http_code}' "$WEB/healthz" || true)
    [ "$code" = 200 ] && break
    sleep 1
done
[ "$code" = 200 ] || fail "/healthz returned $code after 60s"
echo "ok /healthz 200"

for path in / /readyz; do
    code=$(curl -s -o /dev/null -w '%{http_code}' "$WEB$path")
    [ "$code" = 200 ] || fail "$path returned $code"
    echo "ok $path 200"
done

for path in /regulamin/ /polityka-prywatnosci/ /ciasteczka/; do
    body=$(curl -s -w '\n%{http_code}' "$WEB$path")
    [ "${body##*$'\n'}" = 200 ] || fail "$path returned ${body##*$'\n'} (did seed run?)"
    grep -q "PROJEKT" <<<"$body" || fail "$path has no placeholder text"
    echo "ok $path 200"
done

code=$(curl -s -o /dev/null -w '%{http_code}' "$WEB/static/vendor/htmx/htmx.min.js" || true)
[ "$code" = 200 ] || fail "static file returned $code (did collectstatic run?)"
echo "ok static 200"

uv run --frozen --no-dev python manage.py shell -c "exec(open('deploy/pirx/smoke_ping.py').read())"
echo "SMOKE OK"
