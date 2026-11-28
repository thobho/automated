"""Synthetic catalog entries for load tests (T56a, #226): determinism, refusal, delete scope."""

import io
import os
import subprocess
import sys
from datetime import timedelta
from pathlib import Path

import pytest
from django.contrib.auth import get_user_model
from django.core.management import CommandError, call_command
from django.utils import timezone

from apps.artists.models import Artist, ArtistType, Audience, PublicationStatus
from apps.catalog import fake, listing
from apps.catalog.filters import Filters
from apps.catalog.models import CatalogEntry, DictionaryEntry
from apps.core.regions import Voivodeship

pytestmark = pytest.mark.django_db

PROJECT_ROOT = Path(__file__).resolve().parents[3]
URL = "/artysci/"


def rows() -> list[tuple]:
    return list(
        CatalogEntry.objects.order_by("slug").values_list("name", "voivodeships", "price_from")
    )


def test_same_seed_gives_the_same_rows_after_delete():
    assert fake.create_fake_entries(50, seed=1) == 50
    first = rows()
    assert len(first) == 50

    assert fake.delete_fake_entries() == 50
    assert fake.create_fake_entries(50, seed=1) == 50
    assert rows() == first


def test_rows_have_users_published_artists_and_valid_choices():
    assert fake.create_fake_entries(50, seed=1) == 50

    users = get_user_model().objects.filter(email__startswith="fake-")
    assert users.count() == 50
    assert users.filter(email__endswith="@example.invalid").count() == 50

    entry = CatalogEntry.objects.get(slug="syntetyczny-00001")
    assert entry.name == "Artysta Syntetyczny 00001"
    assert entry.artist.name == entry.name
    assert entry.artist.slug == entry.slug
    assert entry.artist.publication_status == PublicationStatus.PUBLISHED
    assert entry.artist_type in ArtistType.values
    assert 1 <= len(entry.voivodeships) <= 3
    assert set(entry.voivodeships) <= set(Voivodeship.values)
    assert 1 <= len(entry.age_groups) <= 3
    assert set(entry.age_groups) <= set(Audience.values)
    assert 1 <= len(entry.topics) <= 3
    assert 1 <= len(entry.forms) <= 3
    assert 1 <= len(entry.offers) <= 4
    for offer in entry.offers:
        assert offer["price"] is None or 200 <= offer["price"] <= 3000
        assert offer["duration"] is None or 30 <= offer["duration"] <= 120
    prices = [o["price"] for o in entry.offers if o["price"] is not None]
    assert entry.price_from == (min(prices) if prices else None)
    assert timezone.now() - timedelta(days=366) <= entry.published_at <= timezone.now()
    assert entry.search_name and entry.search_other and entry.search_fuzzy


def test_repeated_run_updates_the_same_rows_instead_of_failing():
    fake.create_fake_entries(3, seed=1)
    first = rows()
    assert fake.create_fake_entries(3, seed=1) == 3
    assert CatalogEntry.objects.count() == 3
    assert rows() == first


def test_list_and_search_find_a_fake_artist_by_an_offer_title_word(client):
    fake.create_fake_entries(5, seed=7)
    entry = CatalogEntry.objects.order_by("slug").first()

    assert client.get(URL).status_code == 200
    page = listing.cards_page(None, Filters(q="oferta"))
    assert page is not None
    assert entry.name in [card.name for card in page.cards]


def test_zero_count_does_nothing_and_negative_count_is_rejected():
    assert fake.create_fake_entries(0) == 0
    with pytest.raises(ValueError, match="zero or greater"):
        fake.create_fake_entries(-1)


def test_missing_dictionaries_are_reported():
    DictionaryEntry.objects.update(is_active=False)
    with pytest.raises(fake.FakeEntriesError, match="no active topics or forms"):
        fake.create_fake_entries(1)
    with pytest.raises(CommandError, match="no active topics or forms"):
        call_command("catalog_fake_entries", count=1, stdout=io.StringIO())


def test_delete_removes_only_fake_users():
    user_model = get_user_model()
    seed_user = user_model.objects.create_user(email="artysta01@example.invalid")
    seed_artist = Artist.objects.create(user=seed_user, name="Artysta Testowy 01")
    fake.create_fake_entries(3, seed=0)

    assert fake.delete_fake_entries() == 3
    assert not user_model.objects.filter(email__startswith="fake-").exists()
    assert user_model.objects.filter(pk=seed_user.pk).exists()
    assert Artist.objects.filter(pk=seed_artist.pk).exists()
    assert CatalogEntry.objects.count() == 0


def test_command_creates_with_count_and_seed_and_deletes_with_the_flag():
    output = io.StringIO()
    call_command("catalog_fake_entries", count=4, seed=5, stdout=output)
    assert CatalogEntry.objects.count() == 4
    assert "Created 4 fake catalog rows" in output.getvalue()

    output = io.StringIO()
    call_command("catalog_fake_entries", delete=True, stdout=output)
    assert CatalogEntry.objects.count() == 0
    assert "Removed 4 fake users" in output.getvalue()


def test_service_and_command_refuse_outside_debug_and_test_settings(monkeypatch, settings):
    settings.DEBUG = False
    monkeypatch.setenv("DJANGO_SETTINGS_MODULE", "config.settings.prod")

    with pytest.raises(fake.FakeEntriesRefused, match="refuses to run"):
        fake.create_fake_entries(3)

    error = io.StringIO()
    with pytest.raises(CommandError, match="refuses to run"):
        call_command("catalog_fake_entries", count=3, stdout=io.StringIO(), stderr=error)
    assert "refuses to run" in error.getvalue()
    assert CatalogEntry.objects.count() == 0
    assert not get_user_model().objects.filter(email__startswith="fake-").exists()


def test_command_refuses_with_real_prod_settings(tmp_path):
    environment = {
        **os.environ,
        "DJANGO_SETTINGS_MODULE": "config.settings.prod",
        "DJANGO_SECRET_KEY": "test-only-insecure-key",
        "DJANGO_ALLOWED_HOSTS": "testserver",
        "DATABASE_URL": f"sqlite:///{tmp_path / 'prod.sqlite3'}",
        "MEDIA_PUBLIC_BASE_URL": "https://media.example.invalid",
        "SITE_URL": "https://example.invalid",
    }
    result = subprocess.run(
        [sys.executable, "manage.py", "catalog_fake_entries", "--count", "1", "--skip-checks"],
        cwd=PROJECT_ROOT,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode != 0
    assert "refuses to run" in result.stderr
