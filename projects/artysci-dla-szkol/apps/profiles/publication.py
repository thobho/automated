"""Publication and withdrawal of the public page (US-2.8, D6).

    blockers = publication_blockers(artist)   # Polish reasons the page cannot go public yet
    publish(artist)                           # draft/withdrawn -> published, snapshot taken
    update_published(artist)                  # "Opublikuj zmiany": a fresh snapshot, same slug
    withdraw(artist)                          # published -> withdrawn, effective at once
    page = public_page(slug)                  # PageContent of the snapshot, or None

The public page shows the snapshot (`PublishedPage`), never live data: the texts and theme of the
version, name, city, offers, the list of materials and their alt texts. Later edits and uploads
stay private until the artist publishes again. Two things only ever *remove* something at once: a
deleted material is gone, and without a current "Prawa do materiałów" statement (D4, D7) no photo,
video or link shows.

No e-mail or phone goes public (D9): `publication_blockers` refuses a page that has one.

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
from apps.artists.models import Artist, PublicationStatus
from apps.trust import services as trust

from . import completeness, pages
from .contact import contacts_in
from .content import page_data, page_from_data, shown_materials
from .inputs import materials_allowed
from .models import PublishedPage
from .services import theme_for

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


# --- what publishing would show ------------------------------------------------------------------


@dataclass(frozen=True)
class _Draft:
    """What publishing would make public now. Checked and stored as one value, so an edit between
    the check and the save cannot slip through."""

    content: dict  # texts of the current version
    data: dict  # `content.page_data`
    theme: str
    version_number: int | None  # None = no version yet


def _draft(artist: Artist) -> _Draft:
    version = pages.current_version(artist)
    # Without the rights statement nothing is listed, so a later statement alone shows nothing.
    materials = shown_materials(artist) if materials_allowed(artist) else []
    return _Draft(
        content={**pages.empty_content(), **(version.content if version else {})},
        data=page_data(artist, materials),
        theme=theme_for(artist),
        version_number=version.number if version else None,
    )


# --- the D6 minimum and D9 -----------------------------------------------------------------------


def publication_blockers(artist: Artist) -> list[Blocker]:
    """What stands in the way of publication; an empty list means the artist may publish."""
    return _blockers(artist, _draft(artist))


def _blockers(artist: Artist, draft: _Draft) -> list[Blocker]:
    blockers: list[Blocker] = []
    if not draft.data["name"].strip():
        blockers.append(Blocker("name", _("Brak nazwy artysty."), "accounts:settings"))
    if not artist.voivodeships.exists():
        blockers.append(
            Blocker("region", _("Brak regionu działania (województwa)."), "artists:basics")
        )
    if draft.version_number is None:
        blockers.append(
            Blocker(
                "generation",
                _("Brak gotowego profilu: wygeneruj opis artysty."),
                "profiles:generation",
            )
        )
    elif not (draft.content["about"] or "").strip():
        blockers.append(Blocker("about", _("Brak tekstu „O artyście”."), "profiles:preview"))
    if not draft.data["offers"]:
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
    return blockers + _contact_blockers(artist, draft)


def _contact_blockers(artist: Artist, draft: _Draft) -> list[Blocker]:
    """Contact data in what would go public (D9): one reason per place, naming what was found
    (only the artist sees it). Titles of recordings are handled in `content._video_title`."""
    content, data = draft.content, draft.data
    texts = [content["tagline"], content["about"], content["for_schools"], *content["facts"]]
    texts += [text for item in content["faq"] for text in item.values()]
    offers = [text for offer in data["offers"] for text in (offer["title"], offer["description"])]
    alts = [item["alt"] for item in data["materials"]]
    places = (
        ("contact_name", _("nazwa artysty"), "accounts:settings", [data["name"]]),
        ("contact_city", _("miasto"), "artists:basics", [data["city"]]),
        ("contact_texts", _("teksty strony"), "profiles:preview", texts),
        ("contact_offers", _("oferty"), "artists:offers", offers),
        ("contact_photos", _("opisy zdjęć"), "artists:materials", alts),
    )
    reason = _("Dane kontaktowe nie mogą być publiczne (%(place)s). Usuń: %(found)s")
    blockers = []
    for key, place, url_name, values in places:
        found = [hit for value in values for hit in contacts_in(value, artist.user.email)]
        if found:
            listed = ", ".join(dict.fromkeys(found))
            blockers.append(Blocker(key, reason % {"place": place, "found": listed}, url_name))
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


def _ready_draft(artist: Artist) -> _Draft:
    draft = _draft(artist)
    blockers = _blockers(artist, draft)
    if blockers:
        raise PublicationRefused(_("Strony nie można jeszcze opublikować."), blockers)
    return draft


def _save_snapshot(artist: Artist, draft: _Draft) -> None:
    PublishedPage.objects.update_or_create(
        artist=artist,
        defaults={
            "content": draft.content,
            "data": draft.data,
            "theme": draft.theme,
            "version_number": draft.version_number,
        },
    )


def publish(artist: Artist, actor=None) -> Artist:
    """First publication or republication after a withdrawal. Raises `PublicationRefused` with
    the blockers (the state stays as it was) or when the page is already published."""
    with transaction.atomic():
        artist = _locked(artist)
        if artist.publication_status == PublicationStatus.PUBLISHED:
            raise PublicationRefused(_("Strona jest już opublikowana."))
        draft = _ready_draft(artist)
        _assign_slug(artist)
        _save_snapshot(artist, draft)
        artist.publication_status = PublicationStatus.PUBLISHED
        artist.published_at = timezone.now()
        artist.withdrawn_at = None
        artist.save(update_fields=["publication_status", "published_at", "withdrawn_at"])
        props = {"profile_id": artist.pk, "completeness_percent": completeness_percent(artist)}
        analytics.track("profile_published", actor=actor, obj=artist, **props)
    return artist


def update_published(artist: Artist) -> Artist:
    """ "Opublikuj zmiany": replace the snapshot with the current state. Slug and `published_at`
    stay. Refused unless the page is published, and with the blockers like `publish`."""
    with transaction.atomic():
        artist = _locked(artist)
        if artist.publication_status != PublicationStatus.PUBLISHED:
            raise PublicationRefused(_("Strona nie jest opublikowana."))
        _save_snapshot(artist, _ready_draft(artist))
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
    """True when "Opublikuj zmiany" would change what the public sees."""
    snapshot = PublishedPage.objects.filter(artist=artist).first()
    if snapshot is None:
        return False
    draft = _draft(artist)
    ids = {m.pk for m in _visible_materials(artist, snapshot)}
    visible = [item for item in snapshot.data["materials"] if item["id"] in ids]
    return (
        snapshot.version_number != draft.version_number
        or snapshot.theme != draft.theme
        or {**snapshot.data, "materials": visible} != draft.data
    )


def materials_hidden(artist: Artist) -> bool:
    """The artist has photos or videos that stay off the public page: no rights statement."""
    return not materials_allowed(artist) and bool(shown_materials(artist))


# --- public side ---------------------------------------------------------------------------------


def _visible_materials(artist: Artist, snapshot: PublishedPage) -> list:
    """The published materials that may be shown now: still there and ready, and the artist
    currently confirms the rights to them (checked on every request)."""
    if not materials_allowed(artist):
        return []
    published = {item["id"] for item in snapshot.data["materials"]}
    return [m for m in shown_materials(artist) if m.pk in published]


def public_page(slug: str):
    """`PageContent` of a published page, or None for an unknown, draft or withdrawn slug (the
    caller cannot tell these apart)."""
    artist = Artist.objects.published().filter(slug=slug).select_related("published_page").first()
    snapshot = getattr(artist, "published_page", None) if artist else None
    if snapshot is None:
        return None
    visible = _visible_materials(artist, snapshot)
    page = page_from_data(artist.slug, snapshot.data, snapshot.theme, visible)
    pages.overlay_texts(page, snapshot.content)
    return page
