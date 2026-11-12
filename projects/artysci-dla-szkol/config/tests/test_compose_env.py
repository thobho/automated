"""Smoke test: the env vars compose.yaml hands to web/worker are understood by the settings."""

import importlib
import re
import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parents[2]


def test_settings_pick_up_compose_env(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgres://artysci:pw@db:5432/artysci")
    monkeypatch.setenv("DJANGO_SECRET_KEY", "k" * 50)
    monkeypatch.setenv("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1")
    sys.modules.pop("config.settings.prod", None)
    prod = importlib.import_module("config.settings.prod")
    assert prod.DATABASES["default"]["HOST"] == "db"
    assert prod.ALLOWED_HOSTS == ["localhost", "127.0.0.1"]


def test_compose_only_uses_documented_env_vars():
    compose = (PROJECT_DIR / "compose.yaml").read_text()
    example = (PROJECT_DIR / ".env.example").read_text()
    used = set(re.findall(r"\$\{([A-Z0-9_]+)", compose))
    assert used, "compose.yaml should be configurable through .env"
    missing = [name for name in sorted(used) if name not in example]
    assert not missing, f"undocumented in .env.example: {missing}"
