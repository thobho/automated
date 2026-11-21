"""Profile generation status in the artist panel (US-2.5A).

Needs a signed-in artist with ready materials and a running worker: pass the artist's session key
(cookie `sessionid`) as `--artist-session` or `E2E_ARTIST_SESSION`. Without it the test is skipped
(the CI smoke job has no seeded artist); the same flow is covered by apps/profiles tests.
"""

import pytest
from axe_playwright_python.sync_playwright import Axe


@pytest.fixture
def artist_page(browser, base_url, artist_session):
    context = browser.new_context()
    context.add_cookies([{"name": "sessionid", "value": artist_session, "url": base_url}])
    page = context.new_page()
    yield page
    context.close()


def test_artist_starts_a_generation_and_sees_it_finish(artist_page, base_url, shot):
    page = artist_page
    page.goto(base_url + "/artysta/profil/generowanie/")
    assert page.locator("h1").inner_text().strip() == "Generowanie profilu"
    page.get_by_role("button", name="Generuj profil").click()
    page.wait_for_url("**/artysta/profil/generowanie/")
    # The block polls by itself (HTMX, no inline script) until the worker is done.
    page.wait_for_selector("#generation-status[data-status=ready]", timeout=60_000)
    assert "gotowa" in page.locator("#generation-status [data-field=status]").inner_text()
    assert page.get_by_role("button", name="Generuj profil").is_enabled()
    shot("generation-ready")
    critical = [v for v in Axe().run(page).response["violations"] if v["impact"] == "critical"]
    assert not critical, [f"{v['id']}: {v['help']}" for v in critical]
