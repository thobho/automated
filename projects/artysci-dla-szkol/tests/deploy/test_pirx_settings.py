import json
import os
import subprocess
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[2]

ENV = {
    "DJANGO_SETTINGS_MODULE": "config.settings.pirx",
    "DJANGO_SECRET_KEY": "x" * 60,
    "DJANGO_ALLOWED_HOSTS": "192.168.68.62,localhost",
    "DATABASE_URL": "postgres://u:p@127.0.0.1:1/db",
    "MEDIA_PUBLIC_BASE_URL": "http://192.168.68.62:8101/",
    "DJANGO_STATIC_ROOT": "/tmp/static-test",  # noqa: S108
}

SCRIPT = """
import json
import django
from django.conf import settings
django.setup()
from django.urls import resolve
print(json.dumps({
    "session_secure": settings.SESSION_COOKIE_SECURE,
    "csrf_secure": settings.CSRF_COOKIE_SECURE,
    "session_name": settings.SESSION_COOKIE_NAME,
    "redirect": settings.SECURE_SSL_REDIRECT,
    "hsts": settings.SECURE_HSTS_SECONDS,
    "hosts": settings.ALLOWED_HOSTS,
    "debug": settings.DEBUG,
    "static_view": resolve("/static/css/x.css").func.__name__,
}))
"""


def _run(extra_env):
    env = {k: v for k, v in os.environ.items() if not k.startswith(("DJANGO_", "DATABASE_"))}
    env.update(ENV)
    env.update(extra_env)
    return subprocess.run(  # noqa: S603
        [sys.executable, "-c", SCRIPT], cwd=PROJECT, env=env, capture_output=True, text=True
    )


def test_pirx_is_prod_without_tls_only_bits():
    result = _run({})
    assert result.returncode == 0, result.stderr
    data = json.loads(result.stdout.strip().splitlines()[-1])
    assert data["session_secure"] is False
    assert data["csrf_secure"] is False
    assert not data["session_name"].startswith("__Host-")
    assert data["redirect"] is False
    assert data["hsts"] == 0
    assert data["hosts"] == ["192.168.68.62", "localhost"]
    assert data["debug"] is False
    assert data["static_view"] == "serve"


def test_pirx_still_requires_the_secret_key():
    env = {"DJANGO_SECRET_KEY": ""}
    result = _run(env)
    assert result.returncode != 0
