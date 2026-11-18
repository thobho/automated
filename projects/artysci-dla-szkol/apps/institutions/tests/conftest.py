"""Fixtures for institution registration tests: the login tests' clock and job queue, and the
registration tests' published documents and client (same project, same flow)."""

import pytest

from apps.accounts.tests.conftest import IP, clock, queue  # noqa: F401  (fixtures)
from apps.artists.tests.conftest import documents, jobs_for, web  # noqa: F401  (fixtures)
from apps.institutions import services

NEW_EMAIL = "dyrektor.nowy@example.invalid"
TYPED_NAME = "Szkoła Wpisana Ręcznie Testowa"

WROCLAW = 900001
OPOLE = 900002


@pytest.fixture
def staff_client(documents, admin_user):  # noqa: F811  (`documents` is the imported fixture)
    """A superuser who accepted the current documents (so the acceptance gate stays away)."""
    from django.test import Client

    from apps.trust import services as trust

    trust.record_acceptance(admin_user, ["terms", "privacy"])
    client = Client()
    client.force_login(admin_user)
    return client


@pytest.fixture
def rspo(db):
    """Two "Szkoła Podstawowa nr 5" rows, in Wrocław and in Opole, plus one in Łódź."""
    rows = [
        (WROCLAW, "Szkoła Podstawowa nr 5", "primary_school", "Wrocław", "dolnoslaskie"),
        (OPOLE, "Szkoła Podstawowa nr 5", "primary_school", "Opole", "opolskie"),
        (900003, "Przedszkole nr 12 Słoneczko", "kindergarten", "Łódź", "lodzkie"),
    ]
    return {row[0]: services.add_rspo_entry(*row)[0] for row in rows}
