"""Wizard step "Oświadczenia" (US-8.2): views. Service rules are tested in apps/trust."""

from datetime import timedelta

import pytest
from django.test import Client
from django.utils import timezone

from apps.accounts.tests.conftest import make_admin, make_artist, make_institution_member
from apps.artists import services
from apps.artists.models import Artist
from apps.trust import services as trust
from apps.trust.models import STATEMENT_KINDS, ArtistStatement

from .test_wizard import VALID

pytestmark = pytest.mark.django_db

URL = "/artysta/profil/oswiadczenia/"
START = "/artysta/kreator/"


@pytest.fixture
def artist_user():
    user = make_artist()
    services.save_basics(user, VALID)
    return user


@pytest.fixture
def artist(artist_user):
    return Artist.objects.get(user=artist_user)


@pytest.fixture
def web(artist_user):
    client = Client()
    client.force_login(artist_user)
    return client


@pytest.fixture
def wordings(db):
    """Placeholder v1 of each statement (not terms/privacy: their acceptance gate is US-8.1)."""
    for kind in STATEMENT_KINDS:
        trust.publish(kind, f"{trust.PLACEHOLDER_PREFIX}.\n\nTreść testowa {kind}", material=True)


def doc_id(kind):
    return trust.current(kind).pk


def make(web, kind, **extra):
    data = {"kind": kind, "action": "make", "document": doc_id(kind), "confirm": "1", **extra}
    return web.post(URL, data)


def section(body: str, kind: str) -> str:
    start = body.index(f'data-kind="{kind}"')
    end = body.find("<section", start)
    return body[start : end if end != -1 else None]


def test_page_lists_every_statement_with_wording(web, wordings):
    response = web.get(URL)
    body = response.content.decode()
    assert response.status_code == 200
    for label in (
        "Standardy ochrony małoletnich",
        "Prawa do materiałów",
        "Zgoda na wizerunek osób dorosłych",
        "Zgoda na wizerunek dzieci (rodzice lub szkoła)",
        "Forma rozliczenia",
        "Ubezpieczenie OC",
    ):
        assert label in body
    assert "PROJEKT – tekst zastępczy" in body
    assert body.count('data-status="not_made"') == 6
    assert body.count("Nie złożono.") == 6


def test_unpublished_wording_says_not_available(web):
    trust.publish("child_protection", "Treść testowa", material=True)
    body = web.get(URL).content.decode()
    assert "Niedostępne: treść tego oświadczenia nie jest jeszcze opublikowana." in body
    assert section(body, "material_rights").count('name="confirm"') == 0
    response = web.post(
        URL, {"kind": "material_rights", "action": "make", "document": "1", "confirm": "1"}
    )
    assert response.status_code == 400
    assert "To oświadczenie nie jest jeszcze dostępne." in response.content.decode()
    assert not ArtistStatement.objects.exists()


def test_make_child_protection_statement(web, artist, wordings):
    response = make(web, "child_protection")
    assert response.status_code == 302 and response["Location"] == URL
    row = ArtistStatement.objects.get()
    assert row.kind == "child_protection" and row.document.version == 1
    assert trust.has_child_protection_statement(artist)
    body = web.get(URL).content.decode()
    assert "Zapisano oświadczenie." in body
    today = timezone.localdate()
    assert section(body, "child_protection").count('data-status="current"') == 1
    assert "wersja 1" in section(body, "child_protection")
    assert str(today.year) in section(body, "child_protection")
    overview = web.get(START).content.decode()
    assert 'data-step="statements"\n          data-status="done"' in overview
    assert "Oświadczenie artysty" in overview
    assert "zweryfikowany" not in overview.lower() and "rejestr karny" not in overview.lower()


def test_checkbox_is_required(web, wordings):
    response = web.post(
        URL, {"kind": "child_protection", "action": "make", "document": doc_id("child_protection")}
    )
    assert response.status_code == 400
    assert "Zaznacz, że składasz to oświadczenie." in response.content.decode()
    assert not ArtistStatement.objects.exists()


def test_new_version_shows_renewal_needed_and_renewal_works(web, artist, wordings):
    make(web, "child_protection")
    v1_row = ArtistStatement.objects.get()
    trust.publish("child_protection", "Treść testowa v2", material=False)
    body = web.get(URL).content.decode()
    assert "wymaga ponownego oświadczenia" in section(body, "child_protection")
    assert not trust.has_child_protection_statement(artist)
    assert make(web, "child_protection").status_code == 302
    assert ArtistStatement.objects.filter(document__version=2).count() == 1
    assert ArtistStatement.objects.get(pk=v1_row.pk).document.version == 1


def test_stale_page_cannot_make_a_statement(web, wordings):
    shown = doc_id("child_protection")
    trust.publish("child_protection", "Treść testowa v2", material=False)
    response = web.post(
        URL, {"kind": "child_protection", "action": "make", "document": shown, "confirm": "1"}
    )
    assert response.status_code == 400
    assert "Treść oświadczenia zmieniła się." in response.content.decode()


def test_billing_form_choice(web, wordings):
    assert make(web, "billing_form", billing_form="rachunek").status_code == 302
    assert ArtistStatement.objects.get().billing_form == "rachunek"
    assert 'value="rachunek" checked' in web.get(URL).content.decode()


@pytest.mark.parametrize("value", ["", "paragon"])
def test_billing_form_outside_values_is_refused(web, wordings, value):
    response = make(web, "billing_form", billing_form=value)
    assert response.status_code == 400
    assert "Wybierz fakturę albo rachunek." in response.content.decode()
    assert not ArtistStatement.objects.exists()


def test_insurance_with_and_without_date(web, wordings):
    future = timezone.localdate() + timedelta(days=200)
    assert make(web, "insurance", valid_until=future.isoformat()).status_code == 302
    assert ArtistStatement.objects.get().valid_until == future
    assert make(web, "insurance").status_code == 302
    assert ArtistStatement.objects.order_by("-pk").first().valid_until is None


def test_insurance_date_in_the_past_is_refused(web, wordings):
    past = timezone.localdate() - timedelta(days=1)
    response = make(web, "insurance", valid_until=past.isoformat())
    assert response.status_code == 400
    assert "Data ważności nie może być z przeszłości." in response.content.decode()


def test_extra_fields_on_other_kinds_are_ignored(web, wordings):
    assert make(web, "image_adults", billing_form="faktura", valid_until="2030-01-01").status_code
    row = ArtistStatement.objects.get()
    assert row.billing_form == "" and row.valid_until is None


def test_image_consents_are_independent(web, artist, wordings):
    make(web, "image_children")
    body = web.get(URL).content.decode()
    assert 'data-status="current"' in section(body, "image_children")
    assert 'data-status="not_made"' in section(body, "image_adults")


def test_withdraw(web, artist, wordings):
    make(web, "child_protection")
    response = web.post(URL, {"kind": "child_protection", "action": "withdraw"})
    assert response.status_code == 302
    assert not trust.has_child_protection_statement(artist)
    assert ArtistStatement.objects.filter(withdrawn=True).count() == 1
    assert "Wycofano oświadczenie." in web.get(URL).content.decode()


@pytest.mark.parametrize(
    "data",
    [
        {"kind": "terms", "action": "make", "confirm": "1"},
        {"kind": "child_protection", "action": "delete"},
        {},
    ],
)
def test_tampered_post_is_refused(web, wordings, data):
    assert web.post(URL, data).status_code == 400
    assert not ArtistStatement.objects.exists()


def test_institution_user_gets_403(wordings):
    client = Client()
    client.force_login(make_institution_member())
    assert client.get(URL).status_code == 403
    assert client.post(URL, {"kind": "child_protection", "action": "make"}).status_code == 403
    assert not ArtistStatement.objects.exists()


def test_admin_gets_403_and_anonymous_goes_to_login(wordings):
    client = Client()
    client.force_login(make_admin())
    assert client.get(URL).status_code == 403
    response = Client().get(URL)
    assert response.status_code == 302 and response["Location"] == f"/logowanie/?next={URL}"


def test_other_methods_are_refused(web):
    assert web.put(URL).status_code == 405
