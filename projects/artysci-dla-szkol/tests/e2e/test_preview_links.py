"""Private preview link and "Kopiuj link" (US-3.7) in a real browser.

The artist creates a link on the publication panel, an anonymous visitor opens it, the artist
revokes it, and after publishing copies the public address with the button.
"""

import uuid

import pytest
from axe_playwright_python.sync_playwright import Axe
from test_publication import _seed  # same folder (no package): pytest puts it on sys.path


@pytest.fixture
def seeded(django_db_blocker):
    with django_db_blocker.unblock():
        yield _seed()


def _serious(page):
    violations = Axe().run(page).response["violations"]
    return [v for v in violations if v["impact"] in ("critical", "serious")]


def test_create_open_revoke_and_copy_public_link(browser, base_url, seeded, shot_dir):
    context = browser.new_context(permissions=["clipboard-read", "clipboard-write"])
    host = base_url.split("://", 1)[1].split("/")[0].split(":")[0]
    context.add_cookies([{"name": seeded[0], "value": seeded[1], "domain": host, "path": "/"}])
    page = context.new_page()

    assert page.goto(base_url + "/panel/publikacja/").status == 200
    assert page.locator("[data-public-copy]").count() == 0  # draft: no public address yet
    page.get_by_role("button", name="Utwórz link do podglądu").click()
    field = page.get_by_role("textbox", name="Link do podglądu")
    url = field.input_value()
    assert "/podglad/" in url and field.get_attribute("readonly") is not None
    assert page.locator("[data-preview-link]").count() == 1
    assert page.locator("[style]").count() == 0
    assert not _serious(page)
    page.screenshot(path=str(shot_dir / "preview-link-created.png"), full_page=True)

    # The link is shown once: the panel does not show it again.
    page.goto(base_url + "/panel/publikacja/")
    assert page.get_by_role("textbox", name="Link do podglądu").count() == 0
    path = "/podglad/" + url.split("/podglad/", 1)[1]

    # A logged-out visitor opens it.
    visitor = browser.new_context().new_page()
    response = visitor.goto(base_url + path)
    assert response.status == 200
    assert response.headers["x-robots-tag"] == "noindex, nofollow"
    assert response.headers["cache-control"] == "no-store"
    assert visitor.locator("[data-shared-preview]").is_visible()
    assert visitor.get_by_text("Opis do publikacji.").is_visible()
    assert visitor.locator("meta[name=robots]").get_attribute("content") == "noindex, nofollow"
    assert visitor.get_by_role("button", name="Zapisz").count() == 0  # no owner controls
    assert "mailto:" not in visitor.content() and "tel:" not in visitor.content()
    assert not _serious(visitor)
    visitor.screenshot(path=str(shot_dir / "preview-link-visitor.png"), full_page=True)
    assert visitor.goto(base_url + "/podglad/" + uuid.uuid4().hex + "/").status == 404

    # Revoked: the same address is gone at once.
    page.get_by_role("button", name="Odwołaj link").click()
    assert page.locator("[data-no-preview-links]").is_visible()
    assert visitor.goto(base_url + path).status == 404

    # Published: "Kopiuj link" copies the public address.
    page.get_by_role("button", name="Opublikuj", exact=True).click()
    public = page.get_by_label("Adres Twojej strony")
    assert "/artysci/teatr-laka-" in public.input_value()
    page.get_by_role("button", name="Kopiuj link").click()
    assert page.get_by_text("Skopiowano link.").is_visible()
    assert page.evaluate("navigator.clipboard.readText()") == public.input_value()
    assert not _serious(page)
    page.screenshot(path=str(shot_dir / "preview-link-copy.png"), full_page=True)
    context.close()


def test_without_javascript_the_address_field_is_the_fallback(browser, base_url, seeded):
    context = browser.new_context(java_script_enabled=False)
    host = base_url.split("://", 1)[1].split("/")[0].split(":")[0]
    context.add_cookies([{"name": seeded[0], "value": seeded[1], "domain": host, "path": "/"}])
    page = context.new_page()
    page.goto(base_url + "/panel/publikacja/")
    page.get_by_role("button", name="Opublikuj", exact=True).click()
    assert page.get_by_label("Adres Twojej strony").is_visible()
    assert not page.get_by_role("button", name="Kopiuj link").is_visible()
    context.close()
