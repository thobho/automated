"""Missing items as a task list and the completeness percentage (US-2.7)."""

import re

import pytest
from django.test import Client

from apps.accounts.tests.conftest import make_artist, make_institution_member
from apps.artists import services as artist_services
from apps.artists.models import Artist, ArtistAudience, ArtistVoivodeship, MaterialKind, Offer
from apps.profiles import completeness, generation
from apps.quality import services as quality
from apps.quality.models import Generation
from apps.trust import services as trust
from apps.trust.models import LegalDocument

from .factories import add_material, make_seed_artist, valid_profile

pytestmark = pytest.mark.django_db

PAGE = "/artysta/profil/braki/"


def keys(artist) -> list[str]:
    return [t.key for t in completeness.task_list(artist)]


def run(artist, status=Generation.Status.READY, **profile):
    record = quality.start_generation(artist, "manual", generation.COMPONENTS)
    return quality.finish_generation(record, valid_profile(**profile), [], 0, status)


def fill_basics(artist):
    ArtistVoivodeship.objects.create(artist=artist, voivodeship="dolnoslaskie")
    ArtistAudience.objects.create(artist=artist, audience="kindergarten")


def child_protection(artist):
    trust.publish(LegalDocument.Kind.CHILD_PROTECTION, "Treść testowa", material=False)
    trust.make_statement(artist, LegalDocument.Kind.CHILD_PROTECTION)


def photo(artist):
    return add_material(artist, MaterialKind.PHOTO, checks_version=1)


@pytest.fixture
def empty():
    return Artist.objects.get(user=make_artist("pusty@example.invalid"))


@pytest.fixture
def seed():
    return make_seed_artist()


# --- the mapping -------------------------------------------------------------------------------


def test_two_known_gaps_map_to_their_screens(seed):
    run(
        seed,
        gaps=[
            {"code": "no_stage_photo", "message": "x"},
            {"code": "no_max_audience", "message": "y"},
        ],
    )
    tasks = {t.key: t for t in completeness.task_list(seed)}
    assert tasks["main_photo"].url_name == "artists:materials_photos"
    assert tasks["main_photo"].text == "Dodaj zdjęcie ze sceny"
    assert tasks["max_audience"].url_name == "artists:questionnaire"
    assert tasks["max_audience"].text == "Podaj maksymalną liczbę widzów"


def test_every_mapped_screen_exists():
    from django.urls import reverse

    for kind in (*completeness.GAP_KINDS.values(), *completeness.CHECKLIST):
        assert reverse(kind.url_name)


def test_unknown_kind_is_listed_without_a_button_and_does_not_fail(seed):
    run(seed, gaps=[{"code": "wat", "message": "Brakuje czegoś nowego"}, {"code": 5}, {}])
    unknown = [t for t in completeness.task_list(seed) if t.key.startswith("gap:")]
    assert [t.text for t in unknown] == ["Brakuje czegoś nowego"]
    assert not unknown[0].has_button


def test_a_gap_kind_shows_once_even_with_a_rule_item(seed):
    run(
        seed, gaps=[{"code": "no_photo", "message": "a"}, {"code": "no_main_photo", "message": "b"}]
    )
    assert keys(seed).count("main_photo") == 1


def test_a_held_generation_shows_no_gaps(seed):
    run(seed, status=Generation.Status.REVIEW, gaps=[{"code": "no_price", "message": "x"}])
    assert "price" not in keys(seed)
    assert not any(k.startswith("gap:") for k in keys(seed))


def test_no_generation_only_rule_items(empty):
    assert set(keys(empty)) == {k.key for k in completeness.RULE_ITEMS}


def test_other_artist_gaps_are_not_shown(seed):
    run(seed, gaps=[{"code": "no_price", "message": "x"}])
    other = make_seed_artist("inny@example.invalid")
    other.offers.all().delete()
    assert "price" not in keys(other)


# --- filling an item removes it ----------------------------------------------------------------


def test_filling_an_item_removes_it_and_raises_the_percentage(seed):
    run(
        seed,
        gaps=[{"code": "no_max_audience", "message": "x"}, {"code": "no_photo", "message": "y"}],
    )
    fill_basics(seed)
    before = completeness.completeness_percent(seed)
    assert {"max_audience", "main_photo"} <= set(keys(seed))
    photo(seed)
    seed.q_max_audience = 80
    seed.save()
    assert not {"max_audience", "main_photo"} & set(keys(seed))
    assert completeness.completeness_percent(seed) > before


def test_adding_an_offer_through_the_service_removes_the_item(empty):
    fill_basics(empty)
    assert "offers" in keys(empty)
    artist_services.create_offer(
        empty, {"title": "Spektakl", "description": "Opis", "price_on_request": True}
    )
    assert "offers" not in keys(empty)


def test_price_gap_is_satisfied_by_an_offer_price(seed):
    run(seed, gaps=[{"code": "no_price", "message": "x"}])
    Offer.objects.filter(artist=seed).delete()
    assert "price" in keys(seed)
    Offer.objects.create(artist=seed, title="Nowa", description="Opis", price_pln=500)
    assert "price" not in keys(seed)


@pytest.mark.parametrize(
    ("code", "field", "value"),
    [
        ("no_duration", "q_duration_minutes", 45),
        ("no_age_range", "q_age_from", 4),
        ("no_tech_requirements", "q_tech_room", "Sala"),
    ],
)
def test_questionnaire_gaps(empty, code, field, value):
    run(empty, gaps=[{"code": code, "message": "x"}])
    kind = completeness.GAP_KINDS[code]
    assert kind.key in keys(empty)
    setattr(empty, field, value)
    empty.save()
    assert kind.key not in keys(empty)


# --- the percentage ----------------------------------------------------------------------------


def test_percent_empty_is_zero(empty):
    assert completeness.completeness_percent(empty) == 0


def test_percent_partial_is_rounded(empty):
    fill_basics(empty)
    empty.city = "Opole"
    empty.artist_type = "theatre"
    empty.save()
    assert completeness.completeness_percent(empty) == 17  # 1 of 6
    empty.q_age_from = 4
    empty.save()
    assert completeness.completeness_percent(empty) == 33  # 2 of 6


def test_percent_full_is_100_and_no_tasks(seed):
    fill_basics(seed)
    seed.artist_type = "theatre"
    seed.save()
    photo(seed)
    child_protection(seed)
    run(seed)
    from apps.profiles import pages

    pages.record_generated(Generation.objects.get())
    assert completeness.completeness_percent(seed) == 100
    assert completeness.task_list(seed) == []


def test_percent_stays_in_range(empty, seed):
    for artist in (empty, seed):
        assert 0 <= completeness.completeness_percent(artist) <= 100


# --- the page ----------------------------------------------------------------------------------


def web(artist):
    client = Client()
    client.force_login(artist.user)
    return client


def test_page_lists_tasks_with_buttons_progress_and_no_inline_style(seed):
    run(seed, gaps=[{"code": "no_max_audience", "message": "x"}, {"code": "zzz", "message": "Coś"}])
    response = web(seed).get(PAGE)
    body = response.content.decode()
    assert response.status_code == 200
    assert "Podaj maksymalną liczbę widzów" in body
    assert 'href="/artysta/profil/kwestionariusz/"' in body
    assert "Coś" in body
    assert re.search(r"<progress[^>]*max=\"100\"[^>]*value=\"\d+\"", body)
    assert "style=" not in body and "<style" not in body
    assert 'href="/panel/podglad/"' in body


def test_page_all_done_note(seed, monkeypatch):
    monkeypatch.setattr(completeness, "task_list", lambda artist: [])
    body = web(seed).get(PAGE).content.decode()
    assert "Wszystko uzupełnione" in body


def test_page_refuses_anonymous_and_other_roles(seed):
    anonymous = Client().get(PAGE)
    assert anonymous.status_code in (302, 403, 404)
    if anonymous.status_code == 302:
        assert "login" in anonymous["Location"] or "logowanie" in anonymous["Location"]
    member = make_institution_member()
    client = Client()
    client.force_login(member)
    assert client.get(PAGE).status_code in (302, 403, 404)


def test_page_shows_only_own_items(seed):
    run(seed, gaps=[{"code": "zzz", "message": "Tylko moje"}])
    other = make_artist("drugi@example.invalid")
    body = web(Artist.objects.get(user=other)).get(PAGE).content.decode()
    assert "Tylko moje" not in body


def test_wizard_overview_shows_the_summary(seed):
    body = web(seed).get("/artysta/kreator/").content.decode()
    assert "data-completeness=" in body and "Zobacz braki" in body and PAGE in body
