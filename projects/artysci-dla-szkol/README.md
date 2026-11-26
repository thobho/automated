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
  Migrations are not reversed, so keep them backward compatible. After a failed deploy the checkout
  stays on a detached HEAD at the last good commit; the next successful deploy checks `main` out again.
  A dirty deployment checkout or a failed `git fetch` is logged in one line and nothing is deployed.
  `deployed.commit` is `git rev-parse HEAD` after the green smoke test.
  - Unit files: `make deploy-pirx` runs `deploy/pirx/refresh-units.sh`, which rewrites only the
    `ads-*` units whose rendered content changed, runs `daemon-reload`, enables and restarts changed
    timers (and `ads-lite`); web/worker/media restart as part of the deploy anyway.
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
`DJANGO_SECRET_KEY`, `DJANGO_ALLOWED_HOSTS`, `DATABASE_URL`, `MEDIA_PUBLIC_BASE_URL` or `SITE_URL`
is missing. All variables are documented in [`.env.example`](.env.example).

`SITE_URL` (public origin, e.g. `https://artysci.example.pl`, no trailing slash) builds the
absolute URLs of canonical links, Open Graph tags, JSON-LD and the sitemap. It is required in
`prod` (no default), defaults to the LAN address `http://192.168.68.62:8100` in `pirx` and to
`http://localhost:8000` in dev and test.

## Search engine visibility (US-3.4)

The public page `/artysci/<slug>/` is server-rendered with `<title>`, a meta description (about
text, at most 155 characters, cut at a word, no HTML), `<link rel="canonical">`,
`robots: index,follow`, Open Graph and Twitter card tags and schema.org JSON-LD
(`PerformingGroup` for theatre and music, `Person` for illusion, `Organization` otherwise: name,
description, image, url, `areaServed` regions, `makesOffer` names without prices; never e-mail,
phone or address). `og:image` is the main photo when the page has one, else
`static/profiles/og-default.png`. All of it is built in `apps/profiles/seo.py` from the published
snapshot, which also stores the artist type and regions (a page published before T39 gets them
with the next "Opublikuj zmiany"). The JSON-LD is an `application/ld+json` data block: no inline script runs and the CSP
is unchanged. `/sitemap.xml` lists published pages only (`lastmod` = last publication time, at most
50,000 URLs, revalidated on every request so a withdrawal is gone at once); `/robots.txt` allows
public pages, disallows `/panel/` (incl. the preview), `/admin/`, `/django-admin/` and `/artysta/`,
and names the sitemap. The preview keeps `noindex` and `X-Robots-Tag`.

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
  (statements, GET + POST), `/artysta/profil/materialy/` (materials),
  `/artysta/profil/braki/` (missing items, US-2.7),
  `/artysta/profil/import/` (website import, GET + POST) and `/artysta/profil/import/<id>/`
  (import status); artists only, login required.
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

App `apps/trust`, logic in `services.py` (D104). Wordings are drafted by an agent (US-8.10), reviewed by a lawyer and approved by the owner (D30, D116);
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

App `apps/trust`. The texts are drafted by an agent (US-8.10), reviewed by a lawyer and approved by the owner (D30, D116).

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
- `generation=` (a running `quality.Generation`) links the `AICall` row to a profile generation.

## Generator versioning (US-11.1)

Every profile generation records which versions of the generator's parts produced it, so a page
can be reproduced and generator changes can be compared (D13, D14). Code: `apps/quality`.

- **Components** are declared in code with a kind (`instructions`, `schema`, `validator`,
  `template`), a name, a version string and their files (paths from the project folder) or
  inline content; register them in a module imported at startup (e.g. the owning app's
  `AppConfig.ready()`):

  ```python
  from apps.quality.registry import Component, registry

  DRAFT = registry.register(
      Component("instructions", "profile_draft", "1", files=("apps/profiles/prompts/draft.md",))
  )
  ```
- **Bumping a version.** `apps/quality/components.json` records `kind:name` → version → SHA-256
  of the content. `test_every_registered_component_matches_the_manifest` fails, naming the
  component, when its content changed without a new version. To change a component: edit it,
  raise its `version`, run `uv run python manage.py generator_manifest --write` and commit
  `components.json` with the change. A recorded version is never rewritten (the command
  refuses); `generator_manifest` without `--write` only checks.
- **A run** goes through `apps/quality/services.py`: `start_generation(artist, trigger,
  components)` (trigger `import`, `questionnaire`, `manual` or `rerun`), AI calls with
  `ai.complete(..., generation=g)` or `record_ai_call(g, result.call_id)`, then
  `finish_generation(g, result, warnings, repair_rounds, status)` (status `ready` „gotowa”,
  `review` „do przeglądu”, `error` „błąd”; `running` „trwa” until then). Finishing stores the
  times, the duration, the AI model(s) the adapter reported and the cost (sum of the linked
  `AICall` rows). A finished generation and every component version are append-only.
- **Stored versions** (`GeneratorComponentVersion`, one row per content hash): instructions and
  schemas keep a full text snapshot; validators and templates keep the file list and hash,
  pointing at the code in git (declared with inline content, they keep the content). `versions_of(generation)` returns exactly that.
- **Input fingerprint** (`input_fingerprint(artist)`, D107): SHA-256 over the ready materials
  (by id: id + a hash of the row's content fields) and the questionnaire values. Same input,
  same fingerprint; no copy of the materials is kept (D12).
- **Inspect:** read-only Django admin at `/django-admin/quality/generation/` (staff only) and
  `uv run python manage.py generation_show <id>` (JSON: versions, fingerprint, status, warnings,
  rounds, duration, cost, AI call ids; no prompt, reply or instruction text).
- Not here yet: the hard-rule validator and repair loop (US-2.5b–c), the public template
  (US-3.1), re-running a stored generation and the evaluation set (US-11.2–11.4).
  `apps/quality/tests/fake_generator.py` is a test-only generator showing the full flow.

## Generator test set (US-11.2)

A versioned set of **synthetic** artist material packages in three quality levels (`weak` słabe,
`medium` średnie, `rich` bogate), each with checkable expectations. A package loads as a test
artist and runs through the existing generator. Code: `apps/quality/testset.py`; the 30 packages
(6 from T41, 24 from T42: 10 per level, every artist type at least 3 times) live in
`apps/quality/testset/<slug>/package.json`.

- **Switch.** `QUALITY_LAB_ENABLED` (env, default off; on in the dev, test and pirx settings,
  off in prod). With it off, `testset_check`, `testset_load` and `load_package` refuse and
  create no rows, so test artists never appear in production.
- **Commands** (from the project folder): `uv run python manage.py testset_check` validates every
  package and prints a table (slug, origin, level, type, number of expectations); exit code 1 and
  the package name plus the problem on an invalid one. `uv run python manage.py testset_load
  [--package <slug>]` creates or updates `testset-<slug>@example.invalid` and prints materials,
  offers and `input_fingerprint`; loading an unchanged package again changes nothing, a changed
  one replaces the materials and offers (stored generations are never touched).
- **Format.** `package.json`, checked against `apps/quality/testset/package.schema.json`:
  `slug` (= folder name), `origin` (`synthetic`; `consented` is part of the format but the loader
  refuses it: the service has no consent record for the test set yet, D12), `level`, `artist`
  (type from the existing list, name, city, voivodeships, audiences), `questionnaire`, `offers`,
  `site_text`, `documents` (`name`, `text`: as extracted from a PDF), `videos` (`url`, `title`:
  the title comes from the package, no oEmbed), `photos` and `expectations`. No binary files:
  a photo is drawn deterministically with Pillow at load time from `{"kind": "normal" |
  "low_resolution" | "poster" | "screenshot", "width", "height"}` and goes through the real
  upload, scan and quality checks, so `build_input` shows the real flags and `can_be_main`.
- **Expectations**, a closed set (an unknown kind or a path not in the profile schema is an
  error when the package is checked, never a silent pass): `field_empty` / `field_not_empty`
  (`path`, dotted, e.g. `hero.main_photo_id`; `null`, `""`, `[]` count as empty), `text_present` /
  `text_absent` (`text`, compared case-insensitively after whitespace normalisation, in the public
  texts), `no_price` (no price such as "1 200 zł" or "cena: 900" in the public texts; fails with
  the path), `gap_reported` (`code` in `gaps`). `check_expectations(package, profile_json)`
  returns `Result(kind, detail, passed, message)` for each.
- **Scripted profile.** `apps/quality/scripted.py: scripted_profile(input_data)` is a profile built
  from `build_input` data only (no AI): valid against the JSON Schema, clean for the validator and
  meeting every expectation of all packages. Use it as the `FakeClient` reply:
  `FakeClient(reply=json.dumps(scripted_profile(build_input(artist))))`.
- **Adding a package.** Create `apps/quality/testset/<slug>/package.json` (copy a package of the
  same level), run `testset_check` (the tests pick the folder up by themselves) and make sure the
  scripted profile meets its expectations (the parametrised test says which one fails). Packages are versioned in git; changing one changes its digest and the next
  `testset_load` replaces the artist's materials.
- **Synthetic only (D12, D57).** Names, towns, texts, offers and video titles are invented. No
  e-mail, phone, account number or real site: `check_package` runs the project scrubber over every
  text (it must change nothing) and allows only `example.invalid` hosts and YouTube/Vimeo links
  (invented ids). Materials of real artists need the separate consent from D12, which is not built.

## Automatic evaluation of the test set, part 1 (US-11.3A)

One command runs the generator on the test set and writes a report: for each package the validator
result, the expectation results and an **independent AI review** with a 1 to 5 score in six
dimensions and quotes of the problems. Code: `apps/quality/evaluation.py` (runner, summary,
report) and `apps/quality/reviewer.py` (reviewer). Page metrics, screenshots, CI and the version
gate are later stories (US-11.3B, US-11.4).

```
uv run python manage.py evaluate_testset [--package <slug>]... [--level weak|medium|rich] \
    [--output report.json] [--resume <run id>] [--key-file ~/.config/automated/secrets.env]
```

- **Refuses** with `QUALITY_LAB_ENABLED` off (no AI call) and for a `consented` package. It prints
  one line per package (generation id and status, hard rules, failed expectations, the six scores
  or `brak oceny` with the reason, problems, unverified quotes, cost) and a summary: packages,
  hard-rule pass share, failed expectations, mean per dimension overall and per level (missing
  scores are left out and their number is shown in brackets), cost. The AI client is `AI_CLIENT`;
  with `--key-file` the real OpenRouter client is used (spends money), the key is read like in
  `ai_smoke` and is never printed or written anywhere. A real run needs `AI_MAX_TOKENS` of about
  8000: with the default 2048 the generator's reply is cut off and every package ends `błąd`
  ("Odpowiedź AI nie jest poprawnym JSON-em").
- **Same path as production.** Each package is loaded (`load_package`), then `start_generation`
  and `profiles.generation.run_generation` run in the foreground (first call, validator, up to 2
  repair rounds). A generation ending `błąd` counts as failed for the hard rules and has no
  review; one ending `do przeglądu` also fails them but is reviewed.
- **The reviewer** (`purpose=profile_review`, one call per package, no retries) is a separate call
  through `apps/profiles/ai`. It gets only `build_input` and the finished profile without its
  `claims_audit`; never the generator instructions, the validator findings, earlier replies or the
  repair history. Its instructions (`apps/quality/prompts/review_instructions.md`, with a Polish
  description of 1, 3 and 5 for every dimension) and reply schema
  (`apps/quality/schemas/review.json`) are registry components `instructions:profile_review` and
  `schema:profile_review`, v0.1, not part of the generator's `COMPONENTS`; changing them needs a
  version bump (`generator_manifest --write`).
- **Rubric.** Dimensions (keys in the reply and in the report): `wiernosc`, `kompletnosc`,
  `przydatnosc`, `jezyk`, `ton`, `uczciwosc` (wierność, kompletność, przydatność, język, ton,
  uczciwość wobec braków), each an integer 1 to 5. A problem has `dimension`, `quote` (verbatim
  from the profile) and `explanation`. A quote that is not a substring of the profile's public
  texts (after whitespace normalisation) is kept with `"unverified": true` and counted.
- **No invented scores.** Invalid JSON, a score of 6, a missing dimension or any AI error gives
  the review status `brak oceny` with the reason (never reply text); the package keeps its other
  results and the run goes on. On the kill switch or a cost cap the run stops, is marked
  `niekompletny` and no further call is made; `--resume <id>` evaluates only the missing packages
  and refuses when a generator or reviewer component, the AI model, the AI client (`ai_client`,
  e.g. `fake` vs `openrouter`) or a package changed since the run started. A generation paid for
  whose review was refused by the cap is redone on resume; its cost stays in the run's
  `abandoned_cost_usd`, so `cost_usd` covers every call. An unexpected error closes the run as
  `niekompletny` (note `przerwano błędem`) and is re-raised; a run left `trwa` by a killed process
  can be resumed after `GENERATION_STALE_SECONDS` without activity.
- **Storage.** `EvaluationRun` (component versions and hashes of the generator and the reviewer,
  AI models, package-set hash, times, cost, status `trwa` / `niekompletny` / `zakończony`) and
  `PackageEvaluation` (run, slug, package hash, generation, validator summary, expectation
  results, six nullable scores, problems, review status and reason, review `AICall` ids, cost).
  Cost is the generation plus the review calls (`AICall`). A finished run and every package row
  are append-only (edits and deletes are refused, like `Generation`). Read-only, staff-only admin:
  `/django-admin/quality/evaluationrun/` and `/django-admin/quality/packageevaluation/`.
- **JSON report** (`--output`), format `evaluation-report/2` (v2 adds `catalog`, the error catalog code or null, to every validator finding, and `summary.catalog_findings`):
  `{"format", "run": {id, status, note, level, started_at, finished_at, generator_components,
  reviewer_components, generator_model, reviewer_model, ai_client, package_set_hash, packages, cost_usd},
  "summary": {as printed, plus the failed expectations}, "packages": [{slug, level, package_hash,
  generation: {id, status, repair_rounds, duration_ms, cost_usd}, hard_pass, validator: {ok, hard,
  soft, repair_rounds, repair_stopped}, expectations: [{kind, detail, passed, message}], review:
  {status, reason, scores: {<dimension>: 1-5 or null}, problems: [{dimension, quote, explanation,
  unverified}]}, profile, cost_usd, duration_ms}]}`. Synthetic data only; no key, prompt or
  instruction text.

## Katalog błędów (US-11.7)

Każdy znaleziony błąd generatora ma typ, sposób zapobiegania i przypadek regresji. Katalog:
`apps/quality/error_catalog.json` (schemat: `error_catalog.schema.json`, kod: `catalog.py`),
zarejestrowany jako komponent `catalog:error_catalog` (v0.2, poza `COMPONENTS` generatora): zmiana
katalogu, schematu lub pliku w `error_cases/` bez podniesienia wersji nie przechodzi testu manifestu.

Wpis: `code` (angielski, kebab-case), `name` i `description` po polsku, `found` (data), `handling`
i `cases`. `handling` to `{"kind": "validator_rule", "rule": "RULE_PHRASES"}` (stała z
`apps/profiles/validator.py`) albo `{"kind": "instruction_example", "anchor": "x"}` (w instrukcjach
`apps/profiles/prompts/profile_instructions.md` stoi znacznik `<!-- katalog:x -->`). Reguła może
mieć dodatkowo `"anchor"`: wtedy błąd jest zwalczany regułą i przykładem w instrukcjach (sprawdzane
są oba). Wpisy z #201: `opinia-ucznia` (twarda `RULE_PUPIL`: autor to dziecko lub uczeń),
`liczba-spoza-zrodel` (twarda `RULE_NUMBERS`), `szacunek-bez-zastrzezenia` (miękka `RULE_HEDGE`:
„około/ponad/prawie/blisko/niemal/nawet” przed liczbą w źródle znika na stronie). Przypadek:
- `validator`: paczka syntetyczna i plik `error_cases/<code>/<paczka>.json` z profilem zawierającym
  błąd (zgodnym ze schematem profilu); walidator musi go oznaczyć regułą wpisu, a skryptowy dobry
  profil paczki nie może;
- `expectation`: paczka syntetyczna i oczekiwanie z jej `package.json` (rodzaje z D118).

Sprawdzenie: `uv run python manage.py error_catalog_check` (jedna linia na wpis; kod wyjścia ≠ 0
i nazwa wpisu przy: schemacie, nieznanej regule, braku znacznika, braku przypadku, paczce
nieistniejącej lub nie-syntetycznej, fixture, którego walidator nie oznacza, oczekiwaniu, którego
paczka nie ma). Wymaga `QUALITY_LAB_ENABLED`. To samo robi `apps/quality/tests/test_catalog.py`,
więc CI zawodzi przy zepsutym katalogu. Raport oceny (`evaluate_testset`) podaje kod katalogu przy
uwadze walidatora, której reguła jest w katalogu.

**Nowy błąd:** (1) nadaj typ i kod; (2) dodaj regułę walidatora albo przykład w instrukcjach ze
znacznikiem; to zmiana generatora (D13, D14): podnieś wersję komponentu i zapisz ją
`manage.py generator_manifest --write`; (3) dodaj przypadek: fixture w `error_cases/<code>/` albo
oczekiwanie w paczce syntetycznej (D12, D57; nigdy dane prawdziwych artystów); (4) dodaj wpis do
katalogu, podnieś `CATALOG_VERSION` w `catalog.py`, `generator_manifest --write`; (5) PR zatwierdza
człowiek (D13, D14). Poza zakresem: wpisy dla pozostałych reguł, typy „opinia ucznia” i „szacunek
jako fakt”, błędy z panelu (US-11.6).

## Profile generation (US-2.5A)

A background job turns an artist's ready materials, questionnaire and offers into a profile JSON
(schema and instructions **v0.2**) and records it as a `Generation`. Code: `apps/profiles`
(`generation.py`, `inputs.py`, `validation.py`, `tasks.py`, `generator_components.py`), schema in
`apps/quality/schemas/profile.json`, instructions in `apps/profiles/prompts/profile_instructions.md`.

- **Flow.** `request_generation(artist, trigger)` refuses while a run is `trwa` for the artist
  (`GenerationRefused`), otherwise records the run (`start_generation`, with the instructions,
  schema and validator components) and queues `profiles.generate_profile` on the `ai` queue. The
  job builds the input, calls the AI only through `apps.profiles.ai` with the per-call cap, checks
  the reply against the JSON Schema and closes the run with `finish_generation`: `gotowa`, or
  `błąd` with a readable Polish reason (invalid JSON, schema mismatch with the JSON paths but never
  the values, cost cap, AI off or failing, unexpected error). No retries; the artist starts a new
  run. A run still `trwa` after `GENERATION_STALE_SECONDS` (900) is closed as failed by the next
  request, so a killed worker never blocks an artist.
- **What the AI gets** (`inputs.build_input`): basics, questionnaire values, offers (ids), the
  imported site text, PDF text, YouTube/Vimeo and video titles, and photos, videos and video frames
  as ids with their flags (US-2.4). Never file bytes, names, keys or URLs. Only `ready` materials
  count, and only while the artist has a current „Prawa do materiałów” statement (D4/D7; without
  it no material or site text is sent). Text is scrubbed (D59) before the adapter scrubs it again.
- **Artist panel.** `/artysta/profil/generowanie/` shows the status (`trwa` / `gotowa` / `błąd`)
  and the start button; the status block polls `/artysta/profil/generowanie/status/` with HTMX
  while a run goes (no inline script). The URLs carry no id: an artist sees only their own latest
  run; other roles get 403, anonymous visitors go to the login page.
- **Run it.** With `AI_CLIENT=fake` (default for dev and tests) the fake client returns a minimal
  profile that matches the schema. Local: `make up-lite`, then `make web` and `make worker`, sign
  in as an artist with ready materials and press „Generuj profil”. Real model: set
  `AI_CLIENT=openrouter` and `OPENROUTER_API_KEY` (see "AI adapter"), then check the run with
  `uv run python manage.py generation_show <id>` (status, duration, cost).
- **Changing the schema or the instructions** needs a new `PROFILE_VERSION` in
  `generator_components.py` plus `generator_manifest --write` (see "Generator versioning");
  editing `validation.py` (the validator component) needs the same.
- **Browser test:** `uv sync --group e2e && uv run pytest tests/e2e/test_generation.py
  --base-url http://127.0.0.1:<port> --artist-session <session key>` (skipped without a session).
- Repair rounds and the admin review fallback: see "Repair loop and manual review (US-2.5C)" below.
- Preview editing, locks and versions: see "Preview editing" below (US-2.6).

### Hard-rule validator (US-2.5B)

`apps/profiles/validator.py`: `validate_profile(result_json, sources) -> ValidationReport` with
`hard` and `soft` lists of `Finding(rule, path, message, value)` and `ok` (true when `hard` is
empty). Deterministic, no AI. `inputs.collect_sources(artist)` builds `Sources` from the same
`build_input` as the AI call (plus the artist's own video links, which the AI never sees). It is
the registered `validator:profile_checks` component, **v0.1** (`validation.py` + `validator.py`).
After the schema check the job runs it: no hard finding = `gotowa`, any = repair rounds, then
`do przeglądu` if still not clean (US-2.5C, below). `Generation.report` holds the whole report as JSON; soft findings are also the
generation's `warnings`.

| Rule (code) | What is checked |
| --- | --- |
| `liczby i ceny tylko ze źródła` | every number in the public text fields appears in a source (site text, PDF text, video titles, questionnaire, offers, name and city); separators (`1 200`, `1.200`, `1200,00`) are normalised, units and currency are ignored (only the number counts); quotes are left to the next rule |
| `opinie dosłownie` | each testimonial quote is a substring of a source after collapsing whitespace |
| `zdjęcia i filmy tylko z materiałów artysty` | main photo, gallery photo and video ids, caption and testimonial material ids and offer ids belong to the artist's ready materials (a video frame counts as a photo); YouTube/Vimeo links in any text must be among the artist's own links |
| `bez języka procesu i bez dodanych obietnic` | none of `BANNED_PROCESS_PHRASES` / `PROMISE_PHRASES` (case-insensitive) in the public text; quotes are exempt |
| `fakty` | label and value of each fact ≤ `FACT_MAX_CHARS` (22), no parentheses |
| `limity długości` | `LENGTH_LIMITS` per field (a text one character over is a finding) |

Soft (report only, never change `ok`): `mało konkretny opis` (no digit, name, city or offer title
in the description, or under 80 characters) and `brak sekcji` (facts, description, schools points,
gallery photos, testimonials or FAQ empty).

**Add a rule:** write `_rule_x(profile, sources) -> list[Finding]` in `validator.py`, add it to
`HARD_RULES` or `SOFT_RULES`, keep thresholds and phrases as named constants, add a passing and a
failing test (with the boundary value), bump `VALIDATOR_VERSION` in `generator_components.py` and
run `manage.py generator_manifest --write` (the manifest test fails otherwise). Only rules listed
in US-2.5 belong here.

### Repair loop and manual review (US-2.5C)

`apps/profiles/repair.py`: when the validator finds **hard** findings, `repair_profile` asks the
AI (through `apps/profiles/ai`, purpose `profile_repair`) for a corrected profile: the user message
is `{"task": "repair", "previous_result", "findings": [{rule, path, message}], "input"}` (the same
source input as the first call; the offending value is not repeated, no e-mail or other personal
data beyond that input, scrubbed as always). The reply is schema-checked and validated again.
At most **2 rounds** (`MAX_ROUNDS`); the loop ends at the first clean result. Soft findings never
trigger a repair. Each round is one `AICall` linked to the `Generation`; `Generation.repair_rounds`
counts the repair calls made. The `instructions` component is **v0.3** (adds the repair task: change
only the listed fields, add no facts); the schema stays v0.2.

Early stops (recorded in `report["repair"] = {"rounds", "stopped"}` and as a warning): `cost_cap`
(no call made), `disabled`, `invalid_json`, `schema`, `provider`, `validator`. The last valid result
and its findings are kept and the generation goes to review, never silently to `gotowa`. A failure of
the *first* call is still `błąd`.

**Review fallback.** A generation with hard findings after the loop is `do przeglądu`. The artist
panel shows only „Profil czeka na przegląd” (no generated text). Staff see these in the Django admin
under *Generacje do przeglądu* (read-only list with the remaining findings and the stop reason; the
view needs the `quality.view_reviewqueue` permission, superusers have it) and run the action
*Oznacz jako gotowa / błąd (z notatką)* with a required note. `quality.services.review_generation`
changes the status (the only edit a finished generation allows, and only from `do przeglądu`) and
writes an append-only `GenerationReview` row (staff user, time, decision, note; visible read-only in
the admin). `błąd` shows the artist a neutral reason, not the note. No dashboard queue and no e-mail
yet (US-9.2).

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
- **Video and audio** (US-2.3B): videos (MP4, MOV, WebM, 500 MB, at most 5, at most 10 minutes)
  and recordings (MP3, M4A, WAV, 50 MB, at most 10) are sent by `static/js/materials.js` in
  resumable chunks (`apps/artists/resumable.py`, own small protocol, no library):
  `POST /artysta/profil/materialy/wysylki/` (`kind`, `size`, `name`; limits checked before any
  byte) → `POST .../wysylki/<id>/` with header `Upload-Offset` and raw bytes (at most
  `UPLOAD_CHUNK_BYTES`; a wrong offset is 409 with the server's offset, bytes past the declared
  size 413) · `GET .../wysylki/<id>/` answers the received offset (resume after a lost connection
  or reload; the browser keeps the session URL per file in `localStorage`) · `POST
  .../wysylki/<id>/zakoncz/` sends the file through `store_upload` and the scan. Chunks live in
  `UPLOAD_TEMP_DIR` (one file per session, never served); sessions expire after
  `UPLOAD_SESSION_TTL_HOURS` and the hourly `artists.cleanup_upload_sessions` job deletes them.
  After a clean scan the `artists.process_media` job (`media` queue, `apps/artists/recordings.py`)
  runs `ffprobe` (container, duration, size) and for a video converts it to MP4 (H.264 + AAC,
  shorter side at most 720 px) with a JPEG thumbnail (`Material.converted_key`, `thumbnail_key`,
  private storage; the list shows them through `media.signed_url`); audio stays as uploaded. Too
  long, unreadable, timeout or crash → `rejected` with `processing_message`, file deleted.
  ffmpeg runs through `apps/core/ffmpeg.py` (argument list, no shell, `FFMPEG_TIMEOUT_SECONDS`,
  `FFMPEG_MEMORY_MB` as `RLIMIT_AS`, paths `FFMPEG_PATH`/`FFPROBE_PATH`). Install ffmpeg locally
  (`apt install ffmpeg`) to run the real conversion tests; without it they are skipped (CI sets
  `REQUIRE_FFMPEG=1`, so there they must run). The Docker image includes ffmpeg.
- **Quality checks and flags** (US-2.4, `apps/artists/checks.py`, D109): after a photo is `ready`
  (scan) or a video is `ready` (processing) the `artists.check_material` job (`media` queue)
  stores on the `Material` its size, orientation, `flags` and `checks_version`
  (`CHECKS_VERSION`). Flags are the closed `Flag` list, each with a Polish label and hint, shown
  in the material list. Photos: `niska rozdzielczość` (longer side < 1200 px), `mocna kompresja`
  (original JPEG quality < 60, estimated from the quantisation tables), `duplikat` (64-bit
  difference hash within 5 bits of an older photo of the same artist), `zdjęcie stockowe` (agency
  name in the metadata), `zrzut ekranu lub obraz AI` (common screen size with no camera data, or
  the IPTC `trainedAlgorithmicMedia` / generator markers), `plakat` (flat colour blocks, one
  dominant colour and lettering-like blocks; a heuristic with fixtures). The metadata-based
  flags are decided in `store_upload` from the original bytes (`apps/core/imagemeta.py`) before
  the metadata is stripped; only the flags and one "had camera data" bit are kept. Videos:
  `za krótkie` (< 15 s), `pionowe`, `niska rozdzielczość` (shorter side < 720 px), from the probe
  data. A ready video also gets `FRAME_COUNT` (4) JPEG frames (`VideoFrame`, private storage,
  `ffmpeg.thumbnail`) measured and flagged like photos; the artist can delete a frame
  (`POST /artysta/profil/materialy/klatki/<id>/usun/`), deleting the video removes them all.
  `checks.can_be_main(item)` and `checks.main_photo_candidates(artist)` never offer a photo or
  frame flagged stock, screenshot/AI or poster. Thresholds are named constants at the top of
  `checks.py`. Existing materials: `python manage.py check_materials [--force]` (idempotent).
- Not covered yet: image variants (E2), HEIC photos, players on the public page (US-3.1).
- **Import from the artist's website** (US-2.2, `apps/artists/website_import.py`,
  `/artysta/profil/import/`, status at `/artysta/profil/import/<id>/`): the artist pastes the URL
  and ticks the rights checkbox (records or reuses the `material_rights` statement). The
  `artists.run_website_import` job (`media` queue) fetches up to `WEBSITE_IMPORT_MAX_PAGES` (10)
  pages of the same host, `WEBSITE_IMPORT_PAGE_TIMEOUT` (30 s) per request and
  `WEBSITE_IMPORT_MAX_BYTES` (20 MB) in total including photos, at most
  `WEBSITE_IMPORT_MAX_REDIRECTS` (3) redirects. It stores the visible text scrubbed
  (`apps/profiles/ai/scrub.py` + postal addresses), copies photos through `materials.add_file`
  (imported, scanned, 40-photo limit), adds YouTube/Vimeo links through oEmbed, and keeps
  e-mails, phones and addresses separately for the artist only. Status: `w kolejce`, `trwa`,
  `gotowy`, `częściowy`, `nieudany`, with a readable message and what was skipped. Every
  user-given URL goes through **`apps/core/safefetch.py`** (the only fetcher of user URLs: public
  addresses only, connection pinned to the checked IP, redirects re-checked). For a local test
  site in dev only, `SAFE_FETCH_ALLOW_LOOPBACK=true` lets it reach `127.0.0.1` on any port; prod
  and pirx settings refuse to start with it.


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

## Public artist page template (US-3.1)

- `apps/profiles/content.py`: `PageContent` (hero, facts, about, for_schools, offers, videos,
  photos, faq, slug) is what the template renders. `page_content_for(artist)` fills it from
  existing data only (name, city, offers, ready photos/videos/links); no AI, no texts, no main
  photo. US-2.5 (AI) and US-2.6 (editor) fill the rest later.
- `apps/profiles/templates/profiles/page.html` + `_*.html` partials, CSS in
  `static/profiles/page.css`. Fixed order: start, facts, about, "Dla szkół i przedszkoli", offer,
  recordings, photos (only with ≥ 4), questions, "Sprawdź termin". A section without data is not
  rendered (no heading, no nav anchor). Offers: 6 visible, the rest in `<details>`; tags every
  offer shares are hidden; no prices anywhere = one note. No public phone or e-mail (D9).
- A YouTube/Vimeo link is a local thumbnail or placeholder plus a link; nothing is requested from
  the provider before the click. Uploaded video is a native `<video>`.
- Owner-only preview: `GET /panel/podglad/` (artist role), `noindex` meta + `X-Robots-Tag`.
  Publishing and the public URL are US-2.8.

## Preview editing, locks and versions (US-2.6)

- `PageVersion` (`apps/profiles/models.py`) stores the editable texts (tagline, facts, about,
  "for schools", FAQ) as JSON, a number, a source (`generated|edited|regenerated|restored`) and the
  locked field paths (`about`, `facts.0`, `faq.1.answer`). The newest version is current. A `gotowa`
  run (or an admin-approved one) creates version 1+; a held `do przeglądu` run creates none.
  Photos, videos and offers always come live from the artist's data.
- `apps/profiles/pages.py`: `edit_field` (validated with the generator's length limits; facts max 22
  characters, no brackets; the artist's own numbers are not checked), `unlock`, `restore`
  (a new version, current locks kept), `apply_locks`. Max 10 versions; the oldest go, never the current.
- `apps/profiles/sections.py`: regenerate one section (`tagline|facts|about|schools|faq`) as a
  background job on the AI queue (`trigger=section` run in the registry, counts against the daily
  cost cap). Locked fields are passed as fixed text and kept; up to 2 repair rounds; on failure or
  cap no version is created and a Polish reason is shown. Instructions are v0.4.
- Routes (artist only, POST + CSRF): `/panel/podglad/{edycja,odblokuj,sekcja,przywroc}/`,
  status `GET /panel/podglad/sekcja/status/` (HTMX).

## Missing items and completeness (US-2.7)

- `GET /artysta/profil/braki/` (artist only, own data only): the missing items as a task list, each
  with an „Uzupełnij” button to the target screen, a `<progress>` bar with the percentage, and a link
  to the preview. A compact summary with the percentage is on the wizard overview.
- `apps/profiles/completeness.py` stores nothing: the list is recomputed on each view, so filling an
  item on its screen removes it. Sources: the `gaps` of the latest finished run when it is `gotowa`
  (a held `do przeglądu` run shows none), mapped by a closed table (`GAP_KINDS`: photo, offers,
  price, max audience, duration, age range, tech requirements, questionnaire, child protection,
  basics) to a screen and a check; an unknown code is listed with the generator's text and no
  button. Plus the rule-based items (basics, offers, child-protection statement, main-photo
  candidate, questionnaire, description).
- Percentage = `round(100 × satisfied / 6)` over the fixed `CHECKLIST`: (1) basics (name, region,
  type, city, audience), (2) description present, (3) at least one offer, (4) child-protection
  statement, (5) a main-photo candidate, (6) any questionnaire answer. (1)–(4) are the D6
  publication minimum. `completeness_percent(artist)` is the function US-2.8 uses for the
  "published" event; no event is emitted here.

## Publication and withdrawal (US-2.8)

`apps/profiles/publication.py`. Panel: `/panel/publikacja/` (status, blockers with links),
POST-only `opublikuj/`, `zmiany/` ("Opublikuj zmiany"), `wycofaj/`, and a GET confirmation page
`wycofanie/`. Public page: `/artysci/<slug>/` (anonymous, server-rendered, T32 template).

- `publication_blockers(artist)`: Polish reasons (name, region, generated page, "O artyście" text,
  an offer, child-protection statement; an e-mail or phone in the name, city, texts, offers or photo
  alt texts, D9, found by `contact.py`). Publishing is refused while the list is not empty.
- Publishing copies everything the page shows into `PublishedPage`: texts and theme of the current
  version, name, city, offers and the ids and alt texts of the materials. Later edits, uploads,
  offers and renames stay private until "Opublikuj zmiany" (`has_unpublished_changes`).
- Slug, state and dates are read-only in the Django admin: only `publication.py` writes them.
- Only removal is immediate: a deleted material disappears, and without a current "Prawa do
  materiałów" statement (checked per request) no photo, video or link is shown.
- Recordings never show the uploaded file's name ("Nagranie 1" instead).
- Slug: made once on the first publication from the name (ASCII, lowercase, hyphens, `-2`, `-3` on
  collision), never changed by renames, kept after withdrawal (never reused, republication gives
  the same one); reserved words (`RESERVED_SLUGS`) are skipped.
- Draft, withdrawn and unknown slugs give the same 404. `Cache-Control: no-cache` (a cache must
  revalidate, so a withdrawal is visible at once). Preview stays `noindex`; the public page is not.
- `Artist.objects.published()` is the only definition of "publicly visible" (catalog, US-4.1); it
  leaves out deactivated accounts.
- Events `profile_published` (`profile_id`, `completeness_percent`) and `profile_withdrawn`.
- "Kopiuj link" on the panel of a published page copies the absolute public address (from
  `SITE_URL`) with `static/js/copy-link.js`; without JavaScript the read-only field is the fallback.

## Private preview links (US-3.7)

`apps/profiles/previews.py`. On `/panel/publikacja/` the artist creates a link ("Utwórz link do
podglądu", POST `podglad/utworz/`) and revokes one ("Odwołaj link", POST `podglad/odwolaj/`).
`/podglad/<token>/` shows the current version read-only to anyone with the link, also before the
D6 minimum; contact data is replaced by "[ukryte]", materials need the rights statement.

- The full URL is shown once, in the answer to the create POST; the database holds only the
  SHA-256 of the token. Valid 7 days, at most 3 active links, none while the page is withdrawn.
- Expired, revoked, unknown and malformed tokens give the same 404. Wrong tokens are limited per
  IP (`PREVIEW_LIMIT_PER_IP`, `PREVIEW_LIMIT_WINDOW`; then 429).
- Headers: `noindex` meta, `X-Robots-Tag: noindex, nofollow`, `Cache-Control: no-store`,
  `Referrer-Policy: no-referrer`. Logs show `/podglad/[token]/`; visits are not counted.
- Daily job `profiles.purge_preview_links` (04:41) deletes links that ended over 30 days ago.

## Page themes (US-3.2)

Four themes, a closed list (`Theme` in `apps/profiles/themes.py`; slugs equal the `theme` enum of
the AI schema): `burgundy_light` (jasny burgund, the default), `cream_green` (kremowa zieleń),
`navy_gold` (granat ze złotem), `coral_dark` (ciemny koral). The page root is
`<div class="artist-root" data-theme="<slug>">`; an unknown value falls back to the default.
- **Single source of truth:** `THEME_TOKENS` (token → hex) in `themes.py`. `static/profiles/themes.css`
  holds one `[data-theme="<slug>"]` block per theme with the same values; `test_themes.py` parses the
  CSS and compares it with the mapping, so they cannot drift. `page.css` uses only `var(--token)`.
- **Contrast:** `contrast_ratio(fg, bg)` (WCAG relative luminance). `TEXT_PAIRS` (text, link, button
  text, "for schools" band) must reach 4.5:1, `LARGE_PAIRS` (focus outline, accent) 3:1. Run
  `uv run pytest -s apps/profiles/tests/test_themes.py -k wcag` to print the ratios.
- **Choice:** the artist's own pick is `Artist.theme` (empty = not chosen), saved by
  `POST /panel/podglad/motyw/` from the form in the preview (owner only, CSRF). Without a choice the
  valid `theme` proposed by the latest finished generation is used, else the default
  (`services.theme_for`); a later generation never overrides a choice.
- **Adding a fifth theme:** add a `Theme` member, a full token set in `THEME_TOKENS` (all 14
  tokens: paper, ink, muted, heading, link, card, band, band-ink, band-link, accent, accent-ink,
  accent-hover, focus, line), the matching `[data-theme]` and `[data-swatch]` block in
  `themes.css`, and add the slug to the AI schema enum (separate task: the schema is not changed
  here). The tests pick it up through `Theme`; they fail until the CSS matches and the contrast holds.

## Accessibility of the public page (US-3.6)

What the page and its preview guarantee, and where it is tested:
- **Alt texts:** `Material.alt_text` (optional, set by the artist next to each photo on the materials
  page, `POST artysta/profil/materialy/<id>/opis/`); without it `accessibility.photo_alt()` gives the
  Polish fallback "<name> – zdjęcie <n>". No AI call. Decorative images (the initial frame, the video
  placeholder) are `aria-hidden` / `alt=""`.
- **Keyboard:** skip link "Przejdź do treści" first in the tab order; gallery photos are links that
  `static/profiles/page.js` opens in a modal `<dialog>` (Esc closes, Tab loops inside, arrows move,
  focus returns to the photo); "Pokaż pozostałe" is a button with `aria-expanded`/`aria-controls`
  (without script the extra offers simply stay visible); FAQ is a plain `<dl>`.
- **Focus:** `.artist-page :focus-visible` draws a 3 px `var(--focus)` outline; `LARGE_PAIRS` in
  `themes.py` keeps it at 3:1 or more on paper, card and band in every theme. Everything outside the
  themed root (skip link, account links, theme switch, editor, footer) gets a `#111` outline. The
  browser walk measures every tab stop in all four themes.
- **Motion:** `page.css` ends with a `prefers-reduced-motion: reduce` block that shortens animations
  and transitions and turns smooth scrolling off; `test_accessibility.py` scans every
  `static/profiles/*.css` and fails on a `transition`, `animation` or `scroll-behavior` that is not
  inside `@media (prefers-reduced-motion: no-preference)`.
- **Tests:** `apps/profiles/tests/test_accessibility.py` (service, template, stylesheets) and
  `tests/e2e/test_accessibility.py` (axe in all four themes, keyboard walk, button, dialog, reduced
  motion).

**Checklist for a new section or control** (copy into the PR):
1. Every `<img>` has `alt` (text from the service, or `""` when decorative).
2. One `h1`; the section has an `h2` and `aria-labelledby`; no skipped heading levels.
3. Everything clickable is a real `<a href>` or `<button>`; labels are visible or `aria-label`; link
   texts make sense out of context.
4. Tab order follows the visual order; a widget that opens (dialog, expander) manages focus and Esc.
5. Colours come from theme tokens only; a new token pair goes into `TEXT_PAIRS`/`LARGE_PAIRS`.
6. Any motion lives under `prefers-reduced-motion: no-preference`; no inline script or style.
7. Add the section to the seeded data of `tests/e2e/test_accessibility.py` and run it.

## Catalog dictionaries: topics and forms (US-4.6)

- Two closed dictionaries, "Tematyka" (`topic`) and "Forma" (`form`), live in `apps/catalog`
  (`DictionaryEntry`, plus `ArtistEntry` for the artist ↔ entry assignment). Starting entries come from
  a data migration (topics: uzależnienia, hejt, bezpieczeństwo, emocje, ekologia; forms: spektakl,
  warsztaty, pokaz).
- The administrator works in `/django-admin/` → "Pozycje słowników": add, rename, deactivate, and the
  action "Połącz z inną pozycją" (confirmation page with the number of profiles to move; same dictionary
  only). Kind and slug are read-only after creation; the slug is made once from the name and never changes,
  so filter URLs stay stable. An entry with assignments cannot be deleted, only merged or deactivated.
- All writes go through `apps/catalog/services.py` (`add_entry`, `rename_entry`, `deactivate_entry`,
  `merge_entries`, `set_artist_entries`, `active_entries`). Step 1 of the wizard offers the active entries
  as two optional checkbox groups and saves them in the same transaction as the basics.
- Not yet: filters in the catalog (US-4.2), AI assignment, the admin panel outside django-admin (US-9.1).

## Public catalog (US-4.1)

- `/artysci/` (anonymous, GET only, `Cache-Control: no-cache`): published artists as cards, 24 per page,
  `?strona=N` with plain-link pagination; an invalid or out-of-range page is the site 404. A link
  "Artyści" is in the header. Temporary order: latest publication first, then id (D16 comes with US-4.4).
- Read model `CatalogEntry` (`apps/catalog/listing.py`): one row per publicly visible artist, copied from
  the publication snapshot only (name, type, voivodeships, age groups, topics, forms, main photo id and alt,
  lowest price in whole zł, each offer's price and duration, publication time). Age groups, topics, forms
  and offer prices/durations are part of the snapshot since T52, so a change shows after "Opublikuj
  zmiany"; an older snapshot gives a row without them.
- `listing.sync` runs inside publish and "Opublikuj zmiany"; `listing.remove` on withdrawal. The list also
  asks `Artist.objects.published()`, so a deactivated account disappears at once. After restoring data or
  deploying: `uv run python manage.py rebuild_catalog` (idempotent; also drops stale rows).
- The badge "zweryfikowany" depends on `listing.is_verified()`, which returns False until US-8.3.

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
Added with T31: no new dependency; D114 (repair loop: at most 2 rounds, early stops go to review).
Added with T26: no new dependency; D106 (website import: SSRF-safe fetcher, limits, scrub of
PESEL and ID card numbers, contact data kept for the artist only).
New dependencies or structural choices need a line in the decision log first
(see [CLAUDE.md](CLAUDE.md)).
