"""Environment helpers shared by all settings modules.

All configuration comes from environment variables (D91: no hosting provider assumed).
"""

import environ
from django.core.exceptions import ImproperlyConfigured

env = environ.Env()


def require(name: str, settings_module: str) -> str:
    """Return a required env var, or fail fast with a message naming it.

    An empty value counts as missing: an empty SECRET_KEY or DATABASE_URL is never valid.
    """
    value = env.str(name, default="").strip()
    if not value:
        raise ImproperlyConfigured(
            f"Missing required environment variable {name} for {settings_module}. "
            f"Set it in the environment (see .env.example)."
        )
    return value


def scanner_from_env(allowed: tuple[str, ...], *, default: str, module: str) -> str:
    """`MALWARE_SCANNER` if it is one of `allowed`, else fail fast (prod allows only clamd)."""
    value = env.str("MALWARE_SCANNER", default=default).strip().lower() or default
    if value not in allowed:
        raise ImproperlyConfigured(
            f"MALWARE_SCANNER={value!r} is not allowed in {module}; "
            f"use one of: {', '.join(allowed)} (see .env.example)."
        )
    return value
