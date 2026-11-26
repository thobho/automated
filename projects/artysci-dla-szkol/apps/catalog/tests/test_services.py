"""Catalog dictionaries: services and the starting entries (US-4.6)."""

import pytest
from django.db.models.deletion import ProtectedError

from apps.accounts.tests.conftest import make_artist
from apps.artists.models import Artist
from apps.catalog import services
from apps.catalog.models import ArtistEntry, DictionaryEntry, EntryKind
from apps.catalog.services import EntryError

pytestmark = pytest.mark.django_db

TOPIC, FORM = EntryKind.TOPIC, EntryKind.FORM


def artist(n: int) -> Artist:
    return Artist.objects.get(user=make_artist(f"a{n}@example.invalid"))


def names(artist_, kind):
    return {e.name for e in services.entries_of(artist_, kind)}


def test_starting_entries_migrated():
    topics = DictionaryEntry.objects.filter(kind=TOPIC, is_active=True)
    forms = DictionaryEntry.objects.filter(kind=FORM, is_active=True)
    assert [e.slug for e in topics] == [
        "uzaleznienia",
        "hejt",
        "bezpieczenstwo",
        "emocje",
        "ekologia",
    ]
    assert [e.name for e in topics][:3] == ["uzależnienia", "hejt", "bezpieczeństwo"]
    assert [e.slug for e in forms] == ["spektakl", "warsztaty", "pokaz"]


def test_add_and_rename_keep_slug():
    entry = services.add_entry(TOPIC, "Cyberprzemoc")
    assert entry.slug == "cyberprzemoc" and entry.is_active
    services.rename_entry(entry, "Przemoc w sieci")
    entry.refresh_from_db()
    assert (entry.name, entry.slug) == ("Przemoc w sieci", "cyberprzemoc")
    # the slug stays taken by the renamed entry
    with pytest.raises(EntryError):
        services.add_entry(TOPIC, "cyberprzemoc")


def test_add_transliterates_polish_letters_and_refuses_bad_input():
    assert services.add_entry(FORM, "Łódzki żywioł").slug == "lodzki-zywiol"
    for bad in ("", "   ", "!!!"):
        with pytest.raises(EntryError):
            services.add_entry(TOPIC, bad)
    with pytest.raises(EntryError):
        services.add_entry("nonsense", "x")
    with pytest.raises(EntryError):
        services.add_entry(TOPIC, "HEJT")  # same name, any case


def test_same_name_allowed_in_other_kind():
    assert services.add_entry(FORM, "Hejt").slug == "hejt"


def test_rename_refuses_name_of_another_entry():
    other = DictionaryEntry.objects.get(kind=TOPIC, slug="emocje")
    with pytest.raises(EntryError):
        services.rename_entry(other, "hejt")


def test_deactivate_hides_from_active_entries():
    entry = DictionaryEntry.objects.get(kind=TOPIC, slug="hejt")
    services.deactivate_entry(entry)
    assert "hejt" not in [e.slug for e in services.active_entries(TOPIC)]


def test_merge_with_overlap():
    a = services.add_entry(TOPIC, "A")
    b = services.add_entry(TOPIC, "B")
    one, two, three = artist(1), artist(2), artist(3)
    services.set_artist_entries(one, TOPIC, [a])
    services.set_artist_entries(two, TOPIC, [b])
    services.set_artist_entries(three, TOPIC, [a, b])
    assert services.profiles_to_move(a) == 2
    assert services.merge_entries(a, b) == 2
    assert not DictionaryEntry.objects.filter(pk=a.pk).exists()
    for who in (one, two, three):
        assert ArtistEntry.objects.filter(artist=who, entry=b).count() == 1
    assert ArtistEntry.objects.filter(entry=b).count() == 3


def test_merge_refuses_other_kind_and_itself():
    topic = DictionaryEntry.objects.get(kind=TOPIC, slug="hejt")
    form = DictionaryEntry.objects.get(kind=FORM, slug="pokaz")
    who = artist(1)
    services.set_artist_entries(who, TOPIC, [topic])
    with pytest.raises(EntryError, match="tego samego słownika"):
        services.merge_entries(topic, form)
    with pytest.raises(EntryError):
        services.merge_entries(topic, topic)
    assert DictionaryEntry.objects.filter(pk=topic.pk).exists()
    assert ArtistEntry.objects.filter(artist=who, entry=topic).exists()


def test_merge_rolls_back_on_failure(monkeypatch):
    a = services.add_entry(TOPIC, "A")
    b = services.add_entry(TOPIC, "B")
    who = artist(1)
    services.set_artist_entries(who, TOPIC, [a])

    def boom(self, *args, **kwargs):
        raise RuntimeError("db went away")

    monkeypatch.setattr(DictionaryEntry, "delete", boom)
    with pytest.raises(RuntimeError):
        services.merge_entries(a, b)
    assert ArtistEntry.objects.filter(artist=who, entry=a).exists()
    assert not ArtistEntry.objects.filter(entry=b).exists()


def test_entry_with_assignments_cannot_be_deleted():
    entry = DictionaryEntry.objects.get(kind=TOPIC, slug="hejt")
    services.set_artist_entries(artist(1), TOPIC, [entry])
    with pytest.raises(ProtectedError):
        entry.delete()


def test_set_artist_entries_replaces_and_is_idempotent():
    who = artist(1)
    hejt = DictionaryEntry.objects.get(kind=TOPIC, slug="hejt")
    emocje = DictionaryEntry.objects.get(kind=TOPIC, slug="emocje")
    pokaz = DictionaryEntry.objects.get(kind=FORM, slug="pokaz")
    services.set_artist_entries(who, FORM, [pokaz])
    services.set_artist_entries(who, TOPIC, [hejt])
    services.set_artist_entries(who, TOPIC, [hejt, emocje])
    services.set_artist_entries(who, TOPIC, [emocje, emocje])
    assert names(who, TOPIC) == {"emocje"}
    assert names(who, FORM) == {"pokaz"}  # the other kind is untouched
    services.set_artist_entries(who, TOPIC, [])
    assert names(who, TOPIC) == set()


def test_set_artist_entries_refuses_inactive_and_other_kind_atomically():
    who = artist(1)
    hejt = DictionaryEntry.objects.get(kind=TOPIC, slug="hejt")
    emocje = DictionaryEntry.objects.get(kind=TOPIC, slug="emocje")
    pokaz = DictionaryEntry.objects.get(kind=FORM, slug="pokaz")
    services.set_artist_entries(who, TOPIC, [hejt])
    services.deactivate_entry(emocje)
    with pytest.raises(EntryError, match="nieaktywna"):
        services.set_artist_entries(who, TOPIC, [emocje])
    with pytest.raises(EntryError, match="innego słownika"):
        services.set_artist_entries(who, TOPIC, [pokaz])
    assert names(who, TOPIC) == {"hejt"}
