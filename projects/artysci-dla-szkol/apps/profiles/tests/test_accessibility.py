"""Accessibility of the public page (US-3.6): alt texts, landmarks, headings, skip link, aria on the
expander and gallery, focus contrast in every theme, reduced motion, no inline code. The browser
side (keyboard walk, axe) is in tests/e2e/test_accessibility.py."""

import re
from pathlib import Path

import pytest
from django.conf import settings
from django.test import Client

from apps.accounts.tests.conftest import make_artist
from apps.artists.models import Material, MaterialKind, ScanStatus
from apps.profiles import themes
from apps.profiles.accessibility import ALT_MAX_LENGTH, fallback_photo_alt, photo_alt
from apps.profiles.content import PhotoItem, page_content_for
from apps.profiles.tests.test_page import MEDIA, Page, full_content, offers, render

STATIC = Path(settings.BASE_DIR) / "static"


# --- alt texts --------------------------------------------------------------------------------


def test_fallback_alt_uses_name_and_position():
    assert fallback_photo_alt("Teatr Kwiatki", 2) == "Teatr Kwiatki – zdjęcie 2"
    assert fallback_photo_alt("  ", 3) == "Zdjęcie 3"


def test_stored_alt_wins_and_is_trimmed_and_capped():
    assert photo_alt("  Scena   z lalką ", "Teatr", 1) == "Scena z lalką"
    assert len(photo_alt("x" * 500, "Teatr", 1)) == ALT_MAX_LENGTH
    assert photo_alt("", "Teatr", 4) == "Teatr – zdjęcie 4"
    assert photo_alt("   ", "Teatr", 4) == "Teatr – zdjęcie 4"


@pytest.mark.django_db
def test_page_content_uses_stored_alt_or_fallback(artist_with_photos):
    artist = artist_with_photos
    alts = [p.alt for p in page_content_for(artist).photos]
    assert alts == ["Dzieci klaszczą", "Zespół Żółw – zdjęcie 2", "Zespół Żółw – zdjęcie 3"]


@pytest.fixture
def artist_with_photos(db):
    artist = make_artist(email="alt@example.invalid").artist
    artist.name = "Zespół Żółw"
    artist.save()
    for i, alt in enumerate(["Dzieci klaszczą", "", "  "]):
        Material.objects.create(
            artist=artist,
            kind=MaterialKind.PHOTO,
            status=ScanStatus.READY,
            storage_key=f"k/{i}",
            alt_text=alt,
        )
    return artist


def test_every_img_has_alt_and_decorative_ones_are_empty():
    html = render(full_content(videos=[]))
    imgs = Page(html).attrs_of("img")
    assert imgs and all("alt" in a for a in imgs)
    assert all(a["alt"] for a in imgs)  # the hero and gallery photos carry content


def test_typographic_start_initial_is_hidden_from_readers():
    html = render(full_content(hero=full_content().hero.__class__(name="Teatr")))
    assert 'class="start__initial" aria-hidden="true"' in html


def test_video_thumbnail_has_alt_and_placeholder_is_decorative():
    from apps.profiles.content import VideoItem

    with_poster = render(
        full_content(
            videos=[VideoItem(title="Film", link_url="https://youtu.be/x", poster_url="/t.jpg")]
        )
    )
    assert 'alt="Miniatura filmu: Film"' in with_poster
    without = render(full_content(videos=[VideoItem(title="Film", link_url="https://youtu.be/x")]))
    assert 'class="video-link__placeholder" aria-hidden="true"' in without


# --- structure --------------------------------------------------------------------------------


def test_skip_link_is_first_and_targets_the_content():
    html = render(full_content())
    assert html.index("Przejdź do treści") < html.index("<header")
    assert 'href="#artist-page"' in html and 'id="artist-page"' in html


def test_language_one_h1_no_skipped_levels_and_landmarks():
    page = Page(render(full_content(offers=offers(9))))
    html_tag = next(a for t, a in page.tags if t == "html")
    assert html_tag["lang"] == "pl"
    levels = [int(tag[1]) for tag, _ in page.headings]
    assert levels.count(1) == 1
    for previous, current in zip(levels, levels[1:], strict=False):
        assert current <= previous + 1, levels
    tags = {t for t, _ in page.tags}
    assert {"main", "nav", "header", "footer"} <= tags


def test_offers_expander_is_a_button_with_aria():
    page = Page(render(full_content(offers=offers(8))))
    buttons = [a for a in page.attrs_of("button") if "offers-more__toggle" in a.get("class", "")]
    assert len(buttons) == 1
    assert buttons[0]["aria-expanded"] == "false"
    assert buttons[0]["aria-controls"] == "offers-more-list"
    assert "offers-more-list" in page.ids()


def test_gallery_dialog_has_labelled_controls():
    html = render(full_content())
    page = Page(html)
    dialog = page.attrs_of("dialog")[0]
    assert dialog["aria-label"] == "Galeria zdjęć"
    for name in ("Poprzednie", "Następne", "Zamknij"):
        assert name in html
    assert all(a.get("href") for a in page.attrs_of("a") if "gallery__open" in a.get("class", ""))


def test_link_texts_are_meaningful():
    html = render(full_content())
    assert not re.search(r">\s*(tutaj|kliknij|więcej)\s*</a>", html, re.I)


def test_no_inline_script_or_style():
    html = render(full_content(offers=offers(8), photos=[PhotoItem(MEDIA + "a.jpg", "A")] * 4))
    assert not re.search(r"<script(?![^>]*\ssrc=)", html)
    assert "<style" not in html and " style=" not in html
    assert not re.search(r"\son(click|load|error)=", html)


@pytest.mark.django_db
def test_public_view_carries_the_skip_link():
    client = Client()
    client.force_login(make_artist(email="skip@example.invalid"))
    response = client.get("/panel/podglad/")
    assert response.status_code == 200
    assert "Przejdź do treści" in response.content.decode()


# --- focus and motion -------------------------------------------------------------------------


@pytest.mark.parametrize("slug", sorted(themes.Theme.values))
@pytest.mark.parametrize("surface", ["paper", "card", "band"])
def test_focus_outline_is_at_least_3_to_1_on_every_surface(slug, surface):
    tokens = themes.THEME_TOKENS[slug]
    assert themes.contrast_ratio(tokens["focus"], tokens[surface]) >= themes.AA_LARGE


def test_focus_pairs_stay_in_the_wcag_check():
    for surface in ("paper", "card", "band"):
        assert ("focus", surface) in themes.LARGE_PAIRS
    assert themes.AA_LARGE == 3.0


def test_page_stylesheet_draws_a_visible_focus_outline():
    css = (STATIC / "profiles/page.css").read_text()
    rule = re.search(r"\.artist-page :focus-visible\s*\{([^}]*)\}", css).group(1)
    assert "var(--focus)" in rule
    assert int(re.search(r"outline:\s*(\d+)px", rule).group(1)) >= 2
    assert "outline: none" not in css.replace(".artist-page:focus { outline: none; }", "")


@pytest.mark.parametrize("selector", [r"\.skip-link:focus", r"(?m)^:focus-visible"])
def test_focus_outline_outside_the_themed_root_contrasts_with_the_white_page(selector):
    css = (STATIC / "profiles/page.css").read_text()
    rule = re.search(selector + r"\s*\{([^}]*)\}", css).group(1)
    width, colour = re.search(r"outline:\s*(\d+)px solid (#[0-9a-f]{3,6});", rule).groups()
    if len(colour) == 4:
        colour = "#" + "".join(c * 2 for c in colour[1:])
    assert int(width) >= 2
    assert themes.contrast_ratio(colour, "#ffffff") >= themes.AA_LARGE


def _strip_comments(css):
    return re.sub(r"/\*.*?\*/", "", css, flags=re.S)


def _blocks(css):
    """(media query or "", declarations) for every rule; one nesting level is enough here."""
    css = _strip_comments(css)
    out = []
    for media in re.finditer(r"@media([^{]+)\{((?:[^{}]*\{[^{}]*\})*)\s*\}", css):
        for rule in re.finditer(r"[^{}]*\{([^}]*)\}", media.group(2)):
            out.append((media.group(1).strip(), rule.group(1)))
    plain = re.sub(r"@media[^{]+\{(?:[^{}]*\{[^{}]*\})*\s*\}", "", css)
    for rule in re.finditer(r"[^{}]*\{([^}]*)\}", plain):
        out.append(("", rule.group(1)))
    return out


# `transition-duration` too: transition-property is `all` by default, so a duration alone moves.
MOTION = re.compile(
    r"(?<![\w-])(animation(?:-name)?|transition(?:-property|-duration)?|scroll-behavior)"
    r"\s*:\s*([^;}]+)"
)
MOTION_OFF = {"none", "auto", "0s", ".01ms"}  # the whole value, never just its start


def _unguarded_motion(css):
    bad = []
    for media, body in _blocks(css):
        for prop, value in MOTION.findall(body):
            value = value.strip()
            if re.sub(r"\s*!\s*important$", "", value) in MOTION_OFF:
                continue  # switching motion off
            if "prefers-reduced-motion: no-preference" in media:
                continue
            bad.append(f"{prop}: {value}")
    return bad


@pytest.mark.parametrize("path", sorted(STATIC.glob("profiles/*.css")), ids=lambda p: p.name)
def test_stylesheets_have_no_unguarded_motion(path):
    assert _unguarded_motion(path.read_text()) == []


def test_scan_fails_on_an_unguarded_animation():
    assert _unguarded_motion(".a { transition: color .3s ease; }") == ["transition: color .3s ease"]
    assert _unguarded_motion(".a { animation: spin 1s infinite; }")
    assert _unguarded_motion("html { scroll-behavior: smooth; }")
    # `!important` is no excuse, nor is a value that only starts with an "off" keyword.
    assert _unguarded_motion(".a { animation: spin 1s infinite !important; }") == [
        "animation: spin 1s infinite !important"
    ]
    assert _unguarded_motion(".a { transition: color 3s !important; }")
    assert _unguarded_motion(".a { transition: 0s color, 3s opacity; }")
    assert _unguarded_motion(".a { animation: none 0s, spin 1s; }")
    assert _unguarded_motion(".a { transition-duration: .3s; }")
    for off in ("transition: none", "animation: none !important", "scroll-behavior: auto"):
        assert _unguarded_motion(f".a {{ {off}; }}") == []
    guarded = "@media (prefers-reduced-motion: no-preference) { .a { transition: color .3s; } }"
    assert _unguarded_motion(guarded) == []


def test_page_stylesheet_switches_motion_off_for_reduce():
    css = _strip_comments((STATIC / "profiles/page.css").read_text())
    reduce_block = re.search(r"@media \(prefers-reduced-motion: reduce\)\s*\{(.*?)\n\}", css, re.S)
    assert reduce_block
    for needle in ("animation-duration", "transition-duration", "scroll-behavior: auto"):
        assert needle in reduce_block.group(1)


# --- artist edits the alt text ----------------------------------------------------------------


@pytest.mark.django_db
def test_artist_saves_alt_text_and_cannot_edit_another_artists_photo():
    from apps.artists import materials

    mine = make_artist(email="mine@example.invalid").artist
    other = make_artist(email="other@example.invalid").artist
    photo = Material.objects.create(
        artist=mine, kind=MaterialKind.PHOTO, status=ScanStatus.READY, storage_key="k/1"
    )
    materials.set_alt_text(mine, photo.pk, "  Dzieci   na scenie ")
    photo.refresh_from_db()
    assert photo.alt_text == "Dzieci na scenie"
    with pytest.raises(Material.DoesNotExist):
        materials.set_alt_text(other, photo.pk, "cudze")
    pdf = Material.objects.create(
        artist=mine, kind=MaterialKind.PDF, status=ScanStatus.READY, storage_key="k/2"
    )
    with pytest.raises(Material.DoesNotExist):
        materials.set_alt_text(mine, pdf.pk, "to nie zdjęcie")
