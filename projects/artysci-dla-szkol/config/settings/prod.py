"""Production. Every value that matters is required; startup fails fast if one is missing.

Hosting is not decided (D91): nothing here assumes a provider. TLS/HSTS hardening is T04.
"""

from .base import *  # noqa: F403
from .base import DATABASE_CONN_MAX_AGE
from .env import env, require
from .storage import build_storages

_MODULE = "config.settings.prod"

DEBUG = False
SECRET_KEY = require("DJANGO_SECRET_KEY", _MODULE)
ALLOWED_HOSTS = [
    host.strip() for host in require("DJANGO_ALLOWED_HOSTS", _MODULE).split(",") if host.strip()
]

DATABASES = {"default": env.db_url_config(require("DATABASE_URL", _MODULE))}
DATABASES["default"]["CONN_MAX_AGE"] = DATABASE_CONN_MAX_AGE

CSRF_TRUSTED_ORIGINS = env.list("DJANGO_CSRF_TRUSTED_ORIGINS", default=[])
EMAIL_BACKEND = env.str(
    "DJANGO_EMAIL_BACKEND", default="django.core.mail.backends.smtp.EmailBackend"
)

# Public media must come from its own origin, never the app's: no localhost default in prod.
MEDIA_PUBLIC_BASE_URL = require("MEDIA_PUBLIC_BASE_URL", _MODULE)
STORAGES = build_storages(
    STORAGE_BACKEND,  # noqa: F405
    public_base_url=MEDIA_PUBLIC_BASE_URL,
    private_root=MEDIA_PRIVATE_ROOT,  # noqa: F405
    public_root=MEDIA_PUBLIC_ROOT,  # noqa: F405
    signed_url_ttl=MEDIA_SIGNED_URL_TTL,  # noqa: F405
)
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
