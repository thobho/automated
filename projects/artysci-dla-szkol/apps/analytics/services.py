"""Event tracking and cookie-free visit counting."""

import hashlib
import hmac
import re
import secrets
from datetime import date

from django.conf import settings
from django.db import IntegrityError, transaction
from django.db.models import F
from django.utils import timezone

from .catalog import EVENT_CATALOG
from .models import DailySalt, Event, Visit

BOT_RE = re.compile(
    r"bot|crawl|spider|slurp|curl|wget|python-requests|httpx|headless|monitor|uptime|"
    r"preview|facebookexternalhit|lighthouse",
    re.IGNORECASE,
)
EXCLUDED_PREFIXES = ("/healthz", "/readyz", "/static/", "/django-admin/")
MAX_PATH = 200


class UnknownEvent(ValueError):
    pass


class DisallowedProperty(ValueError):
    pass


def actor_id(user) -> str:
    """Stable pseudonym of a user: HMAC of the pk under SECRET_KEY. Empty for anonymous."""
    if user is None or not getattr(user, "pk", None):
        return ""
    digest = hmac.new(settings.SECRET_KEY.encode(), f"actor:{user.pk}".encode(), hashlib.sha256)
    return digest.hexdigest()[:32]


def track(name: str, *, actor=None, obj=None, **props) -> Event:
    """Record a catalog event. Unknown names or properties raise.

    `actor` is a user (stored as a pseudonym); `obj` is any model instance (type and id only).
    """
    allowed = EVENT_CATALOG.get(name)
    if allowed is None:
        raise UnknownEvent(f"Event {name!r} is not in the catalog")
    extra = set(props) - allowed
    if extra:
        raise DisallowedProperty(f"Event {name!r} does not allow properties {sorted(extra)}")
    return Event.objects.create(
        name=name,
        actor=actor_id(actor),
        object_type=obj._meta.label_lower if obj is not None else "",
        object_id=str(obj.pk) if obj is not None else "",
        properties=props,
    )


# Visits ---------------------------------------------------------------------------------------


def is_bot(user_agent: str) -> bool:
    return not user_agent or bool(BOT_RE.search(user_agent))


def should_count(path: str, user_agent: str) -> bool:
    return not path.startswith(EXCLUDED_PREFIXES) and not is_bot(user_agent)


def salt_for(day: date) -> str:
    """Today's random salt; created on first use, older days' salts are deleted."""
    row = DailySalt.objects.filter(day=day).first()
    if row is None:
        try:
            with transaction.atomic():
                row = DailySalt.objects.create(day=day, salt=secrets.token_hex(32))
        except IntegrityError:  # another worker won the race
            row = DailySalt.objects.get(day=day)
        DailySalt.objects.filter(day__lt=day).delete()
    return row.salt


def visitor_hash(ip: str, user_agent: str, day: date) -> str:
    message = f"{ip}\n{user_agent}".encode()
    return hmac.new(salt_for(day).encode(), message, hashlib.sha256).hexdigest()[:32]


def record_visit(path: str, ip: str, user_agent: str) -> bool:
    """Count one page view. Returns False when the request is excluded."""
    if not should_count(path, user_agent):
        return False
    day = timezone.localdate()
    visitor = visitor_hash(ip, user_agent, day)
    path = path[:MAX_PATH]
    updated = Visit.objects.filter(day=day, path=path, visitor=visitor).update(views=F("views") + 1)
    if not updated:
        try:
            with transaction.atomic():
                Visit.objects.create(day=day, path=path, visitor=visitor)
        except IntegrityError:
            Visit.objects.filter(day=day, path=path, visitor=visitor).update(views=F("views") + 1)
    return True
