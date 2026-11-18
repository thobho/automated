# Artyści dla szkół

[![CI](https://github.com/thobho/automated/actions/workflows/artysci-dla-szkol-ci.yml/badge.svg)](https://github.com/thobho/automated/actions/workflows/artysci-dla-szkol-ci.yml)

A Polish web service that connects **artists** (musicians, actors, educators, workshop leaders)
with **schools and other institutions** that want to invite them. Artists get a generated public
page and appear in a searchable catalog; institutions send inquiries or post notices that artists
answer. UI language: Polish.

Status: M0 foundation (skeleton only, no product features yet).

## Stack

Python 3.13, Django 5.2 LTS, PostgreSQL 17, HTMX (vendored), uv with a lock file
(decision log: D42, D68). HTMX is served from `static/vendor/`, never from a CDN (D11).
Hosting is not decided yet (D91), so configuration is env-only and provider-neutral.

## Quick start (local)

Needs [uv](https://docs.astral.sh/uv/) and a PostgreSQL 17 you can reach.

```bash
cd projects/artysci-dla-szkol
cp .env.example .env          # adjust DATABASE_URL if needed
uv sync
uv run python manage.py migrate
uv run python manage.py runserver
curl http://127.0.0.1:8000/healthz   # {"db": "ok"}
```

## Local environment (Compose)

`compose.yaml` has two profiles; the `Makefile` wraps them (needs `make`, rootless Podman or
Docker with Compose, and uv). Run from this folder.

| Command | What it does |
| --- | --- |
| `make up-lite` | `postgres:17` (shared_buffers 64MB, 256m limit) + Mailpit (64m). Fits a 4 GB machine. |
| `make web` | migrate, then `runserver` natively on `127.0.0.1:18001` (talks to the lite stack) |
| `make worker` | native Procrastinate worker on all queues (see "Background jobs") |
| `make seed` | synthetic data, idempotent: 10 artists, 5 institutions (`@example.invalid`, no passwords), placeholder v1 of each legal document ("PROJEKT – tekst zastępczy…") |
| `make up-full` | lite + MinIO + `web` (gunicorn) and `worker` containers built from `Dockerfile` |
| `make down` | stop and remove all containers (data stays in the state dir) |
| `make test` / `make lint` | pytest with coverage / ruff + format check + migrations check |

Ports (all bound to `127.0.0.1`, chosen to avoid 3000, 5037, 8080, 8384, 22000 on pirx;
override in `.env`, see `.env.example`):

| Service | Port | Variable |
| --- | --- | --- |
| PostgreSQL | 54320 | `POSTGRES_PORT` |
| Mailpit SMTP / web UI | 12025 / 18025 | `MAILPIT_SMTP_PORT` / `MAILPIT_UI_PORT` |
| MinIO API / console (full) | 19000 / 19001 | `MINIO_PORT` / `MINIO_CONSOLE_PORT` |
| web container (full) | 18000 | `WEB_PORT` |
| native `make web` | 18001 | `WEB_NATIVE_PORT` |

State (database, MinIO data) lives outside the repo in `ARTYSCI_STATE_DIR`, default
`~/runtime/artysci-dla-szkol/` (the Makefile sets it; without `make` set it in `.env`).
Without `make`: `podman compose -f compose.yaml --profile lite up -d`.
The `full` web container runs `config.settings.prod`, so over plain HTTP the admin login cookies
are `Secure`-only; `/healthz` and `/readyz` work as usual.

## Dev instance on pirx

Reachable from the home network, plain HTTP, **never public** (D55), synthetic data only (D57).

| What | URL / place |
|---|---|
| Web (gunicorn, 2 workers) | `http://192.168.68.62:8100/` (`/healthz`, `/readyz`) |
| Public media origin | `http://192.168.68.62:8101/` |
| Postgres, Mailpit | `127.0.0.1` only (54320, SMTP 12025, UI 18025); all mail goes to Mailpit |
| Logs (rotated hourly at 5 MB, 5 files) | `~/runtime/artysci-dla-szkol/logs/{web,worker,media}.log` |
| Config (secrets, outside the repo) | `~/.config/artysci-dla-szkol/pirx.env` (template: `deploy/pirx/pirx.env.example`) |

Settings: `config.settings.pirx` = prod without TLS-only parts (no Secure/`__Host-` cookies, no
HTTPS redirect or HSTS; `/static/` served by the app). The AI uses only the dev key with a low
limit (`ANTHROPIC_API_KEY` in `pirx.env`, unset until needed).

systemd user units (`deploy/pirx/ads-*.service`): `ads-lite` (Postgres + Mailpit containers),
`ads-web`, `ads-worker`, `ads-media`, `ads-logrotate.timer`. Restart on failure, enabled at boot
(needs `loginctl enable-linger agent`).

- One-time setup, owner (needs root once: `deploy/pirx/root-setup.sh` via the sudo queue, see
  `scripts/SUDO-QUEUE.md`). Then, in a dedicated clone, e.g. `~/runtime/artysci-dla-szkol/app`:
  `cd projects/artysci-dla-szkol && make install-units-pirx`.
- Update: `make deploy-pirx` (`DEPLOY_REF=main` by default): fetch + fast-forward, `uv sync --frozen`,
  migrate, collectstatic, restart units, smoke test (`/healthz`, `/`, `/readyz`, a static file, a
  `core.ping` job processed by the worker). Run just the smoke test with `make smoke-pirx`.
- Status: `systemctl --user status ads-web ads-worker`; logs: `tail -f ~/runtime/artysci-dla-szkol/logs/web.log`.

## Tests and lint

```bash
uv run pytest --cov             # uses config.settings.test (SQLite in memory unless DATABASE_URL is set)
uv run ruff check . && uv run ruff format --check .
uv run python manage.py makemigrations --check --dry-run --settings=config.settings.test
```

## Settings

| Module | Use | Database |
| --- | --- | --- |
| `config.settings.dev` | `manage.py` default, local work | PostgreSQL (`DATABASE_URL`, default local `artysci`) |
| `config.settings.test` | pytest | `DATABASE_URL`, else SQLite in memory (the only fallback) |
| `config.settings.prod` | `wsgi.py`/`asgi.py` default | `DATABASE_URL`, required |

`prod` fails at startup with `Missing required environment variable <NAME>` when
`DJANGO_SECRET_KEY`, `DJANGO_ALLOWED_HOSTS` or `DATABASE_URL` is missing. All variables are
documented in [`.env.example`](.env.example).

## Security and logging

Threat model, headers, cookie rules and the ASVS checklist: [SECURITY.md](SECURITY.md).

- Every response carries a strict CSP (no inline script; use `nonce="{{ csp_nonce }}"` if one is
  ever unavoidable), Permissions-Policy, nosniff, Referrer-Policy and `frame-ancestors 'none'`.
  Prod adds HSTS, the HTTPS redirect and `__Host-` cookies.
- HTMX POSTs send the CSRF token as `X-CSRFToken` (`templates/base.html`); nothing to add per form.
- Logs are JSON lines on stdout in every environment (`apps/core/logs.py`): request id (also in
  the `X-Request-ID` response header), pseudonymised user, an `access` line per request without
  the query string. Never log e-mails or tokens on purpose; the redaction is a safety net.
- Login throttling for E1: `apps/accounts/throttling.py` (`is_locked`, `register_failure`, `reset`).

## Endpoints

- `/healthz`: liveness, `{"db": "ok"}` with 200, or 503 when the database is unreachable.
- `/readyz`: readiness, `{"db": "ok", "migrations": "ok"}` with 200, or 503 when the database is
  down or migrations are pending.
- `/django-admin/`: Django's built-in admin (staff only). The product's own staff tools will live
  in the `adminpanel` app.
- `/regulamin/`, `/polityka-prywatnosci/`, `/ciasteczka/`: current version of each legal
  document (404 until one is published), linked from the footer.
- `/akceptacja-dokumentow/`: re-acceptance page (logged-in users with pending versions).

## Legal documents (US-8.1)

App `apps/trust`. The texts come from the owner's lawyer (D30); agents only build the mechanism.

- `LegalDocument`: kind (`terms`, `privacy`, `cookies`), version (1, 2, ... per kind), plain-text
  body (rendered escaped with `linebreaks`), `published_at`, `material`. Published versions are
  immutable (model `save()`/`delete()` and queryset `update()`/`delete()` raise
  `DocumentImmutable`); a correction is a new version.
- `services.publish(kind, body, material)`, `current(kind)`, `record_acceptance(user, kinds)`
  (stores the current version of each kind, raises `NoPublishedVersion` if one is missing; US-1.1
  calls it at registration), `pending_acceptances(user)`.
- `LegalAcceptanceMiddleware` redirects a logged-in user who has not accepted the newest
  *material* `terms`/`privacy` version to the acceptance page (HTMX requests get `HX-Redirect`).
  Exempt: the legal pages, the acceptance page, logout, `/healthz`, `/readyz`, static files.
- **Publishing a new version:** `/django-admin/trust/legaldocument/add/` (staff), pick the kind,
  paste the text, tick "Istotna zmiana" if users must accept again. Versions cannot be edited
  or deleted there. Acceptances are read-only at `/django-admin/trust/legalacceptance/`.

## Background jobs

[Procrastinate](https://procrastinate.readthedocs.io) (Django integration) keeps the queue in
PostgreSQL; there is no Redis. Queues: `default`, `ai`, `media`, `email` (`apps/core/jobs.py`).

- Define a task in `apps/<name>/tasks.py` with `@app.task(queue=..., retry=default_retry())`
  (`from procrastinate.contrib.django import app`). Retries back off exponentially
  (5 s, 10 s, 20 s, ... up to 5 attempts).
- Defer with `jobs.enqueue(task, idempotency_key="...", **kwargs)`. While a job with the same key
  is still waiting, deferring again does nothing (returns `None`). Once it started the key is
  free, so tasks must still be safe to run twice.
- Periodic (cron-like) tasks: `@app.periodic(cron="...")` above a task taking `timestamp: int`;
  see `core.cleanup_old_jobs` in `apps/core/tasks.py`.
- `make worker` runs `manage.py worker` (`--once` processes due jobs
  and exits). The Compose `full` profile runs the same command in the `worker` container.
- Recent jobs and failures: `/django-admin/procrastinate/procrastinatejob/` (read-only, staff).
- Demo job `core.ping` writes a `PingRecord` row (used by tests and the smoke check):
  `uv run python manage.py shell -c "from apps.core import jobs, tasks; jobs.enqueue(tasks.ping, token='x')"`.
- Tests use the in-memory connector (`apps/core/testing.py`) on SQLite and run against real
  PostgreSQL when `DATABASE_URL` is set (`test_jobs_postgres.py`).

## AI adapter

`apps/profiles/ai` is the only way to call an LLM (D46, D59, D60, D63):

```python
from apps.profiles import ai

result = ai.complete(
    [{"role": "user", "content": "..."}],
    purpose="profile_draft",  # label stored in AICall
    max_cost_usd="0.01",  # ceiling for this call, at most AI_PER_CALL_CAP_USD
    schema=None,  # JSON Schema -> structured output in result.data
    user_ref=artist.pk,  # sent only as an HMAC pseudonym
)
```

- `AI_CLIENT=fake` (default in dev and tests; deterministic, offline) or `openrouter` (prod
  default). Tests always use the fake client and never reach the network.
- Before anything is sent: kill switch `AI_KILL_SWITCH` (`AIDisabled`), PII scrubbing (e-mails,
  phone numbers, IBANs/account numbers, names in `AI_SCRUB_NAMES` or `scrub_names=`), per-call
  cap (`max_tokens` is limited so the prompt plus the longest reply fit in `max_cost_usd`) and
  the daily cap `AI_DAILY_CAP_USD` (Europe/Warsaw day). A cap breach raises `AICapExceeded`.
- Each call is an `AICall` row (model, provider, tokens, `usage.cost`, purpose, latency,
  status; never prompt or reply text), visible read-only at `/django-admin/profiles/aicall/`.
  The row is created `pending` with the worst-case cost (so concurrent calls see it) and
  settled with the real cost.
- OpenRouter requests: pinned `AI_MODEL`; `provider` with `data_collection: "deny"`,
  `zdr: true`, `only`/`order` = `AI_PROVIDERS` (fallbacks stay inside the list) and
  `max_price` from `AI_PRICE_*_USD_PER_MTOK`. Change the model and its prices together.
- The key comes only from `OPENROUTER_API_KEY` and never appears in logs or errors.
- Check a key by hand: `uv run python manage.py ai_smoke [--key-file path/to/secrets.env]`
  makes one real, tiny call (synthetic prompt, well under $0.001) and prints the `AICall` row.
- Only artists' marketing materials go to AI; never messages, inquiries or contact data.

## File storage

One API (`apps/core/media.py`, `apps/core/uploads.py`), two backends chosen by `STORAGE_BACKEND`:
`filesystem` (default; lean pirx, tests) or `s3` (`django-storages`; MinIO in Compose `full` and CI,
any S3-compatible service later). Two storages: **private** (originals, documents) and **public**
(processed images, video).

- Store: `uploads.store_upload(file, kind="photo"|"video"|"audio"|"pdf", visibility="private"|"public")`.
  It enforces the size limit (photo 15 MB, video 500 MB, audio 50 MB, PDF 20 MB), sniffs the
  content type from magic bytes (the name is ignored), uses a random key and re-encodes images
  without EXIF/GPS. Failures raise `UploadRejected(code, message)`.
- Private files: only `media.signed_url(key, expires=...)` (default `MEDIA_SIGNED_URL_TTL`, 300 s).
  S3: presigned bucket URL. Filesystem: a signed token served by `/media/private/<token>` as an
  attachment with `nosniff` and a sandbox CSP.
- Public files: `media.public_url(key)`, always under `MEDIA_PUBLIC_BASE_URL`, a different origin
  from the app (prod requires it). Filesystem backend: `make media` (or
  `manage.py serve_public_media --port 8101`) serves `MEDIA_PUBLIC_ROOT` there.
- S3: `manage.py ensure_buckets` creates both buckets (public one gets anonymous read); Compose
  `full` runs it at web start-up. Run the suite against MinIO by setting `S3_*` (see
  `.env.example`) and `S3_ENDPOINT_URL`; without it the S3-parametrised tests are skipped.
- Not covered yet: video transcoding and image variants (E2), virus scanning (later).

## Analytics (events and visits)

App `apps/analytics`. No cookies, no PII, no third party (D38, D39).

- **Events:** `services.track("inquiry_sent", actor=user, obj=inquiry, inquiry_id=1)`. Only names
  and properties listed in `apps/analytics/catalog.py` are accepted; anything else raises
  `UnknownEvent` / `DisallowedProperty`. The actor is stored as an HMAC pseudonym, the object as
  type and id. To add an event, extend the catalog, emit it from the feature's service, and move
  it from `PENDING` to `EMITTERS` in `tests/test_events.py`.
- **Visits:** `VisitMiddleware` counts successful HTML `GET` views per path and day in `Visit`
  (one row per day, path and visitor hash, with a view counter). The visitor hash is
  HMAC-SHA256 of IP + user agent under a random per-day salt (`DailySalt`); salts of earlier
  days are deleted on first use of a new day, so old hashes cannot be recomputed. Excluded:
  bots and empty user agents, `/healthz`, `/readyz`, `/static/`, `/django-admin/`.
- Unique visitors for a day and path = `Visit.objects.filter(day=..., path=...).count()`.
  Dashboards come later (E10).

## Decision log

Decisions referenced here: D11 (vendored front-end assets, no CDN), D42 and D68 (stack: Python
3.13, Django 5.2 LTS, PostgreSQL 17, HTMX, uv), D91 (hosting not decided, stay provider-neutral).
Added with T10: no new dependency; D95 (legal documents: when re-acceptance is required).
Added with T06: `django-storages[s3]` (+ boto3) for the S3 backend, `Pillow` for EXIF stripping.
Added with T05: `procrastinate[django]` as the job queue (on PostgreSQL, no extra service).
Added with T04: no new dependency for security (own CSP middleware, own JSON formatter and
cache-based login throttle instead of django-csp, python-json-logger and django-axes); D61
(ASVS 5.0 L1 + chosen L2), D62 (user files on a separate origin).
Added with T07: no new dependency for the AI adapter (OpenRouter over the standard library's
`urllib`); D46, D60 (OpenRouter with ZDR-only routing, pinned model), D59 (PII minimisation),
D63 (daily and per-call cost caps, kill switch). Default model `anthropic/claude-haiku-5.5` on
Google Vertex / Amazon Bedrock ZDR endpoints until model selection in E11.
New dependencies or structural choices need a line in the decision log first
(see [CLAUDE.md](CLAUDE.md)).
