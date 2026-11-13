"""Automated tests. The only settings module with a SQLite fallback.

Set DATABASE_URL to run the suite against PostgreSQL (CI will do this).
"""

from .base import *  # noqa: F403
from .env import env

DEBUG = False
SECRET_KEY = "test-only-insecure-key"
ALLOWED_HOSTS = ["testserver", "localhost", "127.0.0.1"]

DATABASES = {"default": env.db("DATABASE_URL", default="sqlite://:memory:")}

if DATABASES["default"]["ENGINE"].endswith("sqlite3"):  # noqa: F405
    # Procrastinate's schema is PostgreSQL-only SQL; its tables are not built on SQLite.
    # Job tests use an in-memory connector there (see apps/core/tests/conftest.py).
    MIGRATION_MODULES = {"procrastinate": None}

# Fast hashing: tests create many users.
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

# Tests never reach a real AI provider, whatever the environment says.
AI_CLIENT = "fake"
OPENROUTER_API_KEY = ""
AI_KILL_SWITCH = False
