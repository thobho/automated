"""Publish, see the public page, withdraw (US-2.8) in a real browser.

Seeds a ready artist (synthetic data, a fresh address per test) in the live database the server
uses, then clicks through the panel like the artist does.
"""

import json
import uuid

import pytest
from axe_playwright_python.sync_playwright import Axe


def _seed():
    from django.conf import settings
    from django.test import Client

    from apps.artists.models import ArtistAudience, ArtistVoivodeship
    from apps.profiles import generation, pages
    from apps.profiles.tests.factories import make_seed_artist, valid_profile
    from apps.quality import services as quality
    from apps.quality.models import Generation
    from apps.trust import services as trust
    from apps.trust.models import LegalDocument

    tag = uuid.uuid4().hex[:8]
    artist = make_seed_artist(f"e2e-pub-{tag}@example.invalid")
    artist.name = f"Teatr Łąka {tag}"
    artist.save()
    ArtistVoivodeship.objects.create(artist=artist, voivodeship="dolnoslaskie")
    ArtistAudience.objects.create(artist=artist, audience="kindergarten")
    if trust.current(LegalDocument.Kind.CHILD_PROTECTION) is None:
        trust.publish(LegalDocument.Kind.CHILD_PROTECTION, "Treść testowa", material=False)
    trust.make_statement(artist, LegalDocument.Kind.CHILD_PROTECTION)
    record = quality.start_generation(artist, Generation.Trigger.MANUAL, generation.COMPONENTS)
    pages.record_generated(
        quality.finish_generation(
            record,
            valid_profile(description={"paragraphs": ["Opis do publikacji."]}),
            [],
            0,
            Generation.Status.READY,
        )
    )
    client = Client()
    client.force_login(artist.user)
    return settings.SESSION_COOKIE_NAME, client.cookies[settings.SESSION_COOKIE_NAME].value, tag


@pytest.fixture
def seeded(django_db_blocker):
    with django_db_blocker.unblock():
        yield _seed()


def _save(page):
    page.get_by_role("button", name="Zapisz", exact=True).click()
    page.wait_for_load_state()


def test_publish_view_public_page_and_withdraw(browser, base_url, seeded, shot_dir):
    context = browser.new_context()
    host = base_url.split("://", 1)[1].split("/")[0].split(":")[0]
    context.add_cookies([{"name": seeded[0], "value": seeded[1], "domain": host, "path": "/"}])
    page = context.new_page()

    assert page.goto(base_url + "/panel/publikacja/").status == 200
    assert page.locator("[data-state=draft]").is_visible()
    page.screenshot(path=str(shot_dir / "publication-draft.png"), full_page=True)
    page.get_by_role("button", name="Opublikuj", exact=True).click()
    link = page.locator("[data-public-link]")
    assert link.is_visible()
    public_path = link.get_attribute("href")
    assert public_path.startswith("/artysci/teatr-laka-")
    assert page.locator("[style]").count() == 0
    violations = Axe().run(page).response["violations"]
    assert not [v for v in violations if v["impact"] in ("critical", "serious")]

    # An anonymous visitor sees the page.
    visitor = browser.new_context().new_page()
    assert visitor.goto(base_url + public_path).status == 200
    assert visitor.get_by_text("Opis do publikacji.").is_visible()
    assert "mailto:" not in visitor.content() and "tel:" not in visitor.content()
    visitor.screenshot(path=str(shot_dir / "publication-public.png"), full_page=True)

    # Search visibility (US-3.4): head tags, JSON-LD that the strict CSP lets through, sitemap.
    assert visitor.locator("link[rel=canonical]").get_attribute("href").endswith(public_path)
    assert visitor.locator("meta[name=robots]").get_attribute("content") == "index,follow"
    assert visitor.locator("meta[property='og:type']").get_attribute("content") == "profile"
    ld = json.loads(visitor.locator("script[type='application/ld+json']").inner_text())
    assert ld["@context"] == "https://schema.org" and ld["name"].startswith("Teatr Łąka")
    sitemap = visitor.request.get(base_url + "/sitemap.xml")
    assert sitemap.ok and public_path in sitemap.text()
    assert "Disallow: /panel/" in visitor.request.get(base_url + "/robots.txt").text()

    # An edited offer stays private until "Opublikuj zmiany"; a phone in it stops the publication.
    page.goto(base_url + "/artysta/profil/oferty/")
    page.get_by_role("link", name="Edytuj").first.click()
    page.locator("[name=description]").fill("Telefony:\n600 700 800\n601 700 800")
    _save(page)
    page.goto(base_url + "/panel/publikacja/")
    assert page.locator("[data-unpublished]").is_visible()
    blocker = page.locator("[data-blocker=contact_offers]")
    assert "600 700 800" in blocker.inner_text() and "601 700 800" in blocker.inner_text()
    assert page.get_by_role("button", name="Opublikuj zmiany").count() == 0
    violations = Axe().run(page).response["violations"]
    assert not [v for v in violations if v["impact"] in ("critical", "serious")]
    page.screenshot(path=str(shot_dir / "publication-blocked.png"), full_page=True)
    visitor.reload()
    assert "600 700 800" not in visitor.content()
    assert visitor.get_by_text("Kwiatowa opowieść").first.is_visible()

    blocker.get_by_role("link", name="Popraw").click()
    page.get_by_role("link", name="Edytuj").first.click()
    page.locator("[name=title]").fill("Nowy spektakl")
    page.locator("[name=description]").fill("Opis bez danych kontaktowych.")
    _save(page)
    page.goto(base_url + "/panel/publikacja/")
    visitor.reload()
    assert visitor.get_by_text("Nowy spektakl").count() == 0
    page.get_by_role("button", name="Opublikuj zmiany").click()
    assert page.locator("[data-unpublished]").count() == 0
    visitor.reload()
    assert visitor.get_by_text("Nowy spektakl").first.is_visible()

    # Withdraw with the confirmation page.
    page.get_by_role("link", name="Wycofaj stronę").click()
    assert page.get_by_role("heading", name="Wycofać stronę?").is_visible()
    page.screenshot(path=str(shot_dir / "publication-confirm.png"), full_page=True)
    page.get_by_role("button", name="Tak, wycofaj stronę").click()
    assert page.locator("[data-state=withdrawn]").is_visible()
    assert visitor.goto(base_url + public_path).status == 404
    assert public_path not in visitor.request.get(base_url + "/sitemap.xml").text()
    context.close()
