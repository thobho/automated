"""Profile generation status in the artist panel (US-2.5A) in a real browser.

Each test seeds its own artist with ready materials in the live database the server uses
(DATABASE_URL) and logs in with a session cookie. The CI e2e job runs no worker, so the flow is
split: one test starts a run and sees the `trwa` block, the other seeds a finished `gotowa` run
and checks the Polish status and accessibility. The whole run with a worker is covered by
apps/profiles/tests/test_generation.py.

The seeded rows stay in the database: a `Generation` cannot be deleted (registry, D107) and
protects its artist. The data is synthetic (`example.invalid`, a fresh address per test).
"""

import uuid

import pytest
from axe_playwright_python.sync_playwright import Axe

PAGE = "/artysta/profil/generowanie/"


def _seed_artist(finished: bool):
    from django.conf import settings
    from django.test import Client

    from apps.profiles.generator_components import COMPONENTS
    from apps.profiles.tests.factories import make_seed_artist, valid_profile
    from apps.quality import services as quality
    from apps.quality.models import Generation

    artist = make_seed_artist(f"e2e-gen-{uuid.uuid4().hex[:8]}@example.invalid")
    if finished:
        record = quality.start_generation(artist, Generation.Trigger.MANUAL, COMPONENTS)
        quality.finish_generation(record, valid_profile(), [], 0, Generation.Status.READY)
    client = Client()
    client.force_login(artist.user)
    return settings.SESSION_COOKIE_NAME, client.cookies[settings.SESSION_COOKIE_NAME].value


def _page(browser, base_url, cookie):
    context = browser.new_context()
    host = base_url.split("://", 1)[1].split("/")[0].split(":")[0]
    context.add_cookies([{"name": cookie[0], "value": cookie[1], "domain": host, "path": "/"}])
    return context, context.new_page()


def _no_serious_axe_violations(page):
    violations = Axe().run(page).response["violations"]
    bad = [v for v in violations if v["impact"] in ("critical", "serious")]
    assert not bad, [f"{v['id']}: {v['help']}" for v in bad]


@pytest.fixture
def new_artist(django_db_blocker):
    with django_db_blocker.unblock():
        yield _seed_artist(finished=False)


@pytest.fixture
def artist_with_ready_profile(django_db_blocker):
    with django_db_blocker.unblock():
        yield _seed_artist(finished=True)


def test_generation_page_is_not_public(page, base_url):
    page.goto(base_url + PAGE)
    assert "logowanie" in page.url


def test_artist_starts_a_generation_and_sees_trwa(browser, base_url, new_artist, shot_dir):
    context, page = _page(browser, base_url, new_artist)
    response = page.goto(base_url + PAGE)
    assert response.status == 200
    assert page.locator("h1").inner_text().strip() == "Generowanie profilu"
    assert "Profil nie był jeszcze generowany" in page.locator("#generation-status").inner_text()

    page.get_by_role("button", name="Generuj profil").click()
    page.wait_for_selector("#generation-status[data-status=running]")
    status = page.locator("#generation-status [data-field=status]").inner_text()
    assert "trwa" in status
    assert page.get_by_role("button", name="Generuj profil").is_disabled()
    # The block polls by itself through HTMX attributes, without inline script.
    assert page.locator("#generation-status").get_attribute("hx-trigger") == "every 3s"
    assert page.locator("script:not([src])").count() == 0
    page.screenshot(path=str(shot_dir / "generation-running.png"), full_page=True)
    _no_serious_axe_violations(page)
    context.close()


def test_artist_sees_a_ready_generation(browser, base_url, artist_with_ready_profile, shot_dir):
    context, page = _page(browser, base_url, artist_with_ready_profile)
    response = page.goto(base_url + PAGE)
    assert response.status == 200
    block = page.locator("#generation-status")
    assert block.get_attribute("data-status") == "ready"
    assert block.get_attribute("hx-get") is None  # finished: no more polling
    assert "gotowa" in page.locator("#generation-status [data-field=status]").inner_text()
    assert page.get_by_role("button", name="Generuj profil").is_enabled()
    page.screenshot(path=str(shot_dir / "generation-ready.png"), full_page=True)
    _no_serious_axe_violations(page)
    context.close()
