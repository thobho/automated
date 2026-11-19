"""Profile wizard step 1, the basics (US-2.1, D102): services and views."""

import pytest
from django.contrib.auth import get_user_model
from django.test import Client

from apps.accounts.tests.conftest import make_admin, make_artist, make_institution_member
from apps.artists import services
from apps.artists.models import Artist, ArtistAudience, ArtistVoivodeship
from apps.artists.services import InvalidBasics

pytestmark = pytest.mark.django_db

START = "/artysta/kreator/"
BASICS = "/artysta/profil/dane/"
LATER = ("/artysta/profil/oferty/", "/artysta/profil/oswiadczenia/", "/artysta/profil/materialy/")

VALID = {
    "artist_type": "theatre",
    "name": "Teatr Testowy Kwiatki",
    "city": "Wrocław",
    "voivodeships": ["dolnoslaskie", "opolskie"],
    "audiences": ["kindergarten", "grades_0_3", "families"],
}


@pytest.fixture
def artist_user():
    return make_artist()


@pytest.fixture
def web(artist_user):
    client = Client()
    client.force_login(artist_user)
    return client


def artist_of(user) -> Artist:
    return Artist.objects.get(user=user)


# --- services --------------------------------------------------------------------------------


def test_save_basics_stores_everything(artist_user):
    artist = services.save_basics(artist_user, VALID)
    basics = services.basics_of(artist)
    assert basics.artist_type == "theatre"
    assert basics.name == "Teatr Testowy Kwiatki" and basics.city == "Wrocław"
    assert basics.voivodeships == ("dolnoslaskie", "opolskie")
    assert basics.audiences == ("kindergarten", "grades_0_3", "families")
    assert services.basics_complete(artist)


def test_save_basics_strips_and_deduplicates(artist_user):
    data = {**VALID, "name": "  Nowa  ", "city": " Opole ", "voivodeships": ["opolskie"] * 2}
    artist = services.save_basics(artist_user, data)
    assert artist.name == "Nowa" and artist.city == "Opole"
    assert ArtistVoivodeship.objects.filter(artist=artist).count() == 1


def test_save_basics_replaces_multi_values(artist_user):
    services.save_basics(artist_user, VALID)
    artist = services.save_basics(
        artist_user, {**VALID, "voivodeships": ["opolskie", "slaskie"], "audiences": ["families"]}
    )
    basics = services.basics_of(artist)
    assert basics.voivodeships == ("opolskie", "slaskie")
    assert basics.audiences == ("families",)
    assert ArtistAudience.objects.count() == 1


def test_save_basics_uses_rename_artist(artist_user, monkeypatch):
    calls = []
    original = services.rename_artist
    monkeypatch.setattr(
        services, "rename_artist", lambda user, name: calls.append(name) or original(user, name)
    )
    services.save_basics(artist_user, VALID)
    assert calls == ["Teatr Testowy Kwiatki"]


@pytest.mark.parametrize(
    "field, value",
    [
        ("artist_type", ""),
        ("artist_type", "opera"),
        ("name", "   "),
        ("city", ""),
        ("voivodeships", []),
        ("voivodeships", ["bawaria"]),
        ("audiences", []),
        ("audiences", ["studenci"]),
    ],
)
def test_save_basics_refuses_invalid_and_saves_nothing(artist_user, field, value):
    with pytest.raises(InvalidBasics) as error:
        services.save_basics(artist_user, {**VALID, field: value})
    assert str(error.value) == field
    artist = artist_of(artist_user)
    assert artist.name == "Artysta Rola" and artist.city == "" and artist.artist_type == ""
    assert not ArtistVoivodeship.objects.exists() and not ArtistAudience.objects.exists()


def test_save_basics_for_a_non_artist_fails(db):
    user = get_user_model().objects.create_user(email="ktos@example.invalid")
    with pytest.raises(Artist.DoesNotExist):
        services.save_basics(user, VALID)


def test_basics_complete_needs_every_field(artist_user):
    assert not services.basics_complete(None)
    artist = artist_of(artist_user)
    assert not services.basics_complete(artist)
    artist = services.save_basics(artist_user, VALID)
    assert services.basics_complete(artist)
    ArtistAudience.objects.filter(artist=artist).delete()
    assert not services.basics_complete(artist)
    services.save_basics(artist_user, VALID)
    ArtistVoivodeship.objects.filter(artist=artist).delete()
    assert not services.basics_complete(artist)
    services.save_basics(artist_user, VALID)
    Artist.objects.filter(pk=artist.pk).update(city="")
    assert not services.basics_complete(artist_of(artist_user))


def test_wizard_steps(artist_user):
    steps = services.wizard_steps(artist_of(artist_user))
    assert [(s.step.key, s.done, s.available) for s in steps] == [
        ("basics", False, True),
        ("offers", False, False),
        ("statements", False, False),
        ("materials", False, False),
    ]
    steps = services.wizard_steps(services.save_basics(artist_user, VALID))
    assert [(s.step.key, s.done, s.available) for s in steps] == [
        ("basics", True, True),
        ("offers", False, True),
        ("statements", False, True),
        ("materials", False, True),
    ]


def test_two_voivodeships_and_three_audiences_round_trip(artist_user):
    """Runs on SQLite by default and on PostgreSQL when DATABASE_URL is set (CI does both)."""
    services.save_basics(
        artist_user,
        {
            **VALID,
            "voivodeships": ["zachodniopomorskie", "lodzkie"],
            "audiences": ["secondary", "grades_7_8", "grades_4_6"],
        },
    )
    basics = services.basics_of(Artist.objects.get(user=artist_user))
    assert basics.voivodeships == ("lodzkie", "zachodniopomorskie")
    assert basics.audiences == ("grades_4_6", "grades_7_8", "secondary")
    # filterable by the catalog later (US-4.2): a join, no ArrayField
    assert Artist.objects.filter(voivodeships__voivodeship="lodzkie").count() == 1
    assert Artist.objects.filter(audiences__audience="families").count() == 0


# --- views -----------------------------------------------------------------------------------


def test_overview_with_empty_basics(web):
    response = web.get(START)
    body = response.content.decode()
    assert response.status_code == 200
    assert 'data-step="basics"\n          data-status="open"' in body
    assert "obowiązkowe" in body
    for key in ("offers", "statements", "materials"):
        assert f'data-step="{key}"\n          data-status="locked"' in body
    assert 'href="/artysta/profil/oferty/"' not in body


def test_send_step_1_stores_and_prefills(web, artist_user):
    response = web.post(BASICS, VALID, follow=True)
    assert response.redirect_chain == [(START, 302)]
    assert "Zapisano dane podstawowe." in response.content.decode()
    artist = artist_of(artist_user)
    assert services.basics_of(artist) == services.Basics(
        "theatre",
        "Teatr Testowy Kwiatki",
        "Wrocław",
        ("dolnoslaskie", "opolskie"),
        ("kindergarten", "grades_0_3", "families"),
    )
    body = web.get(BASICS).content.decode()
    assert 'value="Teatr Testowy Kwiatki"' in body and 'value="Wrocław"' in body
    for value in ("theatre", "dolnoslaskie", "opolskie", "kindergarten", "families"):
        assert f'value="{value}"' in body
    assert body.count("checked") == 6  # 1 type + 2 voivodeships + 3 audiences
    overview = web.get(START).content.decode()
    assert 'data-step="basics"\n          data-status="done"' in overview


@pytest.mark.parametrize(
    "field, message",
    [
        ("artist_type", "Wybierz rodzaj."),
        ("name", "Podaj nazwę."),
        ("city", "Podaj miasto."),
        ("voivodeships", "Wybierz co najmniej jedno województwo."),
        ("audiences", "Wybierz co najmniej jedną grupę odbiorców."),
    ],
)
def test_missing_field_saves_nothing_and_shows_error(web, artist_user, field, message):
    data = {k: v for k, v in VALID.items() if k != field}
    response = web.post(BASICS, data)
    assert response.status_code == 400
    assert message in response.content.decode()
    assert f'id="{field}-error"' in response.content.decode()
    assert not services.basics_complete(artist_of(artist_user))
    assert artist_of(artist_user).name == "Artysta Rola"


@pytest.mark.parametrize(
    "field, value",
    [
        ("artist_type", "opera"),
        ("audiences", ["families", "studenci"]),
        ("voivodeships", ["bawaria"]),
    ],
)
def test_tampered_values_are_refused(web, artist_user, field, value):
    response = web.post(BASICS, {**VALID, field: value})
    assert response.status_code == 400
    assert f'id="{field}-error"' in response.content.decode()
    assert not services.basics_complete(artist_of(artist_user))


@pytest.mark.parametrize("path", LATER)
def test_later_step_redirects_to_step_1_with_empty_basics(web, path):
    response = web.get(path, follow=True)
    assert response.redirect_chain == [(BASICS, 302)]
    assert "Najpierw uzupełnij dane podstawowe." in response.content.decode()


@pytest.mark.parametrize("path", LATER)
def test_later_steps_open_and_can_be_skipped_after_basics(web, artist_user, path):
    services.save_basics(artist_user, VALID)
    assert web.get(path).status_code == 200
    overview = web.get(START).content.decode()  # skipped: overview still lets them continue
    assert f'href="{path}"' in overview and f'href="{BASICS}"' in overview
    assert web.get(BASICS).status_code == 200


@pytest.mark.parametrize("path", [START, BASICS, *LATER])
def test_other_roles_get_403_and_anonymous_goes_to_login(path):
    for user in (make_institution_member(), make_admin()):
        client = Client()
        client.force_login(user)
        assert client.get(path).status_code == 403
        assert client.post(path, VALID).status_code in (403, 405)
    response = Client().get(path)
    assert response.status_code == 302 and response["Location"] == f"/logowanie/?next={path}"


def test_institution_post_to_step_1_saves_nothing():
    client = Client()
    client.force_login(make_institution_member())
    assert client.post(BASICS, VALID).status_code == 403
    assert not Artist.objects.exists()


def test_basics_page_rejects_other_methods(web):
    assert web.put(BASICS).status_code == 405
