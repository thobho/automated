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
export DATABASE_URL ?= postgres://artysci:artysci@127.0.0.1:$(POSTGRES_PORT)/artysci
export DJANGO_EMAIL_BACKEND ?= django.core.mail.backends.smtp.EmailBackend
export EMAIL_HOST ?= 127.0.0.1
export EMAIL_PORT ?= $(MAILPIT_SMTP_PORT)

.PHONY: up-lite up-full down web worker seed test lint migrate

up-lite:
	mkdir -p $(ARTYSCI_STATE_DIR)/postgres
	$(COMPOSE) --profile lite up -d

up-full:
	mkdir -p $(ARTYSCI_STATE_DIR)/postgres $(ARTYSCI_STATE_DIR)/minio
	$(COMPOSE) --profile full up -d --build

down:
	$(COMPOSE) --profile full down

migrate:
	uv run python manage.py migrate --noinput

web: migrate
	uv run python manage.py runserver 127.0.0.1:$(WEB_NATIVE_PORT)

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
