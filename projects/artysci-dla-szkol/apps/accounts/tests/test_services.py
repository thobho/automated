import re

import pytest
from django.core import mail

from apps.accounts import services, throttling
from apps.accounts.models import LoginChallenge

from .conftest import EMAIL, INACTIVE_EMAIL, IP, LINK_BASE, UNKNOWN_EMAIL, login_jobs, run_worker

pytestmark = pytest.mark.django_db


def issue(user, clock=None):
    """Create a challenge as the e-mail job would; returns (token, code)."""
    _, token, code = services.create_challenge(user)
    return token, code


# --- request_login ---------------------------------------------------------------------------


def test_request_for_active_user_queues_one_email_job(user, queue, clock):
    assert services.request_login(EMAIL, IP, link_base=LINK_BASE) is True
    (job,) = login_jobs(queue)
    assert job["queue_name"] == "email"
    # no code, no token
    assert job["args"] == {"user_id": user.pk, "link_base": LINK_BASE, "next_path": ""}


@pytest.mark.parametrize("email", [UNKNOWN_EMAIL, INACTIVE_EMAIL])
def test_request_for_unknown_or_inactive_sends_nothing(email, inactive_user, queue, clock):
    from django.contrib.auth import get_user_model

    before = get_user_model().objects.count()
    assert services.request_login(email, IP, link_base=LINK_BASE) is True
    assert login_jobs(queue) == []
    assert get_user_model().objects.count() == before  # no account is created


def test_sixth_request_per_address_within_an_hour_is_not_queued(user, queue, clock):
    for i in range(5):
        assert services.request_login(EMAIL, f"198.51.100.{i}", link_base=LINK_BASE)
        queue.jobs.clear()  # as if the worker sent it; frees the idempotency lock
    assert services.request_login(EMAIL, "198.51.100.99", link_base=LINK_BASE) is False
    assert login_jobs(queue) == []
    clock.advance(hours=1)
    assert services.request_login(EMAIL, "198.51.100.99", link_base=LINK_BASE) is True


def test_21st_request_per_ip_within_an_hour_is_not_queued(user, queue, clock):
    for i in range(19):
        assert services.request_login(f"x{i}@example.invalid", IP, link_base=LINK_BASE)
    assert services.request_login(EMAIL, IP, link_base=LINK_BASE) is True  # 20th
    assert len(login_jobs(queue)) == 1
    queue.jobs.clear()
    assert services.request_login(EMAIL, IP, link_base=LINK_BASE) is False  # 21st
    assert login_jobs(queue) == []


def test_limits_count_unknown_addresses_too(queue, clock, db):
    """Known and unknown addresses hit the limit at the same request (no enumeration)."""
    results = [services.request_login(UNKNOWN_EMAIL, IP, link_base=LINK_BASE) for _ in range(6)]
    assert results == [True] * 5 + [False]


# --- the e-mail job --------------------------------------------------------------------------


def test_send_login_email_contains_link_and_code(user, clock):
    assert services.send_login_email(user.pk, LINK_BASE) is True
    (message,) = mail.outbox
    assert message.to == [EMAIL]
    assert message.subject == "Logowanie do serwisu Artyści dla szkół"
    link = re.search(r"http://testserver/logowanie/link/\?t=(\S+)", message.body)
    code = re.search(r"^(\d{6})$", message.body, re.M)
    assert link and code
    assert "15 minut" in message.body
    # Only hashes are stored.
    challenge = LoginChallenge.objects.get()
    assert link.group(1) not in (challenge.token_hash, challenge.code_hash)
    assert code.group(1) not in challenge.code_hash


def test_send_login_email_for_inactive_user_sends_nothing(inactive_user, clock):
    assert services.send_login_email(inactive_user.pk, LINK_BASE) is False
    assert mail.outbox == []


@pytest.mark.django_db(transaction=True)
def test_worker_runs_the_email_job(user, queue, clock):
    services.request_login(EMAIL, IP, link_base=LINK_BASE)
    run_worker()
    assert len(mail.outbox) == 1
    assert [j["status"] for j in login_jobs(queue)] == ["succeeded"]


def test_new_challenge_closes_the_previous_one(user, clock):
    old_token, old_code = issue(user)
    new_token, new_code = issue(user)
    assert services.login_with_link(old_token) is None
    assert services.login_with_code(EMAIL, new_code) == user


def test_codes_are_six_digits_and_random(user, clock):
    codes = {issue(user)[1] for _ in range(20)}
    assert all(len(c) == 6 and c.isdigit() for c in codes)
    assert len(codes) > 1


# --- login_with_code / login_with_link -------------------------------------------------------


def test_code_logs_in_once_then_link_is_refused(user, clock):
    token, code = issue(user)
    clock.advance(minutes=14)
    assert services.login_with_code(EMAIL.upper(), code) == user
    assert services.login_with_link(token) is None
    assert services.login_with_code(EMAIL, code) is None


def test_link_logs_in_once_then_code_is_refused(user, clock):
    token, code = issue(user)
    assert services.check_link(token) is True
    assert services.login_with_link(token) == user
    assert services.check_link(token) is False
    assert services.login_with_code(EMAIL, code) is None


def test_challenge_expires_after_15_minutes(user, clock):
    token, code = issue(user)
    clock.advance(minutes=15)
    assert services.check_link(token) is False
    assert services.login_with_link(token) is None
    assert services.login_with_code(EMAIL, code) is None


@pytest.mark.parametrize("bad", ["", "12345", "abcdef", "1234567"])
def test_malformed_codes_fail(user, clock, bad):
    issue(user)
    assert services.login_with_code(EMAIL, bad) is None


def test_unknown_link_token_fails(db, clock):
    assert services.check_link("") is False
    assert services.login_with_link("nope") is None


def test_five_wrong_codes_lock_code_login_for_15_minutes(user, clock):
    _, code = issue(user)
    wrong = "000000" if code != "000000" else "111111"
    for _ in range(5):
        assert services.login_with_code(EMAIL, wrong) is None
    assert services.login_with_code(EMAIL, code) is None  # correct, but locked
    clock.advance(minutes=15)
    _, fresh = issue(user)
    assert services.login_with_code(EMAIL, fresh) == user


def test_success_resets_the_failure_count(user, clock):
    _, code = issue(user)
    for _ in range(4):
        services.login_with_code(EMAIL, "999999" if code != "999999" else "888888")
    assert services.login_with_code(EMAIL, code) == user
    assert throttling.count(throttling.CODE, EMAIL) == 0


def test_unknown_email_failures_count_the_same(db, clock):
    for _ in range(5):
        assert services.login_with_code(UNKNOWN_EMAIL, "123456") is None
    assert throttling.exceeded(throttling.CODE, UNKNOWN_EMAIL)


def test_inactive_user_cannot_log_in(user, clock):
    token, code = issue(user)
    user.is_active = False
    user.save()
    assert services.check_link(token) is False
    assert services.login_with_link(token) is None
    assert services.login_with_code(EMAIL, code) is None


def test_consume_is_single_use_under_a_race(user, clock):
    challenge, token, _ = services.create_challenge(user)
    LoginChallenge.objects.filter(pk=challenge.pk).update(consumed_at=clock.now)
    assert services._consume(challenge, clock.now) is False


# --- housekeeping ----------------------------------------------------------------------------


def test_purge_expired(user, clock):
    from django.contrib.sessions.backends.db import SessionStore

    issue(user)
    session = SessionStore()
    session["x"] = 1
    session.create()
    throttling.hit(throttling.CODE, EMAIL)
    clock.advance(days=31)
    assert services.purge_expired() == {"challenges": 1, "throttle_events": 1, "sessions": 1}
