> Recovered 2026-11-17: original definitions of tasks T01-T09 (issues #63-#71, all done). Kept for reference; the issues are the source of truth for what was built.

# E0a Foundation (local, pirx): tasks T01–T09 (draft for review)

Project: `artysci-dla-szkol` · Milestone: **M0 Foundation** · Labels on every issue: `agent:todo`, `project:artysci-dla-szkol`, plus the model label below.
Task text is in English (D66); UI texts will be Polish. `T0x` references become issue numbers when the issues are created.

| Task | Title | Model | Depends on | Notes |
|---|---|---|---|---|
| T01 | Project skeleton and agent conventions | opus | – | architecture and conventions for every later task |
| T02 | Local environment: Compose `lite`/`full`, native web and worker | sonnet | T01, #60 | waits for the container runtime on pirx |
| T03 | CI pipeline in GitHub Actions | sonnet | T01 | the main quality gate, including browser tests |
| T04 | Security baseline and structured logging | opus, `area:security` | T01 | OWASP ASVS L1 baseline |
| T05 | Background jobs with Procrastinate | sonnet | T02 | |
| T06 | File storage behind the S3 interface, separate media origin | sonnet | T02 | |
| T07 | AI adapter (OpenRouter) with cost cap | opus, `area:security` | T01 | |
| T08 | Events and visits (analytics foundation) | sonnet | T01 | |
| T09 | Run the dev instance on pirx | sonnet | T02, T05, T06 | |

**Shared Definition of Done (every task):**
- ruff (lint + format) clean; pytest passes with coverage ≥ 85% for new code;
- migrations committed, and `makemigrations --check` is clean;
- no secrets in code, logs or the repo; configuration through environment variables only (portability, D58);
- README/CLAUDE.md updated where behaviour changes;
- CI green; PR with Summary, Verification, Decisions, Action for you;
- approved and merged by the **AI reviewer** (a separate run on a different model than the builder; the owner does not review, D94).

---

## T01: Project skeleton and agent conventions
**Model:** opus · **Depends on:** – · **Story:** US-0.1, US-0.11

**Goal:** a Django project every later task can build on without re-deciding structure.

**Context:** stack decided in D42/D68: Python 3.13, Django 5.2 LTS, PostgreSQL 17, HTMX, uv with a lock file. Code lives only in `projects/artysci-dla-szkol/`. Hosting is not decided (D91), so nothing may depend on one provider.

**In scope**
- `uv init` project with `pyproject.toml` + `uv.lock`; Django 5.2 project `config/`, with settings split into `base`, `dev`, `test` and `prod`, all read from env vars (`django-environ` or plain `os.environ`) with a documented `.env.example`.
- Apps, empty but wired: `accounts`, `artists`, `institutions`, `profiles` (generator), `catalog`, `inquiries`, `notices`, `notifications`, `trust`, `adminpanel`, `analytics`, `quality` (E11). One-line purpose in each `apps.py` docstring.
- Base templates with HTMX (vendored, no CDN, D11), Polish locale `pl` and time zone Europe/Warsaw, `/healthz` (DB check) and `/readyz`.
- `projects/artysci-dla-szkol/CLAUDE.md`: layout, how to run, test and lint, rules for agents (one app per concern, services in `services.py`, no logic in views or templates, tests next to code, no new dependencies without a line in Decisions, UI strings in Polish via gettext).
- `README.md`: what the product is, the local quick start, links to the decision log items.

**Out of scope:** Docker/Compose (T02), CI (T03), real models beyond a custom `User` model (create `accounts.User` now: email login, no username, as Django requires it from the first migration).

**Acceptance criteria**
- Given a fresh clone, when I run `uv sync && uv run python manage.py migrate && uv run python manage.py runserver` with SQLite fallback **only** in `test` settings and Postgres in `dev`, then `/healthz` returns 200 with `{"db": "ok"}`.
- Given `DJANGO_SETTINGS_MODULE=config.settings.prod` without required env vars, when Django starts, then it fails fast with a clear message naming the missing variable.
- The custom `User` model is in place before any other migration.

**Tests:** settings loading (missing var fails), `/healthz` and `/readyz`, the `User` manager (create_user/create_superuser by email).

**Verification:** run the dev server on pirx with Postgres if available (else the test settings), `curl` `/healthz`; paste the output.

---

## T02: Local environment: Compose `lite` and `full`, native web and worker
**Model:** sonnet · **Depends on:** T01, #60 (container runtime on pirx) · **Uses:** pirx · **Story:** US-0.2

**Goal:** one command brings up the dependencies, in a lean mode that fits pirx's 4 GB and a full mode identical to the future server.

**Context:** D87 lean mode. pirx has 4 GB now (about 1.4 GB free), 12 GB after the upgrade. Containers are rootless (Podman or rootless Docker), and the agent is never in the docker group.

**In scope**
- `compose.yaml` with profiles:
  - `lite`: `postgres:17` (shared_buffers 64MB, `mem_limit` 256m) and `mailpit` (64m);
  - `full`: adds `minio` plus `web` and `worker` containers built from a `Dockerfile` (multi-arch, non-root user, `uv sync --frozen`).
- Ports bound to `127.0.0.1` only and chosen so they don't clash with existing pirx services. Document them; the defaults are configurable via `.env`.
- `Makefile` or `justfile` targets: `up-lite`, `up-full`, `down`, `web` (runserver natively with uv), `worker`, `seed`, `test`, `lint`.
- `seed` management command: synthetic data only (D57): 10 artists, 5 institutions, a few offers. No real names, phone numbers or e-mails (use `example.invalid`).
- State and volumes outside the repo: `~/runtime/artysci-dla-szkol/` (workspace rule 4).

**Out of scope:** CI (T03), the job queue (T05), storage code (T06).

**Acceptance criteria**
- Given pirx in lean mode, when I run `make up-lite && make web`, then `/healthz` is 200 and `free -m` shows the stack (postgres + mailpit + web) using under 700 MB.
- Given `make up-full`, then web and worker run in containers and `/healthz` is 200 (verify locally if memory allows, otherwise in T03's CI).
- `make seed` is idempotent (running twice gives the same counts).

**Tests:** seed idempotency; a smoke test that settings pick up the Compose env.

**Verification:** paste `podman ps` (or `docker ps`), memory numbers and the `curl` of `/healthz` from pirx.

---

## T03: CI pipeline in GitHub Actions
**Model:** sonnet · **Depends on:** T01 · **Story:** US-0.3

**Goal:** every PR is checked automatically, including the browser checks that cannot run on pirx.

**Context:** D56 hosted runners; D67 allows `.github/workflows/artysci-dla-szkol-ci.yml` with a path filter. Browser tests run only here (lean pirx).

**In scope**
- A workflow with `paths: projects/artysci-dla-szkol/**` and the workflow file itself. Jobs:
  1. lint (`ruff check`, `ruff format --check`);
  2. test (pytest with a Postgres 17 service, coverage ≥ 85% on changed code, `makemigrations --check`);
  3. security (`pip-audit`, `bandit -ll`, `gitleaks` on the diff);
  4. image (build the `Dockerfile` for amd64 and arm64, no push);
  5. e2e (start the app with Postgres and MinIO services, then Playwright smoke: home, `/healthz`, one page at 375 px; `axe` with zero critical violations; screenshots uploaded as an artifact).
- Caching for uv and Playwright browsers. Total runtime under 10 minutes.
- A status badge in the project README.

**Out of scope:** deployment (E0b), Lighthouse budgets (added with E3).

**Acceptance criteria**
- Given a PR touching only this project, then all 5 jobs run and pass.
- Given a PR touching another project only, then this workflow does not run.
- Given a deliberately failing test pushed on a scratch branch, then the test job fails with a readable message (show it in Verification, then revert).

**Tests:** the workflow itself; Playwright smoke tests in `tests/e2e/`.

**Verification:** links to a green run and to the failing-then-fixed run.

---

## T04: Security baseline and structured logging
**Model:** opus · **Labels:** `area:security` · **Depends on:** T01 · **Story:** NFR step 5 (D61, D62)

**Goal:** secure defaults in place before any feature handles user data.

**Context:** standard OWASP ASVS (current version) level 1, plus chosen level 2 items (D61). User files will be served from a separate origin (D62, done in T06).

**In scope**
- Security headers:
  - a strict CSP (no inline script; nonces for any needed inline; HTMX allowed from self);
  - HSTS in prod;
  - `X-Content-Type-Options`, `Referrer-Policy: strict-origin-when-cross-origin`;
  - `Permissions-Policy` minimal;
  - `frame-ancestors 'none'`.
- Cookie flags: Secure in prod, HttpOnly and SameSite=Lax; CSRF on for all unsafe methods, including HTMX requests (header-based).
- Login throttling scaffold (django-axes or a small rate limiter) for later use by E1.
- Structured JSON logging (request id, user id pseudonymised, no PII, no secrets): one logger config for dev and prod; a request-id middleware; access logs without query strings.
- `SECURITY.md` in the project: threat model in one page (users, assets, trust boundaries) and the ASVS L1 checklist with status per item (done / planned in task X).
- A `check --deploy` clean run in prod settings.

**Out of scope:** authentication flows (E1), file upload checks (T06/E2), admin 2FA (E9).

**Acceptance criteria**
- Given the dev server, when I `curl -I /`, then all the headers above are present with the agreed values.
- Given prod settings with the required env, then `manage.py check --deploy` reports no warnings.
- Given any request, then its log line is valid JSON with a request id, and contains no e-mail, IP in full, or cookie values.

**Tests:** header tests, CSRF on HTMX POST, a log redaction test (feed a fake e-mail and token, assert they are not in the output).

**Verification:** paste `curl -I` from pirx and a sample log line.

---

## T05: Background jobs with Procrastinate
**Model:** sonnet · **Depends on:** T02 · **Story:** US-0.6

**Goal:** a reliable job queue on Postgres for generation, e-mail and media work.

**In scope**
- Procrastinate with the Django integration: one queue per kind (`default`, `ai`, `media`, `email`), retries with backoff, idempotency keys, a periodic task scaffold (cron-like) for reminders and cleanups.
- `make worker` (native) and the `worker` service in Compose `full`.
- A `jobs` admin page (read-only list of recent jobs and failures) for the admin panel later.
- A demo job `ping` that writes a row, used by tests and by T09's smoke check.

**Out of scope:** actual AI/e-mail/media jobs (their own tasks).

**Acceptance criteria**
- Given the worker running, when `ping` is deferred, then it runs within 5 s and its row exists.
- Given a job that fails twice and then succeeds, then it is retried with backoff and ends `succeeded`.
- Given the same idempotency key deferred twice, then the job runs once.

**Tests:** the three criteria, using Procrastinate's test connector or a real Postgres in CI.

**Verification:** on pirx, defer `ping` and show the worker log line.

---

## T06: File storage behind the S3 interface, separate media origin
**Model:** sonnet · **Depends on:** T02 · **Story:** US-0.7 (D58, D62)

**Goal:** one storage API for uploads that works with a local disk now and any S3-compatible service later.

**In scope**
- `django-storages` S3 backend for `private` (originals, documents) and `public` (processed images and video); a filesystem backend behind the same interface for lean pirx. Choose by env var.
- Private files only through short-lived signed URLs; public files under a **separate origin** (`MEDIA_PUBLIC_BASE_URL`, e.g. `http://pirx:8101` locally) so user content never runs on the app origin.
- Upload helper: size limits per type (D8: photos 15 MB, video 500 MB, audio 50 MB, PDF 20 MB), content-type sniffing by magic bytes (not the extension), random object keys, EXIF stripping for images.
- MinIO in Compose `full` and in CI (T03) with a bucket bootstrap.

**Out of scope:** video transcoding and image variants (E2), virus scanning (later, noted in SECURITY.md).

**Acceptance criteria**
- Given the filesystem backend, when a JPEG with GPS EXIF is uploaded, then the stored file has no EXIF and the key is random.
- Given a file renamed `.jpg` that is really HTML, then the upload is rejected.
- Given a private file, when its signed URL expires, then access is denied.
- The same test suite passes against MinIO in CI.

**Tests:** the criteria, parametrised over both backends.

**Verification:** an upload on pirx with the filesystem backend; a link to the CI run with MinIO.

---

## T07: AI adapter (OpenRouter) with cost cap
**Model:** opus · **Labels:** `area:security` · **Depends on:** T01 · **Story:** US-0.10 (D46, D59, D60, D63)

**Goal:** one provider-independent way to call LLMs, safe for personal data and capped in cost.

**In scope**
- `profiles/ai/` adapter interface `complete(messages, *, schema=None, purpose, max_cost_usd)` with two implementations: `OpenRouterClient` and `FakeClient` (deterministic, used in tests and CI).
- Every OpenRouter request sends:
  - `provider: {data_collection: "deny", zdr: true}`;
  - `allow_fallbacks` limited to an allowlist of providers from config;
  - the model pinned in config;
  - a `user` field that is a pseudonymous id.
- Usage and cost read from `usage.cost` and stored per call (model, tokens, cost, purpose, latency) in a `AICall` model.
- **Cost cap (D63):** a global daily cap (env `AI_DAILY_CAP_USD`) and a per-call cap; a kill switch (env or admin flag). Exceeding either raises a typed error, and nothing is sent.
- PII minimisation (D59): a scrubber that removes e-mails, phone numbers, IBANs and names in a configured list before sending, with tests. Only artists' marketing materials ever go to AI.
- The key comes only from the env (`OPENROUTER_API_KEY`, a dev key with a low limit), never logged.

**Out of scope:** the profile generator itself (E2), model selection (E11).

**Acceptance criteria**
- Given the daily cap reached, when `complete()` is called, then no HTTP request is made and `AICapExceeded` is raised.
- Given a prompt with an e-mail and a phone number, then the request body sent (captured in a test) contains neither.
- Given one real call with the dev key (in Verification only, never in CI), then `AICall.cost_usd` matches the `usage.cost` in the response.

**Tests:** cap, kill switch, scrubber, request shape (provider flags present), FakeClient determinism.

**Verification:** one real call on pirx with a cheap model and the dev key; paste the stored `AICall` row (no prompt text).

**Action for the owner:** a separate OpenRouter **dev key for the app** with a low limit, placed in the agent's `~/.config/automated/secrets.env` as `OPENROUTER_API_KEY`.

---

## T08: Events and visits (analytics foundation)
**Model:** sonnet · **Depends on:** T01 · **Story:** US-10.1, US-10.2, US-10.6 (D38, D39)

**Goal:** record the business events the pilot will be judged on, from day one, without cookies or PII.

**In scope**
- `analytics.Event` model (name, actor pseudonymous id, object type and id, properties JSON, created_at) and `track(name, **props)` with a **closed catalog** of event names and allowed properties (a Python registry; unknown names or properties raise in tests).
- Initial catalog: `artist_registered`, `profile_generated`, `profile_published`, `inquiry_sent`, `inquiry_answered`, `offer_accepted`, `performance_confirmed`, `notice_published`, `notice_applied`.
- Cookie-free visits: a middleware that counts page views per path and day with a daily-rotating salted hash of IP and user agent (salt not stored after the day), excluding bots and health checks.
- Contract tests: each catalog entry has a test that the code path emits it (scaffold now, filled as features land).

**Out of scope:** dashboards (E10), surveys.

**Acceptance criteria**
- Given `track("inquiry_sent", email=...)`, then it fails because `email` is not an allowed property.
- Given two requests from the same client on the same day, then one unique visitor is counted; on the next day the hash differs.
- No cookie is set by analytics.

**Tests:** the criteria plus catalog validation.

**Verification:** a page view on pirx and the resulting rows (hash shortened).

---

## T09: Run the dev instance on pirx
**Model:** sonnet · **Depends on:** T02, T05, T06 · **Uses:** pirx · **Story:** US-0.12 (D55, D57)

**Goal:** a dev instance the owner can open from the home network, which survives reboots and that agents can restart.

**In scope**
- systemd **user** units for the `agent` user: `ads-web` (gunicorn, 2 workers), `ads-worker`, plus the `lite` containers (`podman generate systemd` or quadlets). Restart on failure, start at boot (lingering is on).
- Bind web on the LAN interface port (e.g. `0.0.0.0:8100`) and public media on `8101`; Postgres and Mailpit stay on 127.0.0.1. Document the URLs.
- `make deploy-pirx`: pull the branch or main, `uv sync --frozen`, migrate, collectstatic, restart the units, smoke test (`/healthz`, `ping` job).
- Data: synthetic only (D57); e-mails go only to Mailpit; the AI uses only the dev key with a low limit.
- Logs to `~/runtime/artysci-dla-szkol/logs` with rotation.

**Out of scope:** public exposure (never on pirx, D55), TLS.

**Acceptance criteria**
- Given a pirx reboot, then web and worker come back without manual steps and `/healthz` is 200 from another LAN device.
- Given `make deploy-pirx`, then it finishes in under 3 minutes and ends with a green smoke test.

**Verification:** `systemctl --user status` output, `curl` from the Mac to `http://192.168.68.62:8100/healthz`.

**Note:** the agent's network guard blocks outgoing LAN traffic. Serving the LAN needs replies allowed (a `ct state established,related accept` rule). That's an owner change to `setup-agent-user.sh`, which Claude will prepare before this task starts.
