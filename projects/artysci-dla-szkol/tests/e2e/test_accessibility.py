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
TABBABLE = (
    "a[href], button:not([disabled]), input:not([type=hidden]), select, textarea, summary, "
    "[tabindex='0']"
)

# Remembers every tab stop of the page (a radio group is one stop: its checked radio) in DOM
# order, which is the visual order here; returns their labels.
TAB_STOPS = """(sel) => {
  window.__stops = [...document.querySelectorAll(sel)].filter(e =>
    e.checkVisibility({checkVisibilityCSS: true}) && !e.closest('dialog')
    && !(e.type === 'radio' && !e.checked));
  return window.__stops.map(e => e.getAttribute('href') || e.value || e.textContent.trim());
}"""

# The focused element: its index in the stops, its outline, and the first opaque background
# behind the outline (the offset puts the outline outside the element, so on its parent).
FOCUSED = """() => {
  const e = document.activeElement, s = getComputedStyle(e);
  let background = 'rgb(255, 255, 255)';
  for (let p = e.parentElement; p; p = p.parentElement) {
    const c = getComputedStyle(p).backgroundColor;
    if (c !== 'rgba(0, 0, 0, 0)') { background = c; break; }
  }
  return {index: (window.__stops || []).indexOf(e), html: e.outerHTML.slice(0, 80),
    cls: e.className, id: e.id, style: s.outlineStyle, width: parseFloat(s.outlineWidth),
    offset: parseFloat(s.outlineOffset), color: s.outlineColor, background};
}"""


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


def _hex(css_colour):
    parts = re.findall(r"[\d.]+", css_colour)
    assert css_colour.startswith("rgb") and (len(parts) == 3 or float(parts[3]) == 1), css_colour
    return "#{:02x}{:02x}{:02x}".format(*(int(p) for p in parts[:3]))


def _assert_visible_outline(info):
    """A solid outline of at least 2px, outside the element, at least 3:1 to what is behind it.
    Returns the ratio."""
    from apps.profiles.themes import AA_LARGE, contrast_ratio

    assert info["style"] == "solid" and info["width"] >= 2 and info["offset"] > 0, info
    ratio = contrast_ratio(_hex(info["color"]), _hex(info["background"]))
    assert ratio >= AA_LARGE, (ratio, info)
    return ratio


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


@pytest.mark.parametrize("theme", THEMES)
def test_keyboard_walk_visits_skip_link_then_every_control_with_a_visible_outline(
    browser, base_url, seeded, shot_dir, theme
):
    context, page = _open(browser, base_url, seeded, theme)
    stops = page.evaluate(TAB_STOPS, TABBABLE)
    assert stops[0] == "#artist-page"  # the skip link
    assert theme in stops and "Zapisz motyw" in stops  # the theme switch
    assert len(stops) >= 25  # account, theme switch, editor, page, 4 photos, footer
    lowest = 21.0
    for index, label in enumerate(stops):
        page.keyboard.press("Tab")
        info = page.evaluate(FOCUSED)
        assert info["index"] == index, (label, info)
        lowest = min(lowest, _assert_visible_outline(info))
        if index == 0:
            assert info["cls"] == "skip-link"
            page.screenshot(path=str(shot_dir / f"a11y-skip-link-{theme}.png"))
    print(f"FOCUS {theme}: {len(stops)} tab stops, lowest outline contrast {lowest:.2f}:1")
    context.close()


def test_skip_link_jumps_to_the_content(browser, base_url, seeded):
    context, page = _open(browser, base_url, seeded, "navy_gold")
    page.keyboard.press("Tab")
    page.keyboard.press("Enter")
    assert page.evaluate("document.activeElement.id") == "artist-page"
    page.keyboard.press("Tab")  # the next stop is the first control of the content
    assert page.evaluate(
        "document.activeElement === document.querySelector('.artist-page a, .artist-page button')"
    )
    context.close()


def test_theme_switch_works_with_the_keyboard_alone(browser, base_url, seeded, shot_dir):
    context, page = _open(browser, base_url, seeded, "burgundy_light")
    root = page.locator(".artist-root")
    assert root.get_attribute("data-theme") == "burgundy_light"
    for _ in range(6):
        page.keyboard.press("Tab")
        if page.evaluate("document.activeElement.name") == "theme":
            break
    assert page.evaluate("document.activeElement.value") == "burgundy_light"  # the checked radio
    _assert_visible_outline(page.evaluate(FOCUSED))
    for _ in range(len(THEMES)):  # arrows move between the themes
        if page.evaluate("document.activeElement.value") == "coral_dark":
            break
        page.keyboard.press("ArrowRight")
        _assert_visible_outline(page.evaluate(FOCUSED))
    assert page.locator("input[name=theme]:checked").get_attribute("value") == "coral_dark"
    page.screenshot(path=str(shot_dir / "a11y-theme-switch-focus.png"))
    page.keyboard.press("Tab")
    assert page.evaluate("document.activeElement.textContent.trim()") == "Zapisz motyw"
    _assert_visible_outline(page.evaluate(FOCUSED))
    with page.expect_navigation():
        page.keyboard.press("Enter")
    assert root.get_attribute("data-theme") == "coral_dark"
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
        _assert_visible_outline(page.evaluate(FOCUSED))
    dialog.locator("[data-lightbox=prev]").focus()  # backwards from the first control: the last
    page.keyboard.press("Shift+Tab")
    assert page.evaluate("document.activeElement.dataset.lightbox") == "close"
    page.keyboard.press("Shift+Tab")
    assert page.evaluate("document.activeElement.dataset.lightbox") == "next"
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


def test_modified_click_on_a_photo_is_left_to_the_browser(browser, base_url, seeded):
    context, page = _open(browser, base_url, seeded, "cream_green")
    with context.expect_page():  # a new tab with the photo, not the dialog
        page.locator(".gallery__open").first.click(modifiers=["ControlOrMeta"])
    assert page.locator("dialog#lightbox").get_attribute("open") is None
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
