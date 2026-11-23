"""Accessibility of the artist page in a real browser (US-3.6, D110): axe in all four themes,
a keyboard walk (skip link, tab order, visible focus), the "Pokaż pozostałe" button, the
gallery dialog and reduced motion. Data is created in the live database the server uses and
removed afterwards (photos have no real files: the images do not load, which the checks do not
need)."""

import re
import uuid

import pytest
from axe_playwright_python.sync_playwright import Axe

PREVIEW = "/panel/podglad/"
THEMES = ["burgundy_light", "cream_green", "navy_gold", "coral_dark"]
TABBABLE = "a[href], button:not([hidden]), input, select, textarea, summary, [tabindex='0']"


@pytest.fixture
def seeded(django_db_blocker):
    """Yields (cookie name, value, artist) of a logged-in artist with 8 offers, 4 photos (one with
    a stored alt text) and a video link."""
    from django.conf import settings
    from django.contrib.auth import get_user_model
    from django.test import Client

    from apps.artists.models import Artist, Material, MaterialKind, Offer, ScanStatus

    with django_db_blocker.unblock():
        email = f"e2e-a11y-{uuid.uuid4().hex[:8]}@example.invalid"
        user = get_user_model().objects.create_user(email=email)
        artist = Artist.objects.create(user=user, name="Zespół Żółw", city="Wrocław")
        for i in range(8):
            Offer.objects.create(
                artist=artist,
                title=f"Spektakl {i + 1}",
                description="Opis spektaklu",
                price_on_request=True,
                position=i,
            )
        for i in range(4):
            Material.objects.create(
                artist=artist,
                kind=MaterialKind.PHOTO,
                status=ScanStatus.READY,
                storage_key=f"e2e/{uuid.uuid4().hex}.jpg",
                alt_text="Dzieci klaszczą na scenie" if i == 0 else "",
            )
        Material.objects.create(
            artist=artist,
            kind=MaterialKind.LINK,
            status=ScanStatus.READY,
            provider="youtube",
            video_id="abc",
            canonical_url="https://www.youtube.com/watch?v=abc",
            title="Fragment spektaklu",
        )
        client = Client()
        client.force_login(user)
        try:
            yield (
                settings.SESSION_COOKIE_NAME,
                client.cookies[settings.SESSION_COOKIE_NAME].value,
                artist,
            )
        finally:
            user.delete()


def _open(browser, base_url, seeded, theme, **context_options):
    from apps.artists.models import Artist

    name, value, artist = seeded
    Artist.objects.filter(pk=artist.pk).update(theme=theme)
    context = browser.new_context(**context_options)
    host = base_url.split("://", 1)[1].split("/")[0].split(":")[0]
    context.add_cookies([{"name": name, "value": value, "domain": host, "path": "/"}])
    page = context.new_page()
    assert page.goto(base_url + PREVIEW).status == 200
    return context, page


@pytest.mark.parametrize("theme", THEMES)
def test_axe_has_no_critical_or_serious_violations(browser, base_url, seeded, shot_dir, theme):
    context, page = _open(browser, base_url, seeded, theme)
    assert page.locator(".artist-root").get_attribute("data-theme") == theme
    page.get_by_role("button", name=re.compile("Pokaż pozostałe")).click()
    page.screenshot(path=str(shot_dir / f"a11y-{theme}.png"), full_page=True)
    violations = Axe().run(page).response["violations"]
    bad = [v for v in violations if v["impact"] in ("critical", "serious")]
    print(f"AXE {theme}: {len(violations)} violations, {len(bad)} critical/serious")
    assert not bad, [f"{v['id']}: {v['help']}" for v in bad]
    context.close()


def test_images_have_alt_and_structure_is_sound(browser, base_url, seeded):
    context, page = _open(browser, base_url, seeded, "burgundy_light")
    assert page.locator("html").get_attribute("lang") == "pl"
    assert page.locator("h1").count() == 1
    imgs = page.locator(".artist-root img")
    assert imgs.count() >= 4
    alts = [imgs.nth(i).get_attribute("alt") for i in range(imgs.count())]
    assert all(a is not None for a in alts)
    assert "Dzieci klaszczą na scenie" in alts
    assert "Zespół Żółw – zdjęcie 2" in alts  # no stored text: the Polish fallback
    assert page.locator("script:not([src])").count() == 0
    context.close()


def test_keyboard_walk_visits_skip_link_then_every_control_with_a_visible_outline(
    browser, base_url, seeded
):
    from apps.profiles.themes import AA_LARGE, THEME_TOKENS, contrast_ratio

    context, page = _open(browser, base_url, seeded, "navy_gold")
    page.keyboard.press("Tab")
    assert page.evaluate("document.activeElement.className") == "skip-link"
    page.keyboard.press("Enter")  # jumps to the content
    assert page.evaluate("document.activeElement.id") == "artist-page"

    expected = page.evaluate(
        """(sel) => [...document.querySelectorAll(
              sel.split(', ').map(s => '.artist-root ' + s).join(', '))]
            .filter(e => e.offsetParent !== null && !e.closest('dialog'))
            .map(e => e.getAttribute('href') || e.textContent.trim().slice(0, 30))""",
        TABBABLE,
    )
    assert len(expected) >= 12  # nav, button, offers, video, 4 photos, inquiry...
    seen = []
    paper = THEME_TOKENS["navy_gold"]["paper"]
    for _ in range(len(expected) + 1):
        page.keyboard.press("Tab")
        info = page.evaluate(
            """() => { const e = document.activeElement; const s = getComputedStyle(e);
              return {inside: !!e.closest('.artist-root'), label: e.getAttribute('href') ||
                e.textContent.trim().slice(0, 30), width: parseFloat(s.outlineWidth),
                style: s.outlineStyle, color: s.outlineColor}; }"""
        )
        if not info["inside"]:
            break
        seen.append(info["label"])
        assert info["style"] != "none" and info["width"] >= 2, info
        rgb = [int(x) for x in re.findall(r"\d+", info["color"])[:3]]
        assert contrast_ratio("#{:02x}{:02x}{:02x}".format(*rgb), paper) >= AA_LARGE, info
    assert seen == expected
    context.close()


def test_offers_button_toggles_with_enter_and_space(browser, base_url, seeded):
    context, page = _open(browser, base_url, seeded, "cream_green")
    button = page.locator("button.offers-more__toggle")
    more = page.locator("#offers-more-list")
    assert button.get_attribute("aria-controls") == "offers-more-list"
    assert button.get_attribute("aria-expanded") == "false"
    assert not more.is_visible()
    button.focus()
    page.keyboard.press("Enter")
    assert button.get_attribute("aria-expanded") == "true"
    assert more.is_visible()
    assert more.locator("li.offer").count() == 2
    page.keyboard.press("Space")
    assert button.get_attribute("aria-expanded") == "false"
    assert not more.is_visible()
    page.keyboard.press("Space")
    assert button.get_attribute("aria-expanded") == "true"
    context.close()


def test_gallery_dialog_keyboard(browser, base_url, seeded, shot_dir):
    context, page = _open(browser, base_url, seeded, "coral_dark")
    opener = page.locator(".gallery__open").nth(1)
    opener.focus()
    page.keyboard.press("Enter")
    dialog = page.locator("dialog#lightbox")
    assert dialog.get_attribute("open") is not None
    assert dialog.locator("img").get_attribute("alt") == "Zespół Żółw – zdjęcie 2"
    for _ in range(6):  # focus stays inside the dialog
        page.keyboard.press("Tab")
        assert page.evaluate("!!document.activeElement.closest('dialog#lightbox')")
    page.screenshot(path=str(shot_dir / "a11y-gallery-open.png"))
    page.keyboard.press("ArrowRight")
    assert dialog.locator("img").get_attribute("alt") == "Zespół Żółw – zdjęcie 3"
    page.keyboard.press("Escape")
    assert dialog.get_attribute("open") is None
    assert page.evaluate("document.activeElement.getAttribute('href')") == opener.get_attribute(
        "href"
    )
    assert page.evaluate("document.activeElement.className") == "gallery__open"
    context.close()


def test_reduced_motion_turns_smooth_scrolling_and_transitions_off(browser, base_url, seeded):
    context, page = _open(browser, base_url, seeded, "burgundy_light", reduced_motion="reduce")
    assert page.evaluate("getComputedStyle(document.documentElement).scrollBehavior") == "auto"
    running = page.evaluate("document.getAnimations().length")
    assert running == 0
    context.close()
    context, page = _open(
        browser, base_url, seeded, "burgundy_light", reduced_motion="no-preference"
    )
    assert page.evaluate("getComputedStyle(document.documentElement).scrollBehavior") == "smooth"
    context.close()
