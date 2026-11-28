"""The PostgreSQL side of the catalog search (skipped on SQLite; CI sets DATABASE_URL)."""

import pytest
from django.db import connection

from apps.catalog.models import CatalogEntry

pytestmark = [
    pytest.mark.skipif(connection.vendor != "postgresql", reason="needs PostgreSQL"),
    pytest.mark.django_db,
]


def test_trigram_extension_and_indexes_exist():
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1 FROM pg_extension WHERE extname = 'pg_trgm'")
        assert cursor.fetchone() is not None
        cursor.execute(
            "SELECT indexname FROM pg_indexes WHERE tablename = 'catalog_catalogentry' "
            "AND indexname LIKE 'catalog_entry_search_%_trgm'"
        )
        assert {row[0] for row in cursor.fetchall()} == {
            "catalog_entry_search_name_trgm",
            "catalog_entry_search_other_trgm",
            "catalog_entry_search_fuzzy_trgm",
        }


def test_word_lookup_can_use_the_index():
    with connection.cursor() as cursor:
        cursor.execute("SET LOCAL enable_seqscan = off")
        plan = str(CatalogEntry.objects.filter(search_name__contains=" hejt ").explain())
    assert "catalog_entry_search_name_trgm" in plan
