"""Preview editing (US-2.6) in a real browser: edit a text, see it locked and escaped, restore the
first version. Regenerating a section needs a worker and is covered by
apps/profiles/tests/test_pages.py. Each test seeds its own synthetic artist (`example.invalid`)."""

import uuid

import pytest
from axe_playwright_python.sync_playwright import Axe

PAGE = "/panel/podglad/"


def _seed():
    from django.conf import settings
    from django.test import Client

    from apps.profiles import pages
    from apps.profiles.generator_components import COMPONENTS
    from apps.profiles.tests.factories import make_seed_artist, valid_profile
    from apps.quality import services as quality
    from apps.quality.models import Generation

    artist = make_seed_artist(f"e2e-edit-{uuid.uuid4().hex[:8]}@example.invalid")
    record = quality.start_generation(artist, Generation.Trigger.MANUAL, COMPONENTS)
    record = quality.finish_generation(record, valid_profile(), [], 0, Generation.Status.READY)
    pages.record_generated(record)
    client = Client()
    client.force_login(artist.user)
    return settings.SESSION_COOKIE_NAME, client.cookies[settings.SESSION_COOKIE_NAME].value


@pytest.fixture
def owner(django_db_blocker):
    with django_db_blocker.unblock():
        yield _seed()


def _no_serious_axe_violations(page):
    violations = Axe().run(page).response["violations"]
    bad = [v for v in violations if v["impact"] in ("critical", "serious")]
    assert not bad, [f"{v['id']}: {v['help']}" for v in bad]


def test_edit_lock_and_restore(browser, base_url, owner, shot_dir):
    context = browser.new_context()
    host = base_url.split("://", 1)[1].split("/")[0].split(":")[0]
    context.add_cookies([{"name": owner[0], "value": owner[1], "domain": host, "path": "/"}])
    page = context.new_page()
    assert page.goto(base_url + PAGE).status == 200
    assert "Opis testowy." in page.locator("#about").inner_text()
    assert page.locator("[data-version]").count() == 1

    field = page.locator("[data-path=about]")
    field.get_by_label("Tekst „O artyście”").fill("Nowy <b>opis</b> artysty")
    field.get_by_role("button", name="Zapisz").click()
    page.wait_for_selector("[data-version='2']")
    assert "Nowy <b>opis</b> artysty" in page.locator("#about").inner_text()  # shown as text
    assert page.locator("#about b").count() == 0  # no markup was created
    assert page.locator("[data-path=about]").get_attribute("data-locked") == "true"
    page.screenshot(path=str(shot_dir / "preview-edited.png"), full_page=True)
    _no_serious_axe_violations(page)

    page.locator("[data-path=facts\\.0]").get_by_label("Informacja 1").fill("x" * 23)
    page.locator("[data-path=facts\\.0]").get_by_role("button", name="Zapisz").click()
    assert "Fakt ma 23 znaków" in page.locator("body").inner_text()
    assert page.locator("[data-version]").count() == 2  # nothing saved

    page.locator("[data-version='1']").get_by_role("button", name="Przywróć").click()
    page.wait_for_selector("[data-version='3']")
    assert "Opis testowy." in page.locator("#about").inner_text()
    assert page.locator("[data-version='3'] td").nth(1).inner_text() == "przywrócona"
    page.screenshot(path=str(shot_dir / "preview-restored.png"), full_page=True)
    _no_serious_axe_violations(page)
    assert page.locator("script:not([src])").count() == 0
    context.close()
