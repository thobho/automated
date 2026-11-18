"""Institution services: registration with RSPO suggestions (US-1.2, D1, D3, D30, D97, D98).

`register_institution()` follows the artist registration flow (`apps.artists.services`, D97):
the legal documents must be published, the login e-mail sending limits are checked before
anything is created, then one transaction creates the unconfirmed user, the institution (or
links to the existing one with the same RSPO number, `needs_review=True`), the member and the
acceptance of the current terms and privacy policy. The login link and code go out through
`accounts.services.request_login()`. An address that already has an account gets the same
answer and a normal login e-mail; nothing is created or recorded for it.

When the user picks an RSPO suggestion, only its number counts: name, type, locality and
voivodeship are copied from `RspoEntry`, whatever the client sent. Logs carry a pseudonymised
user only; events carry enums and booleans only (D39).
"""

import enum
import logging
from dataclasses import dataclass

from django.db import IntegrityError, transaction
from django.urls import reverse

from apps.accounts import services as accounts
from apps.analytics import services as analytics
from apps.core.logs import pseudonymise_user
from apps.trust import services as trust
from apps.trust.errors import NoPublishedVersion

from .models import Institution, InstitutionMember, InstitutionType, RspoEntry, Voivodeship

logger = logging.getLogger("apps.institutions.registration")

REQUIRED_DOCUMENTS = (trust.Kind.TERMS, trust.Kind.PRIVACY)
SUGGESTION_MIN_CHARS = 3
SUGGESTION_LIMIT = 10
QUERY_MAX_CHARS = 200


class Registration(enum.Enum):
    SENT = "sent"  # same for a new and an existing address
    RATE_LIMITED = "rate_limited"
    UNAVAILABLE = "unavailable"  # no published terms or privacy version


@dataclass(frozen=True)
class InstitutionDetails:
    """What the form typed. Ignored when an RSPO number is chosen."""

    institution_type: str = ""
    name: str = ""
    locality: str = ""
    voivodeship: str = ""


# --- RSPO ------------------------------------------------------------------------------------


def normalise(text: str) -> str:
    """Case-folded, single-spaced text for matching (Python does it, so 'Ł' == 'ł' on every
    database)."""
    return " ".join(text.casefold().split())


def add_rspo_entry(
    rspo_number: int, name: str, institution_type: str, locality: str, voivodeship: str
) -> tuple[RspoEntry, bool]:
    """Insert or update one registry row by its RSPO number (the import in US-1.4 and the
    seed use this). Returns (entry, created)."""
    name, locality = " ".join(name.split()), " ".join(locality.split())
    return RspoEntry.objects.update_or_create(
        rspo_number=rspo_number,
        defaults={
            "name": name,
            "institution_type": institution_type,
            "locality": locality,
            "voivodeship": voivodeship,
            "name_search": normalise(name),
            "locality_search": normalise(locality),
        },
    )


def suggest_rspo(name: str, locality: str = "") -> list[RspoEntry]:
    """At most SUGGESTION_LIMIT registry rows whose name contains every word of `name`
    (case-insensitive), narrowed to localities starting with `locality` when given. Nothing
    for fewer than SUGGESTION_MIN_CHARS characters."""
    query = normalise(name[:QUERY_MAX_CHARS])
    if len(query) < SUGGESTION_MIN_CHARS:
        return []
    entries = RspoEntry.objects.all()
    for word in query.split():
        entries = entries.filter(name_search__contains=word)
    place = normalise(locality[:QUERY_MAX_CHARS])
    if place:
        entries = entries.filter(locality_search__startswith=place)
    return list(entries[:SUGGESTION_LIMIT])


def rspo_entry(rspo_number: int | None) -> RspoEntry | None:
    if not rspo_number:
        return None
    return RspoEntry.objects.filter(rspo_number=rspo_number).first()


SEED_RSPO = [
    # Synthetic rows for `make seed` and manual checks (numbers from 900001: not real RSPO).
    (
        900001,
        "Szkoła Podstawowa nr 5 im. Testowej Patronki",
        "primary_school",
        "Wrocław",
        "dolnoslaskie",
    ),
    (900002, "Szkoła Podstawowa nr 5", "primary_school", "Opole", "opolskie"),
    (900003, "Przedszkole Publiczne nr 12 Testowe Słoneczko", "kindergarten", "Łódź", "lodzkie"),
    (900004, "Liceum Ogólnokształcące nr 3 Testowe", "secondary_school", "Kraków", "malopolskie"),
    (900005, "Gminny Ośrodek Kultury Testowy", "culture_centre", "Zębowice", "opolskie"),
    (900006, "Szkoła Podstawowa nr 1 Testowa", "primary_school", "Gdańsk", "pomorskie"),
]


def seed_rspo() -> int:
    """Synthetic registry rows (idempotent). Returns how many were created."""
    return sum(add_rspo_entry(*row)[1] for row in SEED_RSPO)


def seed_members() -> int:
    """An institution and a member link for each synthetic ``szkolaNN@example.invalid`` seed
    user, from the synthetic RSPO rows (idempotent; run after `seed_users` and `seed_rspo`).
    Returns how many members were created."""
    from django.contrib.auth import get_user_model

    created = 0
    for number, row in enumerate(SEED_RSPO[: accounts.INSTITUTION_COUNT], start=1):
        user = (
            get_user_model()
            .objects.filter(email=f"szkola{number:02d}@{accounts.SEED_DOMAIN}")
            .first()
        )
        if user is None or user.is_staff or user.is_superuser:
            continue
        if InstitutionMember.objects.filter(user=user).exists():
            continue
        entry = RspoEntry.objects.get(rspo_number=row[0])
        institution, _ = _institution_for(InstitutionDetails(), entry)
        InstitutionMember.objects.create(user=user, institution=institution, function="director")
        created += 1
    return created


# --- registration ----------------------------------------------------------------------------


def documents_published() -> bool:
    return all(trust.current(kind) is not None for kind in REQUIRED_DOCUMENTS)


def _institution_for(details: InstitutionDetails, entry: RspoEntry | None):
    """(institution, linked_existing). A chosen RSPO row decides every field."""
    if entry is None:
        institution = Institution.objects.create(
            institution_type=InstitutionType(details.institution_type),
            name=details.name.strip(),
            locality=details.locality.strip(),
            voivodeship=Voivodeship(details.voivodeship),
        )
        return institution, False
    existing = Institution.objects.filter(rspo_number=entry.rspo_number).first()
    if existing is not None:
        return existing, True
    try:
        with transaction.atomic():
            institution = Institution.objects.create(
                institution_type=entry.institution_type,
                name=entry.name,
                locality=entry.locality,
                voivodeship=entry.voivodeship,
                rspo_number=entry.rspo_number,
            )
        return institution, False
    except IntegrityError:  # the same RSPO number registered concurrently
        return Institution.objects.get(rspo_number=entry.rspo_number), True


def _create(
    email: str, details: InstitutionDetails, function: str, entry: RspoEntry | None
) -> tuple[InstitutionMember, bool] | None:
    """New user + institution (or link) + member + acceptance, all or nothing.
    None if the address is taken. Returns (member, linked_existing)."""
    with transaction.atomic():
        user, created = accounts.get_or_create_unconfirmed_user(email)
        if not created:
            return None
        institution, linked = _institution_for(details, entry)
        member = InstitutionMember.objects.create(
            user=user, institution=institution, function=function, needs_review=linked
        )
        trust.record_acceptance(user, REQUIRED_DOCUMENTS)  # raises -> rollback
    return member, linked


def register_institution(
    email: str,
    details: InstitutionDetails,
    function: str,
    client_ip: str,
    *,
    rspo_number: int | None = None,
    link_base: str,
) -> Registration:
    """Register an institution account and send the login e-mail. See the module docstring.
    `rspo_number` must be an existing `RspoEntry` (the form checks it)."""
    if not documents_published():
        logger.warning(
            "registration refused, no published legal documents",
            extra={"event": "registration_unavailable"},
        )
        return Registration.UNAVAILABLE
    if not accounts.login_email_allowed(email, client_ip):
        logger.warning("registration rate limited", extra={"event": "registration_rate_limited"})
        return Registration.RATE_LIMITED
    entry = RspoEntry.objects.get(rspo_number=rspo_number) if rspo_number else None
    try:
        result = _create(email, details, function, entry)
    except NoPublishedVersion:  # withdrawn between the check and the insert
        return Registration.UNAVAILABLE

    next_path = ""
    if result is not None:
        member, linked = result
        analytics.track(
            "institution_registered",
            actor=member.user,
            obj=member.institution,
            institution_type=member.institution.institution_type,
            rspo_matched=entry is not None,
            linked_existing=linked,
        )
        logger.info(
            "institution member linked for review" if linked else "institution registered",
            extra={
                "event": "institution_member_linked" if linked else "institution_registered",
                "user": pseudonymise_user(member.user_id),
            },
        )
        next_path = reverse("institutions:start")
    else:
        logger.info("registration for an existing address", extra={"event": "registration_exists"})
    if not accounts.request_login(email, client_ip, link_base=link_base, next_path=next_path):
        return Registration.RATE_LIMITED
    return Registration.SENT


def member_for(user) -> InstitutionMember | None:
    if not getattr(user, "is_authenticated", False):
        return None
    return InstitutionMember.objects.select_related("institution").filter(user=user).first()
