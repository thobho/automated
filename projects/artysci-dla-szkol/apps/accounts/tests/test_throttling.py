import logging

import pytest
from django.core.cache import cache

from apps.accounts import throttling

EMAIL = "Artysta01@example.invalid"


@pytest.fixture(autouse=True)
def _clean_cache(settings):
    settings.LOGIN_THROTTLE_LIMIT = 3
    settings.LOGIN_THROTTLE_WINDOW = 60
    cache.clear()
    yield
    cache.clear()


def test_locks_after_limit():
    for _ in range(2):
        throttling.register_failure(EMAIL)
    assert not throttling.is_locked(EMAIL)
    throttling.register_failure(EMAIL)
    assert throttling.is_locked(EMAIL)


def test_keys_are_normalised():
    for _ in range(3):
        throttling.register_failure(f"  {EMAIL.upper()} ")
    assert throttling.is_locked(EMAIL.lower())


def test_any_locked_key_locks():
    for _ in range(3):
        throttling.register_failure("203.0.113.0")
    assert throttling.is_locked("someone@example.invalid", "203.0.113.0")
    assert not throttling.is_locked("someone@example.invalid")


def test_reset_clears_failures():
    for _ in range(3):
        throttling.register_failure(EMAIL)
    throttling.reset(EMAIL)
    assert throttling.failures(EMAIL) == 0
    assert not throttling.is_locked(EMAIL)


def test_empty_keys_are_ignored():
    throttling.register_failure("", EMAIL)
    assert throttling.failures(EMAIL) == 1
    assert not throttling.is_locked("")


def test_cache_never_holds_the_raw_identifier():
    throttling.register_failure(EMAIL)
    key = throttling._cache_key(EMAIL)
    assert EMAIL.lower() not in key and cache.get(key) == 1


def test_window_expiry_between_add_and_incr(monkeypatch):
    def incr(*args, **kwargs):
        raise ValueError

    monkeypatch.setattr(cache, "incr", incr)
    throttling.register_failure(EMAIL)
    assert throttling.failures(EMAIL) == 1


def test_lockout_is_logged_without_the_identifier(caplog):
    with caplog.at_level(logging.WARNING, logger="apps.accounts.throttling"):
        for _ in range(3):
            throttling.register_failure(EMAIL)
    (record,) = caplog.records
    assert record.event == "login_throttled"
    assert EMAIL.lower() not in caplog.text.lower()
