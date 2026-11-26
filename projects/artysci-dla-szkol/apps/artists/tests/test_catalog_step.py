"""Wizard step 1: the closed dictionaries "Tematyka" and "Forma" (US-4.6)."""

import re

import pytest
from django.test import Client

from apps.accounts.tests.conftest import make_artist
from apps.artists import services
from apps.artists.models import Artist
from apps.artists.services import InvalidBasics
from apps.catalog import services as catalog
from apps.catalog.models import ArtistEntry, DictionaryEntry

pytestmark = pytest.mark.django_db

BASICS = "/artysta/profil/dane/"
VALID = {
    "artist_type": "theatre",
    "name": "Teatr Testowy Kwiatki",
    "city": "Wrocław",
    "voivodeships": ["dolnoslaskie"],
    "audiences": ["kindergarten"],
}


@pytest.fixture
def artist_user():
    return make_artist()


@pytest.fixture
def web(artist_user):
    client = Client()
    client.force_login(artist_user)
    return client


def entry(kind, slug):
    return DictionaryEntry.objects.get(kind=kind, slug=slug)


def assigned(user):
    rows = ArtistEntry.objects.filter(artist__user=user)
    return set(rows.values_list("entry__slug", flat=True))


def test_step_one_offers_active_entries_in_position_order(web):
    catalog.deactivate_entry(entry("topic", "hejt"))
    html = web.get(BASICS).content.decode()
    assert "Tematyka" in html and "Forma" in html
    assert "hejt" not in html
    order = [html.index(name) for name in ("uzależnienia", "bezpieczeństwo", "emocje", "ekologia")]
    assert order == sorted(order)
    assert "warsztaty" in html


def test_step_one_saves_exactly_the_ticked_entries(web, artist_user):
    post = {**VALID, "topics": [entry("topic", "hejt").pk]}
    post["catalog_forms"] = [entry("form", "warsztaty").pk]
    assert web.post(BASICS, post).status_code == 302
    assert assigned(artist_user) == {"hejt", "warsztaty"}
    html = web.get(BASICS).content.decode()
    assert len(re.findall(r"checked", html)) >= 4  # the saved ticks come back
    web.post(BASICS, VALID)  # nothing ticked: removed (the groups are optional)
    assert assigned(artist_user) == set()


def test_invalid_basics_change_no_entries(web, artist_user):
    web.post(BASICS, {**VALID, "topics": [entry("topic", "hejt").pk]})
    bad = {**VALID, "name": "", "topics": [entry("topic", "emocje").pk]}
    assert web.post(BASICS, bad).status_code == 400
    assert assigned(artist_user) == {"hejt"}


def test_inactive_entry_stays_until_the_step_is_saved_again(web, artist_user):
    hejt = entry("topic", "hejt")
    web.post(BASICS, {**VALID, "topics": [hejt.pk]})
    catalog.deactivate_entry(hejt)
    assert assigned(artist_user) == {"hejt"}
    assert web.post(BASICS, {**VALID, "topics": [hejt.pk]}).status_code == 400  # not offered
    web.post(BASICS, {**VALID, "topics": [entry("topic", "emocje").pk]})
    assert assigned(artist_user) == {"emocje"}


def test_entry_of_the_wrong_group_is_refused(web, artist_user):
    post = {**VALID, "topics": [entry("form", "pokaz").pk]}
    assert web.post(BASICS, post).status_code == 400
    assert assigned(artist_user) == set()


def test_save_basics_with_a_refused_entry_saves_nothing(artist_user):
    hejt = entry("topic", "hejt")
    catalog.deactivate_entry(hejt)
    with pytest.raises(InvalidBasics):
        services.save_basics(artist_user, {**VALID, "topics": [hejt]})
    assert Artist.objects.get(user=artist_user).city == ""
