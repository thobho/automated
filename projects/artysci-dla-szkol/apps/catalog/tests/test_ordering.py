"""The D16 order of the catalog (US-4.4): match, verified, completeness, daily shuffle."""

import re
from datetime import UTC, date, datetime, timedelta

import pytest
from django.test import Client
from django.utils import timezone

from apps.accounts.tests.conftest import make_artist
from apps.artists.models import Artist, MaterialKind, PublicationStatus
from apps.catalog import listing, ordering, search
from apps.catalog.models import CatalogEntry
from apps.profiles import publication
from apps.profiles.tests.factories import add_material

pytestmark = pytest.mark.django_db

URL = "/artysci/"


def make(number: int, *, bucket: int = 0, name: str | None = None, **fields) -> Artist:
    artist = Artist.objects.get(user=make_artist(f"porzadek{number}@example.invalid"))
    artist.name = name or f"Artysta {number:03d}"
    artist.slug = f"artysta-{number:03d}"
    artist.publication_status = PublicationStatus.PUBLISHED
    artist.save()
    CatalogEntry.objects.create(
        artist=artist,
        slug=artist.slug,
        name=artist.name,
        published_at=timezone.now(),
        completeness_bucket=bucket,
        **fields,
    )
    return artist


def names(page_number: str | None = None, **filters) -> list[str]:
    page = listing.cards_page(page_number, listing.Filters(**filters))
    return [card.name for card in page.cards]


def all_names() -> list[str]:
    found, number = [], 1
    while (page := listing.cards_page(str(number))) is not None:
        found += [c.name for c in page.cards]
        number += 1
    return found


def set_day(monkeypatch, day: date) -> None:
    monkeypatch.setattr(ordering, "today", lambda: day)


# --- units -----------------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("percent", "bucket"), [(0, 0), (9, 0), (10, 10), (67, 60), (99, 90), (100, 100), (150, 100)]
)
def test_completeness_buckets_round_down_to_tens(percent, bucket):
    assert ordering.completeness_bucket(percent) == bucket


def test_today_is_the_warsaw_day(monkeypatch):
    late = datetime(2026, 11, 28, 23, 30, tzinfo=UTC)  # 00:30 on the 29th in Warsaw
    monkeypatch.setattr(timezone, "now", lambda: late)
    assert ordering.today() == date(2026, 11, 29)
    before = datetime(2026, 11, 28, 22, 30, tzinfo=UTC)  # 23:30 on the 28th
    monkeypatch.setattr(timezone, "now", lambda: before)
    assert ordering.today() == date(2026, 11, 28)


# --- the criteria ----------------------------------------------------------------------------


def test_same_day_same_order_for_every_client():
    for n in range(1, 8):
        make(n)
    first = Client().get(URL).content.decode()
    second = Client().get(URL).content.decode()
    assert re.findall(r"Artysta \d{3}", first) == re.findall(r"Artysta \d{3}", second)
    assert len(re.findall(r"Artysta \d{3}", first)) >= 7


def test_the_shuffle_changes_with_the_day(monkeypatch):
    for n in range(1, 11):
        make(n)
    orders = []
    for offset in range(5):
        set_day(monkeypatch, date(2026, 12, 1) + timedelta(days=offset))
        orders.append(all_names())
    assert len({tuple(o) for o in orders}) > 1
    assert all(sorted(o) == sorted(orders[0]) for o in orders)


def test_the_order_is_stable_within_a_day(monkeypatch):
    for n in range(1, 11):
        make(n)
    set_day(monkeypatch, date(2026, 12, 1))
    assert all_names() == all_names()


def test_more_complete_comes_first_on_any_day(monkeypatch):
    make(1, bucket=40, name="Mniej")
    make(2, bucket=80, name="Więcej")
    for offset in range(6):
        set_day(monkeypatch, date(2026, 12, 1) + timedelta(days=offset))
        assert all_names() == ["Więcej", "Mniej"]


def test_verified_beats_completeness(monkeypatch):
    a = make(1, bucket=100, name="Pelny A")
    b = make(2, bucket=10, name="Zweryfikowany B")
    monkeypatch.setattr(listing, "is_verified", lambda artist_id: artist_id == b.pk)
    assert all_names() == ["Zweryfikowany B", "Pelny A"]
    assert a.pk != b.pk


def test_match_beats_verification_and_completeness(monkeypatch):
    # B matches only by a typo, but is verified and more complete; A matches by name.
    a = make(1, bucket=0, name="Hejtowy teatr", **search.index_terms("Hejtowy teatr", [], []))
    make(2, bucket=100, name="Hajtowy zespol", **search.index_terms("Hajtowy zespol", [], []))
    monkeypatch.setattr(listing, "is_verified", lambda artist_id: artist_id != a.pk)
    page = listing.cards_page(None, listing.Filters(q="hejtowy"))
    assert [c.name for c in page.cards][0] == "Hejtowy teatr"
    assert page.total == 2


def test_pages_hold_every_artist_exactly_once(monkeypatch):
    for n in range(1, 61):
        make(n, bucket=(n % 4) * 10)
    set_day(monkeypatch, date(2026, 12, 3))
    found = []
    for number in (1, 2, 3):
        page = listing.cards_page(str(number))
        assert len(page.cards) == 24 if number < 3 else 12
        found += [c.name for c in page.cards]
    assert len(found) == len(set(found)) == 60
    assert listing.cards_page("4") is None


def test_filters_keep_the_order_rules(monkeypatch):
    make(1, bucket=20, name="A", artist_type="music")
    make(2, bucket=70, name="B", artist_type="music")
    make(3, bucket=90, name="C", artist_type="theatre")
    assert names(rodzaj="music") == ["B", "A"]


# --- completeness is a published-state value -------------------------------------------------


def test_completeness_moves_only_after_publishing_changes():
    from apps.profiles.tests.test_publication import make_ready

    artist = publication.publish(make_ready("kompletnosc@example.invalid"))
    before = CatalogEntry.objects.get(artist=artist).completeness_bucket
    add_material(artist, MaterialKind.PHOTO, storage_key="p/9.jpg", alt_text="Scena")
    assert CatalogEntry.objects.get(artist=artist).completeness_bucket == before  # draft only
    publication.update_published(artist)
    assert CatalogEntry.objects.get(artist=artist).completeness_bucket >= before
    assert CatalogEntry.objects.get(artist=artist).completeness_bucket % 10 == 0


def test_rebuild_writes_the_bucket():
    from apps.profiles.tests.test_publication import make_ready

    artist = publication.publish(make_ready("przebudowa@example.invalid"))
    CatalogEntry.objects.filter(artist=artist).update(completeness_bucket=0)
    listing.rebuild_all()
    assert CatalogEntry.objects.get(artist=artist).completeness_bucket > 0


# --- no paid boosts --------------------------------------------------------------------------


def test_catalog_entry_has_no_boost_field():
    fields = {f.name for f in CatalogEntry._meta.get_fields()}
    forbidden = ("boost", "priority", "sponsor", "promot", "paid", "featured", "pinned", "rank")
    assert not [f for f in fields if any(word in f for word in forbidden)]


def test_other_changes_do_not_change_the_group(monkeypatch):
    """Only match, verification and completeness choose the group; everything else (name, price,
    publication time, photo) leaves the key's group part untouched."""
    a = make(1, bucket=50, name="Alfa")
    day = date(2026, 12, 1)
    key = lambda e: ordering.order_key(  # noqa: E731
        score=0, verified=False, bucket=e.completeness_bucket, artist_id=e.artist_id, day=day
    )
    entry = CatalogEntry.objects.get(artist=a)
    before = key(entry)
    CatalogEntry.objects.filter(pk=entry.pk).update(
        name="Zupelnie inna", price_from=1, published_at=timezone.now() + timedelta(days=9)
    )
    assert key(CatalogEntry.objects.get(pk=entry.pk)) == before
