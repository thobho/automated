"""Public artist page template (US-3.1): rendering, content builder, preview route."""

import re
from html.parser import HTMLParser

import pytest
from django.template.loader import render_to_string
from django.test import Client

from apps.accounts.tests.conftest import make_artist, make_institution_member
from apps.artists import services
from apps.artists.models import Artist, Material, MaterialKind, ScanStatus
from apps.profiles.content import (
    FaqItem,
    Hero,
    OfferItem,
    PageContent,
    PhotoItem,
    VideoItem,
    page_content_for,
)

PREVIEW = "/panel/podglad/"
MEDIA = "http://localhost:8101/"


class Page(HTMLParser):
    """Collects what the tests assert on: tags in order, headings, ids, attributes."""

    def __init__(self, html):
        super().__init__()
        self.tags = []  # (tag, attrs dict)
        self.headings = []  # (tag, text)
        self._open = None
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))
        if tag in ("h1", "h2", "h3"):
            self._open = [tag, ""]

    def handle_data(self, data):
        if self._open:
            self._open[1] += data

    def handle_endtag(self, tag):
        if self._open and self._open[0] == tag:
            self.headings.append((tag, " ".join(self._open[1].split())))
            self._open = None

    def h(self, level):
        return [t for tag, t in self.headings if tag == level]

    def ids(self):
        return [a["id"] for _, a in self.tags if "id" in a]

    def attrs_of(self, tag):
        return [a for t, a in self.tags if t == tag]


def render(content, **extra):
    return render_to_string("profiles/page.html", {"content": content, **extra})


def full_content(**over):
    data = dict(
        slug="teatr",
        hero=Hero(name="Teatr Kwiatki", tagline="Bajki", city="Opole", photo_url="/m/x.jpg"),
        facts=["Od 2010 roku"],
        about="O nas",
        for_schools="Dla szkół",
        offers=[OfferItem("Spektakl", "Opis", "800 zł", ("5–9 lat",))],
        videos=[VideoItem(title="Film", src=MEDIA + "v.mp4")],
        photos=[PhotoItem(f"/m/{i}.jpg", f"zdjęcie {i}") for i in range(4)],
        faq=[FaqItem("Ile trwa?", "45 minut")],
    )
    data.update(over)
    return PageContent(**data)


def offers(n, **kw):
    return [OfferItem(f"Oferta {i}", "opis", "100 zł", **kw) for i in range(n)]


# --- order and hidden sections ----------------------------------------------------------------


def test_sections_in_fixed_order():
    page = Page(render(full_content()))
    order = page.ids()
    keys = ["start", "facts", "about", "schools", "offer", "videos", "photos", "faq", "inquiry"]
    positions = [order.index(k) for k in keys]
    assert positions == sorted(positions)
    assert page.h("h2") == [
        "O artyście",
        "Dla szkół i przedszkoli",
        "Oferta",
        "Nagrania",
        "Zdjęcia",
        "Pytania",
        "Sprawdź termin",
    ]
    assert len(page.h("h1")) == 1


def test_empty_sections_are_not_rendered():
    content = full_content(faq=[], videos=[], about="  ", facts=[])
    html = render(content)
    page = Page(html)
    for key in ("facts", "about", "videos", "faq"):
        assert key not in page.ids()
        assert f'href="#{key}"' not in html
    for heading in ("O artyście", "Nagrania", "Pytania"):
        assert heading not in page.h("h2")
    assert "schools" in page.ids() and "offer" in page.ids()


def test_minimal_content_has_start_and_inquiry_only():
    page = Page(render(PageContent(slug="a", hero=Hero(name="A"))))
    assert page.h("h2") == ["Sprawdź termin"]


@pytest.mark.parametrize("count,shown", [(3, False), (4, True)])
def test_gallery_needs_four_photos(count, shown):
    content = full_content(photos=[PhotoItem(f"/m/{i}.jpg") for i in range(count)])
    html = render(content)
    assert ("photos" in Page(html).ids()) is shown
    assert ("Zdjęcia" in Page(html).h("h2")) is shown


# --- offers -----------------------------------------------------------------------------------


def test_nine_offers_collapse_three():
    page_html = render(full_content(offers=offers(9)))
    assert page_html.count('class="offer"') == 9
    details = page_html.split('class="offers-more"')[1]
    assert "Pokaż pozostałe" in details
    assert details.count('class="offer"') == 3
    assert page_html.split('class="offers-more"')[0].count('class="offer"') == 6


def test_six_offers_no_collapse():
    html = render(full_content(offers=offers(6)))
    assert "offers-more" not in html and "Pokaż pozostałe" not in html


def test_no_prices_shows_note_once():
    html = render(full_content(offers=[OfferItem(f"O{i}", "") for i in range(3)]))
    assert "Cena na zapytanie" not in html
    assert html.count('class="note"') == 1


def test_mixed_prices_mark_unpriced_items():
    items = [OfferItem("A", "", "100 zł"), OfferItem("B", "")]
    html = render(full_content(offers=items))
    assert html.count("Cena na zapytanie") == 1 and 'class="note"' not in html


def test_shared_tags_hidden_partial_tags_shown():
    items = [
        OfferItem("A", "", "1 zł", ("wspólny", "tylko A")),
        OfferItem("B", "", "1 zł", ("wspólny",)),
    ]
    html = render(full_content(offers=items))
    assert "wspólny" not in html and "tylko A" in html


def test_single_offer_keeps_its_tags():
    html = render(full_content(offers=[OfferItem("A", "", "1 zł", ("45 min",))]))
    assert "45 min" in html


# --- start section ----------------------------------------------------------------------------


def test_without_main_photo_shows_initial_frame():
    html = render(full_content(hero=Hero(name="ola kowalska")))
    page = Page(html)
    assert 'class="start__initial"' in html and ">O<" in html
    assert not [a for a in page.attrs_of("img") if a.get("src") in ("", None)]
    assert "start__photo" not in html


def test_with_main_photo_has_alt():
    page = Page(render(full_content()))
    start_img = [a for a in page.attrs_of("img") if "start__photo" in a.get("class", "")]
    assert start_img and start_img[0]["alt"] == "Teatr Kwiatki"


# --- videos -----------------------------------------------------------------------------------


def test_uploaded_video_uses_native_element():
    page = Page(render(full_content()))
    sources = page.attrs_of("source")
    assert page.attrs_of("video") and sources[0]["src"].startswith(MEDIA)


def test_youtube_link_is_a_button_without_requests():
    link = VideoItem(
        title="Występ", link_url="https://www.youtube.com/watch?v=abc", provider="YouTube"
    )
    html = render(full_content(videos=[link]))
    page = Page(html)
    assert not page.attrs_of("video") and not page.attrs_of("iframe")
    assert "Obejrzyj film" in html and "video-link__placeholder" in html  # placeholder, no thumb
    for _tag, attrs in page.tags:
        assert "youtube.com" not in attrs.get("src", "")
    buttons = [a for a in page.attrs_of("a") if "youtube.com" in a.get("href", "")]
    assert len(buttons) == 1


@pytest.mark.parametrize("bad", ["javascript:alert(1)", "data:text/html,x", "//evil.example/x"])
def test_unsafe_video_link_is_never_rendered(bad):
    content = PageContent(slug="a", hero=Hero(name="A"), videos=[VideoItem(link_url=bad)])
    html = render(content)
    assert content.videos == []
    assert "javascript:" not in html and "data:text" not in html and "evil.example" not in html
    assert "Nagrania" not in html


def test_link_with_local_thumbnail():
    link = VideoItem(link_url="https://vimeo.com/1", poster_url="/m/t.jpg")
    html = render(full_content(videos=[link]))
    assert 'src="/m/t.jpg"' in html


# --- safety -----------------------------------------------------------------------------------


EXTERNAL = re.compile(r"""(?:src|href)=["']\s*(?:https?:)?//""", re.I)


def test_no_inline_script_style_or_external_assets():
    link = VideoItem(link_url="https://www.youtube.com/watch?v=abc")
    html = render(full_content(videos=[link, VideoItem(src="/m/v.mp4")]), noindex=True)
    page = Page(html)
    assert not [a for a in page.attrs_of("script") if "src" not in a]
    assert "<style" not in html
    assert not any("style" in attrs for _, attrs in page.tags)
    assert not any(
        tag == "link" and attrs.get("href", "").startswith("http") for tag, attrs in page.tags
    )
    assert not any(
        attrs.get("src", "").startswith(("http:", "https:", "//")) for _, attrs in page.tags
    )
    assert "mailto:" not in html and "tel:" not in html
    assert 'lang="pl"' in html


def test_user_text_is_escaped():
    evil = "<script>alert(1)</script>"
    content = full_content(
        hero=Hero(name=evil, tagline=evil, city=evil),
        about=evil,
        for_schools=evil,
        facts=[evil],
        offers=[OfferItem(evil, evil, evil, (evil,)), OfferItem(evil, evil, evil)],
        faq=[FaqItem(evil, evil)],
        videos=[VideoItem(title=evil, link_url="https://www.youtube.com/watch?v=a")],
        photos=[PhotoItem("/m/1.jpg", evil)] * 4,
    )
    html = render(content)
    assert evil not in html
    assert "&lt;script&gt;" in html


# --- content builder and preview ---------------------------------------------------------------


@pytest.fixture
def artist_user():
    return make_artist()


@pytest.fixture
def web(artist_user):
    client = Client()
    client.force_login(artist_user)
    return client


@pytest.mark.django_db
def test_builder_uses_only_existing_data(artist_user):
    artist = Artist.objects.get(user=artist_user)
    artist.city = "Opole"
    artist.save()
    services.create_offer(
        artist,
        {"title": "Show", "description": "Opis", "age_from": 5, "age_to": 9, "price_pln": 900},
    )
    services.create_offer(
        artist, {"title": "Bez ceny", "description": "x", "price_on_request": True}
    )
    Material.objects.create(
        artist=artist,
        kind=MaterialKind.LINK,
        status=ScanStatus.READY,
        provider="youtube",
        video_id="abc",
        canonical_url="https://www.youtube.com/watch?v=abc",
        title="Film",
    )
    Material.objects.create(
        artist=artist, kind=MaterialKind.PHOTO, status=ScanStatus.PENDING, storage_key="k"
    )
    content = page_content_for(artist)
    assert content.hero.name == "Artysta Rola" and content.hero.city == "Opole"
    assert content.hero.photo_url == "" and content.about == "" and content.faq == []
    assert [o.title for o in content.offers] == ["Show", "Bez ceny"]
    assert content.offers[0].price_note == "900 zł" and content.offers[1].price_note == ""
    assert "wiek 5–9 lat" in content.offers[0].tags
    assert len(content.videos) == 1 and content.videos[0].provider == "YouTube"
    assert content.photos == []  # a pending photo does not count
    assert content.slug == "artysta-rola"


@pytest.mark.django_db
def test_builder_photos_and_video_files(artist_user):
    artist = Artist.objects.get(user=artist_user)
    for i in range(2):
        Material.objects.create(
            artist=artist, kind=MaterialKind.PHOTO, status=ScanStatus.READY, storage_key=f"p{i}"
        )
    Material.objects.create(
        artist=artist,
        kind=MaterialKind.VIDEO,
        status=ScanStatus.READY,
        storage_key="v",
        converted_key="v.mp4",
        thumbnail_key="v.jpg",
        original_name="film.mov",
    )
    content = page_content_for(artist)
    assert len(content.photos) == 2 and not content.show_gallery
    assert content.videos[0].is_file and content.videos[0].poster_url
    assert content.videos[0].title == "film.mov"


@pytest.mark.django_db
def test_preview_for_owner(web, artist_user):
    artist = Artist.objects.get(user=artist_user)
    services.create_offer(artist, {"title": "Show", "description": "Opis", "price_pln": 100})
    response = web.get(PREVIEW)
    assert response.status_code == 200
    assert "noindex" in response["X-Robots-Tag"]
    html = response.content.decode()
    assert '<meta name="robots" content="noindex' in html
    page = Page(html)
    assert page.h("h1") == ["Artysta Rola"]
    assert page.h("h2") == [
        "Edycja tekstów",
        "Oferta",
        "Sprawdź termin",
    ]  # the owner's editor first
    assert "Show" in page.h("h3")


@pytest.mark.django_db
def test_preview_refuses_anonymous_and_other_roles():
    anonymous = Client().get(PREVIEW)
    assert anonymous.status_code == 302 and "next=" in anonymous["Location"]
    client = Client()
    client.force_login(make_institution_member())
    assert client.get(PREVIEW).status_code == 403


@pytest.mark.django_db
def test_preview_only_shows_own_data(web):
    other = make_artist("inny@example.invalid")
    other_artist = Artist.objects.get(user=other)
    other_artist.name = "Ktoś Inny"
    other_artist.save()
    assert "Ktoś Inny" not in web.get(PREVIEW).content.decode()


@pytest.mark.django_db
def test_preview_post_not_allowed(web):
    assert web.post(PREVIEW).status_code == 405


@pytest.mark.django_db
def test_seed_artist_preview_renders_only_existing_data(capsys):
    from django.contrib.auth import get_user_model

    from apps.accounts import services as accounts

    accounts.seed_users()
    services.seed_artists()
    user = get_user_model().objects.get(email="artysta01@example.invalid")
    client = Client()
    client.force_login(user)
    response = client.get(PREVIEW)
    assert response.status_code == 200
    html = response.content.decode()
    page = Page(html)
    with capsys.disabled():
        print("SECTION HEADINGS:", page.h("h1"), page.h("h2"))
    assert page.h("h2") == ["Edycja tekstów", "Oferta", "Sprawdź termin"]
    assert html.count('class="offer"') == 20
    assert html.split('class="offers-more"')[1].count('class="offer"') == 14
    assert "mailto:" not in html and "tel:" not in html
