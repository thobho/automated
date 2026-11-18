"""US-1.1: artist registration and e-mail confirmation (acceptance criteria and views)."""

import logging
import re

import pytest
from django.contrib.auth import get_user_model
from django.core import mail

from apps.accounts import services as accounts
from apps.accounts.tests.conftest import EMAIL as EXISTING_EMAIL
from apps.accounts.tests.conftest import IP, run_worker
from apps.analytics.models import Event
from apps.artists.models import Artist
from apps.core.logs import JsonFormatter
from apps.trust import services as trust
from apps.trust.models import LegalAcceptance

from .conftest import NAME, NEW_EMAIL, jobs_for

pytestmark = pytest.mark.django_db

REGISTER = "/rejestracja/artysta/"
START = "/artysta/kreator/"
CODE = "/logowanie/kod/"
LINK = "/logowanie/link/"
LOGIN = "/logowanie/"

User = get_user_model()


def _form(email=NEW_EMAIL, name=NAME, accept=True):
    data = {"email": email, "name": name}
    if accept:
        data["accept"] = "1"
    return data


def _counts():
    return (User.objects.count(), Artist.objects.count(), LegalAcceptance.objects.count())


def _send_queued_email(queue) -> tuple[str, str]:
    """Run the queued login e-mail job inline; return (link path+query, code)."""
    (job,) = jobs_for(queue)
    queue.jobs.clear()
    accounts.send_login_email(**job["args"])
    body = mail.outbox[-1].body
    link = re.search(r"https?://[^/\s]+(/\S+)", body).group(1)
    code = re.search(r"^(\d{6})$", body, re.M).group(1)
    return link, code


def _without_csrf(html: str) -> str:
    html = re.sub(r'name="csrfmiddlewaretoken" value="[^"]+"', "", html)
    return re.sub(r'"X-CSRFToken": "[^"]+"', "", html)


# --- the form --------------------------------------------------------------------------------


def test_registration_page(web, documents):
    response = web.get(REGISTER)
    assert response.status_code == 200
    page = response.content.decode()
    for field in ('name="email"', 'name="name"', 'name="accept"'):
        assert field in page
    assert 'href="/regulamin/"' in page and 'href="/polityka-prywatnosci/"' in page
    assert "no-cache" in response["Cache-Control"] or "no-store" in response["Cache-Control"]


def test_login_page_links_to_registration(web, db):
    assert f'href="{REGISTER}"' in web.get(LOGIN).content.decode()


def test_new_registration_creates_unconfirmed_account(web, documents, queue, clock):
    response = web.post(REGISTER, _form(email=" Nowy.Artysta@Example.invalid "))
    assert response.status_code == 200
    assert "Sprawdź skrzynkę" in response.content.decode()

    user = User.objects.get(email=NEW_EMAIL)
    assert user.email_confirmed_at is None and not user.is_confirmed
    assert not user.has_usable_password()
    assert user.artist.name == NAME

    (job,) = jobs_for(queue)
    assert job["args"]["user_id"] == user.pk and job["args"]["next_path"] == START

    rows = LegalAcceptance.objects.filter(user=user).select_related("document")
    assert {(r.document.kind, r.document.version) for r in rows} == {("terms", 1), ("privacy", 1)}
    assert all(r.accepted_at == clock.now for r in rows)

    link, code = _send_queued_email(queue)
    assert len(mail.outbox) == 1 and mail.outbox[0].to == [NEW_EMAIL]
    assert len(code) == 6


def test_acceptance_holds_the_current_versions(web, documents, queue, clock):
    trust.publish("terms", "Regulamin 2", material=True)
    web.post(REGISTER, _form())
    versions = set(LegalAcceptance.objects.values_list("document__kind", "document__version"))
    assert versions == {("terms", 2), ("privacy", 1)}


def test_unticked_checkbox_creates_nothing(web, documents, queue, clock):
    response = web.post(REGISTER, _form(accept=False))
    assert response.status_code == 400
    assert "zaakceptuj regulamin" in response.content.decode()
    assert _counts() == (0, 0, 0)
    assert jobs_for(queue) == []


@pytest.mark.parametrize(
    "data",
    [
        _form(email="nie-e-mail"),
        _form(name="   "),
        _form(name="x" * 201),
        {},
    ],
)
def test_invalid_form_is_400_and_creates_nothing(web, documents, queue, clock, data):
    assert web.post(REGISTER, data).status_code == 400
    assert _counts() == (0, 0, 0)
    assert jobs_for(queue) == []


@pytest.mark.parametrize("missing", ["terms", "privacy", "both"])
def test_no_published_document_creates_nothing(web, db, queue, clock, missing):
    if missing not in ("terms", "both"):
        trust.publish("terms", "Regulamin", material=True)
    if missing not in ("privacy", "both"):
        trust.publish("privacy", "Polityka", material=True)
    response = web.post(REGISTER, _form())
    assert response.status_code == 503
    assert "chwilowo niedostępna" in response.content.decode()
    assert _counts() == (0, 0, 0)
    assert jobs_for(queue) == []
    assert not Event.objects.exists()


# --- confirmation ----------------------------------------------------------------------------


def test_code_within_15_minutes_confirms_and_opens_the_wizard(web, documents, queue, clock):
    page = web.post(REGISTER, _form()).content.decode()
    assert f'name="next" value="{START}"' in page
    _, code = _send_queued_email(queue)
    clock.advance(minutes=14, seconds=59)

    response = web.post(CODE, {"email": NEW_EMAIL, "code": code, "next": START})
    assert response.status_code == 302 and response["Location"] == START
    user = User.objects.get(email=NEW_EMAIL)
    assert user.email_confirmed_at == clock.now

    wizard = web.get(START)
    assert wizard.status_code == 200
    assert wizard.wsgi_request.user == user
    assert "Kreator profilu" in wizard.content.decode()


def test_link_within_15_minutes_confirms_and_opens_the_wizard(web, documents, queue, clock):
    web.post(REGISTER, _form())
    link, _ = _send_queued_email(queue)
    assert link.startswith(LINK) and "next=%2Fartysta%2Fkreator%2F" in link

    page = web.get(link)
    assert page.status_code == 200
    assert f'name="next" value="{START}"' in page.content.decode()
    token = re.search(r"[?&]t=([^&]+)", link).group(1)
    clock.advance(minutes=10)
    response = web.post(LINK, {"t": token, "next": START})
    assert response.status_code == 302 and response["Location"] == START
    assert User.objects.get(email=NEW_EMAIL).is_confirmed
    assert web.get(START).status_code == 200


def test_after_15_minutes_link_and_code_are_refused(web, documents, queue, clock):
    web.post(REGISTER, _form())
    link, code = _send_queued_email(queue)
    token = re.search(r"[?&]t=([^&]+)", link).group(1)
    clock.advance(minutes=15, seconds=1)

    assert web.post(CODE, {"email": NEW_EMAIL, "code": code, "next": START}).status_code == 400
    assert web.get(link).status_code == 400
    assert web.post(LINK, {"t": token, "next": START}).status_code == 400
    user = User.objects.get(email=NEW_EMAIL)
    assert user.email_confirmed_at is None
    assert not web.get("/").wsgi_request.user.is_authenticated

    # Not a dead end: a normal login later confirms the account.
    assert web.post(LOGIN, {"email": NEW_EMAIL}).status_code == 200
    _, new_code = _send_queued_email(queue)
    response = web.post(CODE, {"email": NEW_EMAIL, "code": new_code})
    assert response.status_code == 302
    user.refresh_from_db()
    assert user.email_confirmed_at == clock.now


# --- existing address ------------------------------------------------------------------------


def test_existing_address_gets_the_same_answer_and_a_login_email(web, documents, queue, clock):
    existing = User.objects.create_user(email=EXISTING_EMAIL)
    answers = []
    for email in (NEW_EMAIL, EXISTING_EMAIL):
        response = web.post(REGISTER, _form(email=email))
        page = _without_csrf(response.content.decode()).replace(email, "EMAIL")
        answers.append((response.status_code, page))
    assert answers[0] == answers[1]
    assert answers[0][0] == 200

    assert User.objects.count() == 2
    assert Artist.objects.count() == 1
    assert not Artist.objects.filter(user=existing).exists()
    assert not LegalAcceptance.objects.filter(user=existing).exists()
    assert Event.objects.filter(name="artist_registered").count() == 1

    jobs = {j["args"]["user_id"]: j["args"] for j in jobs_for(queue)}
    assert jobs[existing.pk]["next_path"] == ""  # a normal login link
    queue.jobs.clear()
    accounts.send_login_email(**{**jobs[existing.pk]})
    assert mail.outbox[-1].to == [EXISTING_EMAIL]


def test_registering_twice_creates_one_account(web, documents, queue, clock):
    web.post(REGISTER, _form())
    queue.jobs.clear()
    web.post(REGISTER, _form(name="Inna nazwa"))
    assert _counts() == (1, 1, 2)
    assert Artist.objects.get().name == NAME


# --- limits ----------------------------------------------------------------------------------


def test_over_the_sending_limit_nothing_is_created(web, documents, queue, clock, settings):
    settings.LOGIN_EMAIL_LIMIT_PER_IP = 2
    web.post(REGISTER, _form(email="a@example.invalid"))
    web.post(REGISTER, _form(email="b@example.invalid"))
    queue.jobs.clear()
    response = web.post(REGISTER, _form())
    assert response.status_code == 429
    assert "Spróbuj ponownie później" in response.content.decode()
    assert not User.objects.filter(email=NEW_EMAIL).exists()
    assert jobs_for(queue) == []


def test_address_limit_answer_is_the_same_for_new_and_existing(web, documents, queue, clock):
    User.objects.create_user(email=EXISTING_EMAIL)
    answers = []
    for email in (NEW_EMAIL, EXISTING_EMAIL):
        for n in range(5):
            web.post(LOGIN, {"email": email}, REMOTE_ADDR=f"198.51.100.{n + 10 * len(answers)}")
        response = web.post(REGISTER, _form(email=email), REMOTE_ADDR="192.0.2.1")
        answers.append(
            (response.status_code, _without_csrf(response.content.decode()).replace(email, "EMAIL"))
        )
    assert answers[0] == answers[1] and answers[0][0] == 429
    assert not User.objects.filter(email=NEW_EMAIL).exists()


# --- the wizard start ------------------------------------------------------------------------


def test_wizard_start_needs_login(web, db):
    response = web.get(START)
    assert response.status_code == 302 and response["Location"].startswith(LOGIN)


def test_wizard_start_sends_non_artists_home(client, documents):
    user = User.objects.create_user(email=EXISTING_EMAIL)
    trust.record_acceptance(user, ["terms", "privacy"])
    client.force_login(user)
    response = client.get(START)
    assert response.status_code == 302 and response["Location"] == "/"


def test_register_rejects_other_methods(web, db):
    assert web.put(REGISTER).status_code == 405


# --- analytics -------------------------------------------------------------------------------


def test_events_have_no_email_or_name(web, documents, queue, clock):
    web.post(REGISTER, _form())
    _, code = _send_queued_email(queue)
    web.post(CODE, {"email": NEW_EMAIL, "code": code, "next": START})
    user = User.objects.get(email=NEW_EMAIL)

    registered = Event.objects.get(name="artist_registered")
    confirmed = Event.objects.get(name="account_confirmed")
    assert registered.properties == {"source": "form"}
    assert (registered.object_type, registered.object_id) == ("artists.artist", str(user.artist.pk))
    assert confirmed.properties == {}
    assert registered.actor == confirmed.actor != ""
    for event in (registered, confirmed):
        dump = repr(event.__dict__)
        assert NEW_EMAIL not in dump and NAME not in dump and "Kwiatki" not in dump

    # A second login does not confirm again.
    web.post("/wyloguj/")
    web.post(LOGIN, {"email": NEW_EMAIL})
    _, code = _send_queued_email(queue)
    web.post(CODE, {"email": NEW_EMAIL, "code": code})
    assert Event.objects.filter(name="account_confirmed").count() == 1


# --- logs ------------------------------------------------------------------------------------


@pytest.mark.django_db(transaction=True)
def test_whole_flow_logs_no_email_name_code_token_or_ip(web, documents, queue, clock, caplog):
    User.objects.create_user(email=EXISTING_EMAIL)
    caplog.handler.setFormatter(JsonFormatter())
    with caplog.at_level(logging.INFO):
        web.post(REGISTER, _form())
        web.post(REGISTER, _form(email=EXISTING_EMAIL))
        run_worker()
        body = next(m.body for m in mail.outbox if m.to == [NEW_EMAIL])
        token = re.search(r"\?t=([^&\s]+)", body).group(1)
        code = re.search(r"^(\d{6})$", body, re.M).group(1)
        web.get(LINK, {"t": token, "next": START})
        web.post(CODE, {"email": NEW_EMAIL, "code": code, "next": START})
        web.get(START)

    events = {getattr(r, "event", None) for r in caplog.records}
    assert {"artist_registered", "registration_exists", "account_confirmed"} <= events
    text = caplog.text
    for secret in (NEW_EMAIL, EXISTING_EMAIL, NAME, IP, token, code):
        assert secret not in text, secret
