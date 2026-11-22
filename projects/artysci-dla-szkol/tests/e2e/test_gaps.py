"""The missing-items list and the completeness percentage (US-2.7) in a real browser.

Seeds an artist with a finished run that has two known gaps and one unknown, in the live database
the server uses; the data is synthetic (`example.invalid`, a fresh address per test).
"""

import uuid

import pytest
from axe_playwright_python.sync_playwright import Axe

PAGE = "/artysta/profil/braki/"


def _seed():
    from django.conf import settings
    from django.test import Client

    from apps.artists.models import ArtistAudience, ArtistVoivodeship
    from apps.profiles.generator_components import COMPONENTS
    from apps.profiles.tests.factories import make_seed_artist, valid_profile
    from apps.quality import services as quality
    from apps.quality.models import Generation

    artist = make_seed_artist(f"e2e-gaps-{uuid.uuid4().hex[:8]}@example.invalid")
    ArtistVoivodeship.objects.create(artist=artist, voivodeship="dolnoslaskie")
    ArtistAudience.objects.create(artist=artist, audience="kindergarten")
    gaps = [
        {"code": "no_max_audience", "message": "Brak liczby widzów"},
        {"code": "no_stage_photo", "message": "Brak zdjęcia"},
        {"code": "something_new", "message": "Nowy rodzaj braku"},
    ]
    record = quality.start_generation(artist, Generation.Trigger.MANUAL, COMPONENTS)
    quality.finish_generation(record, valid_profile(gaps=gaps), [], 0, Generation.Status.READY)
    client = Client()
    client.force_login(artist.user)
    return (
        settings.SESSION_COOKIE_NAME,
        client.cookies[settings.SESSION_COOKIE_NAME].value,
        artist.pk,
    )


@pytest.fixture
def seeded(django_db_blocker):
    with django_db_blocker.unblock():
        yield _seed()


def test_gaps_list_button_and_percentage(browser, base_url, seeded, shot_dir):
    context = browser.new_context()
    host = base_url.split("://", 1)[1].split("/")[0].split(":")[0]
    context.add_cookies([{"name": seeded[0], "value": seeded[1], "domain": host, "path": "/"}])
    page = context.new_page()
    assert page.goto(base_url + PAGE).status == 200
    assert page.locator("h1").inner_text() == "Braki w profilu"
    assert page.get_by_text("Podaj maksymalną liczbę widzów").is_visible()
    assert page.get_by_text("Dodaj zdjęcie ze sceny").is_visible()
    unknown = page.locator("li", has_text="Nowy rodzaj braku")
    assert unknown.get_by_role("link").count() == 0
    assert page.locator("progress").get_attribute("max") == "100"
    assert page.locator("[style]").count() == 0
    page.screenshot(path=str(shot_dir / "gaps-list.png"), full_page=True)
    violations = Axe().run(page).response["violations"]
    assert not [v for v in violations if v["impact"] in ("critical", "serious")]

    # Fill an item on its target screen: the item is gone when the list is opened again.
    row = page.locator("li[data-task=max_audience]")
    row.get_by_role("link", name="Uzupełnij").click()
    assert page.url.endswith("/artysta/profil/kwestionariusz/")
    page.get_by_label("Maksymalna liczba widzów").fill("80")
    page.get_by_role("button", name="Zapisz").click()
    page.goto(base_url + PAGE)
    assert page.locator("li[data-task=max_audience]").count() == 0
    assert page.get_by_text("Dodaj zdjęcie ze sceny").is_visible()
    context.close()
