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
    "MEDIA_PUBLIC_BASE_URL": "https://media.example.pl/",
    "SITE_URL": "https://example.pl/",
}


def _load(module: str):
    for name in (module, "config.settings.hosted"):  # prod and pirx build on hosted
        sys.modules.pop(name, None)
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


def test_prod_site_url_has_no_trailing_slash(prod_env):
    assert _load("config.settings.prod").SITE_URL == "https://example.pl"


def test_dev_site_url_defaults_to_localhost(settings):
    assert settings.SITE_URL.startswith("http") and not settings.SITE_URL.endswith("/")


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


def test_prod_scans_uploads_with_clamd_by_default(prod_env):
    assert _load("config.settings.prod").MALWARE_SCANNER == "clamd"


@pytest.mark.parametrize("value", ["none", "fake", "magic"])
def test_prod_refuses_to_load_without_a_real_scanner(prod_env, value):
    prod_env.setenv("MALWARE_SCANNER", value)
    with pytest.raises(ImproperlyConfigured, match="MALWARE_SCANNER"):
        _load("config.settings.prod")


def test_pirx_may_run_unscanned(prod_env):
    pirx = _load("config.settings.pirx")
    assert pirx.MALWARE_SCANNER == "none"
    prod_env.setenv("MALWARE_SCANNER", "clamd")
    assert _load("config.settings.pirx").MALWARE_SCANNER == "clamd"
    prod_env.setenv("MALWARE_SCANNER", "fake")
    with pytest.raises(ImproperlyConfigured, match="MALWARE_SCANNER"):
        _load("config.settings.pirx")


def test_quality_lab_is_off_in_prod_and_on_in_dev_test_and_pirx(prod_env):
    """The synthetic test set (US-11.2) must never run in production by default."""
    prod_env.delenv("QUALITY_LAB_ENABLED", raising=False)
    assert _load("config.settings.prod").QUALITY_LAB_ENABLED is False
    assert _load("config.settings.pirx").QUALITY_LAB_ENABLED is True
    assert _load("config.settings.dev").QUALITY_LAB_ENABLED is True
    assert _load("config.settings.test").QUALITY_LAB_ENABLED is True
    prod_env.setenv("QUALITY_LAB_ENABLED", "false")
    assert _load("config.settings.pirx").QUALITY_LAB_ENABLED is False


def test_dev_defaults_to_no_scanner(monkeypatch):
    monkeypatch.delenv("MALWARE_SCANNER", raising=False)
    sys.modules.pop("config.settings.base", None)
    assert _load("config.settings.dev").MALWARE_SCANNER == "none"


def test_check_deploy_is_clean_with_prod_settings():
    """`manage.py check --deploy --fail-level WARNING` under prod with the required env."""
    env = {
        "PATH": os.environ.get("PATH", ""),
        "HOME": os.environ.get("HOME", ""),
        "DJANGO_SETTINGS_MODULE": "config.settings.prod",
        "DJANGO_SECRET_KEY": "test-only-not-a-secret-" + "abcdefghij" * 3,
        "DJANGO_ALLOWED_HOSTS": "artysci.example",
        "DATABASE_URL": PROD_VARS["DATABASE_URL"],
        "MEDIA_PUBLIC_BASE_URL": PROD_VARS["MEDIA_PUBLIC_BASE_URL"],
        "SITE_URL": PROD_VARS["SITE_URL"],
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
