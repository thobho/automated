import pytest
from django.core.management import call_command
from django.db import connection


@pytest.mark.django_db(transaction=True)
def test_migrations_are_reversible():
    call_command("migrate", "quality", "zero", verbosity=0)
    tables = connection.introspection.table_names()
    assert "quality_generation" not in tables
    assert "profile_generation_id" not in [
        c.name for c in connection.introspection.get_table_description(
            connection.cursor(), "profiles_aicall"
        )
    ]  # fmt: skip
    call_command("migrate", verbosity=0)
    assert "quality_generation" in connection.introspection.table_names()
