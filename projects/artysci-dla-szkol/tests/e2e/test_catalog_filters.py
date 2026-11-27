"""Catalog filters (US-4.2) in a real browser: filter, share the URL in a new context, and reach the
notice button from empty results. Synthetic data in the live database (a fresh tag per test)."""

import uuid
from datetime import timedelta

import pytest
from axe_playwright_python.sync_playwright import Axe


def _seed():
    from django.utils import timezone

    from apps.accounts.tests.conftest import make_artist
    from apps.artists.models import Artist, PublicationStatus
    from apps.catalog.models import CatalogEntry

    tag = uuid.uuid4().hex[:8]
    rows = [
        ("Lodzki", ["lodzkie"], [{"price": 900, "duration": 60}]),
        ("Mazowiecki", ["mazowieckie"], [{"price": 900, "duration": 120}]),
    ]
    for number, (label, regions, offers) in enumerate(rows):
        artist = Artist.objects.get(user=make_artist(f"e2e-flt-{tag}-{number}@example.invalid"))
        artist.name = f"{label} {tag}"
        artist.slug = f"{label.lower()}-{tag}"
        artist.publication_status = PublicationStatus.PUBLISHED
        artist.save()
        CatalogEntry.objects.create(
            artist=artist,
            slug=artist.slug,
            name=artist.name,
            artist_type="theatre",
            voivodeships=regions,
            offers=offers,
            published_at=timezone.now() + timedelta(minutes=number),
        )
    return tag


@pytest.fixture
def tag(django_db_blocker):
    with django_db_blocker.unblock():
        yield _seed()


def test_filter_share_and_empty_results(browser, base_url, tag, shot_dir):
    context = browser.new_context(viewport={"width": 360, "height": 740})
    page = context.new_page()
    page.goto(base_url + "/artysci/")
    page.get_by_label("Województwo").select_option("lodzkie")
    page.get_by_label("Czas trwania maksymalnie (min)").fill("60")
    page.get_by_role("button", name="Pokaż artystów").click()
    page.wait_for_load_state()
    assert "wojewodztwo=lodzkie" in page.url and "czas_max=60" in page.url
    assert page.get_by_role("link", name=f"Lodzki {tag}").is_visible()
    assert page.get_by_role("link", name=f"Mazowiecki {tag}").count() == 0
    assert page.get_by_text("Znaleziono 1 artystę").is_visible()
    violations = Axe().run(page).response["violations"]
    assert not [v for v in violations if v["impact"] in ("critical", "serious")]
    page.screenshot(path=str(shot_dir / "catalog-filtered.png"), full_page=True)
    shared = page.url
    context.close()

    # The shared link in a new browser context (no login, no cookies): same results and values.
    other = browser.new_context()
    page = other.new_page()
    page.goto(shared)
    assert page.get_by_label("Województwo").input_value() == "lodzkie"
    assert page.get_by_label("Czas trwania maksymalnie (min)").input_value() == "60"
    assert page.get_by_role("link", name=f"Lodzki {tag}").is_visible()

    # Empty results: remove one filter, then reach the notice placeholder.
    page.goto(base_url + "/artysci/?wojewodztwo=lodzkie&cena_max=100")
    assert page.get_by_text("Znaleziono 0 artystów").is_visible()
    page.screenshot(path=str(shot_dir / "catalog-empty.png"), full_page=True)
    page.get_by_role("link", name="Usuń filtr: cena do 100 zł").click()
    page.wait_for_load_state()
    assert page.url.endswith("/artysci/?wojewodztwo=lodzkie")
    page.goto(base_url + "/artysci/?wojewodztwo=lodzkie&cena_max=100")
    page.get_by_role("link", name="Opublikuj ogłoszenie, a artyści zgłoszą się sami").click()
    page.wait_for_load_state()
    assert "/ogloszenia/nowe/" in page.url and "wojewodztwo=lodzkie" in page.url
    assert page.get_by_text("wkrótce").is_visible()
    other.close()
