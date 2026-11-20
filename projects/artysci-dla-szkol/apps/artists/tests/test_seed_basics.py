import pytest
from django.core.management import call_command

from apps.artists import services
from apps.artists.models import Artist, ArtistAudience, ArtistVoivodeship

pytestmark = pytest.mark.django_db


def snapshot():
    return sorted(
        (a.user.email, services.basics_of(a)) for a in Artist.objects.select_related("user")
    )


def test_seed_fills_basics_except_one_and_is_idempotent():
    call_command("seed")
    first = snapshot()
    rows = (ArtistVoivodeship.objects.count(), ArtistAudience.objects.count())
    call_command("seed")
    assert snapshot() == first
    assert (ArtistVoivodeship.objects.count(), ArtistAudience.objects.count()) == rows

    complete = {a.user.email: services.basics_complete(a) for a in Artist.objects.all()}
    assert len(complete) == 10
    assert complete.pop("artysta10@example.invalid") is False
    assert all(complete.values())
    for email, basics in first:
        assert email.endswith("@example.invalid")
        if email != "artysta10@example.invalid":
            assert len(basics.voivodeships) == 2 and len(basics.audiences) == 3


def test_seed_keeps_basics_the_artist_changed():
    call_command("seed")
    artist = Artist.objects.get(user__email="artysta01@example.invalid")
    services.save_basics(
        artist.user,
        {
            "artist_type": "other",
            "name": "Zmienione",
            "city": "Hel",
            "voivodeships": ["pomorskie"],
            "audiences": ["families"],
        },
    )
    call_command("seed")
    assert services.basics_of(Artist.objects.get(pk=artist.pk)).city == "Hel"
