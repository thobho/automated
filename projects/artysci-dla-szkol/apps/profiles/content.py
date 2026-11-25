"""The content structure of a public artist page (US-3.1) and its builder.

`PageContent` is what `profiles/page.html` renders. Later stories fill it from AI (US-2.5) and
edit it (US-2.6); `page_content_for()` fills it from existing artist data only (name, city,
offers, ready materials), with no AI call, and leaves the rest empty. A section without data is
not rendered at all (the template checks emptiness; `sections` feeds the page navigation).
"""

from dataclasses import dataclass, field

from django.utils.text import slugify
from django.utils.translation import gettext as _
from django.utils.translation import gettext_lazy

from . import contact
from .accessibility import photo_alt
from .themes import DEFAULT_THEME, theme_or_default

MIN_GALLERY_PHOTOS = 4  # US-3.1: a gallery needs at least four photos
VISIBLE_OFFERS = 6  # the rest collapses under "Pokaż pozostałe"

# Fixed section order (key, nav label). "start" has no nav entry; "inquiry" is always present.
SECTION_LABELS = {
    "facts": gettext_lazy("Informacje"),
    "about": gettext_lazy("O artyście"),
    "schools": gettext_lazy("Dla szkół i przedszkoli"),
    "offer": gettext_lazy("Oferta"),
    "videos": gettext_lazy("Nagrania"),
    "photos": gettext_lazy("Zdjęcia"),
    "faq": gettext_lazy("Pytania"),
    "inquiry": gettext_lazy("Sprawdź termin"),
}


@dataclass
class Hero:
    name: str
    tagline: str = ""
    city: str = ""
    photo_url: str = ""  # main photo; empty = typographic start section
    photo_alt: str = ""

    @property
    def initial(self) -> str:
        stripped = self.name.strip()
        return stripped[:1].upper()


@dataclass
class OfferItem:
    title: str
    description: str = ""
    price_note: str = ""  # e.g. "800 zł"; empty = no price given
    tags: tuple[str, ...] = ()


@dataclass
class VideoItem:
    """An uploaded video (`src` on the media origin) or a YouTube/Vimeo link (`link_url`).
    A link never loads anything from the provider before the click: only a local thumbnail."""

    title: str = ""
    src: str = ""
    poster_url: str = ""
    link_url: str = ""
    provider: str = ""

    def __post_init__(self):
        # Only http(s) targets: a `javascript:` or `data:` href must never reach the page.
        if self.link_url and not self.link_url.lower().startswith(("https://", "http://")):
            self.link_url = ""

    @property
    def is_file(self) -> bool:
        return bool(self.src)


@dataclass
class PhotoItem:
    url: str
    alt: str = ""
    srcset: str = ""  # "url 480w, url 960w" when several sizes are stored; empty = one size


@dataclass
class FaqItem:
    question: str
    answer: str


@dataclass
class OfferBlock:
    visible: list[OfferItem]
    more: list[OfferItem]
    price_note_once: bool  # no offer has a price: one note instead of one per item


@dataclass
class PageContent:
    slug: str
    hero: Hero
    facts: list[str] = field(default_factory=list)
    about: str = ""
    for_schools: str = ""
    offers: list[OfferItem] = field(default_factory=list)
    videos: list[VideoItem] = field(default_factory=list)
    photos: list[PhotoItem] = field(default_factory=list)
    faq: list[FaqItem] = field(default_factory=list)
    theme: str = DEFAULT_THEME.value  # slug; an unknown value falls back to the default

    def __post_init__(self):
        self.theme = theme_or_default(self.theme)
        # A video with neither a file nor a safe link has nothing to play: drop it, so the
        # section (and its heading) disappears when nothing is left.
        self.videos = [v for v in self.videos if v.src or v.link_url]

    @property
    def show_gallery(self) -> bool:
        return len(self.photos) >= MIN_GALLERY_PHOTOS

    @property
    def offer_block(self) -> OfferBlock:
        """Offers ready to show: tags every offer shares are dropped (with 2+ offers), the first
        `VISIBLE_OFFERS` are visible, and prices become one note when none has a price."""
        offers = self.offers
        shared: set[str] = set()
        if len(offers) > 1:
            shared = set(offers[0].tags)
            for offer in offers[1:]:
                shared &= set(offer.tags)
        shown = [
            OfferItem(
                o.title, o.description, o.price_note, tuple(t for t in o.tags if t not in shared)
            )
            for o in offers
        ]
        return OfferBlock(
            visible=shown[:VISIBLE_OFFERS],
            more=shown[VISIBLE_OFFERS:],
            price_note_once=bool(offers) and not any(o.price_note for o in offers),
        )

    @property
    def sections(self) -> list[tuple[str, str]]:
        """(key, label) of the sections present after the start section, in page order."""
        present = {
            "facts": bool(self.facts),
            "about": bool(self.about.strip()),
            "schools": bool(self.for_schools.strip()),
            "offer": bool(self.offers),
            "videos": bool(self.videos),
            "photos": self.show_gallery,
            "faq": bool(self.faq),
            "inquiry": True,
        }
        return [(key, str(SECTION_LABELS[key])) for key, here in present.items() if here]


def _price_note(offer) -> str:
    if offer.price_pln:
        return _("%(price)d zł") % {"price": offer.price_pln}
    return ""


def _offer_tags(offer) -> tuple[str, ...]:
    tags = []
    if offer.age_from is not None and offer.age_to is not None:
        tags.append(_("wiek %(a)d–%(b)d lat") % {"a": offer.age_from, "b": offer.age_to})
    elif offer.age_from is not None:
        tags.append(_("od %(a)d lat") % {"a": offer.age_from})
    if offer.duration_minutes:
        tags.append(_("%(n)d min") % {"n": offer.duration_minutes})
    return tuple(tags)


def _offer_items(artist) -> list[OfferItem]:
    from apps.artists import services

    return [
        OfferItem(o.title, o.description, _price_note(o), _offer_tags(o))
        for o in services.offers_for(artist)
    ]


def shown_materials(artist) -> list:
    """The ready materials a page can show (photos, video files, video links), in page order."""
    from apps.artists import materials
    from apps.artists.models import MaterialKind

    kinds = (MaterialKind.PHOTO, MaterialKind.VIDEO, MaterialKind.LINK)
    return list(
        materials.ready_materials(artist).filter(kind__in=kinds).order_by("created_at", "pk")
    )


def _video_title(material, number: int) -> str:
    """The title of a recording: never the uploaded file's name (it can carry personal data), and
    no title with contact data in it (D9: a link's title comes from YouTube/Vimeo)."""
    if material.title and not contact.contacts_in(material.title):
        return material.title
    return _("Nagranie %(n)d") % {"n": number}


def _media_items(shown, name: str, alts: dict) -> tuple[list[PhotoItem], list[VideoItem]]:
    """`alts` maps material ids to the artist's alt text (a missing one gives the fallback)."""
    from apps.artists import materials
    from apps.artists.models import MaterialKind

    photos, videos = [], []
    for material in shown:
        if material.kind == MaterialKind.PHOTO:
            alt = photo_alt(alts.get(material.pk, ""), name, len(photos) + 1)
            photos.append(PhotoItem(materials.file_url(material), alt))
        elif material.kind == MaterialKind.VIDEO and materials.file_url(material):
            videos.append(
                VideoItem(
                    title=_video_title(material, len(videos) + 1),
                    src=materials.file_url(material),
                    poster_url=materials.thumbnail_url(material),
                )
            )
        elif material.kind == MaterialKind.LINK and material.canonical_url:
            videos.append(
                VideoItem(
                    title=_video_title(material, len(videos) + 1),
                    link_url=material.canonical_url,
                    provider=material.get_provider_display(),
                )
            )
    return photos, videos


def page_content_for(artist) -> PageContent:
    """Build the page content from what exists: name, city, offers, ready photos/videos.
    No AI, no main photo (US-2.6 chooses it), no texts (US-2.5 writes them)."""
    from .services import theme_for

    shown = shown_materials(artist)
    photos, videos = _media_items(shown, artist.name, {m.pk: m.alt_text for m in shown})
    return PageContent(
        slug=slugify(artist.name) or f"artysta-{artist.pk}",
        hero=Hero(name=artist.name, city=artist.city),
        offers=_offer_items(artist),
        videos=videos,
        photos=photos,
        theme=theme_for(artist),
    )


# --- the published copy (US-2.8): everything the artist's data adds to the page, as JSON --------


def page_data(artist, shown) -> dict:
    """The artist's data as it is now, in the form `PublishedPage.data` stores."""
    return {
        "name": artist.name,
        "city": artist.city,
        "offers": [
            {
                "title": o.title,
                "description": o.description,
                "price_note": o.price_note,
                "tags": list(o.tags),
            }
            for o in _offer_items(artist)
        ],
        "materials": [{"id": m.pk, "alt": m.alt_text} for m in shown],
    }


def page_from_data(slug: str, data: dict, theme: str, shown) -> PageContent:
    """The page of a stored copy. `shown` are the materials that may be shown now."""
    alts = {item["id"]: item["alt"] for item in data["materials"]}
    photos, videos = _media_items(shown, data["name"], alts)
    return PageContent(
        slug=slug,
        hero=Hero(name=data["name"], city=data["city"]),
        offers=[
            OfferItem(o["title"], o["description"], o["price_note"], tuple(o["tags"]))
            for o in data["offers"]
        ],
        videos=videos,
        photos=photos,
        theme=theme,
    )
