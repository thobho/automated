"""Local development: DEBUG on, PostgreSQL (no SQLite fallback here).

Values come from the environment; a `.env` file in the project folder is read if present.
"""

from .base import *  # noqa: F403
from .base import BASE_DIR, DATABASE_CONN_MAX_AGE
from .env import env

env.read_env(BASE_DIR / ".env")

DEBUG = env.bool("DJANGO_DEBUG", default=True)
SECRET_KEY = env.str("DJANGO_SECRET_KEY", default="dev-only-insecure-key-do-not-use-in-prod")
ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=["localhost", "127.0.0.1", "[::1]"])

DATABASES = {
    "default": env.db(
        "DATABASE_URL",
        default="postgres://artysci:artysci@127.0.0.1:54320/artysci",
    )
}
DATABASES["default"]["CONN_MAX_AGE"] = DATABASE_CONN_MAX_AGE

EMAIL_BACKEND = env.str(
    "DJANGO_EMAIL_BACKEND", default="django.core.mail.backends.console.EmailBackend"
)
