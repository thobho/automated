"""Catalog text search (US-4.3) in a real browser: an inflected word finds the artist, the text
stays in the box and in the link, and the page has no serious accessibility violations.
Synthetic data in the live database (a fresh tag per test)."""

import uuid

import pytest
from axe_playwright_python.sync_playwright import Axe


def _seed():
    from django.utils import timezone

    from apps.accounts.tests.conftest import make_artist
    from apps.artists.models import Artist, PublicationStatus
    from apps.catalog import search
    from apps.catalog.models import CatalogEntry

    tag = uuid.uuid4().hex[:8]
    name = f"Teatr Hejtex {tag}"
    artist = Artist.objects.get(user=make_artist(f"e2e-q-{tag}@example.invalid"))
    artist.name = name
    artist.slug = f"hejtex-{tag}"
    artist.publication_status = PublicationStatus.PUBLISHED
    artist.save()
    CatalogEntry.objects.create(
        artist=artist,
        slug=artist.slug,
        name=name,
        published_at=timezone.now(),
        **search.index_terms(name, ["Cena hejtu"], ["uzależnienia"]),
    )
    return tag


@pytest.fixture
def tag(django_db_blocker):
    with django_db_blocker.unblock():
        yield _seed()


def test_search_with_an_inflected_word(browser, base_url, tag, shot_dir):
    page = browser.new_context(viewport={"width": 360, "height": 740}).new_page()
    page.goto(base_url + "/artysci/")
    page.get_by_label("Szukaj").fill(f"spektakl o hejcie hejtex{tag}")
    page.get_by_role("button", name="Pokaż artystów").click()
    page.wait_for_load_state()
    assert "q=" in page.url
    assert page.get_by_role("link", name=f"Teatr Hejtex {tag}").is_visible()
    assert page.get_by_label("Szukaj").input_value() == f"spektakl o hejcie hejtex{tag}"
    violations = Axe().run(page).response["violations"]
    assert not [v for v in violations if v["impact"] in ("critical", "serious")]
    page.screenshot(path=str(shot_dir / "catalog-search.png"), full_page=True)

    # Missing Polish letters and a typo, then a text that matches nobody.
    page.goto(base_url + "/artysci/?q=uzaleznieniach+hejtex" + tag)
    assert page.get_by_role("link", name=f"Teatr Hejtex {tag}").is_visible()
    page.goto(base_url + "/artysci/?q=zzzzzzzzqq")
    assert page.get_by_text("Znaleziono 0 artystów").is_visible()
    assert page.get_by_role("link", name=f"Teatr Hejtex {tag}").count() == 0
