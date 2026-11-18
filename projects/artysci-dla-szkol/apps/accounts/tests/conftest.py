"""Fixtures for the login tests: a controllable clock, users, an in-memory job queue."""

import asyncio
from datetime import UTC, datetime, timedelta

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone
from procrastinate.contrib.django import app

from apps.core.testing import in_memory_queue

EMAIL = "artysta01@example.invalid"
INACTIVE_EMAIL = "nieaktywny@example.invalid"
UNKNOWN_EMAIL = "nikt@example.invalid"
IP = "203.0.113.7"
LINK_BASE = "http://testserver/"


class Clock:
    """Replaces django.utils.timezone.now (used by our services and by the session store)."""

    def __init__(self, start: datetime):
        self.now = start

    def __call__(self) -> datetime:
        return self.now

    def advance(self, **kwargs) -> datetime:
        self.now += timedelta(**kwargs)
        return self.now


@pytest.fixture
def clock(monkeypatch):
    fixed = Clock(datetime(2026, 11, 18, 10, 0, tzinfo=UTC))
    monkeypatch.setattr(timezone, "now", fixed)
    return fixed


@pytest.fixture
def user(db):
    return get_user_model().objects.create_user(email=EMAIL)


@pytest.fixture
def inactive_user(db):
    return get_user_model().objects.create_user(email=INACTIVE_EMAIL, is_active=False)


@pytest.fixture
def queue():
    with in_memory_queue() as connector:
        yield connector


def login_jobs(queue) -> list[dict]:
    return [j for j in queue.jobs.values() if j["task_name"] == "accounts.send_login_email"]


def run_worker() -> None:
    asyncio.run(app.run_worker_async(wait=False, install_signal_handlers=False))


# --- one account per role (US-1.5) -----------------------------------------------------------

ROLE_EMAILS = {
    "artist": "rola.artysta@example.invalid",
    "institution": "rola.placowka@example.invalid",
    "admin": "rola.admin@example.invalid",
}


def make_artist(email=ROLE_EMAILS["artist"]):
    from apps.artists.models import Artist

    user = get_user_model().objects.create_user(email=email)
    Artist.objects.create(user=user, name="Artysta Rola")
    return user


def make_institution_member(email=ROLE_EMAILS["institution"]):
    from apps.institutions.models import Institution, InstitutionMember

    user = get_user_model().objects.create_user(email=email)
    institution = Institution.objects.create(
        institution_type="primary_school",
        name="Szkoła Rola",
        locality="Wrocław",
        voivodeship="dolnoslaskie",
    )
    InstitutionMember.objects.create(user=user, institution=institution, function="teacher")
    return user


def make_admin(email=ROLE_EMAILS["admin"]):
    from apps.accounts import services

    return services.create_admin(email)[0]


def pytest_terminal_summary(terminalreporter):
    """Report how many routes the permission matrix covered (when its test ran)."""
    ran = [
        report
        for report in terminalreporter.stats.get("passed", [])
        + terminalreporter.stats.get("failed", [])
        if "test_permission_matrix.py::test_permission_matrix[" in report.nodeid
    ]
    if ran:
        from .test_permission_matrix import EXCLUDED, MATRIX, ROLES

        terminalreporter.write_line(
            f"permission matrix: {len(ran)} of {len(MATRIX)} routes checked for "
            f"{len(ROLES)} roles ({', '.join(ROLES)}); {len(EXCLUDED)} excluded by name"
        )


@pytest.fixture
def legal_documents(db):
    """Published terms, privacy policy and cookie notice (every legal page answers 200)."""
    from apps.trust import services as trust

    return [
        trust.publish(kind, f"Tekst testowy {kind}", material=True)
        for kind in ("terms", "privacy", "cookies")
    ]


@pytest.fixture
def role_users(legal_documents):
    """{role: user} for artist, institution and admin; each accepted the current documents."""
    from apps.trust import services as trust

    users = {
        "artist": make_artist(),
        "institution": make_institution_member(),
        "admin": make_admin(),
    }
    for user in users.values():
        trust.record_acceptance(user, ["terms", "privacy"])
    return users


@pytest.fixture
def role_clients(role_users):
    """{role: Client} logged in as each role, plus an anonymous client."""
    from django.test import Client

    clients = {"anonymous": Client()}
    for role, user in role_users.items():
        clients[role] = Client()
        clients[role].force_login(user)
    return clients
