"""Login throttling scaffold (T04), to be wired into the login flow by E1.

Counts failed attempts per key in a fixed window in the Django cache. A key is anything the
caller wants to limit on (the submitted e-mail, a truncated client IP); it is normalised and
hashed, so no e-mail or IP is stored in the cache or written to logs.

Usage in a login view/service (E1)::

    keys = [email, logs.client_ip(request)]
    if throttling.is_locked(*keys):
        ...  # same generic error as a wrong password, no hint which key is locked
    elif authenticate(...) is None:
        throttling.register_failure(*keys)
    else:
        throttling.reset(email)

The default cache is per process (LocMemCache). With several web workers each counts on its own
until a shared cache is configured (planned with E1, see SECURITY.md).
"""

import hashlib
import logging

from django.conf import settings
from django.core.cache import caches

logger = logging.getLogger(__name__)


def _cache():
    return caches[settings.LOGIN_THROTTLE_CACHE]


def _cache_key(identifier: str) -> str:
    digest = hashlib.sha256(identifier.strip().lower().encode()).hexdigest()
    return f"login-throttle:{digest}"


def failures(identifier: str) -> int:
    return _cache().get(_cache_key(identifier), 0)


def is_locked(*identifiers: str) -> bool:
    """True when any key has reached LOGIN_THROTTLE_LIMIT failures in the current window."""
    return any(failures(i) >= settings.LOGIN_THROTTLE_LIMIT for i in identifiers if i)


def register_failure(*identifiers: str) -> None:
    """Count one failed attempt for every key; the window starts at the first failure."""
    cache = _cache()
    for identifier in filter(None, identifiers):
        key = _cache_key(identifier)
        cache.add(key, 0, timeout=settings.LOGIN_THROTTLE_WINDOW)
        try:
            count = cache.incr(key)
        except ValueError:  # expired between add() and incr()
            cache.set(key, 1, timeout=settings.LOGIN_THROTTLE_WINDOW)
            count = 1
        if count == settings.LOGIN_THROTTLE_LIMIT:
            logger.warning(
                "login throttle engaged",
                extra={"event": "login_throttled", "count": count},
            )


def reset(*identifiers: str) -> None:
    """Forget the failures (call after a successful login)."""
    _cache().delete_many([_cache_key(i) for i in identifiers if i])
