import pytest
from django.contrib.auth import get_user_model
from django.core.management import call_command

pytestmark = pytest.mark.django_db


def test_seed_creates_expected_counts_and_is_idempotent(capsys):
    call_command("seed")
    first = get_user_model().objects.count()
    capsys.readouterr()
    call_command("seed")
    assert first == 15
    assert get_user_model().objects.count() == first
    assert "created 0 artists, 0 institutions" in capsys.readouterr().out


def test_seed_users_have_their_roles_idempotently():
    from apps.accounts.roles import Role, role_of
    from apps.artists.models import Artist
    from apps.institutions.models import InstitutionMember

    call_command("seed")
    call_command("seed")
    users = get_user_model().objects
    assert role_of(users.get(email="artysta01@example.invalid")) is Role.ARTIST
    assert role_of(users.get(email="szkola05@example.invalid")) is Role.INSTITUTION
    assert Artist.objects.count() == 10 and InstitutionMember.objects.count() == 5
    assert all(role_of(user) in (Role.ARTIST, Role.INSTITUTION) for user in users.all())


def test_seed_skips_admin_and_missing_seed_users():
    from apps.accounts import services
    from apps.artists import services as artists
    from apps.institutions import services as institutions

    services.create_admin("artysta01@example.invalid")
    services.create_admin("szkola01@example.invalid")
    institutions.seed_rspo()
    assert artists.seed_artists() == 0 and institutions.seed_members() == 0


def _entries(email, kind):
    from apps.artists.models import Artist
    from apps.catalog import services as catalog

    artist = Artist.objects.get(user__email=email)
    return sorted(entry.slug for entry in catalog.entries_of(artist, kind))


def test_seed_gives_artists_topics_and_forms_but_not_artysta10():
    call_command("seed")
    for number in range(1, 10):
        email = f"artysta{number:02d}@example.invalid"
        assert 1 <= len(_entries(email, "topic")) <= 3
        assert 1 <= len(_entries(email, "form")) <= 2
    last = "artysta10@example.invalid"
    assert _entries(last, "topic") == [] and _entries(last, "form") == []


def test_seed_catalog_entries_are_idempotent():
    call_command("seed")
    emails = [f"artysta{n:02d}@example.invalid" for n in range(1, 11)]
    first = [(_entries(e, "topic"), _entries(e, "form")) for e in emails]
    call_command("seed")
    assert [(_entries(e, "topic"), _entries(e, "form")) for e in emails] == first


def test_seed_keeps_topics_the_artist_changed():
    from apps.artists.models import Artist
    from apps.catalog import services as catalog

    call_command("seed")
    email = "artysta01@example.invalid"
    artist = Artist.objects.get(user__email=email)
    ekologia = [e for e in catalog.active_entries("topic") if e.slug == "ekologia"]
    catalog.set_artist_entries(artist, "topic", ekologia)
    call_command("seed")
    assert _entries(email, "topic") == ["ekologia"]


def test_seed_uses_only_reserved_domain_and_no_password():
    call_command("seed")
    for user in get_user_model().objects.all():
        assert user.email.endswith("@example.invalid")
        assert not user.has_usable_password()
