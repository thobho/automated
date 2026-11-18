"""Legal documents: publishing versions, recording and checking acceptance (US-8.1).

The texts come from the owner's lawyer (D30); this module only stores and serves them. US-1.1
calls `record_acceptance(user, ["terms", "privacy"])` at registration.
"""

from collections.abc import Iterable
from dataclasses import dataclass

from django.db import transaction
from django.db.models import Max
from django.utils import timezone

from .errors import NoPublishedVersion, UnknownKind
from .models import LegalAcceptance, LegalDocument

Kind = LegalDocument.Kind

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
