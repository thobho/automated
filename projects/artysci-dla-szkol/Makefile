# Local environment. Run from this folder. Needs podman (rootless) or docker with compose, and uv.
# Settings come from .env (optional) and the environment; see .env.example.
-include .env
export

COMPOSE ?= $(shell command -v podman >/dev/null 2>&1 && echo "podman compose" || echo "docker compose")
POSTGRES_PORT ?= 54320
MAILPIT_SMTP_PORT ?= 12025
WEB_NATIVE_PORT ?= 18001
ARTYSCI_STATE_DIR ?= $(HOME)/runtime/artysci-dla-szkol
export ARTYSCI_STATE_DIR
# Native web/worker talk to the published ports on 127.0.0.1.
POSTGRES_USER ?= artysci
POSTGRES_PASSWORD ?= artysci
POSTGRES_DB ?= artysci
export DATABASE_URL ?= postgres://$(POSTGRES_USER):$(POSTGRES_PASSWORD)@127.0.0.1:$(POSTGRES_PORT)/$(POSTGRES_DB)
export DJANGO_EMAIL_BACKEND ?= django.core.mail.backends.smtp.EmailBackend
export EMAIL_HOST ?= 127.0.0.1
export EMAIL_PORT ?= $(MAILPIT_SMTP_PORT)

.PHONY: up-lite stop-lite up-full down web media worker seed test lint migrate \
	install-units-pirx deploy-pirx smoke-pirx

up-lite:
	mkdir -p $(ARTYSCI_STATE_DIR)/postgres
	$(COMPOSE) --profile lite up -d

stop-lite:
	$(COMPOSE) --profile lite stop

up-full:
	mkdir -p $(ARTYSCI_STATE_DIR)/postgres $(ARTYSCI_STATE_DIR)/minio
	$(COMPOSE) --profile full up -d --build

down:
	$(COMPOSE) --profile full down

migrate:
	uv run python manage.py migrate --noinput

web: migrate
	uv run python manage.py runserver 127.0.0.1:$(WEB_NATIVE_PORT)

MEDIA_PORT ?= 8101
media:
	uv run python manage.py serve_public_media --host 0.0.0.0 --port $(MEDIA_PORT)

worker:
	uv run python manage.py worker

seed: migrate
	uv run python manage.py seed

test:
	uv run pytest --cov

lint:
	uv run ruff check .
	uv run ruff format --check .
	uv run python manage.py makemigrations --check --dry-run --settings=config.settings.test

# --- pirx dev instance (systemd user units, see README "Dev instance on pirx") ---------------
# Run these from the dedicated checkout the units point to (it is where install runs).
PIRX_ENV ?= $(HOME)/.config/artysci-dla-szkol/pirx.env
PIRX_UNIT_DIR ?= $(HOME)/.config/systemd/user
DEPLOY_REF ?= main
UV_BIN ?= $(shell command -v uv)
PIRX_SH = set -a; . $(PIRX_ENV); set +a;

# One-time, by the owner: writes the env file (new secret key) and units, enables them at boot.
install-units-pirx:
	@test -n "$(UV_BIN)" || { echo "uv not found in PATH"; exit 1; }
	mkdir -p $(PIRX_UNIT_DIR) $(dir $(PIRX_ENV)) $(ARTYSCI_STATE_DIR)/logs $(ARTYSCI_STATE_DIR)/postgres \
		$(ARTYSCI_STATE_DIR)/media/private $(ARTYSCI_STATE_DIR)/media/public
	@test -f $(PIRX_ENV) || { \
		key=$$(python3 -c 'import secrets; print(secrets.token_urlsafe(50))'); \
		sed "s|^DJANGO_SECRET_KEY=.*|DJANGO_SECRET_KEY=$$key|" deploy/pirx/pirx.env.example > $(PIRX_ENV); \
		chmod 600 $(PIRX_ENV); echo "created $(PIRX_ENV)"; }
	@for f in deploy/pirx/ads-*.service deploy/pirx/ads-*.timer; do \
		sed -e "s|@PROJECT@|$(CURDIR)|g" -e "s|@UV@|$(UV_BIN)|g" $$f > $(PIRX_UNIT_DIR)/$$(basename $$f); \
	done
	systemctl --user daemon-reload
	systemctl --user enable --now ads-lite ads-web ads-worker ads-media ads-logrotate.timer
	systemctl --user --no-pager status ads-lite ads-web ads-worker ads-media ads-logrotate.timer || true

# Update the dev instance: pull, sync, migrate, collectstatic, restart, smoke test.
deploy-pirx:
	@test -f $(PIRX_ENV) || { echo "missing $(PIRX_ENV): run make install-units-pirx first"; exit 1; }
	git fetch origin
	git checkout $(DEPLOY_REF)
	git merge --ff-only origin/$(DEPLOY_REF)
	$(PIRX_SH) uv sync --frozen --no-dev
	systemctl --user start ads-lite
	$(PIRX_SH) uv run --frozen --no-dev python manage.py migrate --noinput
	$(PIRX_SH) uv run --frozen --no-dev python manage.py collectstatic --noinput
	systemctl --user restart ads-web ads-worker ads-media
	$(MAKE) smoke-pirx

smoke-pirx:
	$(PIRX_SH) bash deploy/pirx/smoke.sh
