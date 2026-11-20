import importlib
import sys

import pytest
from django.urls import clear_url_caches, resolve

ENV = {
    "DJANGO_SECRET_KEY": "x" * 60,
    "DJANGO_ALLOWED_HOSTS": "192.168.68.62,localhost",
    "DATABASE_URL": "postgres://u:p@127.0.0.1:1/db",
    "MEDIA_PUBLIC_BASE_URL": "http://192.168.68.62:8101/",
}
MODULES = ("config.settings.pirx", "config.settings.prod", "config.settings.hosted")


@pytest.fixture
def pirx(monkeypatch):
    for key, value in ENV.items():
        monkeypatch.setenv(key, value)
    for name in MODULES:
        sys.modules.pop(name, None)
    module = importlib.import_module("config.settings.pirx")
    yield module
    for name in MODULES:
        sys.modules.pop(name, None)


def test_pirx_is_prod_without_tls_only_bits(pirx):
    assert pirx.DEBUG is False
    assert pirx.SESSION_COOKIE_SECURE is False
    assert pirx.CSRF_COOKIE_SECURE is False
    assert not pirx.SESSION_COOKIE_NAME.startswith("__Host-")
    assert not pirx.CSRF_COOKIE_NAME.startswith("__Host-")
    assert pirx.SECURE_SSL_REDIRECT is False
    assert pirx.SECURE_HSTS_SECONDS == 0
    assert pirx.ALLOWED_HOSTS == ["192.168.68.62", "localhost"]
    assert pirx.SERVE_STATIC is True


def test_static_route_only_when_enabled(settings):
    import config.urls

    try:
        settings.SERVE_STATIC = True
        importlib.reload(config.urls)
        clear_url_caches()
        assert resolve("/static/css/x.css").func.__name__ == "serve"
    finally:
        del settings.SERVE_STATIC
        importlib.reload(config.urls)
        clear_url_caches()
    assert not any("static" in str(p.pattern) for p in config.urls.urlpatterns)
