from datetime import timedelta

import pytest
from django.db import connection, connections

from apps.accounts import throttling
from apps.accounts.models import ThrottleEvent

from .conftest import EMAIL

pytestmark = pytest.mark.django_db


def test_limit_reached_after_n_hits(clock):
    for _ in range(4):
        throttling.hit(throttling.CODE, EMAIL)
    assert not throttling.exceeded(throttling.CODE, EMAIL)
    assert throttling.hit(throttling.CODE, EMAIL) == 5
    assert throttling.exceeded(throttling.CODE, EMAIL)


def test_sliding_window_forgets_old_events(clock):
    for _ in range(5):
        throttling.hit(throttling.CODE, EMAIL)
    clock.advance(seconds=899)
    assert throttling.exceeded(throttling.CODE, EMAIL)
    clock.advance(seconds=1)
    assert not throttling.exceeded(throttling.CODE, EMAIL)


def test_explicit_now_argument(clock):
    then = clock.now - timedelta(hours=2)
    throttling.hit(throttling.EMAIL_PER_ADDRESS, EMAIL, now=then)
    assert throttling.count(throttling.EMAIL_PER_ADDRESS, EMAIL, now=then) == 1
    assert throttling.count(throttling.EMAIL_PER_ADDRESS, EMAIL) == 0


def test_keys_are_normalised_and_scoped(clock):
    throttling.hit(throttling.CODE, f"  {EMAIL.upper()} ")
    assert throttling.count(throttling.CODE, EMAIL) == 1
    assert throttling.count(throttling.EMAIL_PER_ADDRESS, EMAIL) == 0


def test_reset_clears_one_key(clock):
    throttling.hit(throttling.CODE, EMAIL)
    throttling.hit(throttling.CODE, "other@example.invalid")
    throttling.reset(throttling.CODE, EMAIL)
    assert throttling.count(throttling.CODE, EMAIL) == 0
    assert throttling.count(throttling.CODE, "other@example.invalid") == 1


def test_database_never_holds_the_raw_identifier(clock):
    throttling.hit(throttling.CODE, EMAIL)
    (event,) = ThrottleEvent.objects.all()
    assert EMAIL not in event.key_hash
    assert event.key_hash == throttling.key_hash(throttling.CODE, EMAIL)
    assert event.key_hash != throttling.key_hash(throttling.EMAIL_PER_ADDRESS, EMAIL)


def test_purge_drops_events_older_than_longest_window(clock):
    throttling.hit(throttling.EMAIL_PER_IP, "203.0.113.7")
    clock.advance(minutes=59)
    throttling.hit(throttling.EMAIL_PER_IP, "203.0.113.7")
    clock.advance(minutes=1)
    assert throttling.purge() == 1
    assert ThrottleEvent.objects.count() == 1


def test_unknown_scope_is_an_error():
    with pytest.raises(ValueError):
        throttling.limit_for("nope")


@pytest.mark.parametrize(
    ("addr", "key"),
    [
        ("203.0.113.7", "203.0.113.7"),
        ("2001:db8:1:2:3:4:5:6", "2001:db8:1:2::"),
        ("", "invalid"),
        ("garbage", "invalid"),
    ],
)
def test_ip_identifier(addr, key):
    assert throttling.ip_identifier(addr) == key


@pytest.mark.skipif(connection.vendor != "postgresql", reason="needs PostgreSQL")
@pytest.mark.django_db(transaction=True)
def test_counters_are_shared_between_database_connections(clock):
    """Two connections stand in for two gunicorn workers: each sees the other's events."""
    other = connections.create_connection("default")
    try:
        for _ in range(5):
            throttling.hit(throttling.CODE, EMAIL)  # "worker A"
        with other.cursor() as cursor:  # "worker B" reads A's failures
            cursor.execute(
                "SELECT count(*) FROM accounts_throttleevent WHERE scope = %s AND key_hash = %s",
                [throttling.CODE, throttling.key_hash(throttling.CODE, EMAIL)],
            )
            assert cursor.fetchone()[0] == 5
            for _ in range(5):  # B records five login e-mails ...
                cursor.execute(
                    "INSERT INTO accounts_throttleevent (scope, key_hash, created_at) "
                    "VALUES (%s, %s, %s)",
                    [
                        throttling.EMAIL_PER_ADDRESS,
                        throttling.key_hash(throttling.EMAIL_PER_ADDRESS, EMAIL),
                        clock.now,
                    ],
                )
        # (Django connections autocommit, so B's rows are visible now) ... and A refuses the sixth.
        assert throttling.exceeded(throttling.EMAIL_PER_ADDRESS, EMAIL)
    finally:
        other.close()
