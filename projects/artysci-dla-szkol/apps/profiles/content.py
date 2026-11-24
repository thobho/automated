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


def page_content_for(artist) -> PageContent:
    """Build the page content from what exists: name, city, offers, ready photos/videos.
    No AI, no main photo (US-2.6 chooses it), no texts (US-2.5 writes them)."""
    from apps.artists import materials, services
    from apps.artists.models import MaterialKind

    from .services import theme_for

    offers = [
        OfferItem(o.title, o.description, _price_note(o), _offer_tags(o))
        for o in services.offers_for(artist)
    ]
    photos, videos = [], []
    for material in materials.ready_materials(artist):
        if material.kind == MaterialKind.PHOTO:
            alt = photo_alt(material.alt_text, artist.name, len(photos) + 1)
            photos.append(PhotoItem(materials.file_url(material), alt))
        elif material.kind == MaterialKind.VIDEO and materials.file_url(material):
            videos.append(
                VideoItem(
                    title=material.title or material.original_name,
                    src=materials.file_url(material),
                    poster_url=materials.thumbnail_url(material),
                )
            )
        elif material.kind == MaterialKind.LINK and material.canonical_url:
            videos.append(
                VideoItem(
                    title=material.title,
                    link_url=material.canonical_url,
                    provider=material.get_provider_display(),
                )
            )
    return PageContent(
        slug=slugify(artist.name) or f"artysta-{artist.pk}",
        hero=Hero(name=artist.name, city=artist.city),
        offers=offers,
        videos=videos,
        photos=photos,
        theme=theme_for(artist),
    )
