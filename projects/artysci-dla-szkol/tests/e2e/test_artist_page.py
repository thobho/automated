"""Owner preview of the artist page (US-3.1) in a real browser: sections, no contact data,
no external requests, accessibility. The test creates its artist in the live database the
server uses (DATABASE_URL), logs in with a session cookie and removes the data afterwards."""

import uuid

import pytest
from axe_playwright_python.sync_playwright import Axe

PREVIEW = "/panel/podglad/"


@pytest.fixture
def artist_session(django_db_blocker):
    """Yields (cookie name, value) of a logged-in artist with 8 offers (2 collapsed)."""
    from django.conf import settings
    from django.contrib.auth import get_user_model
    from django.test import Client

    from apps.artists.models import Artist, Offer

    with django_db_blocker.unblock():
        email = f"e2e-{uuid.uuid4().hex[:8]}@example.invalid"
        user = get_user_model().objects.create_user(email=email)
        artist = Artist.objects.create(user=user, name="Zespół Żółw", city="Wrocław")
        for i in range(8):
            Offer.objects.create(
                artist=artist,
                title=f"Spektakl {i + 1}",
                description="Opis <b>spektaklu</b>",
                price_on_request=True,
                position=i,
            )
        client = Client()
        client.force_login(user)
        try:
            yield settings.SESSION_COOKIE_NAME, client.cookies[settings.SESSION_COOKIE_NAME].value
        finally:
            user.delete()  # cascades to the artist and offers


def test_preview_is_not_public(page, base_url):
    page.goto(base_url + PREVIEW)
    assert "logowanie" in page.url
    assert page.locator("h1", has_text="Zespół").count() == 0


def test_preview_page(browser, base_url, artist_session, shot_dir):
    context = browser.new_context()
    name, value = artist_session
    host = base_url.split("://", 1)[1].split("/")[0].split(":")[0]
    context.add_cookies([{"name": name, "value": value, "domain": host, "path": "/"}])
    page = context.new_page()
    requests = []
    page.on("request", lambda r: requests.append(r.url))

    response = page.goto(base_url + PREVIEW)
    assert response.status == 200
    assert "noindex" in response.headers["x-robots-tag"]
    assert page.locator("html").get_attribute("lang") == "pl"

    assert page.locator("h1").count() == 1
    assert "Zespół Żółw" in page.locator("h1").inner_text()
    headings = [h.strip() for h in page.locator("h2").all_inner_texts()]
    assert "Oferta" in headings
    # Only the offers are filled, so the sections without data are absent.
    for absent in ("Pytania", "Nagrania", "Zdjęcia"):
        assert not any(absent in h for h in headings), headings
    assert page.get_by_role("link", name="Sprawdź termin").count() >= 1

    # 8 offers: 6 visible, 2 behind the "Pokaż pozostałe" button; no "Cena na zapytanie" per item.
    assert page.locator("button.offers-more__toggle").count() == 1
    assert page.locator(".offers-more li.offer").count() == 2
    assert page.locator("section#offer li.offer").count() == 8
    assert page.get_by_text("Cena na zapytanie").count() == 0

    # User text is escaped, no public contact data, no inline script, nothing from other hosts.
    assert page.locator("b").count() == 0
    html = page.content()
    assert "mailto:" not in html and "tel:" not in html
    assert page.locator("script:not([src])").count() == 0
    origin = base_url.rstrip("/")
    foreign = [u for u in requests if not u.startswith((origin, "data:", "blob:"))]
    assert not foreign, foreign

    page.screenshot(path=str(shot_dir / "artist-page-preview.png"), full_page=True)
    results = Axe().run(page)
    bad = [v for v in results.response["violations"] if v["impact"] in ("critical", "serious")]
    assert not bad, [f"{v['id']}: {v['help']}" for v in bad]
    context.close()


def test_owner_switches_theme_in_preview(browser, base_url, artist_session, shot_dir):
    context = browser.new_context()
    name, value = artist_session
    host = base_url.split("://", 1)[1].split("/")[0].split(":")[0]
    context.add_cookies([{"name": name, "value": value, "domain": host, "path": "/"}])
    page = context.new_page()
    page.goto(base_url + PREVIEW)
    root = page.locator(".artist-root")
    assert root.get_attribute("data-theme") == "burgundy_light"

    page.get_by_label("Granat ze złotem").check()
    page.get_by_role("button", name="Zapisz motyw").click()
    page.wait_for_url("**" + PREVIEW)
    assert root.get_attribute("data-theme") == "navy_gold"
    assert page.get_by_label("Granat ze złotem").is_checked()
    # The theme really paints the page: dark navy background from themes.css.
    assert root.evaluate("e => getComputedStyle(e).backgroundColor") == "rgb(15, 31, 61)"
    page.screenshot(path=str(shot_dir / "artist-page-navy-gold.png"), full_page=True)
    results = Axe().run(page)
    bad = [v for v in results.response["violations"] if v["impact"] in ("critical", "serious")]
    assert not bad, [f"{v['id']}: {v['help']}" for v in bad]
    context.close()
