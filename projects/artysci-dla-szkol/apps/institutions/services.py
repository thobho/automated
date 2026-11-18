"""Institution services: registration with RSPO suggestions (US-1.2, D1, D3, D30, D97, D98),
the RSPO CSV import and verification (US-1.4, D100).

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

import csv
import enum
import io
import logging
import re
from dataclasses import dataclass

from django.db import IntegrityError, transaction
from django.urls import reverse
from django.utils import timezone

from apps.accounts import services as accounts
from apps.analytics import services as analytics
from apps.core.logs import pseudonymise_user
from apps.trust import services as trust
from apps.trust.errors import NoPublishedVersion

from .models import (
    Institution,
    InstitutionMember,
    InstitutionType,
    RspoEntry,
    VerificationMethod,
    VerificationStatus,
    Voivodeship,
)

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


class Upsert(enum.Enum):
    CREATED = "created"
    UPDATED = "updated"
    UNCHANGED = "unchanged"


def _rspo_fields(name, institution_type, locality, voivodeship, email_domain) -> dict:
    name, locality = " ".join(name.split()), " ".join(locality.split())
    fields = {
        "name": name,
        "institution_type": institution_type,
        "locality": locality,
        "voivodeship": voivodeship,
        "name_search": normalise(name),
        "locality_search": normalise(locality),
    }
    if email_domain is not None:  # None = the source has no e-mail column: keep what we have
        fields["email_domain"] = email_domain
    return fields


def upsert_rspo_entry(
    rspo_number: int,
    name: str,
    institution_type: str,
    locality: str,
    voivodeship: str,
    email_domain: str | None = None,
) -> Upsert:
    """Insert or update one registry row by its RSPO number; nothing is written when every
    field is already the same (so a repeated import reports it as unchanged)."""
    fields = _rspo_fields(name, institution_type, locality, voivodeship, email_domain)
    entry = RspoEntry.objects.filter(rspo_number=rspo_number).first()
    if entry is None:
        try:
            with transaction.atomic():
                RspoEntry.objects.create(rspo_number=rspo_number, **fields)
            return Upsert.CREATED
        except IntegrityError:  # created concurrently (e.g. a seed during an import)
            entry = RspoEntry.objects.get(rspo_number=rspo_number)
    changed = [key for key, value in fields.items() if getattr(entry, key) != value]
    if not changed:
        return Upsert.UNCHANGED
    for key in changed:
        setattr(entry, key, fields[key])
    entry.save(update_fields=changed)
    return Upsert.UPDATED


def add_rspo_entry(
    rspo_number: int,
    name: str,
    institution_type: str,
    locality: str,
    voivodeship: str,
    email_domain: str | None = None,
) -> tuple[RspoEntry, bool]:
    """`upsert_rspo_entry()` for the seed and tests. Returns (entry, created)."""
    result = upsert_rspo_entry(
        rspo_number, name, institution_type, locality, voivodeship, email_domain
    )
    return RspoEntry.objects.get(rspo_number=rspo_number), result is Upsert.CREATED


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


# --- RSPO CSV import (US-1.4) ----------------------------------------------------------------

#: The one place that maps the export's header names to fields (header read from
#: rspo.gov.pl "Pobierz CSV" on 2026-11-18, see D100). Matching ignores case and spaces.
RSPO_COLUMNS = {
    "rspo_number": "Numer RSPO",
    "name": "Nazwa",
    "institution_type": "Typ",
    "locality": "Miejscowość",
    "voivodeship": "Województwo",
    "email": "E-mail",  # optional: without it the domain rule stays off
}
RSPO_OPTIONAL_COLUMNS = frozenset({"email"})
RSPO_DELIMITERS = (";", ",", "\t")
RSPO_ENCODINGS = ("utf-8-sig", "cp1250")  # the export is UTF-8 with BOM; Excel re-saves cp1250

#: RSPO "Typ" (case-folded) -> our type; unknown types become "other". Prefix rules below.
RSPO_TYPES = {
    "szkoła podstawowa": InstitutionType.PRIMARY_SCHOOL,
    "przedszkole": InstitutionType.KINDERGARTEN,
    "punkt przedszkolny": InstitutionType.KINDERGARTEN,
    "zespół wychowania przedszkolnego": InstitutionType.KINDERGARTEN,
    "technikum": InstitutionType.SECONDARY_SCHOOL,
    "szkoła policealna": InstitutionType.SECONDARY_SCHOOL,
    "młodzieżowy dom kultury": InstitutionType.CULTURE_CENTRE,
    "pałac młodzieży": InstitutionType.CULTURE_CENTRE,
    "ognisko pracy pozaszkolnej": InstitutionType.CULTURE_CENTRE,
    "placówki artystyczne (ognisko artystyczne)": InstitutionType.CULTURE_CENTRE,
}
RSPO_TYPE_PREFIXES = (
    ("liceum", InstitutionType.SECONDARY_SCHOOL),
    ("branżowa szkoła", InstitutionType.SECONDARY_SCHOOL),
    ("technikum", InstitutionType.SECONDARY_SCHOOL),
)
_VOIVODESHIPS = {normalise(str(label)): value for value, label in Voivodeship.choices}
_DOMAIN_RE = re.compile(r"^(?=.{4,253}$)([a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,63}$")

import_logger = logging.getLogger("apps.institutions.rspo_import")


class RspoImportError(Exception):
    """The file cannot be imported at all (unreadable, or a required column is missing)."""


@dataclass
class ImportReport:
    created: int = 0
    updated: int = 0
    unchanged: int = 0
    skipped: int = 0
    verified: int = 0
    has_email_column: bool = False

    def summary(self) -> str:
        return (
            f"created {self.created}, updated {self.updated}, unchanged {self.unchanged}, "
            f"skipped {self.skipped}, verified {self.verified}"
        )


def rspo_type(text: str) -> str:
    key = normalise(text)
    if key in RSPO_TYPES:
        return RSPO_TYPES[key]
    for prefix, value in RSPO_TYPE_PREFIXES:
        if key.startswith(prefix):
            return value
    return InstitutionType.OTHER


def email_domain(address: str) -> str:
    """The lower-case domain of an e-mail address, or "" when it does not look like one."""
    _, at, domain = (address or "").strip().rpartition("@")
    domain = domain.strip().rstrip(".").lower()
    return domain if at and _DOMAIN_RE.match(domain) else ""


def _decode(data: bytes) -> str:
    for encoding in RSPO_ENCODINGS:
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            continue
    raise RspoImportError("the file is neither UTF-8 nor Windows-1250")


def _delimiter(header_line: str) -> str:
    return max(RSPO_DELIMITERS, key=header_line.count)


def _column_map(header: list[str]) -> dict[str, int]:
    """field -> column index. Raises when a required column is missing."""
    positions = {normalise(name).replace(" ", ""): i for i, name in enumerate(header)}
    found, missing = {}, []
    for field, column in RSPO_COLUMNS.items():
        index = positions.get(normalise(column).replace(" ", ""))
        if index is not None:
            found[field] = index
        elif field not in RSPO_OPTIONAL_COLUMNS:
            missing.append(column)
    if missing:
        raise RspoImportError(f"missing columns: {', '.join(missing)}")
    return found


def _parse_row(row: list[str], columns: dict[str, int]) -> dict | None:
    """Clean values for `upsert_rspo_entry()`, or None for an invalid row."""

    def value(field: str) -> str:
        index = columns.get(field)
        return row[index].strip() if index is not None and index < len(row) else ""

    number = value("rspo_number")
    voivodeship = _VOIVODESHIPS.get(normalise(value("voivodeship")))
    name, locality = value("name"), value("locality")
    if not (number.isdigit() and 0 < int(number) < 2**31 and name and locality and voivodeship):
        return None
    return {
        "rspo_number": int(number),
        "name": name[:300],
        "institution_type": rspo_type(value("institution_type")),
        "locality": locality[:100],
        "voivodeship": voivodeship,
        "email_domain": email_domain(value("email")) if "email" in columns else None,
    }


def import_rspo(data: bytes) -> ImportReport:
    """Upsert every valid row of an RSPO CSV export by its RSPO number, then run the domain
    rule for institutions with an RSPO number. Invalid rows are counted, never logged."""
    text = _decode(data)
    first_line = text.split("\n", 1)[0]
    reader = csv.reader(io.StringIO(text), delimiter=_delimiter(first_line))
    try:
        header = next(reader)
    except StopIteration:
        raise RspoImportError("the file is empty") from None
    columns = _column_map(header)
    report = ImportReport(has_email_column="email" in columns)
    counters = {
        Upsert.CREATED: "created",
        Upsert.UPDATED: "updated",
        Upsert.UNCHANGED: "unchanged",
    }
    try:
        for row in reader:
            if not any(cell.strip() for cell in row):
                continue  # blank line
            fields = _parse_row(row, columns)
            if fields is None:
                report.skipped += 1
                continue
            attribute = counters[upsert_rspo_entry(**fields)]
            setattr(report, attribute, getattr(report, attribute) + 1)
    except csv.Error:
        raise RspoImportError(f"malformed CSV near line {reader.line_num}") from None
    report.verified = verify_all_by_domain()
    import_logger.info(  # counts only: never row content
        "rspo import finished: %s",
        report.summary(),
        extra={"event": "rspo_import", "count": report.created + report.updated},
    )
    return report


# --- verification (US-1.4, D3) ---------------------------------------------------------------

#: Free mailbox providers: anyone can get an address there, so they never verify by domain.
PUBLIC_MAILBOX_DOMAINS = frozenset(
    {
        "gmail.com",
        "googlemail.com",
        "wp.pl",
        "o2.pl",
        "onet.pl",
        "onet.eu",
        "op.pl",
        "poczta.onet.pl",
        "vp.pl",
        "interia.pl",
        "interia.eu",
        "poczta.fm",
        "tlen.pl",
        "gazeta.pl",
        "go2.pl",
        "outlook.com",
        "hotmail.com",
        "live.com",
        "yahoo.com",
        "icloud.com",
        "proton.me",
        "protonmail.com",
    }
)

verification_logger = logging.getLogger("apps.institutions.verification")


def is_verified(institution: Institution | None) -> bool:
    return (
        institution is not None and institution.verification_status == VerificationStatus.VERIFIED
    )


def verify(institution: Institution, method: str, *, by=None, now=None) -> bool:
    """Mark the institution verified. True only for the call that changed it (then
    `institution_verified` is recorded once); an already verified institution stays as it is."""
    now = now or timezone.now()
    method = VerificationMethod(method)
    updated = (
        Institution.objects.filter(pk=institution.pk)
        .exclude(verification_status=VerificationStatus.VERIFIED)
        .update(
            verification_status=VerificationStatus.VERIFIED,
            verified_at=now,
            verification_method=method,
            verified_by=by if method is VerificationMethod.MANUAL else None,
        )
    )
    if not updated:
        return False
    institution.refresh_from_db(
        fields=["verification_status", "verified_at", "verification_method", "verified_by"]
    )
    analytics.track("institution_verified", actor=by, obj=institution, method=method.value)
    extra = {"event": "institution_verified"}
    if by is not None:
        extra["user"] = pseudonymise_user(by.pk)
    verification_logger.info(
        "institution %s verified by %s", institution.pk, method.value, extra=extra
    )
    return True


def approve(institutions, by) -> int:
    """Manual approval ("Zatwierdź placówkę"). Returns how many became verified."""
    return sum(
        verify(institution, VerificationMethod.MANUAL, by=by) for institution in institutions
    )


def domain_matches(address: str, rspo_domain: str) -> bool:
    """Exact, case-insensitive domain match; public mailbox domains never match."""
    domain = email_domain(address)
    return bool(domain) and domain == rspo_domain.lower() and domain not in PUBLIC_MAILBOX_DOMAINS


def check_domain(institution: Institution) -> bool:
    """Verify by domain when a confirmed, active member's address is on the institution's
    RSPO e-mail domain. True if it became verified now."""
    if is_verified(institution) or not institution.rspo_number:
        return False
    entry = rspo_entry(institution.rspo_number)
    if entry is None or not entry.email_domain:
        return False
    members = institution.members.select_related("user").filter(
        user__is_active=True, user__email_confirmed_at__isnull=False
    )
    for member in members:
        if domain_matches(member.user.email, entry.email_domain):
            return verify(institution, VerificationMethod.DOMAIN)
    return False


def check_domain_for_user(user) -> bool:
    """Run on account confirmation (the `accounts.signals.email_confirmed` receiver)."""
    member = InstitutionMember.objects.select_related("institution").filter(user=user).first()
    return member is not None and check_domain(member.institution)


def verify_all_by_domain() -> int:
    """Run after each import: every unverified institution whose RSPO row has a domain."""
    domains = RspoEntry.objects.exclude(email_domain="").values("rspo_number")
    candidates = Institution.objects.filter(
        verification_status=VerificationStatus.UNVERIFIED, rspo_number__in=domains
    )
    return sum(check_domain(institution) for institution in candidates.iterator())
