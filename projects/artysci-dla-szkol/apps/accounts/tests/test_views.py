import logging
import re

import pytest
from django.conf import settings
from django.contrib.sessions.models import Session
from django.core import mail

from apps.accounts import services
from apps.core.logs import JsonFormatter

from .conftest import EMAIL, INACTIVE_EMAIL, IP, UNKNOWN_EMAIL, login_jobs

pytestmark = pytest.mark.django_db

LOGIN = "/logowanie/"
CODE = "/logowanie/kod/"
LINK = "/logowanie/link/"
LOGOUT = "/wyloguj/"
COOKIE = settings.SESSION_COOKIE_NAME


@pytest.fixture
def web(client):
    """Test client whose requests come from IP (to check that it never reaches a log)."""
    client.defaults["REMOTE_ADDR"] = IP
    return client


def _without_csrf(html: str) -> str:
    html = re.sub(r'name="csrfmiddlewaretoken" value="[^"]+"', "", html)
    return re.sub(r'"X-CSRFToken": "[^"]+"', "", html)


def _logged_in(response) -> bool:
    return response.wsgi_request.user.is_authenticated


def _code_for(user):
    return services.create_challenge(user)[2]


# --- step 1: e-mail --------------------------------------------------------------------------


def test_login_page(web, db):
    response = web.get(LOGIN)
    assert response.status_code == 200
    assert 'name="email"' in response.content.decode()
    assert "no-cache" in response["Cache-Control"] or "no-store" in response["Cache-Control"]


def test_invalid_email_is_400(web, db):
    assert web.post(LOGIN, {"email": "not-an-email"}).status_code == 400


def test_known_and_unknown_email_get_the_same_answer(web, user, inactive_user, queue, clock):
    answers = []
    for email in (EMAIL, UNKNOWN_EMAIL, INACTIVE_EMAIL):
        response = web.post(LOGIN, {"email": email})
        page = _without_csrf(response.content.decode()).replace(email, "EMAIL")
        answers.append((response.status_code, page))
    assert answers[0][0] == 200
    assert answers[0] == answers[1] == answers[2]
    assert len(login_jobs(queue)) == 1  # only the active user's e-mail


def test_over_the_limit_the_answer_is_neutral_for_everyone(web, user, queue, clock):
    answers = []
    for email in (EMAIL, UNKNOWN_EMAIL):
        for _ in range(5):
            web.post(LOGIN, {"email": email}, REMOTE_ADDR=f"198.51.100.{len(answers)}")
        queue.jobs.clear()
        response = web.post(LOGIN, {"email": email}, REMOTE_ADDR="192.0.2.1")
        page = _without_csrf(response.content.decode()).replace(email, "EMAIL")
        answers.append((response.status_code, page))
    assert answers[0] == answers[1]
    assert answers[0][0] == 429
    assert "Spróbuj ponownie później" in answers[0][1]
    assert login_jobs(queue) == []


# --- step 2: code ----------------------------------------------------------------------------


def test_code_logs_in_and_rotates_the_session(web, user, clock):
    session = web.session
    session["before"] = 1
    session.save()
    old_key = session.session_key
    web.cookies[COOKIE] = old_key
    code = _code_for(user)
    response = web.post(CODE, {"email": EMAIL, "code": code})
    assert response.status_code == 302
    assert response["Location"] == "/"
    assert web.cookies[COOKIE].value != old_key
    assert _logged_in(web.get("/"))


def test_wrong_code_is_400_with_generic_error(web, user, clock):
    _code_for(user)
    response = web.post(CODE, {"email": EMAIL, "code": "abc"})
    assert response.status_code == 400
    assert "nieprawidłowy lub nieaktualny" in response.content.decode()


def test_code_endpoint_is_post_only(web, db):
    assert web.get(CODE).status_code == 405


@pytest.mark.parametrize(
    ("next_url", "expected"),
    [("https://evil.example/", "/"), ("//evil.example/x", "/"), ("/regulamin/", "/regulamin/")],
)
def test_next_redirect_is_same_host_only(web, user, clock, next_url, expected):
    response = web.post(CODE, {"email": EMAIL, "code": _code_for(user), "next": next_url})
    assert response.status_code == 302
    assert response["Location"] == expected


def test_next_survives_from_login_page_to_code_form(web, user, queue, clock):
    page = web.post(LOGIN + "?next=/regulamin/", {"email": EMAIL}).content.decode()
    assert 'name="next" value="/regulamin/"' in page
    evil = web.post(LOGIN, {"email": EMAIL, "next": "https://evil.example"}).content.decode()
    assert 'name="next" value="/"' in evil


# --- the link --------------------------------------------------------------------------------


def test_link_get_shows_a_button_and_does_not_log_in(web, user, clock):
    _, token, _ = services.create_challenge(user)
    response = web.get(LINK, {"t": token})
    assert response.status_code == 200
    page = response.content.decode()
    assert 'method="post"' in page and "Zaloguj" in page
    assert not _logged_in(response)
    assert services.check_link(token)  # not consumed by the GET

    response = web.post(LINK, {"t": token})
    assert response.status_code == 302
    assert _logged_in(web.get("/"))


def test_used_or_bad_link_is_400(web, user, clock):
    _, token, code = services.create_challenge(user)
    assert services.login_with_code(EMAIL, code) == user
    assert web.get(LINK, {"t": token}).status_code == 400
    assert web.post(LINK, {"t": token}).status_code == 400
    assert web.get(LINK).status_code == 400


# --- sessions --------------------------------------------------------------------------------


def _log_in(web, user):
    assert web.post(CODE, {"email": EMAIL, "code": _code_for(user)}).status_code == 302


def test_session_expires_after_30_idle_days(web, user, clock):
    _log_in(web, user)
    clock.advance(days=30, seconds=1)
    assert not _logged_in(web.get("/"))


def test_activity_keeps_the_session_alive(web, user, clock):
    _log_in(web, user)
    clock.advance(days=29)
    assert _logged_in(web.get("/"))
    clock.advance(days=2)  # day 31, two days after the last activity
    assert _logged_in(web.get("/"))


def test_sessions_are_in_the_database(web, user, clock):
    _log_in(web, user)
    assert Session.objects.filter(session_key=web.cookies[COOKIE].value).exists()


# --- logout ----------------------------------------------------------------------------------


def test_logout_ends_the_session_on_the_server(web, user, clock):
    _log_in(web, user)
    old_key = web.cookies[COOKIE].value
    response = web.post(LOGOUT)
    assert response.status_code == 302
    assert response["Clear-Site-Data"] == '"cookies", "storage"'
    assert not Session.objects.filter(session_key=old_key).exists()

    web.cookies[COOKIE] = old_key  # replay the old cookie
    assert not _logged_in(web.get("/"))


def test_logout_is_post_only(web, user, clock):
    _log_in(web, user)
    assert web.get(LOGOUT).status_code == 405
    assert _logged_in(web.get("/"))


def test_logout_needs_csrf(user, clock, db):
    from django.test import Client

    strict = Client(enforce_csrf_checks=True)
    strict.force_login(user)
    assert strict.post(LOGOUT).status_code == 403


def test_logout_anonymous_is_harmless(web, db):
    assert web.post(LOGOUT).status_code == 302


def test_header_shows_login_or_logout(web, user, clock):
    assert 'href="/logowanie/"' in web.get("/").content.decode()
    _log_in(web, user)
    assert 'action="/wyloguj/"' in web.get("/").content.decode()


# --- logs ------------------------------------------------------------------------------------


@pytest.mark.django_db(transaction=True)
def test_whole_flow_logs_no_email_ip_code_or_token(web, user, queue, clock, caplog):
    from .conftest import run_worker

    caplog.handler.setFormatter(JsonFormatter())
    with caplog.at_level(logging.INFO):
        web.post(LOGIN, {"email": EMAIL})
        run_worker()
        body = mail.outbox[0].body
        token = re.search(r"\?t=(\S+)", body).group(1)
        code = re.search(r"^(\d{6})$", body, re.M).group(1)
        web.post(CODE, {"email": EMAIL, "code": "000000" if code != "000000" else "111111"})
        web.get(LINK, {"t": token})
        web.post(CODE, {"email": EMAIL, "code": code})
        web.post(LOGOUT)
        for _ in range(5):
            web.post(CODE, {"email": EMAIL, "code": "abcdef"})
        web.post(LOGIN, {"email": UNKNOWN_EMAIL})

    text = caplog.text
    events = {getattr(r, "event", None) for r in caplog.records}
    assert {
        "login_requested",
        "login_email_sent",
        "login_code_failed",
        "login_succeeded",
        "logout",
        "login_locked",
    } <= events
    assert "login succeeded" in text
    for secret in (EMAIL, UNKNOWN_EMAIL, IP, token, code):
        assert secret not in text, secret
