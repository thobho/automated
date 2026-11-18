"""Artist services: registration (US-1.1, D1, D2, D30).

`register_artist()` creates an unconfirmed account, its artist record and the acceptance of the
current terms and privacy policy in one transaction, then sends the login link and code through
`accounts.services.request_login()`, so the US-1.3 validity, single use and sending limits apply
unchanged. Using the link or code confirms the account (`accounts.services.confirm_email`).

An address that already has an account gets exactly the same answer and a normal login e-mail;
nothing is created or recorded for it. Logs carry a pseudonymised user only.
"""

import enum
import logging

from django.db import transaction
from django.urls import reverse

from apps.accounts import services as accounts
from apps.analytics import services as analytics
from apps.core.logs import pseudonymise_user
from apps.trust import services as trust
from apps.trust.errors import NoPublishedVersion

from .models import Artist

logger = logging.getLogger("apps.artists.registration")

REQUIRED_DOCUMENTS = (trust.Kind.TERMS, trust.Kind.PRIVACY)


class Registration(enum.Enum):
    SENT = "sent"  # same for a new and an existing address
    RATE_LIMITED = "rate_limited"
    UNAVAILABLE = "unavailable"  # no published terms or privacy version


def documents_published() -> bool:
    return all(trust.current(kind) is not None for kind in REQUIRED_DOCUMENTS)


def _create(email: str, name: str) -> Artist | None:
    """New user + artist + acceptance, all or nothing. None if the address is taken."""
    with transaction.atomic():
        user, created = accounts.get_or_create_unconfirmed_user(email)
        if not created:
            return None
        artist = Artist.objects.create(user=user, name=name.strip())
        trust.record_acceptance(user, REQUIRED_DOCUMENTS)  # raises -> rollback
    return artist


def register_artist(email: str, name: str, client_ip: str, *, link_base: str) -> Registration:
    """Register an artist and send the login e-mail. See the module docstring."""
    if not documents_published():
        logger.warning(
            "registration refused, no published legal documents",
            extra={"event": "registration_unavailable"},
        )
        return Registration.UNAVAILABLE
    if not accounts.login_email_allowed(email, client_ip):
        logger.warning("registration rate limited", extra={"event": "registration_rate_limited"})
        return Registration.RATE_LIMITED
    try:
        artist = _create(email, name)
    except NoPublishedVersion:  # withdrawn between the check and the insert
        return Registration.UNAVAILABLE

    next_path = ""
    if artist is not None:
        analytics.track("artist_registered", actor=artist.user, obj=artist, source="form")
        logger.info(
            "artist registered",
            extra={"event": "artist_registered", "user": pseudonymise_user(artist.user_id)},
        )
        next_path = reverse("artists:start")
    else:
        logger.info("registration for an existing address", extra={"event": "registration_exists"})
    if not accounts.request_login(email, client_ip, link_base=link_base, next_path=next_path):
        return Registration.RATE_LIMITED
    return Registration.SENT


def artist_for(user) -> Artist | None:
    if not getattr(user, "is_authenticated", False):
        return None
    return Artist.objects.filter(user=user).first()


def seed_artists() -> int:
    """Artist records for the synthetic ``artystaNN@example.invalid`` seed users (idempotent;
    run after `accounts.services.seed_users`). Returns how many were created."""
    from django.contrib.auth import get_user_model

    created = 0
    for number in range(1, accounts.ARTIST_COUNT + 1):
        user = (
            get_user_model()
            .objects.filter(email=f"artysta{number:02d}@{accounts.SEED_DOMAIN}")
            .first()
        )
        if user is None or Artist.objects.filter(user=user).exists():
            continue
        if user.is_staff or user.is_superuser:
            continue
        Artist.objects.create(user=user, name=f"Artysta Testowy {number:02d}")
        created += 1
    return created
