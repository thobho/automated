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
