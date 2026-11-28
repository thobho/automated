"""The public catalog (US-4.1, D119): the read model and the list of cards.

    sync(artist)           # publish, "Opublikuj zmiany": row from the snapshot, or no row
    remove(artist)         # withdrawal, deactivation: the row goes at once
    rebuild_all()          # every row again (management command `rebuild_catalog`), idempotent
    page = cards_page(n)   # 24 cards of page n, or None for an invalid page (the view gives 404)

The row is built only from the publication snapshot (`PublishedPage`), never from live artist
data, so a change is public only after "Opublikuj zmiany". `Artist.objects.published()` stays the
only definition of "publicly visible": the list asks it on every request, so a deactivated account
disappears at once even before its row is removed. No e-mail or phone is copied (D9).
"""

from dataclasses import dataclass, replace

from django.core.paginator import EmptyPage, Paginator
from django.db import transaction

from apps.artists.models import Artist, ArtistType, Audience, Material, MaterialKind, ScanStatus
from apps.core.regions import Voivodeship

from . import filters as filters_module
from . import search
from .filters import Filters
from .models import CatalogEntry

PAGE_SIZE = 24
_PHOTO_MAX_WIDTH = 480  # shown size of a card photo when the stored size is unknown
_PHOTO_FALLBACK = (480, 360)


def is_verified(artist_id: int) -> bool:
    """Whether the artist shows the "zweryfikowany" badge. Artist verification comes with US-8.3;
    until then nobody is verified. The one place that decides."""
    return False


# --- writing the read model ----------------------------------------------------------------------


def _lowest_price(offers: list[dict]) -> int | None:
    prices = [o["price"] for o in offers if o["price"]]
    return min(prices) if prices else None


def _main_photo(data: dict) -> tuple[int | None, str]:
    """The first published material that is a photo (a deleted or unfinished one is skipped)."""
    listed = {item["id"]: item.get("alt", "") for item in data.get("materials", [])}
    photos = set(
        Material.objects.filter(
            pk__in=listed, kind=MaterialKind.PHOTO, status=ScanStatus.READY
        ).values_list("pk", flat=True)
    )
    for material_id in listed:  # snapshot order
        if material_id in photos:
            return material_id, listed[material_id][:200]
    return None, ""


def _values(artist: Artist, snapshot) -> dict:
    data = snapshot.data
    offers = [
        {"price": o.get("price_pln"), "duration": o.get("duration_minutes")}
        for o in data.get("offers", [])
    ]
    photo_id, photo_alt = _main_photo(data)
    return {
        "slug": artist.slug,
        "name": data["name"],
        "artist_type": data.get("artist_type", ""),
        "voivodeships": list(data.get("regions", [])),
        "age_groups": list(data.get("age_groups", [])),  # an older snapshot has none
        "topics": list(data.get("topics", [])),
        "forms": list(data.get("forms", [])),
        "main_photo_id": photo_id,
        "main_photo_alt": photo_alt,
        "price_from": _lowest_price(offers),
        "offers": offers,
        "published_at": snapshot.updated_at,
        **search.index_terms(
            data["name"],
            [o.get("title", "") for o in data.get("offers", [])],
            [t.get("name", "") for t in data.get("topics", [])],
        ),
    }


def sync(artist: Artist) -> bool:
    """Make the artist's row match the snapshot: written when the artist is publicly visible and
    has a snapshot, removed otherwise. Returns whether a row exists afterwards."""
    from apps.profiles.models import PublishedPage

    with transaction.atomic():
        current = Artist.objects.published().filter(pk=artist.pk, slug__isnull=False).first()
        snapshot = PublishedPage.objects.filter(artist_id=artist.pk).first() if current else None
        if snapshot is None:
            CatalogEntry.objects.filter(artist_id=artist.pk).delete()
            return False
        artist = current
        values = _values(artist, snapshot)
        # Slugs are never reused; still clear a stale row holding it so the unique index is safe.
        CatalogEntry.objects.filter(slug=values["slug"]).exclude(artist_id=artist.pk).delete()
        CatalogEntry.objects.update_or_create(artist=artist, defaults=values)
    return True


def remove(artist: Artist) -> None:
    CatalogEntry.objects.filter(artist_id=artist.pk).delete()


def rebuild_all() -> int:
    """Rows for every publicly visible artist with a snapshot, no row for anyone else.
    Returns the number of rows. Running it twice gives the same rows."""
    count = 0
    with transaction.atomic():
        visible = Artist.objects.published().filter(slug__isnull=False)
        CatalogEntry.objects.exclude(artist__in=visible).delete()
        for artist in visible.iterator():
            count += sync(artist)
    return count


# --- reading: the list of cards ------------------------------------------------------------------


@dataclass(frozen=True)
class Card:
    slug: str
    name: str
    initial: str
    type_label: str
    regions: list[str]
    age_groups: list[str]
    price_from: int | None
    verified: bool
    photo_url: str = ""
    photo_alt: str = ""
    photo_width: int = 0
    photo_height: int = 0


@dataclass(frozen=True)
class CardsPage:
    cards: list[Card]
    number: int
    pages: int
    total: int
    previous: int | None
    next: int | None

    @property
    def numbers(self) -> list[int]:
        """Page links: the first, the last and two on each side of the current page."""
        wanted = {1, self.pages, *range(self.number - 2, self.number + 3)}
        return sorted(n for n in wanted if 1 <= n <= self.pages)


def _labels(choices, codes) -> list[str]:
    known = dict(choices)
    return [str(known[code]) for code in codes if code in known]


def _photos(entries) -> dict:
    """`{material id: Material}` of the main photos that may be shown now: still there and ready,
    and the artist still confirms the rights (D4, D7), as on the profile page."""
    from apps.profiles.inputs import materials_allowed

    ids = [e.main_photo_id for e in entries if e.main_photo_id]
    found = {
        m.pk: m
        for m in Material.objects.filter(
            pk__in=ids, kind=MaterialKind.PHOTO, status=ScanStatus.READY
        )
    }
    allowed = {}
    for entry in entries:
        material = found.get(entry.main_photo_id)
        if material is not None and entry.artist_id not in allowed:
            allowed[entry.artist_id] = materials_allowed(entry.artist)
    return {m.pk: m for m in found.values() if allowed.get(m.artist_id)}


def _card(entry: CatalogEntry, photos: dict) -> Card:
    from apps.artists import materials

    card = Card(
        slug=entry.slug,
        name=entry.name,
        initial=entry.name.strip()[:1].upper(),
        type_label=next(iter(_labels(ArtistType.choices, [entry.artist_type])), ""),
        regions=_labels(Voivodeship.choices, entry.voivodeships),
        age_groups=_labels(Audience.choices, entry.age_groups),
        price_from=entry.price_from,
        verified=is_verified(entry.artist_id),
    )
    material = photos.get(entry.main_photo_id)
    url = materials.file_url(material) if material else ""
    if not url:
        return card
    width, height = _PHOTO_FALLBACK
    if material.width and material.height:
        width, height = material.width, material.height
    scale = min(1, _PHOTO_MAX_WIDTH / width)
    return replace(
        card,
        photo_url=url,
        photo_alt=entry.main_photo_alt or entry.name,
        photo_width=round(width * scale),
        photo_height=round(height * scale),
    )


def public_entries():
    """Rows of the publicly visible artists, in the temporary order: the latest publication first,
    then the highest id (stable across pages). D16 ordering comes with US-4.4."""
    entries = CatalogEntry.objects.filter(artist__in=Artist.objects.published())
    return entries.select_related("artist").order_by("-published_at", "-id")


def cards_page(raw_number: str | None, filters: Filters | None = None) -> CardsPage | None:
    """The cards of one page; `raw_number` is the `?strona=` text (None = page 1), `filters` the
    parsed filters of US-4.2. None for anything that is not a page that exists."""
    if raw_number is None:
        raw_number = "1"
    if not (raw_number.isascii() and raw_number.isdigit() and len(raw_number) <= 9):
        return None
    filters = filters or Filters()
    narrowed = filters_module.apply(public_entries(), filters)
    ranked = search.search(narrowed, filters.q) if filters.q else None
    paginator = Paginator(narrowed if ranked is None else ranked, PAGE_SIZE)
    try:
        page = paginator.page(int(raw_number))
    except EmptyPage:
        return None
    entries = list(page.object_list)
    photos = _photos(entries)
    return CardsPage(
        cards=[_card(entry, photos) for entry in entries],
        number=page.number,
        pages=paginator.num_pages,
        total=paginator.count,
        previous=page.previous_page_number() if page.has_previous() else None,
        next=page.next_page_number() if page.has_next() else None,
    )
