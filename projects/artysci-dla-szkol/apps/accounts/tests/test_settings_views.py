"""Account settings and e-mail change (US-1.6): views."""

import logging
import re

import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core import mail
from django.test import Client

from apps.core.logs import JsonFormatter

from .conftest import EMAIL, IP, make_artist
from .test_email_change import NEW, OTHER, change_jobs, code_and_token, deliver, mails_to

pytestmark = pytest.mark.django_db

SETTINGS = "/konto/"
CHANGE = "/konto/email/"
CODE = "/konto/email/kod/"
LINK = "/konto/email/link/"
COOKIE = settings.SESSION_COOKIE_NAME


@pytest.fixture
def web(user):
    client = Client(REMOTE_ADDR=IP)
    client.force_login(user)
    return client


def _page(response) -> str:
    html = response.content.decode()
    html = re.sub(r'name="csrfmiddlewaretoken" value="[^"]+"', "", html)
    return re.sub(r'"X-CSRFToken": "[^"]+"', "", html)


def _authenticated(client) -> bool:
    return client.get(SETTINGS).status_code == 200


def _request_change(web, queue, address=NEW) -> tuple[str, str]:
    assert web.post(CHANGE, {"email": address}).status_code == 200
    deliver(queue)
    return code_and_token(mails_to(address)[-1])


# --- settings page ---------------------------------------------------------------------------


def test_anonymous_is_sent_to_login(client):
    response = client.get(SETTINGS)
    assert response.status_code == 302
    assert response["Location"] == "/logowanie/?next=/konto/"


def test_settings_shows_the_email_and_links(web):
    response = web.get(SETTINGS)
    page = response.content.decode()
    assert response.status_code == 200
    assert EMAIL in page
    assert 'href="/konto/dane/"' in page and 'href="/konto/usun/"' in page
    assert 'name="artist_name"' not in page  # not an artist
    assert "no-cache" in response["Cache-Control"] or "no-store" in response["Cache-Control"]


def test_artist_changes_both_names_and_sees_them_next_visit(db):
    artist = make_artist()
    web = Client()
    web.force_login(artist)
    response = web.post(SETTINGS, {"full_name": "Anna Nowak", "artist_name": "Teatr Anny"})
    assert response.status_code == 302 and response["Location"] == SETTINGS
    assert "Zapisano zmiany." in web.get(SETTINGS).content.decode()
    page = web.get(SETTINGS).content.decode()
    assert 'value="Anna Nowak"' in page and 'value="Teatr Anny"' in page


def test_artist_name_cannot_be_blank(db):
    artist = make_artist()
    web = Client()
    web.force_login(artist)
    response = web.post(SETTINGS, {"full_name": "Anna", "artist_name": "  "})
    assert response.status_code == 400
    assert 'id="artist-name-error"' in response.content.decode()


def test_too_long_name_is_400(web):
    assert web.post(SETTINGS, {"full_name": "x" * 201}).status_code == 400


def test_placeholders_say_later(web):
    for path in ("/konto/dane/", "/konto/usun/"):
        response = web.get(path)
        assert response.status_code == 200
        assert "wkrótce" in response.content.decode()


# --- requesting a change ---------------------------------------------------------------------


def test_free_and_taken_address_get_identical_answers(web, user, queue, clock):
    get_user_model().objects.create_user(email=OTHER)
    free = web.post(CHANGE, {"email": NEW})
    taken = web.post(CHANGE, {"email": OTHER})
    assert free.status_code == taken.status_code == 200
    assert _page(free) == _page(taken)
    assert "Jeśli adres jest poprawny, wysłaliśmy na niego wiadomość" in _page(free)
    deliver(queue)
    assert mails_to(OTHER) == [] and len(mails_to(NEW)) == 1
    assert get_user_model().objects.get(pk=user.pk).email == EMAIL


def test_invalid_address_is_400(web, queue):
    response = web.post(CHANGE, {"email": "nie-adres"})
    assert response.status_code == 400
    assert 'id="email-error"' in response.content.decode()
    assert change_jobs(queue) == []


def test_over_the_limit_the_answer_is_neutral(web, queue, clock):
    for number in range(5):
        web.post(CHANGE, {"email": f"n{number}@example.invalid"})
    queue.jobs.clear()
    response = web.post(CHANGE, {"email": "n6@example.invalid"})
    assert response.status_code == 429
    assert "Spróbuj ponownie później" in response.content.decode()
    assert change_jobs(queue) == []


def test_get_on_post_only_routes_is_405(web):
    assert web.get(CHANGE).status_code == 405
    assert web.get(CODE).status_code == 405


def test_change_needs_csrf(user):
    strict = Client(enforce_csrf_checks=True)
    strict.force_login(user)
    assert strict.post(CHANGE, {"email": NEW}).status_code == 403


# --- confirming ------------------------------------------------------------------------------


def test_code_changes_address_rotates_session_and_ends_other_sessions(web, user, queue, clock):
    other_device = Client()
    other_device.force_login(user)
    code, _ = _request_change(web, queue)
    old_key = web.cookies[COOKIE].value

    response = web.post(CODE, {"code": code})
    assert response.status_code == 302 and response["Location"] == SETTINGS
    assert get_user_model().objects.get(pk=user.pk).email == NEW
    assert web.cookies[COOKIE].value != old_key
    page = web.get(SETTINGS)
    assert page.status_code == 200
    assert "Adres e-mail został zmieniony." in page.content.decode()
    assert NEW in page.content.decode()
    assert not _authenticated(other_device)


def test_wrong_code_is_400(web, queue, clock):
    _request_change(web, queue)
    response = web.post(CODE, {"code": "abcdef"})
    assert response.status_code == 400
    assert "nieprawidłowy lub nieaktualny" in response.content.decode()


def test_settings_offers_the_code_form_while_a_change_is_pending(web, queue, clock):
    _request_change(web, queue)
    assert 'action="/konto/email/kod/"' in web.get(SETTINGS).content.decode()


def test_link_get_shows_a_button_post_confirms(web, user, queue, clock):
    _, token = _request_change(web, queue)
    response = web.get(LINK, {"t": token})
    assert response.status_code == 200
    assert 'method="post"' in response.content.decode()
    assert get_user_model().objects.get(pk=user.pk).email == EMAIL  # GET changes nothing

    response = web.post(LINK, {"t": token})
    assert response.status_code == 302
    assert get_user_model().objects.get(pk=user.pk).email == NEW
    assert _authenticated(web)


def test_link_opened_by_another_user_is_refused(web, user, queue, clock):
    _, token = _request_change(web, queue)
    intruder = Client()
    intruder.force_login(get_user_model().objects.create_user(email=OTHER))
    assert intruder.get(LINK, {"t": token}).status_code == 400
    assert intruder.post(LINK, {"t": token}).status_code == 400
    assert get_user_model().objects.get(pk=user.pk).email == EMAIL


def test_link_after_15_minutes_is_refused(web, user, queue, clock):
    _, token = _request_change(web, queue)
    clock.advance(minutes=15, seconds=1)
    assert web.get(LINK, {"t": token}).status_code == 400
    assert web.post(LINK, {"t": token}).status_code == 400
    assert get_user_model().objects.get(pk=user.pk).email == EMAIL


def test_anonymous_link_goes_to_login(client, db):
    response = client.get(LINK, {"t": "abc"})
    assert response.status_code == 302
    assert response["Location"].startswith("/logowanie/?next=")


# --- logs ------------------------------------------------------------------------------------


def test_flow_logs_no_email_code_or_token(web, user, queue, clock, caplog):
    get_user_model().objects.create_user(email=OTHER)
    caplog.handler.setFormatter(JsonFormatter())
    with caplog.at_level(logging.INFO):
        web.post(CHANGE, {"email": OTHER})
        code, token = _request_change(web, queue)
        intruder = Client()
        intruder.force_login(get_user_model().objects.get(email=OTHER))
        intruder.post(LINK, {"t": token})
        web.post(CODE, {"code": "abcdef"})
        web.post(CODE, {"code": code})
        for number in range(5):
            web.post(CHANGE, {"email": f"limit{number}@example.invalid"})
        deliver(queue)

    events = {getattr(r, "event", None) for r in caplog.records}
    assert {
        "email_change_requested",
        "email_change_email_sent",
        "email_change_notice_sent",
        "email_change_refused",
        "email_change_confirmed",
        "email_change_rate_limited",
    } <= events
    text = caplog.text
    for secret in (EMAIL, NEW, OTHER, IP, code, token, "limit4@example.invalid"):
        assert secret not in text, secret
    assert len(mail.outbox) >= 3
