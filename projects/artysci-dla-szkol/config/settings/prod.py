"""Production. Every value that matters is required; startup fails fast if one is missing.

Hosting is not decided (D91): nothing here assumes a provider. TLS/HSTS hardening is T04.
"""

from .base import *  # noqa: F403
from .base import DATABASE_CONN_MAX_AGE
from .env import env, require

_MODULE = "config.settings.prod"

DEBUG = False
SECRET_KEY = require("DJANGO_SECRET_KEY", _MODULE)
ALLOWED_HOSTS = [
    host.strip() for host in require("DJANGO_ALLOWED_HOSTS", _MODULE).split(",") if host.strip()
]

DATABASES = {"default": env.db_url_config(require("DATABASE_URL", _MODULE))}
DATABASES["default"]["CONN_MAX_AGE"] = DATABASE_CONN_MAX_AGE

CSRF_TRUSTED_ORIGINS = env.list("DJANGO_CSRF_TRUSTED_ORIGINS", default=[])
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
