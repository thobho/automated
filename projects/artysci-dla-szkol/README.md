# Artyści dla szkół

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
| `make seed` | synthetic data, idempotent: 10 artists, 5 institutions (`@example.invalid`, no passwords) |
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

## Endpoints

- `/healthz`: liveness, `{"db": "ok"}` with 200, or 503 when the database is unreachable.
- `/readyz`: readiness, `{"db": "ok", "migrations": "ok"}` with 200, or 503 when the database is
  down or migrations are pending.
- `/django-admin/`: Django's built-in admin (staff only). The product's own staff tools will live
  in the `adminpanel` app.

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

## Decision log

Decisions referenced here: D11 (vendored front-end assets, no CDN), D42 and D68 (stack: Python
3.13, Django 5.2 LTS, PostgreSQL 17, HTMX, uv), D91 (hosting not decided, stay provider-neutral).
Added with T06: `django-storages[s3]` (+ boto3) for the S3 backend, `Pillow` for EXIF stripping.
Added with T05: `procrastinate[django]` as the job queue (on PostgreSQL, no extra service).
New dependencies or structural choices need a line in the decision log first
(see [CLAUDE.md](CLAUDE.md)).
