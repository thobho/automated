"""Synthetic rows for catalog load tests (T56a, #226).

    create_fake_entries(10_000, seed=0)   # users, artists and catalog rows, in batches
    delete_fake_entries()                 # only the ``fake-*@example.invalid`` users

The data is made directly in the read model (no publication snapshot, no media): a published
`Artist` per row, so `/artysci/` shows the rows, and a `CatalogEntry` with the search columns of
`search.index_terms`. Every choice comes from one `random.Random(seed)`, so the same seed gives
the same names, regions, prices and search words. The command refuses to write outside the dev
and test settings; this module refuses too, so a direct call cannot fill a real database either.
"""

import os
import random
from dataclasses import dataclass
from datetime import datetime, timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone

from apps.artists.models import Artist, ArtistType, Audience, PublicationStatus
from apps.core.regions import Voivodeship

from . import search
from .models import CatalogEntry, EntryKind
from .services import active_entries

BATCH_SIZE = 500
EMAIL_DOMAIN = "example.invalid"
EMAIL_PREFIX = "fake-"
NAME_PREFIX = "Artysta Syntetyczny"
SLUG_PREFIX = "syntetyczny-"
TEST_SETTINGS = "config.settings.test"

CHOICES_MIN, CHOICES_MAX = 1, 3
OFFERS_MIN, OFFERS_MAX = 1, 4
PRICE_MIN, PRICE_MAX = 200, 3000
DURATION_MIN, DURATION_MAX = 30, 120
NONE_CHANCE = 0.2

ENTRY_FIELDS = (
    "slug",
    "name",
    "artist_type",
    "voivodeships",
    "age_groups",
    "topics",
    "forms",
    "price_from",
    "offers",
    "published_at",
    "search_name",
    "search_other",
    "search_fuzzy",
)
ARTIST_FIELDS = ("name", "slug", "artist_type", "publication_status", "published_at")


class FakeEntriesRefused(RuntimeError):
    """The command is not allowed to write synthetic rows in this environment."""


class FakeEntriesError(RuntimeError):
    """The rows cannot be built (the catalog dictionaries have no active entries)."""


@dataclass(frozen=True)
class _Record:
    number: int
    email: str
    name: str
    slug: str
    artist_type: str
    voivodeships: list[str]
    age_groups: list[str]
    topics: list[dict]
    forms: list[dict]
    offers: list[dict]
    price_from: int | None
    published_at: datetime
    search_terms: dict[str, str]


def refusal_reason() -> str | None:
    """Why the command may not run here, or None when it may."""
    if settings.DEBUG or os.environ.get("DJANGO_SETTINGS_MODULE") == TEST_SETTINGS:
        return None
    return (
        "catalog_fake_entries refuses to run: DEBUG is off and DJANGO_SETTINGS_MODULE is not "
        f"{TEST_SETTINGS}. Synthetic data must never reach a real database."
    )


def _sample(rng: random.Random, values, *, low: int = CHOICES_MIN, high: int = CHOICES_MAX):
    values = list(values)
    if not values:
        return []
    return rng.sample(values, rng.randint(low, min(high, len(values))))


def _record(rng: random.Random, number: int, now: datetime, topics, forms) -> _Record:
    chosen_topics = _sample(rng, topics)
    chosen_forms = _sample(rng, forms)
    offers = []
    offer_titles = []
    for position in range(rng.randint(OFFERS_MIN, OFFERS_MAX)):
        price = None if rng.random() < NONE_CHANCE else rng.randint(PRICE_MIN, PRICE_MAX)
        duration = None if rng.random() < NONE_CHANCE else rng.randint(DURATION_MIN, DURATION_MAX)
        offers.append({"price": price, "duration": duration})
        form = chosen_forms[position % len(chosen_forms)]
        topic = chosen_topics[position % len(chosen_topics)]
        offer_titles.append(f"Oferta {form.name} o {topic.name} {number:05d}")

    name = f"{NAME_PREFIX} {number:05d}"
    return _Record(
        number=number,
        email=f"{EMAIL_PREFIX}{number:05d}@{EMAIL_DOMAIN}",
        name=name,
        slug=f"{SLUG_PREFIX}{number:05d}",
        artist_type=rng.choice(ArtistType.values),
        voivodeships=_sample(rng, Voivodeship.values),
        age_groups=_sample(rng, Audience.values),
        topics=[{"slug": entry.slug, "name": entry.name} for entry in chosen_topics],
        forms=[{"slug": entry.slug, "name": entry.name} for entry in chosen_forms],
        offers=offers,
        price_from=min((o["price"] for o in offers if o["price"] is not None), default=None),
        published_at=now - timedelta(days=rng.uniform(0, 365)),
        search_terms=search.index_terms(
            name, offer_titles, [entry.name for entry in chosen_topics]
        ),
    )


def _insert(records: list[_Record]) -> None:
    """One batch: users, then artists, then catalog rows. Existing rows of the same numbers are
    updated, so a repeated run with the same seed does not fail on the unique columns."""
    user_model = get_user_model()
    emails = [record.email for record in records]
    users = []
    for record in records:
        user = user_model(email=record.email)
        user.set_unusable_password()
        users.append(user)
    user_model.objects.bulk_create(users, ignore_conflicts=True)
    users_by_email = {user.email: user for user in user_model.objects.filter(email__in=emails)}
    user_ids = [user.pk for user in users_by_email.values()]

    artists_by_user = {
        artist.user_id: artist for artist in Artist.objects.filter(user_id__in=user_ids)
    }
    new_artists = []
    changed_artists = []
    for record in records:
        artist = artists_by_user.get(users_by_email[record.email].pk)
        if artist is None:
            artist = Artist(user=users_by_email[record.email])
            new_artists.append(artist)
        else:
            changed_artists.append(artist)
        artist.name = record.name
        artist.slug = record.slug
        artist.artist_type = record.artist_type
        artist.publication_status = PublicationStatus.PUBLISHED
        artist.published_at = record.published_at
    Artist.objects.bulk_create(new_artists)
    if changed_artists:
        Artist.objects.bulk_update(changed_artists, ARTIST_FIELDS)

    artists_by_user = {
        artist.user_id: artist for artist in Artist.objects.filter(user_id__in=user_ids)
    }
    entries_by_artist = {
        entry.artist_id: entry
        for entry in CatalogEntry.objects.filter(
            artist_id__in=[artist.pk for artist in artists_by_user.values()]
        )
    }
    new_entries = []
    changed_entries = []
    for record in records:
        artist = artists_by_user[users_by_email[record.email].pk]
        values = {
            "slug": record.slug,
            "name": record.name,
            "artist_type": record.artist_type,
            "voivodeships": record.voivodeships,
            "age_groups": record.age_groups,
            "topics": record.topics,
            "forms": record.forms,
            "price_from": record.price_from,
            "offers": record.offers,
            "published_at": record.published_at,
            **record.search_terms,
        }
        entry = entries_by_artist.get(artist.pk)
        if entry is None:
            new_entries.append(CatalogEntry(artist=artist, **values))
        else:
            for field, value in values.items():
                setattr(entry, field, value)
            changed_entries.append(entry)
    CatalogEntry.objects.bulk_create(new_entries)
    if changed_entries:
        CatalogEntry.objects.bulk_update(changed_entries, ENTRY_FIELDS)


def create_fake_entries(count: int, seed: int = 0) -> int:
    """Create ``count`` synthetic published artists and catalog rows; return the count.

    Refuses with `FakeEntriesRefused` outside the dev and test settings, and with
    `FakeEntriesError` when the topic or form dictionary has no active entry.
    """
    if count < 0:
        raise ValueError("count must be zero or greater")
    reason = refusal_reason()
    if reason is not None:
        raise FakeEntriesRefused(reason)
    if not count:
        return 0

    topics = active_entries(EntryKind.TOPIC)
    forms = active_entries(EntryKind.FORM)
    if not topics or not forms:
        raise FakeEntriesError("The catalog dictionaries have no active topics or forms.")

    rng = random.Random(seed)  # noqa: S311 - deterministic test data, not a security token
    now = timezone.now()
    for start in range(0, count, BATCH_SIZE):
        numbers = range(start + 1, min(start + BATCH_SIZE, count) + 1)
        _insert([_record(rng, number, now, topics, forms) for number in numbers])
    return count


def delete_fake_entries() -> int:
    """Delete the synthetic users (and with them their artists and catalog rows); return the
    number of users removed. Only ``fake-*@example.invalid`` is touched, never a seed user."""
    users = get_user_model().objects.filter(
        email__startswith=EMAIL_PREFIX, email__endswith=f"@{EMAIL_DOMAIN}"
    )
    count = users.count()
    users.delete()
    return count
