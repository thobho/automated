"""Publication and withdrawal of the public page (US-2.8, D6).

    blockers = publication_blockers(artist)   # Polish reasons the page cannot go public yet
    publish(artist)                           # draft/withdrawn -> published, snapshot taken
    update_published(artist)                  # "Opublikuj zmiany": a fresh snapshot, same slug
    withdraw(artist)                          # published -> withdrawn, effective at once
    page = public_page(slug)                  # PageContent of the snapshot, or None

The public page shows the snapshot (`PublishedPage`), not the live current version, so edits stay
private until the artist publishes again. Photos, videos and offers still come live from the
artist's data (they are not part of the page version, see `PageVersion`).

Slug rules: made once from the name on the first publication (Polish letters transliterated,
lowercase, hyphens), unique by a numeric suffix, never changed by renames and never reused (the
artist row keeps it after withdrawal and republication gives the same one). Reserved words
(`RESERVED_SLUGS`) are never handed out.
"""

import re
import unicodedata
from dataclasses import dataclass

from django.db import IntegrityError, transaction
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.analytics import services as analytics
from apps.artists import services as artist_services
from apps.artists.models import Artist, PublicationStatus
from apps.trust import services as trust

from . import completeness, pages
from .content import page_content_for
from .models import PublishedPage
from .themes import theme_or_default

SLUG_BASE_MAX = 60
RESERVED_SLUGS = frozenset(
    {
        "admin", "administrator", "panel", "api", "static", "media", "artysta", "artysci",
        "login", "logout", "rejestracja", "django-admin", "healthz", "readyz", "konto",
        "ustawienia", "regulamin", "pomoc", "kontakt", "szukaj", "katalog", "nowy", "new",
        "edit", "null", "none", "undefined", "www", "mail", "sitemap", "robots", "favicon",
    }
)  # fmt: skip
_EXTRA_LETTERS = str.maketrans({"ł": "l", "Ł": "L", "đ": "d", "ø": "o"})


class PublicationRefused(Exception):
    """Publishing is not allowed now; `blockers` holds the reasons (may be empty for a wrong
    state, see `message`)."""

    def __init__(self, message, blockers=()):
        super().__init__(str(message))
        self.message = message
        self.blockers = list(blockers)


@dataclass(frozen=True)
class Blocker:
    key: str
    text: str  # Polish reason (lazy)
    url_name: str  # the screen where the artist fixes it


# --- the D6 minimum ------------------------------------------------------------------------------


def publication_blockers(artist: Artist) -> list[Blocker]:
    """What is still missing for publication; an empty list means the artist may publish."""
    blockers: list[Blocker] = []
    if not artist.name.strip():
        blockers.append(Blocker("name", _("Brak nazwy artysty."), "accounts:settings"))
    if not artist.voivodeships.exists():
        blockers.append(
            Blocker("region", _("Brak regionu działania (województwa)."), "artists:basics")
        )
    version = pages.current_version(artist)
    if version is None:
        blockers.append(
            Blocker(
                "generation",
                _("Brak gotowego profilu: wygeneruj opis artysty."),
                "profiles:generation",
            )
        )
    elif not (version.content.get("about") or "").strip():
        blockers.append(Blocker("about", _("Brak tekstu „O artyście”."), "profiles:preview"))
    if not artist_services.has_offers(artist):
        blockers.append(
            Blocker("offer", _("Brak oferty: dodaj co najmniej jedną."), "artists:offers")
        )
    if not trust.has_child_protection_statement(artist):
        blockers.append(
            Blocker(
                "child_protection",
                _("Brak oświadczenia o standardach ochrony małoletnich."),
                "artists:statements",
            )
        )
    return blockers


# --- slug ----------------------------------------------------------------------------------------


def slugify_name(name: str) -> str:
    """ASCII, lowercase, hyphens; Polish letters transliterated. Empty input gives "artysta"."""
    text = unicodedata.normalize("NFKD", name.translate(_EXTRA_LETTERS))
    text = text.encode("ascii", "ignore").decode().lower()
    text = re.sub(r"[^a-z0-9]+", "-", text).strip("-")[:SLUG_BASE_MAX].strip("-")
    return text or "artysta"


def _free(slug: str) -> bool:
    return slug not in RESERVED_SLUGS and not Artist.objects.filter(slug=slug).exists()


def generate_slug(name: str) -> str:
    """A free slug for `name`: the plain form, else with -2, -3, ... (never a reserved word)."""
    base = slugify_name(name)
    if _free(base):
        return base
    number = 2
    while not _free(f"{base}-{number}"):
        number += 1
    return f"{base}-{number}"


def _assign_slug(artist: Artist) -> None:
    """Give the artist their slug once (a lost race on the unique column tries the next one)."""
    if artist.slug:
        return
    for _attempt in range(5):
        artist.slug = generate_slug(artist.name)
        try:
            with transaction.atomic():
                artist.save(update_fields=["slug"])
            return
        except IntegrityError:
            artist.slug = None
    raise PublicationRefused(_("Nie udało się nadać adresu strony. Spróbuj ponownie."))


# --- actions -------------------------------------------------------------------------------------


def _locked(artist: Artist) -> Artist:
    return Artist.objects.select_for_update().get(pk=artist.pk)


def _snapshot(artist: Artist) -> None:
    version = pages.current_version(artist)
    content, _locks = pages.current_content(artist)
    PublishedPage.objects.update_or_create(
        artist=artist,
        defaults={
            "content": content,
            "theme": page_content_for(artist).theme,
            "version_number": version.number,
        },
    )


def _require_ready(artist: Artist) -> None:
    blockers = publication_blockers(artist)
    if blockers:
        raise PublicationRefused(_("Strony nie można jeszcze opublikować."), blockers)


def publish(artist: Artist, actor=None) -> Artist:
    """First publication or republication after a withdrawal. Raises `PublicationRefused` with
    the blockers (the state stays as it was) or when the page is already published."""
    with transaction.atomic():
        artist = _locked(artist)
        if artist.publication_status == PublicationStatus.PUBLISHED:
            raise PublicationRefused(_("Strona jest już opublikowana."))
        _require_ready(artist)
        _assign_slug(artist)
        _snapshot(artist)
        artist.publication_status = PublicationStatus.PUBLISHED
        artist.published_at = timezone.now()
        artist.withdrawn_at = None
        artist.save(update_fields=["publication_status", "published_at", "withdrawn_at"])
        props = {"profile_id": artist.pk, "completeness_percent": completeness_percent(artist)}
        analytics.track("profile_published", actor=actor, obj=artist, **props)
    return artist


def update_published(artist: Artist) -> Artist:
    """ "Opublikuj zmiany": replace the snapshot with the current version. Slug and `published_at`
    stay. Refused unless the page is published."""
    with transaction.atomic():
        artist = _locked(artist)
        if artist.publication_status != PublicationStatus.PUBLISHED:
            raise PublicationRefused(_("Strona nie jest opublikowana."))
        _require_ready(artist)
        _snapshot(artist)
    return artist


def withdraw(artist: Artist, actor=None) -> Artist:
    """Take the page down at once (the snapshot is deleted; the slug stays reserved)."""
    with transaction.atomic():
        artist = _locked(artist)
        if artist.publication_status != PublicationStatus.PUBLISHED:
            raise PublicationRefused(_("Strona nie jest opublikowana."))
        artist.publication_status = PublicationStatus.WITHDRAWN
        artist.withdrawn_at = timezone.now()
        artist.save(update_fields=["publication_status", "withdrawn_at"])
        PublishedPage.objects.filter(artist=artist).delete()
        analytics.track("profile_withdrawn", actor=actor, obj=artist, profile_id=artist.pk)
    return artist


def completeness_percent(artist: Artist) -> int:
    return completeness.completeness_percent(artist)


def has_unpublished_changes(artist: Artist) -> bool:
    """True when the current version or theme differs from what the public sees."""
    snapshot = PublishedPage.objects.filter(artist=artist).first()
    version = pages.current_version(artist)
    if snapshot is None or version is None:
        return False
    return (
        snapshot.version_number != version.number
        or snapshot.theme != page_content_for(artist).theme
    )


# --- public side ---------------------------------------------------------------------------------


def public_page(slug: str):
    """`PageContent` of a published page, or None for an unknown, draft or withdrawn slug (the
    caller cannot tell these apart)."""
    artist = Artist.objects.published().filter(slug=slug).select_related("published_page").first()
    snapshot = getattr(artist, "published_page", None) if artist else None
    if snapshot is None:
        return None
    page = page_content_for(artist)
    pages.overlay_texts(page, snapshot.content)
    page.slug = artist.slug
    if snapshot.theme:
        page.theme = theme_or_default(snapshot.theme)
    return page
