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
| `make seed` | synthetic data, idempotent: 10 artists, 5 institutions with their roles (`@example.invalid`, no passwords), 6 synthetic RSPO entries, placeholder v1 of each legal document ("PROJEKT – tekst zastępczy…") |
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
  Deploy also runs `manage.py seed` (synthetic users, placeholder legal documents); the smoke test
  checks `/regulamin/`, `/polityka-prywatnosci/` and `/ciasteczka/` (200, version, "PROJEKT" text).
- Automatic redeploy: `ads-redeploy.timer` (user timer, every 10 min, installed by
  `make install-units-pirx`) runs `deploy/pirx/redeploy.sh` from the deployment checkout. It takes a
  `flock`, fetches, and if `origin/main` differs from the commit in
  `~/runtime/artysci-dla-szkol/deployed.commit` (last commit with a green smoke test) it runs
  `make deploy-pirx` + `make smoke-pirx`, then records the commit. Nothing new = silent exit. On
  failure it rolls back (`make rollback-pirx`: last good commit, restart) and keeps the state file;
  one commit is tried at most 3 times (`failed.commit` holds the count; a newer commit resets it).
  Migrations are not reversed, so keep them backward compatible.
  - Log: `~/runtime/artysci-dla-szkol/logs/redeploy.log` (rotated with the others).
  - Pause (owner): `systemctl --user stop ads-redeploy.timer`; resume with `start`.
  - Force a deploy now: `systemctl --user start ads-redeploy.service` (or, to retry a commit that
    hit the cap, `rm ~/runtime/artysci-dla-szkol/failed.commit` first).
  - Check: `systemctl --user list-timers 'ads-*'`.
- Status: `systemctl --user status ads-web ads-worker`; logs: `tail -f ~/runtime/artysci-dla-szkol/logs/web.log`.
- Restart: `systemctl --user restart ads-web ads-worker` (both are back within seconds).
- Working URLs on pirx itself: `http://127.0.0.1:8100/healthz` (`{"db": "ok"}`), `/readyz`,
  `/regulamin/`, `/polityka-prywatnosci/`, `/ciasteczka/`, `/logowanie/` (login e-mails land in
  Mailpit: `http://127.0.0.1:18025`). From the home network: `http://192.168.68.62:8100/`.
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
Only the session and CSRF cookies are ever set; a test enforces it (`uv run pytest -k cookie`,
list and lifetimes: [SECURITY.md#cookies-us-88-d32](SECURITY.md#cookies-us-88-d32)).

- Every response carries a strict CSP (no inline script; use `nonce="{{ csp_nonce }}"` if one is
  ever unavoidable), Permissions-Policy, nosniff, Referrer-Policy and `frame-ancestors 'none'`.
  Prod adds HSTS, the HTTPS redirect and `__Host-` cookies.
- HTMX POSTs send the CSRF token as `X-CSRFToken` (`templates/base.html`); nothing to add per form.
- Logs are JSON lines on stdout in every environment (`apps/core/logs.py`): request id (also in
  the `X-Request-ID` response header), pseudonymised user, an `access` line per request without
  the query string. Never log e-mails or tokens on purpose; the redaction is a safety net.
- Login limits: `apps/accounts/throttling.py` (`exceeded`, `hit`, `reset`; rows in PostgreSQL).

## Endpoints

- `/healthz`: liveness, `{"db": "ok"}` with 200, or 503 when the database is unreachable.
- `/readyz`: readiness, `{"db": "ok", "migrations": "ok"}` with 200, or 503 when the database is
  down or migrations are pending.
- `/django-admin/`: Django's built-in admin (staff only). The product's own staff tools will live
  in the `adminpanel` app.
- `/regulamin/`, `/polityka-prywatnosci/`, `/ciasteczka/`: current version of each legal
  document (404 until one is published), linked from the footer.
- `/akceptacja-dokumentow/`: re-acceptance page (logged-in users with pending versions).
- `/logowanie/` (e-mail), `/logowanie/kod/` (POST code), `/logowanie/link/?t=...` (GET button,
  POST logs in), `/wyloguj/` (POST only).
- `/konto/` (account settings), `/konto/email/` (POST new address), `/konto/email/kod/` (POST
  code), `/konto/email/link/?t=...` (GET button, POST confirms), `/konto/dane/` and
  `/konto/usun/` (placeholders until US-8.6); all login required.
- `/rejestracja/artysta/` (artist registration), `/artysta/kreator/` (profile wizard overview),
  `/artysta/profil/dane/` (step 1, basics), `/artysta/profil/oferty/` (offers; `nowa/`,
  `<id>/edycja/`, `<id>/usun/`, `<id>/przesun/` POST), `/artysta/profil/oswiadczenia/`
  (statements, GET + POST), `/materialy/` (placeholder); artists only, login required.
- `/rejestracja/placowka/` (institution registration), `/rejestracja/placowka/rspo/` (HTMX RSPO
  suggestions, GET, anonymous), `/placowka/` (institution start, a placeholder; login required).

## Login (US-1.3)

No passwords (D1). App `apps/accounts`, logic in `services.py`:

- `request_login(email, client_ip, link_base=...)`: checks the send limits (5/h per address,
  20/h per IP), then queues `accounts.send_login_email` on the `email` queue for an active user.
  Unknown or inactive addresses get the same page and nothing is sent. Returns False only when
  rate-limited.
- The job calls `send_login_email(user_id, link_base)`: creates a `LoginChallenge` (link token +
  6-digit code, 15 minutes, single use, only hashes stored) and sends a plain-text Polish e-mail.
- `login_with_code(email, code)` / `login_with_link(token)` return the user or None (one generic
  failure). 5 wrong codes for an e-mail lock code login for 15 minutes.
- `start_session(request, user)` (rotates the session key) and `end_session(request)` (deletes
  the session row). Sessions live in the database and expire after 30 idle days.
- A successful link or code login confirms an unconfirmed account (`confirm_email()`, records
  `account_confirmed` once). `request_login(..., next_path=...)` puts a local path into the
  e-mailed link, so the link lands there after logging in.
- Try it locally: `make up-lite && make seed && make web` and `make worker`, open
  `http://127.0.0.1:8000/logowanie/`, enter `artysta01@example.invalid`, read the e-mail in
  Mailpit (`http://127.0.0.1:18025`).

## Account settings and e-mail change (US-1.6)

`/konto/` (any logged-in account; linked as "Ustawienia konta" in the header), logic in
`apps/accounts/services.py` (D101):

- `account_overview(user)` and `update_names(user, full_name=..., artist_name=...)`; the artist
  name goes through `artists.services.rename_artist()`.
- `request_email_change(user, new_email, client_ip, link_base=...)`: 5 requests per hour per user
  (`EMAIL_CHANGE_LIMIT_PER_USER`) and the login per-IP limit (20/h). The page answer is the same
  for a free and a taken address. Free address: an `EmailChangeRequest` is stored and the job
  `accounts.send_email_change_email` sends a link (`/konto/email/link/?t=...`) and a 6-digit code
  to the new address (15 minutes, single use, only hashes stored) and a notice without a link to
  the old one. Taken address: only the notice (`accounts.send_email_change_notice`), plus a
  request without hashes that can never be confirmed, so `/konto/` shows the same pending
  state either way. Both cases close the user's older open request.
- `confirm_email_change_code(user, code)` / `confirm_email_change_link(user, token)`: only the
  logged-in user who asked; sets the e-mail and `email_confirmed_at`. 5 wrong codes lock code
  entry for 15 minutes. The view keeps the current session with a new key; every other session
  of the user stops authenticating (the session hash includes the e-mail).
- Until confirmed, login works with the old address only. A new request replaces an older one.
- `/konto/dane/` and `/konto/usun/` are placeholders until US-8.6.
- Try it locally: log in as `artysta01@example.invalid`, open `/konto/`, enter a new
  `@example.invalid` address, read both e-mails in Mailpit and enter the code.

## Artist registration (US-1.1)

App `apps/artists`, logic in `services.register_artist(email, name, client_ip, link_base=...)`:

- Refuses (503 page, nothing created) when the terms or the privacy policy has no published
  version, and (429) when the login e-mail limits are reached.
- New address: one transaction creates an unconfirmed `User` (`email_confirmed_at` empty, no
  password), its `Artist` (one-to-one, D2, holds the name) and the acceptance of the current
  terms and privacy versions (`trust.record_acceptance`). Records `artist_registered` and sends
  the login e-mail through `accounts.services.request_login` with the wizard start as `next`.
- Existing address: same answer, nothing created, a normal login e-mail goes to the owner.
- The page after sending has the code form; the code or the link (15 minutes) confirms the
  account and opens `artists:start`. An expired code is not a dead end: logging in from
  `/logowanie/` confirms the account too.

## Artist profile wizard, step 1: basics (US-2.1)

App `apps/artists`, logic in `services.py` (D102):

- `Artist` has `artist_type` (teatr, iluzja, muzyka, pokaz naukowy, pokaz ze zwierzętami,
  warsztaty, inne), `name` and `city`; voivodeships of activity (the shared
  `apps.core.regions.Voivodeship` list) and audiences are child rows `ArtistVoivodeship` /
  `ArtistAudience` (one row per value; filter with `Artist.objects.filter(voivodeships__voivodeship=...)`).
- `save_basics(user, data)` stores all fields at once (the name through `rename_artist()`) or
  raises `InvalidBasics`; `basics_complete(artist)`; `basics_of(artist)` for prefilling;
  `wizard_steps(artist)` for the overview.
- `/artysta/kreator/` lists step 1 (required) and the later steps (offers, statements,
  materials). Until the basics are complete the later steps are shown disabled and their URLs
  redirect to step 1 with a message; afterwards they can be skipped and opened in any order
  (materials is a placeholder until US-2.3A).
- `make seed` fills basics for `artysta01`–`artysta09`; `artysta10@example.invalid` keeps empty
  basics to try the wizard.

## Artist profile wizard: offers and repertoire (US-2.9)

App `apps/artists`, model `Offer`, logic in `services.py` (D103):

- An offer has a title and a plain-text description (required), audience age from–to in years
  (optional, 0–99, from ≤ to), duration in minutes (optional, > 0), a price as whole PLN **or**
  "na zapytanie" (exactly one; also a DB check constraint), a position and an optional poster.
  A theatre's repertoire of 20+ shows is many offers in one profile (D2).
- Services: `offers_for(artist)` (in order), `get_offer(artist, id)` (own offers only),
  `create_offer(artist, data, poster=None)`, `update_offer(artist, id, data, poster=None,
  remove_poster=False)`, `delete_offer(artist, id)`, `move_offer(artist, id, "up"|"down")`,
  `reorder_offers(artist, ids)`, `has_offers(artist)` (D6 rule for publication, US-2.8),
  `offer_errors(data)` (the validation the form shares), `poster_url(offer)`.
- Posters go through `apps.core.uploads.store_upload(kind="photo", visibility="private")` (15 MB,
  sniffed type, EXIF stripped) and are shown to the artist through `media.signed_url`. A
  replaced/removed poster and a deleted offer's poster leave storage after the commit.
- `/artysta/profil/oferty/` lists the offers with edit, delete (confirmation page, then POST) and
  up/down buttons; the wizard overview marks the step done with at least one offer.
- `make seed` gives `artysta01@example.invalid` a synthetic 20-offer repertoire (no posters), once.

## Artist statements (US-8.2)

App `apps/trust`, logic in `services.py` (D104). Wordings come from the owner's lawyer (D30);
`make seed` publishes placeholders starting with "PROJEKT – tekst zastępczy".

- Six statement kinds are `LegalDocument` kinds (versioned, immutable): `child_protection`,
  `material_rights` (D4), `image_adults`, `image_children` (parents or school, D7),
  `billing_form`, `insurance` (OC). Publish a new wording at `/django-admin/trust/legaldocument/add/`;
  every new version asks artists to make that statement again (the "Istotna zmiana" box does not
  matter for statements).
- `ArtistStatement` rows are append-only (renewal, a new billing form or OC date and a withdrawal
  are new rows; read-only in the admin). The newest row per kind counts when it is not a
  withdrawal, refers to the current wording and, for OC, `valid_until` (optional) has not passed.
- Services: `make_statement(artist, kind, billing_form=..., valid_until=..., shown_document_id=...)`
  (`faktura`/`rachunek` only, date only for OC; `NoPublishedVersion`, `InvalidStatement`,
  `StaleWording`), `withdraw_statement(artist, kind)`, `statement_overview(artist)` (status per
  kind: unavailable, not made, current, "wymaga ponownego oświadczenia", expired),
  `current_statements(artist)`, `has_child_protection_statement(artist)` (D6, for US-2.8).
- `/artysta/profil/oswiadczenia/`: wording, status, checkbox + submit per statement, billing form
  choice, OC date, withdraw. The step is done with a counted child-protection statement.
- `{% load statements %}{% artist_statement_badges artist %}` lists the counted statements under
  "Oświadczenie artysty" with a note that the service does not check them (D31); on the wizard
  overview now, the public profile (US-3.1) reuses it.
- Daily job `trust.check_insurance_expiry` (07:00) queues one plain-text reminder
  (`trust.send_insurance_reminder`, `email` queue, statement id only) per expired OC statement,
  once (`StatementReminder`). An expired OC stops counting by date even before the job runs.
  Run it by hand: `uv run python manage.py shell -c "from apps.trust import services; print(services.queue_insurance_reminders())"`.

## Institution registration (US-1.2)

App `apps/institutions`, logic in `services.py`, same flow as artist registration (D97, D98):

- Models: `Institution` (type, name, locality, one of the 16 voivodeships, optional unique RSPO
  number, `verification_status` "niezweryfikowana"), `InstitutionMember` (one-to-one with the
  user, function, `needs_review`), `RspoEntry` (registry reference rows; write them with
  `add_rspo_entry()` / `upsert_rspo_entry()`, which fill the case-folded search columns).
- `suggest_rspo(name, locality)`: every word of the name must occur (case-insensitive, also for
  Polish letters), locality is a prefix; at most 10 rows, nothing below 3 characters. The page
  calls `/rejestracja/placowka/rspo/?name=...&locality=...` with HTMX and shows radio buttons.
- `register_institution(email, details, function, client_ip, rspo_number=..., link_base=...)`:
  with an RSPO number the institution data come from the registry, whatever the form sent; an
  RSPO number that already has an `Institution` links the new member to it with
  `needs_review=True` (admin: `/django-admin/institutions/institutionmember/?needs_review__exact=1`).
  Records `institution_registered` (type, `rspo_matched`, `linked_existing`) and sends the login
  e-mail with `institutions:start` (`/placowka/`, a placeholder until M2) as `next`.
- `make seed` adds six synthetic RSPO rows (numbers 900001+, e.g. "Szkoła Podstawowa nr 5" in
  Wrocław and in Opole) to try the suggestions.

## Institution verification and RSPO import (US-1.4)

Logic in `apps/institutions/services.py` (D3, D100):

- **Import:** download the CSV on [rspo.gov.pl](https://rspo.gov.pl/) ("Pobierz CSV" under the
  search results; UTF-8 with BOM, `;`, 54 columns) and run
  `uv run python manage.py import_rspo <path>`. It upserts `RspoEntry` by "Numer RSPO" (running
  it twice changes nothing) and prints
  `import_rspo: created N, updated N, unchanged N, skipped N, verified N`. Rows without a valid
  number, name, locality or voivodeship are skipped and counted, never printed or logged.
  `RSPO_COLUMNS` is the one place that maps header names to fields; Windows-1250 and `,`/tab
  files (an export re-saved in Excel) work too. Of "E-mail" only the domain is stored.
  Never commit a real export: the test fixture `apps/institutions/tests/fixtures/rspo_sample.csv`
  is synthetic (regenerate with `uv run python -m apps.institutions.tests.rspo_fixture`).
- **States:** `Institution.verification_status` is "niezweryfikowana" or "zweryfikowana", with
  `verified_at`, `verification_method` ("domena" or "ręcznie") and, for manual approval,
  `verified_by`. Only `services.verify()` sets them (records `institution_verified` with
  `method`, once per institution).
- **Domain rule:** an institution with an RSPO number becomes verified ("domena") when a
  confirmed member's e-mail domain equals its RSPO e-mail domain exactly (case-insensitive).
  Free mailbox domains (`PUBLIC_MAILBOX_DOMAINS`) never count. Checked when an account is
  confirmed (`accounts.signals.email_confirmed`) and after each import.
- **Manual approval:** `/django-admin/institutions/institution/`, select institutions, action
  "Zatwierdź placówkę" (staff only). Already verified institutions stay as they are.
- **Badge:** `services.is_verified(institution)` and, in templates,
  `{% load institutions %}{% institution_badge institution %}` (nothing for unverified). Shown on
  `/placowka/` now; inquiries and notices use it in M2/M3.

## Roles and permissions (US-1.5)

Code in `apps/accounts/roles.py` (rules) and `apps/accounts/permissions.py` (view guards); D99.

- One role per account, derived, not stored: `roles.role_of(user)` returns `anonymous`,
  `admin` (`is_staff` or `is_superuser`), `artist` (has an `Artist`) or `institution` (has an
  `InstitutionMember`); `none` for an account with no record or, failing closed, with both.
- Rules for views and later features: `can_create_artist_profile(user)` (artists),
  `can_create_inquiry(user)`, `can_create_notice(user)` (institutions; E6 adds verification, D3).
- Guards: `@role_required("artist")` for function views, `RoleRequiredMixin` with
  `required_roles = ("institution",)` for class views. Anonymous visitors go to
  `/logowanie/?next=<path>`; another role gets the Polish 403 page (`templates/403.html`) and one
  JSON log line `permission denied` with `user` (pseudonym), `role`, `url_name`, `required_role`.
- **Admin accounts only from the server:** `uv run python manage.py create_admin <email>` (on pirx:
  `cd ~/runtime/artysci-dla-szkol/app/projects/artysci-dla-szkol && uv run --frozen --no-dev
  python manage.py create_admin <email>` with the instance's env). It creates the account if needed
  (no password) or upgrades one without a role, sets `is_staff` and `is_superuser`, and refuses an
  artist or institution account. The admin logs in with the normal e-mail link or code; that
  session also opens `/django-admin/`. No form or view can set these flags.
- **Permission matrix:** `apps/accounts/tests/test_permission_matrix.py` lists every URL name with
  the expected answer for each role. A new route without a row fails the test with its name, so
  add the row with the route. `uv run pytest -k "permission or role" -v` prints how many routes it
  covered.
- `make seed` gives the seed accounts their roles: `artysta01..10` have an artist record,
  `szkola01..05` are members of institutions made from the synthetic RSPO rows.

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
- **Malware scan** (`apps/core/scanning.py`): `scan(file) -> clean | infected | error`, backend
  from `MALWARE_SCANNER`: `clamd` (ClamAV daemon, INSTREAM over TCP `CLAMD_HOST`/`CLAMD_PORT` or
  the Unix socket `CLAMD_SOCKET`, stdlib only), `none` (nothing scanned, each file logged as
  `upload_unscanned`; dev and pirx, which has no RAM for clamd: D87) or `fake` (tests). **Prod
  refuses to start with anything but `clamd`**; with no clamd address every scan is an error, so
  no upload ever becomes ready. Run the real-clamd test with `CLAMD_HOST=... uv run pytest
  apps/core/tests/test_scanning.py`.
- **Artist materials** (`apps/artists/materials.py`, `/artysta/profil/materialy/`): photos (JPG,
  PNG, WebP, 15 MB, at most 40) and PDFs (20 MB, at most 10) go through `store_upload(...,
  visibility="private")` and become a `Material` in `pending`. The `artists.scan_material` job
  (`media` queue) marks it `ready` (clean), deletes the file and marks it `rejected` (infected), or
  retries 3 times and leaves it `pending` (scanner error). Only `ready` materials count
  (`ready_materials()`). A clean PDF gets the `artists.extract_pdf_text` job (`pypdf`, limits
  `PDF_TEXT_MAX_PAGES`/`_CHARS`/`_SECONDS`; encrypted or broken files end as a text status).
  YouTube/Vimeo links are parsed to a video id and checked through the fixed oEmbed endpoints
  only (`OEMBED_TIMEOUT_SECONDS`); other hosts are refused without a request. Offer posters
  (`Offer.poster_status`) go through the same scan (`artists.scan_poster`).
- Not covered yet: video and audio upload, transcoding, image variants (E2), HEIC photos.

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
