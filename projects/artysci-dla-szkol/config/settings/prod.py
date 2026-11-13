"""Production. Every value that matters is required; startup fails fast if one is missing.

Hosting is not decided (D91): nothing here assumes a provider.
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
EMAIL_BACKEND = env.str(
    "DJANGO_EMAIL_BACKEND", default="django.core.mail.backends.smtp.EmailBackend"
)
# Real AI in prod. OPENROUTER_API_KEY is checked when the first AI call is made (no feature
# uses AI before E2), so startup does not require it yet.
AI_CLIENT = env.str("AI_CLIENT", default="openrouter")

# TLS and cookies (SECURITY.md). `check --deploy --fail-level WARNING` is clean with these.
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
# __Host- prefix: browser enforces Secure, Path=/ and no Domain (ASVS 3.3.1).
SESSION_COOKIE_NAME = "__Host-sessionid"
CSRF_COOKIE_NAME = "__Host-csrftoken"

SECURE_SSL_REDIRECT = env.bool("DJANGO_SECURE_SSL_REDIRECT", default=True)
# Health probes may come over plain HTTP from inside the host network.
SECURE_REDIRECT_EXEMPT = [r"^healthz$", r"^readyz$"]
if env.bool("DJANGO_TRUST_X_FORWARDED_PROTO", default=False):
    # Only behind a proxy that overwrites this header (hosting undecided, D91).
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

SECURE_HSTS_SECONDS = env.int("DJANGO_SECURE_HSTS_SECONDS", default=31_536_000)  # one year
SECURE_HSTS_INCLUDE_SUBDOMAINS = env.bool("DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS", default=True)
SECURE_HSTS_PRELOAD = env.bool("DJANGO_SECURE_HSTS_PRELOAD", default=False)
if not SECURE_HSTS_PRELOAD:
    # Preload is an owner decision (hard to undo once the domain is on the list), so its
    # deploy-check warning is silenced until the domain is chosen. See SECURITY.md.
    SILENCED_SYSTEM_CHECKS = ["security.W021"]
