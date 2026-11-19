"""Legal documents: publishing versions, recording and checking acceptance (US-8.1).

The texts come from the owner's lawyer (D30); this module only stores and serves them. US-1.1
calls `record_acceptance(user, ["terms", "privacy"])` at registration.
"""

import enum
import logging
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date, datetime

from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.db import transaction
from django.db.models import Max
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.translation import gettext

from apps.core.logs import pseudonymise_user

from .errors import InvalidStatement, NoPublishedVersion, StaleWording, UnknownKind
from .models import (
    STATEMENT_KINDS,
    ArtistStatement,
    BillingForm,
    LegalAcceptance,
    LegalDocument,
    StatementReminder,
)

Kind = LegalDocument.Kind
logger = logging.getLogger("apps.trust.statements")

# Kinds a logged-in user must (re-)accept. Cookie information is informational only (D32).
ACCEPTANCE_KINDS: tuple[str, ...] = (Kind.TERMS, Kind.PRIVACY)

PLACEHOLDER_PREFIX = "PROJEKT – tekst zastępczy, nie jest dokumentem prawnym"


def _check_kind(kind: str) -> str:
    if kind not in Kind.values:
        raise UnknownKind(kind)
    return kind


def current(kind: str) -> LegalDocument | None:
    """The newest published version of `kind`, or None when there is none."""
    _check_kind(kind)
    return LegalDocument.objects.filter(kind=kind).order_by("-version").first()


def require_current(kind: str) -> LegalDocument:
    document = current(kind)
    if document is None:
        raise NoPublishedVersion(kind)
    return document


@transaction.atomic
def publish(kind: str, body: str, material: bool) -> LegalDocument:
    """Publish a new version of `kind` (version = previous + 1). Never touches older rows.

    The first version of a kind is always material: nobody can have accepted it before.
    """
    _check_kind(kind)
    body = body.strip()
    if not body:
        raise ValueError("legal document body must not be empty")
    # Lock the newest row so concurrent publishes queue up; the unique (kind, version)
    # constraint catches the race on the very first version.
    latest = (
        LegalDocument.objects.select_for_update().filter(kind=kind).order_by("-version").first()
    )
    previous = latest.version if latest else 0
    return LegalDocument.objects.create(
        kind=kind,
        version=previous + 1,
        body=body,
        material=material or previous == 0,
        published_at=timezone.now(),
    )


@transaction.atomic
def record_acceptance(user, kinds: Iterable[str]) -> list[LegalAcceptance]:
    """Store that `user` accepts the current version of each kind, now.

    Raises NoPublishedVersion (and stores nothing) when any kind has no published version.
    Accepting a version already accepted keeps the original row.
    """
    documents = [require_current(_check_kind(kind)) for kind in dict.fromkeys(kinds)]
    now = timezone.now()
    return [
        LegalAcceptance.objects.get_or_create(
            user=user, document=document, defaults={"accepted_at": now}
        )[0]
        for document in documents
    ]


@dataclass(frozen=True)
class Pending:
    document: LegalDocument  # the current version the user is asked to accept
    accepted_version: int | None  # the newest version the user accepted before, if any


def pending(user) -> list[Pending]:
    """Pending acceptances with the version the user accepted before (for the page)."""
    if not getattr(user, "is_authenticated", False):
        return []
    result = []
    for kind in ACCEPTANCE_KINDS:
        document = current(kind)
        if document is None:
            continue
        last_material = (
            LegalDocument.objects.filter(kind=kind, material=True).aggregate(top=Max("version"))[
                "top"
            ]
            or 1
        )
        accepted = LegalAcceptance.objects.filter(user=user, document__kind=kind).aggregate(
            top=Max("document__version")
        )["top"]
        if accepted is None or accepted < last_material:
            result.append(Pending(document=document, accepted_version=accepted))
    return result


def pending_acceptances(user) -> list[LegalDocument]:
    """Current `terms`/`privacy` versions the user still has to accept.

    A kind is pending when the user has not accepted its newest material version (or any later
    one). Versions published without the material flag never ask for re-acceptance.
    """
    return [item.document for item in pending(user)]


def accept_pending(user, shown_ids: Iterable[int]) -> bool:
    """Accept what the acceptance page showed, if it is still exactly what is pending.

    Returns False (and stores nothing) when a newer version was published meanwhile, so the
    user never accepts a text they were not shown.
    """
    documents = pending_acceptances(user)
    if not documents or {d.pk for d in documents} != set(shown_ids):
        return False
    record_acceptance(user, [d.kind for d in documents])
    return True


def seed_placeholders() -> int:
    """Publish synthetic placeholder v1 of every kind that has no version (idempotent).

    Only for dev and pirx: the body is marked as not being a legal document (D30).
    Returns how many versions were created.
    """
    created = 0
    for kind, label in Kind.choices:
        if current(kind) is None:
            publish(
                kind,
                f"{PLACEHOLDER_PREFIX}.\n\n{label}: ostateczną treść przygotuje prawnik "
                "i opublikuje właściciel serwisu w panelu administracyjnym.",
                material=True,
            )
            created += 1
    return created


# --- artist statements (US-8.2, D4, D6, D7, D31, D104) ----------------------------------------
#
# The wordings are `LegalDocument` versions of the STATEMENT_KINDS. An `ArtistStatement` row is
# never edited; the newest row per (artist, kind) is what the artist currently declares. It
# counts ("Oświadczenie artysty") only when it is not a withdrawal, refers to the current version
# of its wording and, for OC, its `valid_until` (if any) has not passed.


class Status(enum.StrEnum):
    UNAVAILABLE = "unavailable"  # no published wording: cannot be made yet
    NOT_MADE = "not_made"  # never made, or withdrawn
    CURRENT = "current"  # counts
    OUTDATED = "outdated"  # made on an older wording: "wymaga ponownego oświadczenia"
    EXPIRED = "expired"  # OC whose valid_until passed


@dataclass(frozen=True)
class StatementState:
    kind: str
    label: str
    document: LegalDocument | None  # the current wording, None when none is published
    latest: ArtistStatement | None  # the newest row (None if never made or withdrawn)
    status: Status

    @property
    def counts(self) -> bool:
        return self.status is Status.CURRENT


def _now(now: datetime | None) -> datetime:
    return now if now is not None else timezone.now()


def _expired(statement: ArtistStatement, now: datetime) -> bool:
    """OC with a date stops counting the day after `valid_until` (Polish local date)."""
    return statement.valid_until is not None and statement.valid_until < timezone.localdate(now)


def _check_statement_kind(kind: str) -> str:
    if kind not in STATEMENT_KINDS:
        raise UnknownKind(kind)
    return kind


def _latest_rows(artist) -> dict[str, ArtistStatement]:
    """{kind: newest row} for the artist (withdrawals included)."""
    latest: dict[str, ArtistStatement] = {}
    for row in ArtistStatement.objects.filter(artist=artist).select_related("document"):
        latest.setdefault(row.kind, row)  # Meta.ordering: newest first
    return latest


def _current_documents() -> dict[str, LegalDocument]:
    documents: dict[str, LegalDocument] = {}
    for document in LegalDocument.objects.filter(kind__in=STATEMENT_KINDS).order_by("-version"):
        documents.setdefault(document.kind, document)
    return documents


def statement_overview(artist, *, now: datetime | None = None) -> list[StatementState]:
    """Every statement kind in display order with the current wording and the artist's status."""
    now = _now(now)
    latest, documents = _latest_rows(artist), _current_documents()
    states = []
    for kind in STATEMENT_KINDS:
        document, row = documents.get(kind), latest.get(kind)
        if row is not None and row.withdrawn:
            row = None
        if document is None:
            status = Status.UNAVAILABLE
        elif row is None:
            status = Status.NOT_MADE
        elif row.document_id != document.pk:
            status = Status.OUTDATED
        elif _expired(row, now):
            status = Status.EXPIRED
        else:
            status = Status.CURRENT
        states.append(StatementState(kind, Kind(kind).label, document, row, status))
    return states


def current_statements(artist, *, now: datetime | None = None) -> list[ArtistStatement]:
    """The rows that count now (display order): shown as "Oświadczenie artysty"."""
    return [s.latest for s in statement_overview(artist, now=now) if s.counts]


def has_child_protection_statement(artist, *, now: datetime | None = None) -> bool:
    """D6: publication needs a counted child-protection statement (US-2.8 calls this)."""
    if artist is None:
        return False
    return any(s.kind == Kind.CHILD_PROTECTION for s in current_statements(artist, now=now))


def _clean_statement_data(kind, billing_form, valid_until) -> tuple[str, date | None]:
    if kind == Kind.BILLING_FORM:
        if billing_form not in BillingForm.values:
            raise InvalidStatement("billing_form must be 'faktura' or 'rachunek'")
    elif billing_form:
        raise InvalidStatement(f"{kind} takes no billing form")
    if valid_until is not None:
        if kind != Kind.INSURANCE:
            raise InvalidStatement(f"{kind} takes no valid_until date")
        if not isinstance(valid_until, date) or isinstance(valid_until, datetime):
            raise InvalidStatement("valid_until must be a date")
    return billing_form or "", valid_until


def _log(message: str, event: str, artist, kind: str) -> None:
    logger.info(
        f"{message} kind={kind}",
        extra={"event": event, "user": pseudonymise_user(artist.user_id)},
    )


@transaction.atomic
def make_statement(
    artist,
    kind: str,
    *,
    billing_form: str = "",
    valid_until: date | None = None,
    shown_document_id: int | None = None,
    now: datetime | None = None,
) -> ArtistStatement:
    """Store that `artist` makes the statement `kind` on its current wording, at `now`.

    `billing_form` (``faktura``/``rachunek``) is required for the billing form and refused
    elsewhere; `valid_until` is optional and only for OC. With `shown_document_id` (the
    version the page showed) a newer publication in between raises `StaleWording`. Raises
    `UnknownKind`, `NoPublishedVersion` or `InvalidStatement`; nothing is stored then.
    """
    _check_statement_kind(kind)
    billing_form, valid_until = _clean_statement_data(kind, billing_form, valid_until)
    document = require_current(kind)
    if shown_document_id is not None and int(shown_document_id) != document.pk:
        raise StaleWording(kind)
    statement = ArtistStatement.objects.create(
        artist=artist,
        kind=kind,
        document=document,
        made_at=_now(now),
        billing_form=billing_form,
        valid_until=valid_until,
    )
    _log("artist statement made", "artist_statement_made", artist, kind)
    return statement


@transaction.atomic
def withdraw_statement(artist, kind: str, *, now: datetime | None = None) -> ArtistStatement | None:
    """Store a withdrawal row (it references the current wording, if any). None when there is
    nothing to withdraw (never made or already withdrawn)."""
    _check_statement_kind(kind)
    row = _latest_rows(artist).get(kind)
    if row is None or row.withdrawn:
        return None
    statement = ArtistStatement.objects.create(
        artist=artist, kind=kind, document=current(kind), made_at=_now(now), withdrawn=True
    )
    _log("artist statement withdrawn", "artist_statement_withdrawn", artist, kind)
    return statement


# --- OC expiry reminder (daily job) ------------------------------------------------------------


def expired_insurance_statements(*, now: datetime | None = None) -> list[ArtistStatement]:
    """Newest OC rows (one per artist, not withdrawn) whose `valid_until` passed and that have
    no reminder yet."""
    now = _now(now)
    candidates = (
        ArtistStatement.objects.filter(
            kind=Kind.INSURANCE,
            withdrawn=False,
            valid_until__lt=timezone.localdate(now),
            reminder__isnull=True,
        )
        .select_related("artist")
        .order_by("pk")
    )
    expired = []
    for row in candidates:
        newest = (
            ArtistStatement.objects.filter(artist_id=row.artist_id, kind=Kind.INSURANCE)
            .values_list("pk", flat=True)
            .first()
        )
        if newest == row.pk:  # a renewal or withdrawal supersedes it: no reminder
            expired.append(row)
    return expired


def queue_insurance_reminders(*, now: datetime | None = None) -> int:
    """Daily job body: queue one reminder e-mail per expired OC statement, once per expiry.
    Only the statement id goes into the job. Returns how many were queued."""
    from apps.core import jobs

    from . import tasks  # tasks import this module

    now = _now(now)
    queued = 0
    for row in expired_insurance_statements(now=now):
        with transaction.atomic():
            _, created = StatementReminder.objects.get_or_create(
                statement=row, defaults={"queued_at": now}
            )
            if not created:
                continue
            jobs.enqueue(
                tasks.send_insurance_reminder,
                idempotency_key=f"trust.oc_reminder.{row.pk}",
                statement_id=row.pk,
            )
        queued += 1
        _log("insurance reminder queued", "insurance_reminder_queued", row.artist, row.kind)
    return queued


def send_insurance_reminder(statement_id: int) -> bool:
    """E-mail job body: the plain-text Polish reminder to the artist. False (nothing sent) for
    a missing statement or an inactive account."""
    row = (
        ArtistStatement.objects.select_related("artist")
        .filter(pk=statement_id, kind=Kind.INSURANCE, withdrawn=False)
        .first()
    )
    if row is None:
        return False
    user = get_user_model().objects.filter(pk=row.artist.user_id, is_active=True).first()
    if user is None:
        return False
    body = render_to_string(
        "trust/email/insurance_expired.txt",
        {"valid_until": row.valid_until},
    )
    send_mail(gettext("Twoje oświadczenie o ubezpieczeniu OC wygasło"), body, None, [user.email])
    _log("insurance reminder sent", "insurance_reminder_sent", row.artist, row.kind)
    return True
