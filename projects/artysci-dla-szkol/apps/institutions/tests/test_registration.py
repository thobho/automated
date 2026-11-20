"""US-1.2: institution registration with RSPO suggestions (acceptance criteria and views)."""

import logging
import re

import pytest
from django.contrib.auth import get_user_model
from django.core import mail

from apps.accounts import services as accounts
from apps.accounts.tests.conftest import EMAIL as EXISTING_EMAIL
from apps.accounts.tests.conftest import run_worker
from apps.analytics.models import Event
from apps.artists import services as artists
from apps.core.logs import JsonFormatter
from apps.institutions.models import Institution, InstitutionMember
from apps.trust import services as trust
from apps.trust.models import LegalAcceptance

from .conftest import IP, NEW_EMAIL, OPOLE, TYPED_NAME, WROCLAW, jobs_for

pytestmark = pytest.mark.django_db

REGISTER = "/rejestracja/placowka/"
SUGGEST = "/rejestracja/placowka/rspo/"
START = "/placowka/"
CODE = "/logowanie/kod/"
LINK = "/logowanie/link/"
LOGIN = "/logowanie/"

User = get_user_model()


def _form(email=NEW_EMAIL, accept=True, **overrides):
    data = {
        "email": email,
        "institution_type": "primary_school",
        "name": TYPED_NAME,
        "locality": "Zębowice",
        "voivodeship": "opolskie",
        "function": "teacher",
        "rspo_number": "",
    }
    if accept:
        data["accept"] = "1"
    data.update(overrides)
    return data


def _counts():
    return (
        User.objects.count(),
        Institution.objects.count(),
        InstitutionMember.objects.count(),
        LegalAcceptance.objects.count(),
    )


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
    for field in ("email", "institution_type", "name", "locality", "voivodeship", "function"):
        assert f'name="{field}"' in page
    assert 'name="accept"' in page and f'hx-get="{SUGGEST}"' in page
    assert 'href="/regulamin/"' in page and 'href="/polityka-prywatnosci/"' in page
    assert page.count("<option value=") == 5 + 16 + 4 + 3  # types, voivodeships, functions, blanks
    assert "no-cache" in response["Cache-Control"] or "no-store" in response["Cache-Control"]


def test_login_and_home_pages_link_to_both_registrations(web, db):
    for page in (LOGIN, "/"):
        html = web.get(page).content.decode()
        assert f'href="{REGISTER}"' in html and 'href="/rejestracja/artysta/"' in html, page


def test_new_registration_creates_unconfirmed_institution_account(web, documents, queue, clock):
    response = web.post(REGISTER, _form(email=" Dyrektor.Nowy@Example.invalid "))
    assert response.status_code == 200
    assert "Sprawdź skrzynkę" in response.content.decode()

    user = User.objects.get(email=NEW_EMAIL)
    assert user.email_confirmed_at is None and not user.has_usable_password()
    member = user.institution_member
    assert member.function == "teacher" and not member.needs_review
    institution = member.institution
    assert institution.get_verification_status_display() == "niezweryfikowana"
    assert (institution.name, institution.locality, institution.voivodeship) == (
        TYPED_NAME,
        "Zębowice",
        "opolskie",
    )
    assert institution.institution_type == "primary_school" and institution.rspo_number is None

    rows = LegalAcceptance.objects.filter(user=user).select_related("document")
    assert {(r.document.kind, r.document.version) for r in rows} == {("terms", 1), ("privacy", 1)}

    (job,) = jobs_for(queue)
    assert job["args"]["user_id"] == user.pk and job["args"]["next_path"] == START
    _, code = _send_queued_email(queue)
    assert len(mail.outbox) == 1 and mail.outbox[0].to == [NEW_EMAIL] and len(code) == 6


def test_acceptance_holds_the_current_versions(web, documents, queue, clock):
    trust.publish("privacy", "Polityka 2", material=True)
    web.post(REGISTER, _form())
    versions = set(LegalAcceptance.objects.values_list("document__kind", "document__version"))
    assert versions == {("terms", 1), ("privacy", 2)}


def test_unticked_checkbox_creates_nothing(web, documents, queue, clock):
    response = web.post(REGISTER, _form(accept=False))
    assert response.status_code == 400
    assert "zaakceptuj regulamin" in response.content.decode()
    assert _counts() == (0, 0, 0, 0)
    assert jobs_for(queue) == []


@pytest.mark.parametrize(
    ("overrides", "message"),
    [
        ({"email": "nie-e-mail"}, "Podaj poprawny adres e-mail."),
        ({"name": "   "}, "Podaj nazwę placówki"),
        ({"name": "x" * 201}, "Podaj nazwę placówki"),
        ({"locality": ""}, "Podaj miejscowość."),
        ({"voivodeship": ""}, "Wybierz województwo."),
        ({"voivodeship": "bawaria"}, "Wybierz województwo."),
        ({"institution_type": ""}, "Wybierz typ placówki."),
        ({"function": ""}, "Wybierz swoją funkcję."),
        ({"function": "uczeń"}, "Wybierz swoją funkcję."),
        ({"rspo_number": "123"}, "Nie znaleziono placówki w RSPO"),
        ({"rspo_number": "abc"}, 'role="alert"'),
    ],
)
def test_invalid_form_is_400_and_creates_nothing(web, documents, queue, clock, overrides, message):
    response = web.post(REGISTER, _form(**overrides))
    assert response.status_code == 400
    assert message in response.content.decode()
    assert _counts() == (0, 0, 0, 0)
    assert jobs_for(queue) == []


def test_empty_post_is_400(web, documents, queue, clock):
    assert web.post(REGISTER, {}).status_code == 400
    assert _counts() == (0, 0, 0, 0)


def test_form_error_keeps_the_chosen_suggestion(web, documents, rspo):
    page = web.post(REGISTER, _form(accept=False, rspo_number=str(WROCLAW))).content.decode()
    assert f'value="{WROCLAW}" checked' in page


@pytest.mark.parametrize("missing", ["terms", "privacy", "both"])
def test_no_published_document_creates_nothing(web, db, queue, clock, missing):
    if missing not in ("terms", "both"):
        trust.publish("terms", "Regulamin", material=True)
    if missing not in ("privacy", "both"):
        trust.publish("privacy", "Polityka", material=True)
    response = web.post(REGISTER, _form())
    assert response.status_code == 503
    assert "chwilowo niedostępna" in response.content.decode()
    assert _counts()[:3] == (0, 0, 0)
    assert jobs_for(queue) == [] and not Event.objects.exists()


def test_register_rejects_other_methods(web, db):
    assert web.put(REGISTER).status_code == 405


# --- RSPO suggestions ------------------------------------------------------------------------


def test_suggestions_narrowed_by_locality(web, rspo):
    response = web.get(SUGGEST, {"name": "szkoła podstawowa nr 5", "locality": "Wrocław"})
    assert response.status_code == 200
    page = response.content.decode()
    assert f'value="{WROCLAW}"' in page and f'value="{OPOLE}"' not in page
    assert "Wrocław" in page and 'name="rspo_number"' in page


def test_suggestions_without_locality_show_both(web, rspo):
    page = web.get(SUGGEST, {"name": "Szkoła Podstawowa nr 5"}).content.decode()
    assert f'value="{WROCLAW}"' in page and f'value="{OPOLE}"' in page


def test_fewer_than_three_characters_return_nothing(web, rspo):
    response = web.get(SUGGEST, {"name": "sz"})
    assert response.status_code == 200
    assert response.content.decode().strip() == ""
    assert web.get(SUGGEST).content.decode().strip() == ""


def test_more_than_ten_matches_are_cut_to_ten(web, db):
    from apps.institutions import services

    for n in range(1, 16):
        services.add_rspo_entry(800000 + n, f"Szkoła Testowa {n:02d}", "other", "Opole", "opolskie")
    page = web.get(SUGGEST, {"name": "szkoła"}).content.decode()
    assert page.count('name="rspo_number"') == 10 + 1  # ten rows and "none of these"


def test_suggestions_are_get_only_and_anonymous(web, rspo):
    assert web.post(SUGGEST, {"name": "szkoła"}).status_code == 405
    assert web.head(SUGGEST).status_code == 405
    assert web.get(SUGGEST, {"name": "szkoła"}).wsgi_request.user.is_anonymous


def test_chosen_rspo_number_overrides_tampered_fields(web, documents, queue, clock, rspo):
    tampered = _form(
        rspo_number=str(WROCLAW),
        name="Podmieniona nazwa",
        institution_type="culture_centre",
        locality="Gdzieś",
        voivodeship="slaskie",
    )
    assert web.post(REGISTER, tampered).status_code == 200
    institution = Institution.objects.get()
    assert (
        institution.name,
        institution.institution_type,
        institution.locality,
        institution.voivodeship,
        institution.rspo_number,
    ) == ("Szkoła Podstawowa nr 5", "primary_school", "Wrocław", "dolnoslaskie", WROCLAW)


def test_chosen_rspo_number_needs_no_typed_fields(web, documents, queue, clock, rspo):
    data = _form(rspo_number=str(OPOLE), name="", locality="", voivodeship="", institution_type="")
    assert web.post(REGISTER, data).status_code == 200
    assert Institution.objects.get().rspo_number == OPOLE


# --- institution that already has an account -------------------------------------------------


def test_second_person_is_linked_and_listed_for_review(
    web, documents, queue, clock, rspo, staff_client
):
    web.post(REGISTER, _form(rspo_number=str(WROCLAW)))
    queue.jobs.clear()
    response = web.post(
        REGISTER, _form(email="druga.osoba@example.invalid", rspo_number=str(WROCLAW))
    )
    assert response.status_code == 200

    assert Institution.objects.count() == 1
    institution = Institution.objects.get()
    first = InstitutionMember.objects.get(user__email=NEW_EMAIL)
    second = InstitutionMember.objects.get(user__email="druga.osoba@example.invalid")
    assert first.institution == second.institution == institution
    assert not first.needs_review and second.needs_review

    url = "/django-admin/institutions/institutionmember/"
    review = staff_client.get(url, {"needs_review__exact": "1"})
    assert review.status_code == 200
    page = review.content.decode()
    assert (
        f"InstitutionMember {second.pk}<" in page and f"InstitutionMember {first.pk}<" not in page
    )
    assert "needs_review__exact" in staff_client.get(url).content.decode()  # the filter exists


def test_admin_pages_load(staff_client, documents, queue, clock, rspo, web):
    web.post(REGISTER, _form())
    institution = Institution.objects.get()
    for url in (
        "/django-admin/institutions/institution/",
        f"/django-admin/institutions/institution/{institution.pk}/change/",
        "/django-admin/institutions/rspoentry/",
        f"/django-admin/institutions/institutionmember/{institution.members.get().pk}/change/",
    ):
        assert staff_client.get(url).status_code == 200, url
    assert staff_client.get("/django-admin/institutions/rspoentry/add/").status_code == 403


# --- existing address ------------------------------------------------------------------------


@pytest.mark.parametrize("kind", ["artist", "institution"])
def test_existing_address_gets_the_same_answer_and_a_login_email(
    web, documents, queue, clock, kind
):
    if kind == "artist":
        artists.register_artist(EXISTING_EMAIL, "Artysta", "192.0.2.50", link_base="http://x/")
    else:
        web.post(REGISTER, _form(email=EXISTING_EMAIL), REMOTE_ADDR="192.0.2.50")
    queue.jobs.clear()
    existing = User.objects.get(email=EXISTING_EMAIL)
    before = _counts()

    answers = []
    for email in (EXISTING_EMAIL, NEW_EMAIL):
        response = web.post(REGISTER, _form(email=email))
        page = _without_csrf(response.content.decode()).replace(email, "EMAIL")
        answers.append((response.status_code, page))
    assert answers[0] == answers[1] and answers[0][0] == 200

    # Only the new address added rows: one user, one institution, one member, two acceptances.
    assert _counts() == (before[0] + 1, before[1] + 1, before[2] + 1, before[3] + 2)
    assert InstitutionMember.objects.filter(user=existing).count() == (kind == "institution")

    jobs = {j["args"]["user_id"]: j["args"] for j in jobs_for(queue)}
    assert jobs[existing.pk]["next_path"] == ""  # a normal login link
    accounts.send_login_email(**jobs[existing.pk])
    assert mail.outbox[-1].to == [EXISTING_EMAIL]


def test_over_the_sending_limit_nothing_is_created(web, documents, queue, clock, settings):
    settings.LOGIN_EMAIL_LIMIT_PER_IP = 1
    web.post(REGISTER, _form(email="a@example.invalid"))
    queue.jobs.clear()
    response = web.post(REGISTER, _form())
    assert response.status_code == 429
    assert "Spróbuj ponownie później" in response.content.decode()
    assert not User.objects.filter(email=NEW_EMAIL).exists()
    assert Institution.objects.count() == 1 and jobs_for(queue) == []


# --- confirmation ----------------------------------------------------------------------------


def test_code_within_15_minutes_confirms_and_opens_the_start_page(
    web, documents, queue, clock, rspo
):
    page = web.post(REGISTER, _form(rspo_number=str(WROCLAW))).content.decode()
    assert f'name="next" value="{START}"' in page
    _, code = _send_queued_email(queue)
    clock.advance(minutes=14, seconds=59)

    response = web.post(CODE, {"email": NEW_EMAIL, "code": code, "next": START})
    assert response.status_code == 302 and response["Location"] == START
    user = User.objects.get(email=NEW_EMAIL)
    assert user.email_confirmed_at == clock.now

    start = web.get(START)
    assert start.status_code == 200 and start.wsgi_request.user == user
    html = start.content.decode()
    assert "Konto placówki" in html and "niezweryfikowana" in html
    assert "Szkoła Podstawowa nr 5" in html and "Administrator sprawdzi" not in html


def test_link_within_15_minutes_confirms_and_opens_the_start_page(web, documents, queue, clock):
    web.post(REGISTER, _form())
    link, _ = _send_queued_email(queue)
    assert link.startswith(LINK) and "next=%2Fplacowka%2F" in link
    token = re.search(r"[?&]t=([^&]+)", link).group(1)
    clock.advance(minutes=10)
    response = web.post(LINK, {"t": token, "next": START})
    assert response.status_code == 302 and response["Location"] == START
    assert User.objects.get(email=NEW_EMAIL).is_confirmed
    assert web.get(START).status_code == 200


def test_after_15_minutes_the_code_is_refused(web, documents, queue, clock):
    web.post(REGISTER, _form())
    _, code = _send_queued_email(queue)
    clock.advance(minutes=15, seconds=1)
    assert web.post(CODE, {"email": NEW_EMAIL, "code": code, "next": START}).status_code == 400
    assert User.objects.get(email=NEW_EMAIL).email_confirmed_at is None


def test_start_page_shows_review_note_for_linked_member(client, documents, queue, clock, rspo):
    for email in (NEW_EMAIL, "druga.osoba@example.invalid"):
        client.post(REGISTER, _form(email=email, rspo_number=str(WROCLAW)), REMOTE_ADDR=IP)
    client.force_login(User.objects.get(email="druga.osoba@example.invalid"))
    assert "Administrator sprawdzi" in client.get(START).content.decode()


def test_start_needs_login(web, db):
    response = web.get(START)
    assert response.status_code == 302 and response["Location"].startswith(LOGIN)


def test_start_refuses_non_members(client, documents):
    user = User.objects.create_user(email=EXISTING_EMAIL)
    trust.record_acceptance(user, ["terms", "privacy"])
    client.force_login(user)
    response = client.get(START)
    assert response.status_code == 403


# --- analytics -------------------------------------------------------------------------------


def test_events_have_no_email_or_names(web, documents, queue, clock, rspo):
    web.post(REGISTER, _form(rspo_number=str(WROCLAW)))
    _, code = _send_queued_email(queue)
    web.post(CODE, {"email": NEW_EMAIL, "code": code, "next": START})
    user = User.objects.get(email=NEW_EMAIL)

    registered = Event.objects.get(name="institution_registered")
    confirmed = Event.objects.get(name="account_confirmed")
    assert registered.properties == {
        "institution_type": "primary_school",
        "rspo_matched": True,
        "linked_existing": False,
    }
    institution = user.institution_member.institution
    assert (registered.object_type, registered.object_id) == (
        "institutions.institution",
        str(institution.pk),
    )
    assert confirmed.properties == {}
    assert registered.actor == confirmed.actor != ""
    for event in (registered, confirmed):
        dump = repr(event.__dict__)
        for secret in (NEW_EMAIL, "dyrektor", "Szkoła", "Wrocław", TYPED_NAME):
            assert secret not in dump, secret


# --- logs ------------------------------------------------------------------------------------


@pytest.mark.django_db(transaction=True)
def test_whole_flow_logs_no_email_name_code_token_or_ip(web, documents, queue, clock, caplog, rspo):
    User.objects.create_user(email=EXISTING_EMAIL)
    caplog.handler.setFormatter(JsonFormatter())
    with caplog.at_level(logging.INFO):
        web.get(SUGGEST, {"name": "szkoła podstawowa", "locality": "Wrocław"})
        web.post(REGISTER, _form(rspo_number=str(WROCLAW)))
        web.post(REGISTER, _form(email="druga.osoba@example.invalid", rspo_number=str(WROCLAW)))
        web.post(REGISTER, _form(email=EXISTING_EMAIL))
        run_worker()
        body = next(m.body for m in mail.outbox if m.to == [NEW_EMAIL])
        token = re.search(r"\?t=([^&\s]+)", body).group(1)
        code = re.search(r"^(\d{6})$", body, re.M).group(1)
        web.get(LINK, {"t": token, "next": START})
        web.post(CODE, {"email": NEW_EMAIL, "code": code, "next": START})
        web.get(START)

    events = {getattr(r, "event", None) for r in caplog.records}
    assert {
        "institution_registered",
        "institution_member_linked",
        "registration_exists",
        "account_confirmed",
    } <= events
    text = caplog.text
    secrets = (NEW_EMAIL, "druga.osoba", EXISTING_EMAIL, TYPED_NAME, "Szkoła Podstawowa nr 5")
    for secret in (*secrets, IP, token, code):
        assert secret not in text, secret
