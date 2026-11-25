"""Search engine visibility of the public page (US-3.4): tags, JSON-LD, sitemap, robots."""

import json
import re

import pytest
from django.test import Client
from django.urls import reverse

from apps.artists.models import Artist, ArtistType, Offer
from apps.profiles import publication, seo
from apps.profiles.content import Hero, OfferItem, PageContent

from .test_publication import make_ready

pytestmark = pytest.mark.django_db

EVIL = "</script><script>alert(1)</script>"


# --- services ------------------------------------------------------------------------------------


def test_trim_keeps_short_text_and_strips_html():
    assert seo.trim_description("<p>Ala &amp;  ma\n kota</p>") == "Ala & ma kota"


def test_trim_cuts_at_word_boundary_within_limit():
    text = "słowo " * 60
    out = seo.trim_description(text)
    assert len(out) <= 155 and out.endswith("…")
    assert out[:-1].split(" ")[-1] == "słowo"  # no half word


def test_trim_exact_limit_untouched_and_one_long_word_hard_cut():
    assert seo.trim_description("a" * 155) == "a" * 155
    out = seo.trim_description("a" * 400)
    assert len(out) == 155 and out.endswith("…")


def test_description_falls_back_to_tagline_then_name():
    hero = Hero(name="Zespół", tagline="Hasło", city="Wrocław")
    assert seo.description_of(PageContent(slug="z", hero=hero)) == "Hasło"
    bare = PageContent(slug="z", hero=Hero(name="Zespół", city="Wrocław"))
    assert seo.description_of(bare) == "Zespół – Wrocław"


@pytest.mark.parametrize(
    ("artist_type", "expected"),
    [
        (ArtistType.THEATRE, "PerformingGroup"),
        (ArtistType.MUSIC, "PerformingGroup"),
        (ArtistType.ILLUSION, "Person"),
        (ArtistType.SCIENCE_SHOW, "Organization"),
        (ArtistType.OTHER, "Organization"),
    ],
)
def test_schema_type_by_artist_type(artist_type, expected):
    assert seo.schema_type(artist_type) == expected


def test_dump_json_ld_escapes_breakout_characters():
    out = seo.dump_json_ld({"name": EVIL + "&\u2028"})
    assert "<" not in out and ">" not in out and "&" not in out and "\u2028" not in out
    assert json.loads(out)["name"] == EVIL + "&\u2028"


def test_absolute_url_keeps_absolute_and_prefixes_paths(settings):
    settings.SITE_URL = "https://example.pl/"
    assert seo.absolute_url("/static/x.png") == "https://example.pl/static/x.png"
    assert seo.absolute_url("https://m.example/a.jpg") == "https://m.example/a.jpg"


def test_json_ld_has_offers_regions_and_no_contact_data():
    artist = make_ready("ld@example.invalid", name="Teatr Lalek")
    artist.artist_type = ArtistType.THEATRE
    artist.save()
    publication.publish(artist)
    _artist, content = publication.public_page_of(Artist.objects.get(pk=artist.pk).slug)
    data = seo.json_ld_data(artist, content)
    assert data["@type"] == "PerformingGroup" and data["name"] == "Teatr Lalek"
    assert data["areaServed"] == [{"@type": "AdministrativeArea", "name": "dolnośląskie"}]
    names = [o["itemOffered"]["name"] for o in data["makesOffer"]]
    assert names == [o.title for o in content.offers] and names
    assert "price" not in json.dumps(data).lower()
    assert "mail" not in data and "telephone" not in data and "address" not in data


def test_json_ld_without_offers_or_regions_omits_the_keys():
    artist = make_ready("bare@example.invalid")
    artist.voivodeships.all().delete()
    content = PageContent(slug="x", hero=Hero(name="X"), offers=[OfferItem("  ")])
    data = seo.json_ld_data(artist, content)
    assert "areaServed" not in data and "makesOffer" not in data


# --- the public page -----------------------------------------------------------------------------


def published(name="Teatr Lalek", email="seo@example.invalid", about=None):
    artist = make_ready(email, name=name)
    publication.publish(artist)
    return Artist.objects.get(pk=artist.pk)


def fetch(artist):
    return Client().get(reverse("profiles:public", args=[artist.slug]))


def test_page_has_title_description_canonical_and_open_graph(settings):
    settings.SITE_URL = "https://artysci.example.pl"
    artist = published()
    html = fetch(artist).content.decode()
    url = f"https://artysci.example.pl/artysci/{artist.slug}/"
    assert "<title>Teatr Lalek" in html
    assert f'<link rel="canonical" href="{url}">' in html
    assert '<html lang="pl">' in html
    for needle in (
        '<meta name="robots" content="index,follow">',
        '<meta property="og:type" content="profile">',
        '<meta property="og:title" content="Teatr Lalek">',
        f'<meta property="og:url" content="{url}">',
        '<meta property="og:locale" content="pl_PL">',
        '<meta name="twitter:card" content="summary_large_image">',
    ):
        assert needle in html
    description = re.search(r'<meta name="description" content="([^"]*)"', html).group(1)
    assert 0 < len(description) <= 155
    # no main photo: the default image on our own origin, an absolute URL
    image = re.search(r'<meta property="og:image" content="([^"]*)"', html).group(1)
    assert image.startswith("https://artysci.example.pl/") and image.endswith("og-default.png")


def test_json_ld_parses_and_page_has_no_contact_data():
    artist = published(email="tajny.kontakt@example.invalid")
    html = fetch(artist).content.decode()
    raw = re.search(r'<script type="application/ld\+json">(.*?)</script>', html, re.S).group(1)
    data = json.loads(raw)
    assert data["@context"] == "https://schema.org" and data["@type"] in {
        "PerformingGroup",
        "Person",
        "Organization",
    }
    assert data["url"].endswith(f"/artysci/{artist.slug}/")
    for forbidden in ("mailto:", "tel:", "tajny.kontakt", "@example.invalid"):
        assert forbidden not in html


def test_markup_in_name_cannot_break_out_of_json_ld_or_attributes():
    artist = published(name="Teatr Lalek", email="xss@example.invalid")
    # a stored name that slipped past publication (e.g. via old data) must still be inert
    page = artist.published_page
    page.data = {**page.data, "name": EVIL + '"><x'}
    page.save()
    html = fetch(artist).content.decode()
    assert "<script>alert(1)" not in html and '"><x' not in html
    raw = re.search(r'<script type="application/ld\+json">(.*?)</script>', html, re.S).group(1)
    assert json.loads(raw)["name"] == EVIL + '"><x'
    assert html.count("</script>") == html.count("<script")


def test_public_page_has_only_data_blocks_inline_and_unchanged_csp():
    artist = published()
    response = fetch(artist)
    html = response.content.decode()
    inline = re.findall(r"<script(?![^>]*\bsrc=)[^>]*>", html)
    assert inline == ['<script type="application/ld+json">']
    assert "<style" not in html and " style=" not in html
    csp = response["Content-Security-Policy"]
    assert "script-src 'self' 'nonce-" in csp and "unsafe-inline" not in csp
    assert "unsafe-eval" not in csp


def test_withdrawn_and_unknown_pages_are_plain_404_without_tags():
    artist = published()
    publication.withdraw(artist)
    for slug in (artist.slug, "nie-ma-takiej"):
        response = Client().get(reverse("profiles:public", args=[slug]))
        assert response.status_code == 404
        assert b"canonical" not in response.content


# --- sitemap and robots --------------------------------------------------------------------------


def test_sitemap_lists_only_published_with_absolute_url_and_lastmod(settings):
    settings.SITE_URL = "https://artysci.example.pl/"
    live = published(name="Teatr Pierwszy", email="a@example.invalid")
    draft = make_ready("b@example.invalid", name="Teatr Szkic")
    gone = published(name="Teatr Wycofany", email="c@example.invalid")
    publication.withdraw(gone)
    response = Client().get(reverse("profiles:sitemap"))
    assert response.status_code == 200
    assert response["Content-Type"].startswith("application/xml")
    body = response.content.decode()
    assert f"<loc>https://artysci.example.pl/artysci/{live.slug}/</loc>" in body
    assert re.search(r"<lastmod>\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ</lastmod>", body)
    assert "Szkic" not in body and "wycofany" not in body
    assert draft.slug is None and gone.slug not in body
    cache = response["Cache-Control"]
    assert "public" in cache and "no-cache" in cache


def test_withdrawal_removes_the_page_from_the_sitemap_at_once():
    artist = published()
    assert artist.slug in Client().get(reverse("profiles:sitemap")).content.decode()
    publication.withdraw(artist)
    assert artist.slug not in Client().get(reverse("profiles:sitemap")).content.decode()


def test_sitemap_skips_deactivated_accounts_and_respects_the_limit():
    first = published(name="Teatr A", email="d@example.invalid")
    second = published(name="Teatr B", email="e@example.invalid")
    assert [s for s, _t in publication.sitemap_entries(limit=1)] == [first.slug]
    second.user.is_active = False
    second.user.save()
    assert [s for s, _t in publication.sitemap_entries()] == [first.slug]


def test_sitemap_lastmod_moves_on_update_published():
    artist = published()
    before = dict(publication.sitemap_entries())[artist.slug]
    Offer.objects.filter(artist=artist).update(title="Nowy tytuł")
    publication.update_published(artist)
    assert dict(publication.sitemap_entries())[artist.slug] > before


def test_robots_txt_disallows_private_areas_and_names_the_sitemap(settings):
    settings.SITE_URL = "https://artysci.example.pl"
    response = Client().get("/robots.txt")
    assert response.status_code == 200 and response["Content-Type"].startswith("text/plain")
    body = response.content.decode()
    assert "Disallow: /panel/" in body and "Disallow: /admin/" in body
    assert "Disallow: /artysci/" not in body and "Allow: /" in body
    assert "Sitemap: https://artysci.example.pl/sitemap.xml" in body
    assert "max-age=3600" in response["Cache-Control"]
