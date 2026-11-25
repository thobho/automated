"""What search engines and link previews see of a public artist page (US-3.4).

    meta = page_meta(content)  # title, description, canonical, Open Graph, JSON-LD

Everything comes from the published snapshot (`PageContent`), never from live data, and holds no
e-mail, phone or street address (D9): publication already refuses a page with contact data, and
the JSON-LD only carries name, description, image, url, regions and offer names. The JSON-LD is
data (`application/ld+json`), not script execution, so the strict CSP needs no nonce; `<`, `>`,
`&` and the line separators are escaped so no text can break out of the element.
"""

import datetime
import html
import json
import re
from dataclasses import dataclass
from xml.sax.saxutils import escape

from django.conf import settings
from django.templatetags.static import static
from django.urls import reverse
from django.utils.html import strip_tags
from django.utils.safestring import SafeString, mark_safe

from apps.artists.models import ArtistType
from apps.core.regions import Voivodeship

DESCRIPTION_MAX = 155
DEFAULT_IMAGE = "profiles/og-default.png"  # 1200x630, ours (no external host)

# schema.org type by artist type: groups perform, an illusionist is usually one person, the rest
# (shows, workshops, other) are run by an organisation.
SCHEMA_TYPES = {
    ArtistType.THEATRE: "PerformingGroup",
    ArtistType.MUSIC: "PerformingGroup",
    ArtistType.ILLUSION: "Person",
}
DEFAULT_SCHEMA_TYPE = "Organization"

_SPACES = re.compile(r"\s+")
_JSON_ESCAPES = {
    ord("<"): "\\u003c",
    ord(">"): "\\u003e",
    ord("&"): "\\u0026",
    0x2028: "\\u2028",
    0x2029: "\\u2029",
}


@dataclass(frozen=True)
class PageMeta:
    title: str
    description: str
    canonical: str
    image: str
    json_ld: SafeString  # ready to put inside <script type="application/ld+json">


def site_url() -> str:
    return settings.SITE_URL.rstrip("/")


def absolute_url(path_or_url: str) -> str:
    """`path_or_url` as an absolute URL; an absolute one is returned as it is."""
    if re.match(r"^https?://", path_or_url, re.IGNORECASE):
        return path_or_url
    return site_url() + "/" + path_or_url.lstrip("/")


def trim_description(text: str, limit: int = DESCRIPTION_MAX) -> str:
    """Plain text of at most `limit` characters, cut at a word boundary (with "…" when cut)."""
    plain = _SPACES.sub(" ", html.unescape(strip_tags(text or ""))).strip()
    if len(plain) <= limit:
        return plain
    cut = plain[: limit - 1]
    if plain[limit - 1] != " ":  # the cut falls inside a word: drop its beginning
        head, _sep, _tail = cut.rpartition(" ")
        cut = head or cut
    return cut.rstrip(" ,;:.–-") + "…"


def description_of(content) -> str:
    """The about text, else the school text, else the tagline, else name and city."""
    for text in (content.about, content.for_schools, content.hero.tagline):
        trimmed = trim_description(text)
        if trimmed:
            return trimmed
    return trim_description(" – ".join(p for p in (content.hero.name, content.hero.city) if p))


def schema_type(artist_type: str) -> str:
    return SCHEMA_TYPES.get(artist_type, DEFAULT_SCHEMA_TYPE)


def image_url(content) -> str:
    """The main photo when the page has one, else our default image. Gallery photos are
    short-lived signed links, so they never serve as the share image."""
    if content.hero.photo_url:
        return absolute_url(content.hero.photo_url)
    return absolute_url(static(DEFAULT_IMAGE))


def json_ld_data(content) -> dict:
    regions = [
        {"@type": "AdministrativeArea", "name": str(Voivodeship(code).label)}
        for code in content.regions
        if code in Voivodeship.values
    ]
    data = {
        "@context": "https://schema.org",
        "@type": schema_type(content.artist_type),
        "name": content.hero.name,
        "description": description_of(content),
        "image": image_url(content),
        "url": absolute_url(reverse("profiles:public", args=[content.slug])),
    }
    if regions:
        data["areaServed"] = regions
    offers = [
        {"@type": "Offer", "itemOffered": {"@type": "Service", "name": offer.title}}
        for offer in content.offers
        if offer.title.strip()
    ]
    if offers:
        data["makesOffer"] = offers
    return data


def dump_json_ld(data: dict) -> SafeString:
    """JSON that is safe inside a `<script>` element: no `</script>` or `<!--` breakout."""
    return mark_safe(json.dumps(data, ensure_ascii=False).translate(_JSON_ESCAPES))  # noqa: S308


def sitemap_xml(entries) -> str:
    """The sitemap document for `(slug, lastmod)` pairs (absolute URLs, W3C datetime in UTC)."""
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    for slug, lastmod in entries:
        loc = absolute_url(reverse("profiles:public", args=[slug]))
        stamp = lastmod.astimezone(datetime.UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
        lines.append(f"<url><loc>{escape(loc)}</loc><lastmod>{stamp}</lastmod></url>")
    lines.append("</urlset>")
    return "\n".join(lines) + "\n"


def page_meta(content) -> PageMeta:
    return PageMeta(
        title=content.hero.name,
        description=description_of(content),
        canonical=absolute_url(reverse("profiles:public", args=[content.slug])),
        image=image_url(content),
        json_ld=dump_json_ld(json_ld_data(content)),
    )
