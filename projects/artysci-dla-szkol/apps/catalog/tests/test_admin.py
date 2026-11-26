"""Dictionaries in /django-admin/ (US-4.6, D100): list, add, rename, merge, delete, access."""

import pytest
from django.test import Client
from django.urls import reverse

from apps.accounts.tests.conftest import make_admin, make_artist, make_institution_member
from apps.artists.models import Artist
from apps.catalog import services
from apps.catalog.models import ArtistEntry, DictionaryEntry, EntryKind

pytestmark = pytest.mark.django_db

LIST = "/django-admin/catalog/dictionaryentry/"


@pytest.fixture
def admin_client():
    client = Client()
    client.force_login(make_admin())
    return client


def entry(kind, slug):
    return DictionaryEntry.objects.get(kind=kind, slug=slug)


def test_list_shows_starting_entries(admin_client):
    response = admin_client.get(LIST)
    assert response.status_code == 200
    html = response.content.decode()
    for slug in ("uzaleznienia", "bezpieczenstwo", "spektakl", "pokaz"):
        assert slug in html


def test_add_then_rename_keeps_slug(admin_client):
    response = admin_client.post(
        LIST + "add/", {"kind": "topic", "name": "Cyberprzemoc", "is_active": "on", "position": 9}
    )
    assert response.status_code == 302
    created = entry("topic", "cyberprzemoc")
    response = admin_client.post(
        f"{LIST}{created.pk}/change/",
        {"name": "Przemoc w sieci", "is_active": "on", "position": 9},
    )
    assert response.status_code == 302
    created.refresh_from_db()
    assert (created.name, created.slug, created.kind) == (
        "Przemoc w sieci",
        "cyberprzemoc",
        "topic",
    )


def test_kind_and_slug_are_read_only_after_creation(admin_client):
    hejt = entry("topic", "hejt")
    admin_client.post(
        f"{LIST}{hejt.pk}/change/",
        {"kind": "form", "slug": "inny", "name": "hejt", "is_active": "on", "position": 1},
    )
    hejt.refresh_from_db()
    assert (hejt.kind, hejt.slug) == ("topic", "hejt")


def test_add_duplicate_name_is_refused(admin_client):
    response = admin_client.post(
        LIST + "add/", {"kind": "topic", "name": "Hejt", "is_active": "on", "position": 1}
    )
    assert response.status_code == 200  # form redisplayed with an error
    assert DictionaryEntry.objects.filter(kind="topic", name__iexact="hejt").count() == 1


def merge_post(client, source, target=None, apply=False):
    data = {"action": "merge", "_selected_action": [source.pk]}
    if apply:
        data |= {"apply": "1", "target": target.pk}
    return client.post(LIST, data)


def test_merge_confirmation_shows_count_and_merge_moves_profiles(admin_client):
    a = services.add_entry(EntryKind.TOPIC, "A")
    b = services.add_entry(EntryKind.TOPIC, "B")
    people = [Artist.objects.get(user=make_artist(f"m{i}@example.invalid")) for i in range(3)]
    services.set_artist_entries(people[0], "topic", [a])
    services.set_artist_entries(people[1], "topic", [b])
    services.set_artist_entries(people[2], "topic", [a, b])
    page = merge_post(admin_client, a)
    assert page.status_code == 200
    assert b'merge-count">2<' in page.content
    assert DictionaryEntry.objects.filter(pk=a.pk).exists()  # nothing happens before confirming
    # only entries of the same kind are offered as the target
    assert "pokaz" not in " ".join(str(c[1]) for c in page.context["form"].fields["target"].choices)
    done = merge_post(admin_client, a, b, apply=True)
    assert done.status_code == 302
    assert not DictionaryEntry.objects.filter(pk=a.pk).exists()
    for person in people:
        assert ArtistEntry.objects.filter(artist=person, entry=b).count() == 1


def test_merge_across_kinds_is_refused(admin_client):
    topic, form = entry("topic", "hejt"), entry("form", "pokaz")
    done = merge_post(admin_client, topic, form, apply=True)
    assert done.status_code == 200  # the form refuses the target: not in the same kind
    assert DictionaryEntry.objects.filter(pk=topic.pk).exists()


def test_merge_needs_exactly_one_selected(admin_client):
    data = {
        "action": "merge",
        "_selected_action": [entry("topic", "hejt").pk, entry("topic", "emocje").pk],
    }
    response = admin_client.post(LIST, data, follow=True)
    assert "dokładnie jedną" in response.content.decode()
    assert DictionaryEntry.objects.filter(kind="topic").count() == 5


def test_deactivate_action(admin_client):
    hejt = entry("topic", "hejt")
    admin_client.post(LIST, {"action": "deactivate", "_selected_action": [hejt.pk]})
    hejt.refresh_from_db()
    assert not hejt.is_active


def test_delete_of_entry_with_assignments_is_refused(admin_client):
    hejt = entry("topic", "hejt")
    services.set_artist_entries(Artist.objects.get(user=make_artist()), "topic", [hejt])
    response = admin_client.post(f"{LIST}{hejt.pk}/delete/", {"post": "yes"})
    assert response.status_code == 403
    assert DictionaryEntry.objects.filter(pk=hejt.pk).exists()
    # an unused entry can still be deleted
    unused = entry("topic", "ekologia")
    admin_client.post(f"{LIST}{unused.pk}/delete/", {"post": "yes"})
    assert not DictionaryEntry.objects.filter(pk=unused.pk).exists()


@pytest.mark.parametrize("who", ["anonymous", "artist", "institution"])
def test_others_never_see_the_list(who):
    client = Client()
    if who == "artist":
        client.force_login(make_artist())
    elif who == "institution":
        client.force_login(make_institution_member())
    response = client.get(LIST)
    assert response.status_code in (302, 403)
    if response.status_code == 302:
        assert "login" in response["Location"]
    assert b"uzaleznienia" not in response.content


def test_staff_without_change_permission_cannot_merge(django_user_model):
    staff = django_user_model.objects.create_user(email="staff@example.invalid", is_staff=True)
    from django.contrib.auth.models import Permission

    staff.user_permissions.add(Permission.objects.get(codename="view_dictionaryentry"))
    client = Client()
    client.force_login(staff)
    assert client.get(LIST).status_code == 200
    hejt = entry("topic", "hejt")
    emocje = entry("topic", "emocje")
    merge_post(client, hejt, emocje, apply=True)
    assert DictionaryEntry.objects.filter(pk=hejt.pk).exists()
    assert reverse("admin:catalog_dictionaryentry_changelist") == LIST
