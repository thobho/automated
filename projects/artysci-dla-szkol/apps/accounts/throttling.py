"""Rate limits and lockouts for the e-mail login (US-1.3), shared through PostgreSQL (D96).

Every counted event is a `ThrottleEvent` row (scope, HMAC of the key, time); a limit is "at
most N events for one key within the last W seconds" (sliding window). The rows live in the
main database, so the two gunicorn workers (and the job worker) see the same counts without a
new service. Keys are normalised and HMAC'd with SECRET_KEY: no e-mail or IP is stored or
logged.

Scopes and their settings:

- ``code``: failed 6-digit codes per e-mail (LOGIN_THROTTLE_LIMIT / LOGIN_THROTTLE_WINDOW).
  At the limit, code login for that e-mail is locked; even a correct code is refused.
- ``email_addr`` / ``email_ip``: login e-mails requested per address / per client IP
  (LOGIN_EMAIL_LIMIT_PER_ADDRESS / LOGIN_EMAIL_LIMIT_PER_IP within LOGIN_EMAIL_LIMIT_WINDOW).

Every function takes an explicit ``now`` so tests control time without sleeping.

Concurrency: check and record are two statements, so simultaneous requests may overshoot a
limit by at most the number of requests in flight; that is acceptable for these limits.
"""

import ipaddress
from dataclasses import dataclass
from datetime import datetime, timedelta

from django.conf import settings
from django.utils import timezone
from django.utils.crypto import salted_hmac

from .models import ThrottleEvent

CODE = "code"
EMAIL_PER_ADDRESS = "email_addr"
EMAIL_PER_IP = "email_ip"


@dataclass(frozen=True)
class Limit:
    scope: str
    limit: int
    window: int  # seconds


def limit_for(scope: str) -> Limit:
    if scope == CODE:
        return Limit(CODE, settings.LOGIN_THROTTLE_LIMIT, settings.LOGIN_THROTTLE_WINDOW)
    if scope == EMAIL_PER_ADDRESS:
        return Limit(scope, settings.LOGIN_EMAIL_LIMIT_PER_ADDRESS, settings.LOGIN_EMAIL_WINDOW)
    if scope == EMAIL_PER_IP:
        return Limit(scope, settings.LOGIN_EMAIL_LIMIT_PER_IP, settings.LOGIN_EMAIL_WINDOW)
    raise ValueError(f"unknown throttle scope {scope!r}")


def key_hash(scope: str, identifier: str) -> str:
    """HMAC of the normalised identifier; different per scope."""
    return salted_hmac(f"accounts.throttle.{scope}", identifier.strip().lower()).hexdigest()


def ip_identifier(remote_addr: str) -> str:
    """Key for per-IP limits: the full IPv4 address, or the /64 of an IPv6 address (one
    subscriber usually holds a whole /64). Unparseable values share one bucket."""
    try:
        ip = ipaddress.ip_address((remote_addr or "").strip())
    except ValueError:
        return "invalid"
    if ip.version == 6:
        return str(ipaddress.ip_network(f"{ip}/64", strict=False).network_address)
    return str(ip)


def _now(now: datetime | None) -> datetime:
    return now or timezone.now()


def count(scope: str, identifier: str, *, now: datetime | None = None) -> int:
    """Events for this key within the scope's window, ending at ``now``."""
    now = _now(now)
    window = limit_for(scope).window
    return ThrottleEvent.objects.filter(
        scope=scope,
        key_hash=key_hash(scope, identifier),
        created_at__gt=now - timedelta(seconds=window),
        created_at__lte=now,
    ).count()


def exceeded(scope: str, identifier: str, *, now: datetime | None = None) -> bool:
    """True when the key has reached the scope's limit (the next event is refused)."""
    return count(scope, identifier, now=now) >= limit_for(scope).limit


def hit(scope: str, identifier: str, *, now: datetime | None = None) -> int:
    """Record one event and return the new count within the window."""
    now = _now(now)
    ThrottleEvent.objects.create(scope=scope, key_hash=key_hash(scope, identifier), created_at=now)
    return count(scope, identifier, now=now)


def reset(scope: str, identifier: str) -> None:
    """Forget the events of one key (e.g. failed codes after a successful login)."""
    ThrottleEvent.objects.filter(scope=scope, key_hash=key_hash(scope, identifier)).delete()


def purge(*, now: datetime | None = None) -> int:
    """Delete events older than the longest window; returns how many were removed."""
    now = _now(now)
    longest = max(limit_for(s).window for s in (CODE, EMAIL_PER_ADDRESS, EMAIL_PER_IP))
    deleted, _ = ThrottleEvent.objects.filter(
        created_at__lte=now - timedelta(seconds=longest)
    ).delete()
    return deleted
