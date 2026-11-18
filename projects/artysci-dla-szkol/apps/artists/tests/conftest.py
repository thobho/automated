"""Fixtures for registration tests. The clock and the in-memory job queue are the login
tests' fixtures (same project, same login flow)."""

import pytest

from apps.accounts.tests.conftest import IP, clock, queue  # noqa: F401  (fixtures)
from apps.trust import services as trust

NEW_EMAIL = "nowy.artysta@example.invalid"
NAME = "Zespół Testowy Kwiatki"


@pytest.fixture
def documents(db):
    """Published v1 of the terms and the privacy policy."""
    return {
        "terms": trust.publish("terms", "Regulamin testowy", material=True),
        "privacy": trust.publish("privacy", "Polityka testowa", material=True),
    }


@pytest.fixture
def web(client):
    client.defaults["REMOTE_ADDR"] = IP
    return client


def jobs_for(connector, task_name="accounts.send_login_email") -> list[dict]:
    return [j for j in connector.jobs.values() if j["task_name"] == task_name]
