"""Roles, rule functions, view guards, admin accounts (US-1.5)."""

import json
import logging

import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.core.management import CommandError, call_command
from django.test import Client

from apps.accounts import roles, services
from apps.accounts.permissions import role_required
from apps.accounts.roles import Role
from apps.artists.models import Artist
from apps.core.logs import JsonFormatter, pseudonymise_user
from apps.institutions.models import InstitutionMember

from .conftest import IP, ROLE_EMAILS, make_admin, make_artist, make_institution_member

pytestmark = pytest.mark.django_db
User = get_user_model()

ARTIST_START = "/artysta/kreator/"
INSTITUTION_START = "/placowka/"


def denied_records(caplog):
    return [
        r
        for r in caplog.records
        if r.name == "apps.accounts.permissions" and r.getMessage() == "permission denied"
    ]


# --- role_of ---------------------------------------------------------------------------------


def test_role_of_each_kind_of_account():
    assert roles.role_of(None) is Role.ANONYMOUS
    assert roles.role_of(AnonymousUser()) is Role.ANONYMOUS
    assert roles.role_of(make_artist()) is Role.ARTIST
    assert roles.role_of(make_institution_member()) is Role.INSTITUTION
    assert roles.role_of(make_admin()) is Role.ADMIN
    assert roles.role_of(User.objects.create_user(email="bez.roli@example.invalid")) is Role.NONE


def test_role_of_staff_or_superuser_is_admin():
    staff = User.objects.create_user(email="staff@example.invalid", is_staff=True)
    superuser = User.objects.create_user(email="super@example.invalid", is_superuser=True)
    assert roles.role_of(staff) is roles.role_of(superuser) is Role.ADMIN


def test_role_of_contradictory_account_fails_closed(caplog):
    from apps.institutions.models import Institution

    user = make_artist()
    institution = Institution.objects.create(
        institution_type="other", name="X", locality="Y", voivodeship="opolskie"
    )
    InstitutionMember.objects.create(user=user, institution=institution, function="other")
    with caplog.at_level(logging.WARNING, logger="apps.accounts.permissions"):
        assert roles.role_of(user) is Role.NONE
    assert [r.event for r in caplog.records] == ["role_conflict"]


def test_has_any_role():
    assert not roles.has_any_role(None)
    assert not roles.has_any_role(User.objects.create_user(email="bez.roli@example.invalid"))
    assert roles.has_any_role(make_artist())
    assert roles.has_any_role(make_institution_member())
    assert roles.has_any_role(make_admin())


# --- rule functions --------------------------------------------------------------------------


def test_rules_for_an_artist():
    artist = make_artist()
    assert roles.can_create_artist_profile(artist)
    assert not roles.can_create_inquiry(artist)
    assert not roles.can_create_notice(artist)


def test_rules_for_an_institution_member():
    member = make_institution_member()
    assert not roles.can_create_artist_profile(member)
    assert roles.can_create_inquiry(member)
    assert roles.can_create_notice(member)


@pytest.mark.parametrize(
    "rule",
    [roles.can_create_artist_profile, roles.can_create_inquiry, roles.can_create_notice],
)
def test_rules_refuse_anonymous_admin_and_no_role(rule):
    assert not rule(AnonymousUser())
    assert not rule(make_admin())
    assert not rule(User.objects.create_user(email="bez.roli@example.invalid"))


# --- acceptance criteria through the views ---------------------------------------------------


def test_artist_gets_403_on_institution_start(role_clients):
    response = role_clients["artist"].get(INSTITUTION_START)
    assert response.status_code == 403
    assert "Brak dostępu" in response.content.decode()


def test_institution_member_gets_403_on_artist_start(role_clients):
    assert role_clients["institution"].get(ARTIST_START).status_code == 403


@pytest.mark.parametrize("path", [ARTIST_START, INSTITUTION_START])
def test_anonymous_goes_to_login_with_next(client, path):
    response = client.get(path + "?krok=1")
    assert response.status_code == 302
    assert response["Location"] == f"/logowanie/?next={path}%3Fkrok%3D1"


def test_403_writes_exactly_one_permission_denied_line(role_clients, role_users, caplog):
    with caplog.at_level(logging.INFO):
        role_clients["artist"].get(INSTITUTION_START + "?q=secret")
    [record] = denied_records(caplog)
    assert record.user == pseudonymise_user(role_users["artist"].pk)
    assert (record.role, record.url_name, record.required_role) == (
        "artist",
        "institutions:start",
        "institution",
    )
    line = JsonFormatter().format(record)
    entry = json.loads(line)
    assert entry["msg"] == "permission denied" and entry["event"] == "permission_denied"
    assert {"role", "url_name", "required_role", "user"} <= entry.keys()
    assert ROLE_EMAILS["artist"] not in line and "secret" not in line and "127.0.0.1" not in line
    assert "ip" not in entry and "path" not in entry
    # Only one line in the whole request mentions it (Django logs "Forbidden: <path>").
    assert sum("permission denied" in r.getMessage().lower() for r in caplog.records) == 1


def test_allowed_and_anonymous_requests_log_no_denial(role_clients, caplog):
    with caplog.at_level(logging.INFO):
        assert role_clients["institution"].get(INSTITUTION_START).status_code == 200
        assert role_clients["anonymous"].get(INSTITUTION_START).status_code == 302
    assert denied_records(caplog) == []


def test_role_required_marks_the_view_and_needs_a_role():
    from apps.artists.views import start

    assert start.required_roles == frozenset({Role.ARTIST})
    with pytest.raises(ValueError):
        role_required()
    with pytest.raises(ValueError):
        role_required("superhero")


def test_role_required_mixin(settings, role_clients):
    settings.ROOT_URLCONF = "apps.accounts.tests.matrix_urls"
    path = "/test/tylko-placowka/"
    assert role_clients["institution"].get(path).status_code == 200
    assert role_clients["artist"].get(path).status_code == 403
    assert role_clients["admin"].get(path).status_code == 403
    assert role_clients["anonymous"].get(path)["Location"] == f"/logowanie/?next={path}"


def test_role_required_can_allow_anonymous(rf):
    view = role_required("anonymous", "artist")(lambda request: "ok")
    request = rf.get("/")
    request.user = AnonymousUser()
    assert view(request) == "ok"


# --- registration ignores extra fields and never adds a second role --------------------------


TAMPER = {"is_staff": "1", "is_superuser": "1", "role": "admin"}


def test_artist_registration_ignores_role_fields(client, legal_documents, queue):
    email = "nowy.artysta@example.invalid"
    form = {"email": email, "name": "Nowy", "accept": "on", **TAMPER}
    assert client.post("/rejestracja/artysta/", form, REMOTE_ADDR=IP).status_code == 200
    user = User.objects.get(email=email)
    assert not (user.is_staff or user.is_superuser)
    assert roles.role_of(user) is Role.ARTIST


def test_institution_registration_ignores_role_fields(client, legal_documents, queue):
    email = "nowa.placowka@example.invalid"
    form = {
        "email": email,
        "institution_type": "primary_school",
        "name": "Szkoła Nowa",
        "locality": "Opole",
        "voivodeship": "opolskie",
        "function": "director",
        "accept": "on",
        **TAMPER,
    }
    assert client.post("/rejestracja/placowka/", form, REMOTE_ADDR=IP).status_code == 200
    user = User.objects.get(email=email)
    assert not (user.is_staff or user.is_superuser)
    assert roles.role_of(user) is Role.INSTITUTION


def test_institution_registration_with_an_artist_email_adds_no_role(client, legal_documents, queue):
    artist = make_artist()
    form = {
        "email": artist.email,
        "institution_type": "primary_school",
        "name": "Szkoła Druga",
        "locality": "Opole",
        "voivodeship": "opolskie",
        "function": "director",
        "accept": "on",
    }
    assert client.post("/rejestracja/placowka/", form, REMOTE_ADDR=IP).status_code == 200
    assert not InstitutionMember.objects.filter(user=artist).exists()
    assert roles.role_of(artist) is Role.ARTIST


def test_artist_registration_with_an_institution_email_adds_no_role(client, legal_documents, queue):
    member = make_institution_member()
    form = {"email": member.email, "name": "Ktoś", "accept": "on"}
    assert client.post("/rejestracja/artysta/", form, REMOTE_ADDR=IP).status_code == 200
    assert not Artist.objects.filter(user=member).exists()
    assert roles.role_of(member) is Role.INSTITUTION


# --- admin accounts --------------------------------------------------------------------------


def test_create_admin_command_makes_an_admin_without_password(capsys):
    call_command("create_admin", "Admin@Example.invalid")
    user = User.objects.get(email="admin@example.invalid")
    assert roles.role_of(user) is Role.ADMIN
    assert user.is_staff and user.is_superuser and not user.has_usable_password()
    assert f"admin created: user id {user.pk}" in capsys.readouterr().out


def test_create_admin_is_idempotent_and_upgrades_an_account_without_role(capsys):
    user = User.objects.create_user(email="admin@example.invalid")
    call_command("create_admin", "admin@example.invalid")
    call_command("create_admin", "admin@example.invalid")
    user.refresh_from_db()
    assert user.is_staff and user.is_superuser
    assert User.objects.filter(email="admin@example.invalid").count() == 1
    assert capsys.readouterr().out.count("admin updated") == 2


def test_create_admin_refuses_artist_and_institution_accounts():
    for user in (make_artist(), make_institution_member()):
        with pytest.raises(CommandError, match="one account = one role"):
            call_command("create_admin", user.email)
        user.refresh_from_db()
        assert not (user.is_staff or user.is_superuser)


def test_create_admin_rejects_a_bad_address():
    with pytest.raises(CommandError, match="not a valid e-mail"):
        call_command("create_admin", "nie-adres")
    assert not User.objects.exists()


def test_admin_logs_in_with_the_normal_email_flow(legal_documents, queue, clock):
    import re

    from django.core import mail

    from .conftest import login_jobs

    call_command("create_admin", "admin@example.invalid")
    client = Client()
    response = client.post("/logowanie/", {"email": "admin@example.invalid"}, REMOTE_ADDR=IP)
    (job,) = login_jobs(queue)
    assert response.status_code == 200
    services.send_login_email(**job["args"])
    code = re.search(r"^(\d{6})$", mail.outbox[-1].body, re.M).group(1)
    client.post("/logowanie/kod/", {"email": "admin@example.invalid", "code": code})
    user = client.get("/").wsgi_request.user
    assert user.is_authenticated and roles.role_of(user) is Role.ADMIN


def test_no_form_field_can_set_admin_flags():
    from apps.artists.views import ArtistRegistrationForm
    from apps.institutions.views import InstitutionRegistrationForm

    for form in (ArtistRegistrationForm, InstitutionRegistrationForm):
        assert not {"is_staff", "is_superuser", "role"} & set(form.base_fields)


def test_services_create_admin_raises_for_a_role():
    with pytest.raises(services.AdminRefused):
        services.create_admin(make_artist().email)
