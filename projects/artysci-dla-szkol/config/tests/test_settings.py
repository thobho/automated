import importlib
import os
import subprocess
import sys
from pathlib import Path

import pytest
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

PROJECT_DIR = Path(__file__).resolve().parents[2]

PROD_VARS = {
    "DJANGO_SECRET_KEY": "x" * 50,
    "DJANGO_ALLOWED_HOSTS": "example.pl, www.example.pl",
    "DATABASE_URL": "postgres://u:p@db.example:5432/app",
}


def _load(module: str):
    sys.modules.pop(module, None)
    return importlib.import_module(module)


@pytest.fixture
def prod_env(monkeypatch):
    for name, value in PROD_VARS.items():
        monkeypatch.setenv(name, value)
    return monkeypatch


def test_prod_loads_with_all_vars(prod_env):
    prod = _load("config.settings.prod")
    assert prod.DEBUG is False
    assert prod.ALLOWED_HOSTS == ["example.pl", "www.example.pl"]
    assert prod.DATABASES["default"]["ENGINE"] == "django.db.backends.postgresql"
    assert prod.DATABASES["default"]["HOST"] == "db.example"
    assert prod.SESSION_COOKIE_SECURE and prod.CSRF_COOKIE_SECURE


@pytest.mark.parametrize("missing", sorted(PROD_VARS))
def test_prod_fails_fast_naming_missing_var(prod_env, missing):
    prod_env.delenv(missing)
    with pytest.raises(ImproperlyConfigured, match=missing):
        _load("config.settings.prod")


def test_prod_treats_empty_var_as_missing(prod_env):
    prod_env.setenv("DJANGO_SECRET_KEY", "  ")
    with pytest.raises(ImproperlyConfigured, match="DJANGO_SECRET_KEY"):
        _load("config.settings.prod")


def test_django_startup_with_prod_and_no_env_fails_with_clear_message():
    """End to end: `manage.py check` under prod settings with an empty environment."""
    env = {
        "PATH": os.environ.get("PATH", ""),
        "HOME": os.environ.get("HOME", ""),
        "DJANGO_SETTINGS_MODULE": "config.settings.prod",
    }
    result = subprocess.run(  # noqa: S603 - fixed argv, no shell
        [sys.executable, "manage.py", "check"],
        cwd=PROJECT_DIR,
        env=env,
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    assert result.returncode != 0
    assert "Missing required environment variable DJANGO_SECRET_KEY" in result.stderr


def test_prod_tls_and_cookie_hardening(prod_env):
    prod = _load("config.settings.prod")
    assert prod.SECURE_SSL_REDIRECT is True
    assert prod.SECURE_HSTS_SECONDS >= 31_536_000
    assert prod.SECURE_HSTS_INCLUDE_SUBDOMAINS is True
    assert prod.SESSION_COOKIE_NAME.startswith("__Host-")
    assert prod.CSRF_COOKIE_NAME.startswith("__Host-")
    assert not hasattr(prod, "SECURE_PROXY_SSL_HEADER")
    assert prod.SILENCED_SYSTEM_CHECKS == ["security.W021"]


def test_prod_preload_and_proxy_header_opt_in(prod_env):
    prod_env.setenv("DJANGO_SECURE_HSTS_PRELOAD", "true")
    prod_env.setenv("DJANGO_TRUST_X_FORWARDED_PROTO", "true")
    prod = _load("config.settings.prod")
    assert prod.SECURE_HSTS_PRELOAD is True
    assert prod.SECURE_PROXY_SSL_HEADER == ("HTTP_X_FORWARDED_PROTO", "https")
    assert "security.W021" not in getattr(prod, "SILENCED_SYSTEM_CHECKS", [])


def test_check_deploy_is_clean_with_prod_settings():
    """`manage.py check --deploy --fail-level WARNING` under prod with the required env."""
    env = {
        "PATH": os.environ.get("PATH", ""),
        "HOME": os.environ.get("HOME", ""),
        "DJANGO_SETTINGS_MODULE": "config.settings.prod",
        "DJANGO_SECRET_KEY": "test-only-not-a-secret-" + "abcdefghij" * 3,
        "DJANGO_ALLOWED_HOSTS": "artysci.example",
        "DATABASE_URL": PROD_VARS["DATABASE_URL"],
    }
    result = subprocess.run(  # noqa: S603 - fixed argv, no shell
        [sys.executable, "manage.py", "check", "--deploy", "--fail-level", "WARNING"],
        cwd=PROJECT_DIR,
        env=env,
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert "System check identified no issues" in result.stdout


def test_dev_uses_postgres_by_default(monkeypatch, tmp_path):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    dev = _load("config.settings.dev")
    assert dev.DEBUG is True
    assert dev.DATABASES["default"]["ENGINE"] == "django.db.backends.postgresql"


def test_test_settings_fall_back_to_sqlite(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    test_settings = _load("config.settings.test")
    assert test_settings.DATABASES["default"]["ENGINE"] == "django.db.backends.sqlite3"


def test_locale_and_timezone():
    assert settings.LANGUAGE_CODE == "pl"
    assert settings.TIME_ZONE == "Europe/Warsaw"
    assert settings.USE_TZ is True
    assert settings.AUTH_USER_MODEL == "accounts.User"


def test_all_planned_apps_installed():
    expected = {
        "accounts", "artists", "institutions", "profiles", "catalog", "inquiries",
        "notices", "notifications", "trust", "adminpanel", "analytics", "quality",
    }  # fmt: skip
    installed = {app.rsplit(".", 1)[-1] for app in settings.LOCAL_APPS}
    assert expected <= installed
