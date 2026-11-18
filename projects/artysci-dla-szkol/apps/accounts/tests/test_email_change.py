"""Account settings and e-mail change (US-1.6): services."""

import re

import pytest
from django.contrib.auth import get_user_model
from django.core import mail

from apps.accounts import services, throttling
from apps.accounts.models import EmailChangeRequest, LoginChallenge

from .conftest import EMAIL, IP, LINK_BASE, login_jobs, make_artist

pytestmark = pytest.mark.django_db

NEW = "nowy.adres@example.invalid"
OTHER = "zajety@example.invalid"
CHANGE_TASKS = ("accounts.send_email_change_email", "accounts.send_email_change_notice")


def change_jobs(queue) -> list[dict]:
    return [j for j in queue.jobs.values() if j["task_name"] in CHANGE_TASKS]


def deliver(queue) -> None:
    """Run the queued e-mail change jobs synchronously (same bodies the worker calls)."""
    for job in change_jobs(queue):
        args = job["args"]
        if job["task_name"] == "accounts.send_email_change_email":
            services.send_email_change_email(args["change_id"], args["link_base"])
        else:
            services.send_email_change_notice(args["user_id"])
        del queue.jobs[job["id"]]


def mails_to(address: str) -> list:
    return [m for m in mail.outbox if m.to == [address]]


def request(user, address=NEW, ip=IP) -> bool:
    return services.request_email_change(user, address, ip, link_base=LINK_BASE)


def code_and_token(message) -> tuple[str, str]:
    code = re.search(r"^(\d{6})$", message.body, re.M).group(1)
    token = re.search(r"\?t=(\S+)", message.body).group(1)
    return code, token


def requested(user, queue, address=NEW) -> tuple[str, str]:
    """Request a change, deliver the e-mails; returns (code, token) from the new address."""
    assert request(user, address)
    deliver(queue)
    return code_and_token(mails_to(address)[-1])


def reload(user):
    return get_user_model().objects.get(pk=user.pk)


@pytest.fixture
def other(db):
    return get_user_model().objects.create_user(email=OTHER)


# --- names -----------------------------------------------------------------------------------


def test_update_names_for_an_artist():
    user = make_artist()
    services.update_names(user, full_name="  Anna Nowak ", artist_name=" Teatr Anny ")
    overview = services.account_overview(reload(user))
    assert overview["full_name"] == "Anna Nowak"
    assert overview["artist_name"] == "Teatr Anny"
    assert overview["is_artist"] is True


def test_update_names_without_artist_record_ignores_artist_name(user):
    services.update_names(user, full_name="Jan", artist_name="Nie dotyczy")
    overview = services.account_overview(reload(user))
    assert overview == {
        "email": EMAIL,
        "full_name": "Jan",
        "is_artist": False,
        "artist_name": "",
        "change_pending": False,
    }


def test_rename_artist_refuses_blank_and_non_artists(user):
    from apps.artists import services as artists

    assert artists.rename_artist(user, "X") is False
    artist_user = make_artist()
    assert artists.rename_artist(artist_user, "   ") is False
    assert artists.artist_for(artist_user).name == "Artysta Rola"


# --- request ---------------------------------------------------------------------------------


def test_free_address_gets_link_and_code_old_address_gets_a_notice(user, queue, clock):
    assert request(user)
    assert [j["task_name"] for j in change_jobs(queue)] == ["accounts.send_email_change_email"]
    assert set(change_jobs(queue)[0]["args"]) == {"change_id", "link_base"}  # no address
    deliver(queue)

    [new_mail] = mails_to(NEW)
    code, token = code_and_token(new_mail)
    assert f"/konto/email/link/?t={token}" in new_mail.body
    [notice] = mails_to(EMAIL)
    assert "http" not in notice.body and not re.search(r"\d{6}", notice.body)
    assert len(mail.outbox) == 2
    assert reload(user).email == EMAIL
    assert services.account_overview(user)["change_pending"] is True


def test_only_hashes_are_stored(user, queue, clock):
    code, token = requested(user, queue)
    change = EmailChangeRequest.objects.get()
    stored = " ".join([change.token_hash, change.code_hash, change.code_salt])
    assert code not in stored and token not in stored


@pytest.mark.parametrize("address", [OTHER, OTHER.upper(), EMAIL])
def test_taken_address_gets_nothing_and_nothing_changes(user, other, queue, clock, address):
    assert request(user, address)
    deliver(queue)
    assert mails_to(OTHER) == []
    assert [m.to for m in mail.outbox] == [[EMAIL]]  # only the notice
    assert not EmailChangeRequest.objects.exists()
    assert reload(user).email == EMAIL and reload(other).email == OTHER


def test_sixth_request_within_an_hour_queues_nothing(user, queue, clock):
    for number in range(5):
        assert request(user, f"n{number}@example.invalid", ip=f"198.51.100.{number}")
    queue.jobs.clear()
    assert request(user, "n6@example.invalid", ip="192.0.2.1") is False
    assert change_jobs(queue) == []
    clock.advance(hours=1, seconds=1)
    assert request(user, "n7@example.invalid")


def test_per_ip_limit_is_shared_with_login(user, queue, clock):
    for _ in range(20):
        throttling.hit(throttling.EMAIL_PER_IP, IP)
    assert request(user) is False
    assert change_jobs(queue) == []


def test_newer_request_replaces_the_older_one(user, queue, clock):
    old_code, old_token = requested(user, queue, "pierwszy@example.invalid")
    new_code, _ = requested(user, queue, "drugi@example.invalid")
    assert services.check_email_change_link(user, old_token) is False
    if old_code != new_code:
        assert services.confirm_email_change_code(user, old_code) is False
    assert services.confirm_email_change_code(user, new_code) is True
    assert reload(user).email == "drugi@example.invalid"


def test_replaced_request_job_sends_nothing(user, queue, clock):
    request(user, "pierwszy@example.invalid")
    request(user, "drugi@example.invalid")
    first = EmailChangeRequest.objects.order_by("created_at", "pk").first()
    assert services.send_email_change_email(first.pk, LINK_BASE) is False
    assert mail.outbox == []


def test_jobs_for_inactive_or_missing_users_send_nothing(user, queue, clock):
    request(user)
    get_user_model().objects.filter(pk=user.pk).update(is_active=False)
    assert services.send_email_change_email(EmailChangeRequest.objects.get().pk, LINK_BASE) is False
    assert services.send_email_change_notice(user.pk) is False
    assert mail.outbox == []


# --- confirmation ----------------------------------------------------------------------------


def test_code_within_15_minutes_changes_the_address(user, queue, clock):
    code, _ = requested(user, queue)
    clock.advance(minutes=14, seconds=59)
    assert services.confirm_email_change_code(user, code) is True
    stored = reload(user)
    assert stored.email == NEW
    assert stored.email_confirmed_at == clock.now
    assert services.account_overview(stored)["change_pending"] is False


def test_code_after_15_minutes_is_refused(user, queue, clock):
    code, token = requested(user, queue)
    clock.advance(minutes=15)
    assert services.confirm_email_change_code(user, code) is False
    assert services.confirm_email_change_link(user, token) is False
    assert reload(user).email == EMAIL


def test_code_is_single_use(user, queue, clock):
    code, token = requested(user, queue)
    assert services.confirm_email_change_code(user, code)
    assert services.confirm_email_change_code(user, code) is False
    assert services.confirm_email_change_link(user, token) is False


def test_link_of_another_user_is_refused_and_stays_usable(user, other, queue, clock):
    _, token = requested(user, queue)
    assert services.check_email_change_link(other, token) is False
    assert services.confirm_email_change_link(other, token) is False
    assert reload(user).email == EMAIL and reload(other).email == OTHER
    assert services.confirm_email_change_link(user, token) is True
    assert reload(user).email == NEW


def test_code_of_another_users_request_does_not_work(user, other, queue, clock):
    code, _ = requested(user, queue)
    assert services.confirm_email_change_code(other, code) is False
    assert reload(other).email == OTHER


def test_wrong_codes_lock_code_entry(user, queue, clock):
    code, token = requested(user, queue)
    wrong = "000000" if code != "000000" else "111111"
    for _ in range(5):
        assert services.confirm_email_change_code(user, wrong) is False
    assert services.confirm_email_change_code(user, code) is False
    assert reload(user).email == EMAIL
    assert services.confirm_email_change_link(user, token) is True  # the link still works


def test_bad_code_formats_are_refused(user, queue, clock):
    requested(user, queue)
    for bad in ("", "abc", "1234567", None):
        assert services.confirm_email_change_code(user, bad) is False


def test_address_taken_meanwhile_is_refused(user, queue, clock):
    code, _ = requested(user, queue)
    get_user_model().objects.create_user(email=NEW)
    assert services.confirm_email_change_code(user, code) is False
    assert reload(user).email == EMAIL


def test_confirmation_closes_open_login_challenges(user, queue, clock):
    _, login_token, _ = services.create_challenge(user)
    code, _ = requested(user, queue)
    assert services.confirm_email_change_code(user, code)
    assert services.check_link(login_token) is False
    assert not LoginChallenge.objects.filter(consumed_at__isnull=True).exists()


def test_pending_change_does_not_affect_login(user, queue, clock):
    requested(user, queue)
    queue.jobs.clear()
    assert services.request_login(NEW, IP, link_base=LINK_BASE) is True  # neutral answer
    assert login_jobs(queue) == []  # no account for the new address
    assert services.request_login(EMAIL, IP, link_base=LINK_BASE) is True
    assert len(login_jobs(queue)) == 1
    _, _, login_code = services.create_challenge(user)
    assert services.login_with_code(EMAIL, login_code) == user


def test_link_and_check_refuse_garbage(user, queue, clock):
    requested(user, queue)
    assert services.check_email_change_link(user, "") is False
    assert services.confirm_email_change_link(user, "nie-ma-takiego") is False


def test_session_hash_follows_the_email(user):
    before = user.get_session_auth_hash()
    user.email = NEW
    assert user.get_session_auth_hash() != before
