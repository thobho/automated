# artysci-dla-szkol

Django 5.2 LTS service connecting artists with schools. Independent project: never import code
from other `projects/` folders. Product overview and quick start: [README.md](README.md).

## Plan and decisions
- [ROADMAP.md](ROADMAP.md) — owner-approved milestones and stories; the planner makes issues from it.
- [docs/STORIES.md](docs/STORIES.md) — full approved stories with acceptance criteria (Polish). Every task's
  `Story:` id is defined there; build to those criteria, not to your own reading of the title.
- [docs/DECISIONS.md](docs/DECISIONS.md) — the decision log (D1, D2, ...); later entries override earlier ones.
  Append new decisions there with the next free number.

## Layout
- `config/` — project package: `urls.py`, `wsgi.py`, `asgi.py`, `settings/{base,dev,test,prod,pirx}.py`
  (`prod` and `pirx` share `settings/hosted.py`), `settings/env.py` (`env`, `require()` for
  mandatory vars).
- `apps/<name>/` — one Django app per concern (label = folder name):
  `accounts` (custom `User`, email login), `artists`, `institutions`, `profiles` (page generator;
  `profiles/ai/` is the only way to call an LLM: never call a provider directly),
  `catalog`, `inquiries`, `notices`, `notifications`, `trust`, `adminpanel`, `analytics`,
  `quality` (E11), `core` (health checks, home page, security headers `security.py`, JSON
  logging `logs.py`; nothing domain-specific).
- `SECURITY.md` — threat model and ASVS checklist. Update a row's status when a task delivers it.
- `templates/base.html` — base layout (Polish, vendored HTMX, CSRF header for HTMX).
  App templates live in `apps/<name>/templates/<name>/`.
- `static/vendor/` — vendored front-end libraries with a `VERSION` note. No CDNs (D11).
- `locale/` — gettext catalogs.

## Run, test, lint (from this folder)
- `uv sync` · `uv run python manage.py migrate` · `uv run python manage.py runserver`
  (dev settings need PostgreSQL; see README for a one-line container).
- Local stack: `make up-lite && make web` (or `make up-full`); see README "Local environment".
  Seed data is synthetic only (`example.invalid`), idempotent: `make seed`.
- `uv run pytest --cov` — test settings, SQLite in memory unless `DATABASE_URL` is set.
- `uv run ruff check . && uv run ruff format --check .`
- `uv run python manage.py makemigrations --check --dry-run --settings=config.settings.test`
- Coverage target: ≥85% on new code.

## Skills (read the file yourself)
Vendored, pinned skills in `.claude/skills/` of this folder (sources and licenses in each `NOTICE`). Read the file
yourself; do not rely on automatic skill loading, which is unreliable in a subfolder.
- **Building or reshaping UI** (templates, CSS, the public profile and its themes): read and follow
  `.claude/skills/frontend-design/SKILL.md`. The brief is the story in `docs/STORIES.md` and the decisions in
  `docs/DECISIONS.md`; do not ask the client to confirm anything, decide and write the design plan (palette, type,
  layout, principles) into the PR under **Decisions I made**.
- **Motion** (only where a user action changes something): `.claude/skills/animate/SKILL.md`; ignore its "initial
  response" line.
- **Before opening the PR, and for the AI reviewer:** check every changed template and stylesheet against
  `.claude/skills/web-design-guidelines/references/command.md` (accessibility, focus, forms, images, performance) and
  any motion against `.claude/skills/review-animations/STANDARDS.md`; list the findings and fixes in the PR. Together
  with the Playwright test (D110) this is the evidence for a user-visible change.
- **Before you say a task is done, open the PR or flip a label:** follow
  `.claude/skills/verification-before-completion/SKILL.md`: re-read the issue, check every acceptance criterion and
  in-scope item against fresh command output, and report gaps instead of claiming completion.
- **A failing test, red CI or a red `main`:** follow `.claude/skills/systematic-debugging/SKILL.md` (root cause before
  any fix; after 3 failed fixes stop with a ❌ comment).
- **Security-relevant code** (auth and login, permissions, settings and defaults, tokens and links, uploads, e-mail
  flows, anything that can reveal whether an account exists): run the four-phase workflow of
  `.claude/skills/sharp-edges/SKILL.md` yourself (there is no separate agent) with `references/lang-python.md`,
  `auth-patterns.md` and `config-patterns.md`. The AI reviewer does the same for `area:security` PRs.
- **Database work** (models, migrations, queries, indexes, Polish full-text search, queues): apply
  `.claude/skills/postgres-best-practices/` (read `references/_sections.md`, then the matching rule files) through
  the Django ORM and migrations. Ignore its RLS category: authorization is done in the app, and those rules are not
  included.

## Rules for agents
- **One app per concern.** Put code in the app that owns the concept; add a new app only with a
  line in the decision log. Apps talk to each other through services, not each other's views.
- **Logic lives in `services.py`** (or a `services/` package). Views parse the request, call a
  service, render a response. No business logic in views, templates, signals or model `save()`.
- **Tests next to code:** `apps/<name>/tests/test_*.py`, pytest + pytest-django. Every service
  function gets tests; every view gets at least a status-code test.
- **No new dependencies** without a line in Decisions (PR "Decisions I made" and the decision log).
  Add them with `uv add` so `uv.lock` stays in sync; commit the lock file.
- **UI strings in Polish via gettext:** `gettext_lazy as _` in Python, `{% translate %}` in
  templates. Source strings are Polish (the only language, `LANGUAGES = [("pl", ...)]`).
- **Config only from env vars.** New settings go through `config/settings/env.py`; anything prod
  cannot run without uses `require()`, and gets a line in `.env.example`. No secrets in the repo.
- **Users:** always `get_user_model()` / `settings.AUTH_USER_MODEL`; the user logs in by email,
  there is no username. Never add migrations that run before `accounts.0001_initial`.
- **Migrations:** commit them with the model change; `makemigrations --check` must be clean.
- **Security:** no inline `<script>`/`<style>` or `style=""` (strict CSP); unsafe methods stay
  CSRF-protected (no `csrf_exempt`); never put e-mails, tokens or IPs into log messages or URLs.
- Time zone is Europe/Warsaw with `USE_TZ = True`: store aware datetimes, use `django.utils.timezone`.
- Hosting is undecided (D91): no provider-specific code or settings.
