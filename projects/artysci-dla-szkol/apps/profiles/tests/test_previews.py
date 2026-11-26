"""Private preview links (US-3.7) and the "Kopiuj link" button."""

import hashlib
import io
import json
import logging
import re
from datetime import timedelta

import pytest
from django.test import Client
from django.urls import reverse
from django.utils import timezone

from apps.accounts.models import ThrottleEvent
from apps.accounts.tests.conftest import make_artist
from apps.analytics.models import Visit
from apps.artists.models import Artist, MaterialKind
from apps.core.logs import JsonFormatter, RequestContextFilter, redact
from apps.profiles import pages, previews, publication
from apps.profiles.models import PreviewLink

from .factories import add_material
from .test_publication import client_for, make_ready

pytestmark = pytest.mark.django_db

CREATE = reverse("profiles:preview_link_create")
REVOKE = reverse("profiles:preview_link_revoke")
PANEL = reverse("profiles:publication")


def shared(token):
    return reverse("profiles:shared_preview", args=[token])


def bare_artist(email="szkic@example.invalid") -> Artist:
    return Artist.objects.get(user=make_artist(email))


# --- service: tokens, hashing, expiry ------------------------------------------------------------


def test_create_stores_only_the_hash_and_expires_in_7_days():
    artist = bare_artist()
    now = timezone.now()
    link, token = previews.create_link(artist, now=now)
    assert len(token) == 43 and previews.is_well_formed(token)  # 256 bits, URL-safe
    row = PreviewLink.objects.get(pk=link.pk)
    assert row.token_hash == hashlib.sha256(token.encode()).hexdigest()
    assert token not in json.dumps([str(v) for v in PreviewLink.objects.values().first().values()])
    assert row.expires_at - row.created_at == timedelta(days=7)
    assert previews.artist_for_token(token, now=now) == artist


def test_tokens_are_unique():
    artist = bare_artist()
    tokens = {previews.create_link(artist)[1] for _ in range(3)}
    assert len(tokens) == 3


def test_expiry_boundary():
    artist = bare_artist()
    now = timezone.now()
    _link, token = previews.create_link(artist, now=now)
    almost = now + previews.VALIDITY - timedelta(seconds=1)
    assert previews.artist_for_token(token, now=almost) == artist
    assert previews.artist_for_token(token, now=now + previews.VALIDITY) is None


@pytest.mark.parametrize("token", ["", "x", "a" * 42, "a" * 44, "a" * 42 + "!", "../" * 15])
def test_malformed_tokens_open_nothing(token):
    previews.create_link(bare_artist())
    assert previews.artist_for_token(token) is None


def test_at_most_three_active_links():
    artist = bare_artist()
    now = timezone.now()
    for _ in range(3):
        previews.create_link(artist, now=now)
    with pytest.raises(previews.PreviewRefused) as refused:
        previews.create_link(artist, now=now)
    assert "Odwołaj jeden" in str(refused.value.message)
    # An expired or revoked link frees a place.
    first = previews.active_links(artist, now=now)[-1]
    assert previews.revoke_link(artist, first.pk, now=now)
    previews.create_link(artist, now=now)
    later = now + previews.VALIDITY
    assert previews.active_links(artist, now=later) == []
    previews.create_link(artist, now=later)


def test_revoke_works_at_once_and_only_on_own_links():
    owner, other = bare_artist("a@example.invalid"), bare_artist("b@example.invalid")
    link, token = previews.create_link(owner)
    assert not previews.revoke_link(other, link.pk)
    assert previews.artist_for_token(token) == owner
    assert not previews.revoke_link(owner, "nie-liczba")
    assert previews.revoke_link(owner, link.pk)
    assert previews.artist_for_token(token) is None
    assert not previews.revoke_link(owner, link.pk)  # already revoked


def test_withdrawn_or_deactivated_artist_link_stops_working():
    artist = make_ready()
    _link, token = previews.create_link(artist)
    publication.publish(artist)
    assert previews.artist_for_token(token) is not None  # published is fine
    publication.withdraw(artist)
    assert previews.artist_for_token(token) is None

    other = bare_artist("dezaktywowany@example.invalid")
    _link, token = previews.create_link(other)
    other.user.is_active = False
    other.user.save()
    assert previews.artist_for_token(token) is None


def test_deleted_artist_takes_its_links_along():
    artist = bare_artist()
    _link, token = previews.create_link(artist)
    artist.user.delete()
    assert not PreviewLink.objects.exists() and previews.artist_for_token(token) is None


def test_a_token_never_opens_another_artists_page():
    one, two = bare_artist("one@example.invalid"), bare_artist("two@example.invalid")
    Artist.objects.filter(pk=one.pk).update(name="Pierwszy")
    Artist.objects.filter(pk=two.pk).update(name="Drugi")
    _l1, t1 = previews.create_link(Artist.objects.get(pk=one.pk))
    _l2, t2 = previews.create_link(Artist.objects.get(pk=two.pk))
    assert previews.artist_for_token(t1).pk == one.pk
    assert previews.artist_for_token(t2).pk == two.pk


def test_purge_deletes_only_links_ended_over_30_days_ago():
    artist = bare_artist()
    now = timezone.now()
    old, _t = previews.create_link(artist, now=now - timedelta(days=40))  # expired 33 days ago
    recent, _t = previews.create_link(artist, now=now - timedelta(days=10))  # expired 3 days ago
    revoked, _t = previews.create_link(artist, now=now - timedelta(days=35))
    PreviewLink.objects.filter(pk=revoked.pk).update(revoked_at=now - timedelta(days=31))
    active, _t = previews.create_link(artist, now=now)
    assert previews.purge(now=now) == 2
    assert set(PreviewLink.objects.values_list("pk", flat=True)) == {recent.pk, active.pk}


def test_purge_job_deletes_old_links():
    from apps.profiles import tasks

    artist = bare_artist()
    old, _t = previews.create_link(artist, now=timezone.now() - timedelta(days=60))
    tasks.purge_preview_links(0)
    assert not PreviewLink.objects.filter(pk=old.pk).exists()


# --- the page a link shows -----------------------------------------------------------------------


@pytest.mark.parametrize(
    ("text", "kept"),
    [
        ("Piszcie: jan@example.invalid, dzwońcie 600 700 800.", "Piszcie: "),
        ("Tel. +48 600-700-800 albo 601700801", "Tel. "),
        ("Zwykły tekst 12.05.2026, 800 - 1200 zł", "Zwykły tekst 12.05.2026, 800 - 1200 zł"),
    ],
)
def test_without_contacts(text, kept):
    clean = previews.without_contacts(text)
    assert kept in clean
    assert previews.contacts_in(clean) == []


def test_without_contacts_hides_the_login_email_however_written():
    assert "JAN@EXAMPLE.INVALID" not in previews.without_contacts(
        "Mail JAN@EXAMPLE.INVALID", "jan@example.invalid"
    )


def test_preview_page_works_before_d6_minimum_and_has_no_contacts():
    artist = bare_artist("tajny@example.invalid")
    Artist.objects.filter(pk=artist.pk).update(name="Zespół 600 700 800")
    artist = Artist.objects.get(pk=artist.pk)
    assert publication.publication_blockers(artist)  # not ready for publication
    page = previews.preview_page(artist)
    assert "600 700 800" not in page.hero.name and previews.HIDDEN in page.hero.name


def test_preview_page_hides_materials_without_rights_statement():
    artist = make_ready(consent=False)
    add_material(artist, MaterialKind.PHOTO, storage_key="public/p.jpg", alt_text="Scena")
    assert previews.preview_page(artist).photos == []


# --- views: owner actions ------------------------------------------------------------------------


def test_owner_creates_link_and_sees_the_url_once():
    artist = bare_artist()
    client = client_for(artist)
    response = client.post(CREATE)
    assert response.status_code == 200
    assert "no-store" in response["Cache-Control"]
    html = response.content.decode()
    token = re.search(r"/podglad/([A-Za-z0-9_-]{43})/", html).group(1)
    assert PreviewLink.objects.get().token_hash == previews.hash_token(token)
    assert "data-new-link" in html and "Kopiuj link" in html
    again = client.get(PANEL).content.decode()
    assert token not in again and "data-preview-link" in again and "Odwołaj link" in again


def test_fourth_link_is_refused_with_a_polish_message():
    client = client_for(bare_artist())
    for _ in range(3):
        assert client.post(CREATE).status_code == 200
    response = client.post(CREATE, follow=True)
    assert "Masz już 3 aktywne linki" in response.content.decode()
    assert PreviewLink.objects.count() == 3


def test_owner_revokes_and_the_link_is_404_at_once():
    artist = bare_artist()
    link, token = previews.create_link(artist)
    assert Client().get(shared(token)).status_code == 200
    response = client_for(artist).post(REVOKE, {"link": link.pk})
    assert response.status_code == 302
    assert Client().get(shared(token)).status_code == 404


def test_another_artist_cannot_revoke():
    owner = bare_artist("a@example.invalid")
    link, token = previews.create_link(owner)
    response = client_for(bare_artist("b@example.invalid")).post(REVOKE, {"link": link.pk})
    assert response.status_code == 302
    assert previews.artist_for_token(token) == owner


def test_anonymous_cannot_create_or_revoke():
    link, _token = previews.create_link(bare_artist())
    assert Client().post(CREATE).status_code == 302  # to the login page
    assert Client().post(REVOKE, {"link": link.pk}).status_code == 302
    assert PreviewLink.objects.count() == 1 and PreviewLink.objects.get().revoked_at is None


def test_actions_need_post_and_csrf():
    artist = bare_artist()
    client = client_for(artist)
    assert client.get(CREATE).status_code == 405
    assert client.get(REVOKE).status_code == 405
    strict = Client(enforce_csrf_checks=True)
    strict.force_login(artist.user)
    assert strict.post(CREATE).status_code == 403
    assert strict.post(REVOKE, {"link": 1}).status_code == 403
    assert not PreviewLink.objects.exists()


# --- views: the shared preview -------------------------------------------------------------------


def test_valid_token_shows_current_version_read_only():
    artist = make_ready("kontakt-tajny@example.invalid")
    pages.edit_field(
        artist, "about", "Nowy opis, pisz na kontakt-tajny@example.invalid lub 600700800."
    )
    _link, token = previews.create_link(artist)
    response = Client().get(shared(token))
    assert response.status_code == 200
    html = response.content.decode()
    assert "Nowy opis" in html and "Kwiatowa opowieść" in html and "data-shared-preview" in html
    for forbidden in ("mailto:", "tel:", "kontakt-tajny@example.invalid", "600700800"):
        assert forbidden not in html
    for owner_control in ("theme-switch", 'name="theme"', 'name="path"', "Przywróć"):
        assert owner_control not in html
    assert '<meta name="robots" content="noindex, nofollow">' in html
    assert response["X-Robots-Tag"] == "noindex, nofollow"
    assert response["Cache-Control"] == "no-store"
    assert response["Referrer-Policy"] == "no-referrer"
    assert not re.search(r"<script(?![^>]*\bsrc=)", html)
    assert "<style" not in html and " style=" not in html


def test_shared_preview_csp_matches_other_pages():
    _link, token = previews.create_link(bare_artist())
    csp = "Content-Security-Policy"

    def plain(response):
        return re.sub(r"nonce-[\w-]+", "nonce-X", response[csp])

    assert plain(Client().get(shared(token))) == plain(Client().get(reverse("accounts:login")))


def test_expired_revoked_unknown_and_malformed_give_the_same_404():
    artist = bare_artist()
    now = timezone.now()
    _l, expired = previews.create_link(artist, now=now - timedelta(days=8))
    link, revoked = previews.create_link(artist)
    previews.revoke_link(artist, link.pk)
    unknown = "A" * 43
    responses = [Client().get(shared(t)) for t in (expired, revoked, unknown, "zly-token")]
    assert [r.status_code for r in responses] == [404] * 4
    assert len({r.content for r in responses}) == 1
    assert len({(r["Cache-Control"], r["X-Robots-Tag"]) for r in responses}) == 1


def test_shared_preview_accepts_only_get_and_head():
    _link, token = previews.create_link(bare_artist())
    assert Client().post(shared(token)).status_code == 405
    assert Client().head(shared(token)).status_code == 200


def test_rate_limit_answers_429_and_logs_without_token(settings, caplog):
    settings.PREVIEW_LIMIT_PER_IP = 3
    _link, token = previews.create_link(bare_artist())
    client = Client(REMOTE_ADDR="203.0.113.9")
    wrong = "B" * 43
    with caplog.at_level(logging.WARNING, logger="apps.profiles.previews"):
        assert [client.get(shared(wrong)).status_code for _ in range(3)] == [404] * 3
        assert client.get(shared(wrong)).status_code == 429
        assert client.get(shared(token)).status_code == 429  # the whole IP waits
    assert Client(REMOTE_ADDR="198.51.100.1").get(shared(token)).status_code == 200
    limited = [r for r in caplog.records if getattr(r, "event", "") == "preview_rate_limited"]
    assert limited
    lines = "\n".join(JsonFormatter().format(r) for r in caplog.records)  # what the logs hold
    assert wrong not in lines and token not in lines
    assert ThrottleEvent.objects.filter(scope="preview_ip").count() == 3


def test_valid_tokens_do_not_count_towards_the_limit(settings):
    settings.PREVIEW_LIMIT_PER_IP = 2
    _link, token = previews.create_link(bare_artist())
    client = Client(REMOTE_ADDR="203.0.113.10")
    assert {client.get(shared(token)).status_code for _ in range(5)} == {200}


# --- the token stays out of logs and analytics ---------------------------------------------------


def test_redact_masks_the_preview_token():
    token = "C" * 43
    assert token not in redact(f"GET /podglad/{token}/ 200")
    assert redact(f"Not Found: /podglad/{token}/") == "Not Found: /podglad/[token]/"


def test_token_never_reaches_log_lines_or_analytics():
    """Every log line written while the link is created and opened (access log, django.request
    404 warnings) goes through the JSON formatter; none may hold the token."""
    stream = io.StringIO()
    handler = logging.StreamHandler(stream)
    handler.setFormatter(JsonFormatter())
    handler.addFilter(RequestContextFilter())
    loggers = [logging.getLogger(name) for name in ("", "access", "django.request")]
    for logger in loggers:
        logger.addHandler(handler)
    old_levels = [logger.level for logger in loggers]
    for logger in loggers:
        logger.setLevel(logging.INFO)
    try:
        artist = bare_artist()
        html = client_for(artist).post(CREATE).content.decode()
        token = re.search(r"/podglad/([A-Za-z0-9_-]{43})/", html).group(1)
        Client().get(shared(token))
        Client().get(shared(token[:-1] + ("x" if token[-1] != "x" else "y")))
    finally:
        for logger, level in zip(loggers, old_levels, strict=True):
            logger.removeHandler(handler)
            logger.setLevel(level)
    lines = stream.getvalue()
    assert "/podglad/[token]/" in lines  # the access log saw the requests
    assert token not in lines and token[:20] not in lines
    assert not Visit.objects.filter(path__startswith="/podglad/").exists()


# --- "Kopiuj link" -------------------------------------------------------------------------------


def test_published_panel_shows_copy_button_with_absolute_public_url(settings):
    settings.SITE_URL = "https://artysci.example.pl"
    artist = make_ready()
    publication.publish(artist)
    slug = Artist.objects.get(pk=artist.pk).slug
    html = client_for(artist).get(PANEL).content.decode()
    assert "data-public-copy" in html and "Kopiuj link" in html
    assert f'value="https://artysci.example.pl/artysci/{slug}/"' in html
    assert "js/copy-link.js" in html
    assert not re.search(r"<script(?![^>]*\bsrc=)", html)


def test_draft_panel_has_no_public_copy_button():
    html = client_for(make_ready()).get(PANEL).content.decode()
    assert "data-public-copy" not in html and 'id="public-url"' not in html
    assert "Utwórz link do podglądu" in html


def test_withdrawn_panel_offers_no_preview_links():
    artist = make_ready()
    publication.publish(artist)
    publication.withdraw(artist)
    html = client_for(artist).get(PANEL).content.decode()
    assert "data-preview-links" not in html and "data-public-copy" not in html
