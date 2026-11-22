"""Page themes (US-3.2): contrast, CSS vs mapping, choice, switch, AI proposal, no inline style."""

import re
from pathlib import Path

import pytest
from django.contrib.staticfiles import finders
from django.template.loader import render_to_string
from django.test import Client
from django.utils import timezone

from apps.accounts.tests.conftest import make_artist, make_institution_member
from apps.artists.models import Artist
from apps.profiles import services
from apps.profiles.content import Hero, PageContent
from apps.profiles.themes import (
    AA_LARGE,
    AA_TEXT,
    DEFAULT_THEME,
    LARGE_PAIRS,
    TEXT_PAIRS,
    THEME_TOKENS,
    Theme,
    contrast_ratio,
    theme_or_default,
)
from apps.quality.models import Generation

from .factories import make_seed_artist, valid_profile

PREVIEW = "/panel/podglad/"
SWITCH = "/panel/podglad/motyw/"
THEMES = [t.value for t in Theme]
CSS = Path(finders.find("profiles/themes.css")).read_text()


def parse_css(css: str) -> dict[str, dict[str, str]]:
    """{slug: {token: value}} from the `[data-theme="slug"]` blocks."""
    found = {}
    for selector, body in re.findall(r"([^{}]+)\{([^{}]*)\}", css):
        match = re.search(r'\[data-theme="([a-z_]+)"\]', selector)
        if match:
            found[match.group(1)] = dict(re.findall(r"--([a-z-]+):\s*(#[0-9a-fA-F]{6})\s*;", body))
    return found


def mismatches(css: str) -> list[str]:
    parsed = parse_css(css)
    problems = []
    for slug, tokens in THEME_TOKENS.items():
        if parsed.get(slug) != tokens:
            problems.append(slug)
    problems += [s for s in parsed if s not in THEME_TOKENS]
    return problems


# --- contrast -----------------------------------------------------------------------------------


def test_contrast_ratio_extremes():
    assert contrast_ratio("#000000", "#ffffff") == pytest.approx(21)
    assert contrast_ratio("#ffffff", "#000000") == pytest.approx(21)
    assert contrast_ratio("#7a1f3d", "#7a1f3d") == 1
    assert contrast_ratio("#fff", "#000") == pytest.approx(21)  # short form


def test_contrast_ratio_known_value():
    # WCAG reference: #767676 on white is 4.54:1.
    assert contrast_ratio("#767676", "#ffffff") == pytest.approx(4.54, abs=0.01)


@pytest.mark.parametrize("slug", THEMES)
def test_every_theme_meets_wcag_aa(slug, capsys):
    tokens = THEME_TOKENS[slug]
    lines = []
    for fg, bg in TEXT_PAIRS:
        ratio = contrast_ratio(tokens[fg], tokens[bg])
        lines.append(f"  {slug}: {fg} on {bg} = {ratio:.2f}:1 (min {AA_TEXT})")
        assert ratio >= AA_TEXT, lines[-1]
    for fg, bg in LARGE_PAIRS:
        ratio = contrast_ratio(tokens[fg], tokens[bg])
        lines.append(f"  {slug}: {fg} on {bg} = {ratio:.2f}:1 (min {AA_LARGE})")
        assert ratio >= AA_LARGE, lines[-1]
    with capsys.disabled():
        print("\n" + "\n".join(lines))


def test_all_themes_define_the_same_tokens():
    assert len({frozenset(t) for t in THEME_TOKENS.values()}) == 1
    assert set(THEME_TOKENS) == set(THEMES)


# --- CSS and mapping ----------------------------------------------------------------------------


def test_stylesheet_matches_the_mapping():
    assert mismatches(CSS) == []


def test_a_drifted_token_fails_the_consistency_check():
    drifted = CSS.replace("--ink: #f4efe0;", "--ink: #f4efe1;", 1)
    assert drifted != CSS
    assert mismatches(drifted) == ["navy_gold"]


def test_a_missing_theme_block_fails_the_consistency_check():
    assert mismatches(CSS.replace('[data-theme="coral_dark"]', '[data-theme="other"]')) == [
        "coral_dark",
        "other",
    ]


# --- fallback and rendering ---------------------------------------------------------------------


def test_unknown_theme_falls_back_to_default():
    assert theme_or_default("neon") == DEFAULT_THEME == "burgundy_light"
    assert theme_or_default(None) == DEFAULT_THEME
    content = PageContent(slug="x", hero=Hero(name="X"), theme="neon")
    assert content.theme == DEFAULT_THEME.value


def render(theme):
    return render_to_string(
        "profiles/page.html",
        {
            "content": PageContent(
                slug="x", hero=Hero(name="X"), for_schools="Dla szkół", theme=theme
            )
        },
    )


@pytest.mark.parametrize("slug", THEMES)
def test_root_carries_only_the_chosen_theme(slug):
    html = render(slug)
    assert f'class="artist-root" data-theme="{slug}"' in html
    assert html.count("data-theme=") == 1
    assert "themes.css" in html


@pytest.mark.parametrize("slug", [*THEMES, "neon"])
def test_no_inline_style_and_no_external_host(slug):
    html = render(slug)
    assert "<style" not in html and "style=" not in html
    assert not re.search(r"(?:href|src)=\"(?:https?:)?//", html)
    assert "@import" not in CSS and "url(" not in CSS


# --- views and services -------------------------------------------------------------------------


@pytest.fixture
def artist():
    return make_seed_artist()


@pytest.fixture
def web(artist):
    client = Client()
    client.force_login(artist.user)
    return client


@pytest.mark.django_db
def test_default_theme_without_choice_or_proposal(web):
    html = web.get(PREVIEW).content.decode()
    assert 'class="artist-root" data-theme="burgundy_light"' in html


@pytest.mark.django_db
def test_owner_chooses_a_theme_and_preview_renders_it(web, artist):
    response = web.post(SWITCH, {"theme": "navy_gold"})
    assert response.status_code == 302 and response["Location"] == PREVIEW
    artist.refresh_from_db()
    assert artist.theme == "navy_gold"
    html = web.get(PREVIEW).content.decode()
    assert 'class="artist-root" data-theme="navy_gold"' in html
    for other in ("burgundy_light", "cream_green", "coral_dark"):
        assert f'class="artist-root" data-theme="{other}"' not in html
    assert 'value="navy_gold" checked' in html
    assert html.count('type="radio"') == 4 and html.count("data-swatch=") == 4


@pytest.mark.django_db
def test_unknown_theme_is_refused_and_changes_nothing(web, artist):
    web.post(SWITCH, {"theme": "navy_gold"})
    response = web.post(SWITCH, {"theme": "neon"}, follow=True)
    assert "Nieznany motyw" in response.content.decode()
    artist.refresh_from_db()
    assert artist.theme == "navy_gold"
    assert web.post(SWITCH, {}).status_code == 302


@pytest.mark.django_db
def test_unknown_stored_value_uses_default_without_error(web, artist):
    Artist.objects.filter(pk=artist.pk).update(theme="neon")
    response = web.get(PREVIEW)
    assert response.status_code == 200
    assert 'data-theme="burgundy_light"' in response.content.decode()


@pytest.mark.django_db
def test_switch_refuses_anonymous_and_other_roles():
    anonymous = Client().post(SWITCH, {"theme": "navy_gold"})
    assert anonymous.status_code == 302 and "logowanie" in anonymous["Location"]
    client = Client()
    client.force_login(make_institution_member())
    assert client.post(SWITCH, {"theme": "navy_gold"}).status_code == 403


@pytest.mark.django_db
def test_an_artist_only_changes_their_own_theme(web, artist):
    other_user = make_artist("inny@example.invalid")
    other = Artist.objects.get(user=other_user)
    web.post(SWITCH, {"theme": "coral_dark"})
    other.refresh_from_db()
    assert other.theme == ""


@pytest.mark.django_db
def test_switch_needs_a_csrf_token(artist):
    client = Client(enforce_csrf_checks=True)
    client.force_login(artist.user)
    assert client.post(SWITCH, {"theme": "navy_gold"}).status_code == 403
    artist.refresh_from_db()
    assert artist.theme == ""


@pytest.mark.django_db
def test_switch_is_post_only(web):
    assert web.get(SWITCH).status_code == 405


@pytest.mark.django_db
def test_preview_form_carries_a_csrf_token(web):
    assert "csrfmiddlewaretoken" in web.get(PREVIEW).content.decode()


def finished_generation(artist, theme, status=Generation.Status.READY):
    now = timezone.now()
    return Generation.objects.create(
        artist=artist,
        trigger="manual",
        status=status,
        result=valid_profile(theme=theme),
        started_at=now,
        finished_at=now,
    )


@pytest.mark.django_db
def test_valid_ai_proposal_is_used_without_a_choice(artist):
    finished_generation(artist, "cream_green")
    assert services.theme_for(artist) == "cream_green"


@pytest.mark.django_db
def test_ai_proposal_in_review_status_is_used_too(artist):
    finished_generation(artist, "coral_dark", Generation.Status.REVIEW)
    assert services.theme_for(artist) == "coral_dark"


@pytest.mark.django_db
def test_invalid_ai_proposal_or_failed_run_gives_default(artist):
    finished_generation(artist, "neon")
    finished_generation(artist, "navy_gold", Generation.Status.ERROR)
    assert services.theme_for(artist) == DEFAULT_THEME


@pytest.mark.django_db
def test_artist_choice_beats_a_later_generation(artist):
    services.set_theme(artist, "navy_gold")
    finished_generation(artist, "cream_green")
    assert services.theme_for(artist) == "navy_gold"


@pytest.mark.django_db
def test_set_theme_rejects_unknown_slug(artist):
    with pytest.raises(services.InvalidTheme):
        services.set_theme(artist, "neon")
