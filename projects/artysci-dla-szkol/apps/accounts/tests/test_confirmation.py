"""US-1.1 parts of the accounts app: unconfirmed users, confirmation on first login, links
that lead to a page after logging in."""

from datetime import timedelta

import pytest
from django.contrib.auth import get_user_model
from django.db import IntegrityError

from apps.accounts import services
from apps.analytics.models import Event

from .conftest import EMAIL, IP, LINK_BASE, login_jobs

pytestmark = pytest.mark.django_db


def test_new_user_is_unconfirmed(db):
    user, created = services.get_or_create_unconfirmed_user(" New@Example.invalid ")
    assert created and user.email == "new@example.invalid"
    assert user.email_confirmed_at is None and not user.is_confirmed
    assert not user.has_usable_password()


def test_existing_user_is_returned_untouched(user):
    found, created = services.get_or_create_unconfirmed_user(EMAIL.upper())
    assert (found, created) == (user, False)


def test_concurrent_registration_returns_the_existing_user(user, monkeypatch):
    model = get_user_model()
    real_filter = model.objects.filter
    calls = []

    def first_miss(*args, **kwargs):  # the other request inserted between check and insert
        calls.append(1)
        return model.objects.none() if len(calls) == 1 else real_filter(*args, **kwargs)

    monkeypatch.setattr(model.objects, "filter", first_miss)

    def boom(**kwargs):
        raise IntegrityError("duplicate")

    monkeypatch.setattr(model.objects, "create_user", boom)
    found, created = services.get_or_create_unconfirmed_user(EMAIL)
    assert created is False and found.pk == user.pk


def test_confirm_email_only_once(user, clock):
    assert services.confirm_email(user) is True
    user.refresh_from_db()
    assert user.email_confirmed_at == clock.now
    clock.advance(days=1)
    assert services.confirm_email(user) is False
    user.refresh_from_db()
    assert user.email_confirmed_at == clock.now - timedelta(days=1)
    assert Event.objects.filter(name="account_confirmed").count() == 1


def test_code_login_confirms(user, clock):
    _, _, code = services.create_challenge(user)
    assert services.login_with_code(EMAIL, code) == user
    user.refresh_from_db()
    assert user.is_confirmed


def test_link_login_confirms(user, clock):
    _, token, _ = services.create_challenge(user)
    assert services.login_with_link(token) == user
    user.refresh_from_db()
    assert user.is_confirmed


def test_failed_login_does_not_confirm(user, clock):
    _, token, _ = services.create_challenge(user)
    clock.advance(minutes=16)
    assert services.login_with_link(token) is None
    user.refresh_from_db()
    assert not user.is_confirmed
    assert not Event.objects.filter(name="account_confirmed").exists()


@pytest.mark.parametrize(
    ("next_path", "expected"),
    [
        ("/artysta/kreator/", "&next=%2Fartysta%2Fkreator%2F"),
        ("", ""),
        ("https://evil.example/", ""),
        ("//evil.example/", ""),
    ],
)
def test_login_link_carries_only_local_next(next_path, expected):
    link = services.login_link(LINK_BASE, "tok", next_path)
    assert link == f"http://testserver/logowanie/link/?t=tok{expected}"


def test_request_login_passes_next_path_to_the_job(user, queue, clock):
    assert services.request_login(EMAIL, IP, link_base=LINK_BASE, next_path="/x/")
    (job,) = login_jobs(queue)
    assert job["args"]["next_path"] == "/x/"


def test_login_email_allowed_counts_nothing(user, queue, clock, settings):
    settings.LOGIN_EMAIL_LIMIT_PER_ADDRESS = 1
    for _ in range(3):
        assert services.login_email_allowed(EMAIL, IP)
    services.request_login(EMAIL, IP, link_base=LINK_BASE)
    assert not services.login_email_allowed(EMAIL, IP)
