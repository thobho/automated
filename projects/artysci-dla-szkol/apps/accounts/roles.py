"""Roles and permission rules (US-1.5, D2, D37, D99).

Every account has exactly one role, derived (not stored) from data that already exists:

- ``admin``: ``is_staff`` or ``is_superuser``. Only `manage.py create_admin` sets these (D37);
  no form or view can.
- ``artist``: the account has an `artists.Artist` record (D2: one account = one artist).
- ``institution``: the account has an `institutions.InstitutionMember` record.
- ``anonymous``: not logged in.

An account with both an artist and an institution record cannot be created through the
services; if the data says so anyway, `role_of()` fails closed with ``none`` (no role-protected
page opens) and logs a warning. ``none`` is also the answer for an account with no record at
all (for example a half-created one); it is not a role anyone can choose.

The rule functions (`can_*`) are the questions views and later features ask; they read the role
only, so the permission matrix test covers them through the views that use them.
"""

import enum
import logging

from django.apps import apps

from apps.core.logs import pseudonymise_user

logger = logging.getLogger("apps.accounts.permissions")


class Role(enum.StrEnum):
    ANONYMOUS = "anonymous"
    ARTIST = "artist"
    INSTITUTION = "institution"
    ADMIN = "admin"
    NONE = "none"  # logged in, but no (or a contradictory) role: fails closed


def _has(model: str, user) -> bool:
    app_label, model_name = model.split(".")
    return apps.get_model(app_label, model_name).objects.filter(user_id=user.pk).exists()


def role_of(user) -> Role:
    """The one role of `user` (an `AnonymousUser`, None or a `User`)."""
    if user is None or not getattr(user, "is_authenticated", False):
        return Role.ANONYMOUS
    if user.is_staff or user.is_superuser:
        return Role.ADMIN
    artist = _has("artists.Artist", user)
    institution = _has("institutions.InstitutionMember", user)
    if artist and institution:
        logger.warning(
            "account has two roles",
            extra={"event": "role_conflict", "user": pseudonymise_user(user.pk)},
        )
        return Role.NONE
    if artist:
        return Role.ARTIST
    if institution:
        return Role.INSTITUTION
    return Role.NONE


def has_any_role(user) -> bool:
    """True if the account already is an artist, an institution or an admin. Registration and
    `create_admin` use it so an account never gets a second role."""
    if user is None or getattr(user, "pk", None) is None:
        return False
    return bool(
        user.is_staff
        or user.is_superuser
        or _has("artists.Artist", user)
        or _has("institutions.InstitutionMember", user)
    )


# --- rules -----------------------------------------------------------------------------------


def can_create_artist_profile(user) -> bool:
    """Artist profile wizard (US-2.1): artists only."""
    return role_of(user) is Role.ARTIST


def can_create_inquiry(user) -> bool:
    """Sending an inquiry to an artist (E5): institutions only."""
    return role_of(user) is Role.INSTITUTION


def can_create_notice(user) -> bool:
    """Publishing a notice (E6): institutions only. E6 adds the verification rule (D3)."""
    return role_of(user) is Role.INSTITUTION


def log_denied(user, role: Role, url_name: str, required: frozenset[Role]) -> None:
    """The one `permission denied` line: pseudonymised user, role, URL name, required role.
    No e-mail, IP or query string."""
    logger.warning(
        "permission denied",
        extra={
            "event": "permission_denied",
            "user": pseudonymise_user(user.pk) if user is not None else "-",
            "role": str(role),
            "url_name": url_name,
            "required_role": ",".join(sorted(str(r) for r in required)),
        },
    )
