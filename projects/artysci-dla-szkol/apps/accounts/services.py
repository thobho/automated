"""Account services: e-mail login (US-1.3, D1), account settings and e-mail change (US-1.6)
and synthetic seed users.

Login flow: `request_login()` (rate-limited, silent for unknown or inactive addresses) queues
`send_login_email()` on the `email` queue; that job creates the challenge, so the raw link
token and code exist only in the e-mail and never in the jobs table. The user then calls
`login_with_code()` or `login_with_link()`; either one consumes the challenge, confirms the
address on first use (`confirm_email()`, US-1.1), and the view starts the session with
`start_session()`.

E-mail change: `request_email_change()` (rate-limited, same answer for free and taken
addresses) stores the new address; the `send_email_change_email()` job creates the link token
and code like a login challenge and mails them to the new address, plus a notice to the old
one. `confirm_email_change_code()` / `confirm_email_change_link()` apply it for the same
logged-in user only.

Auth events are logged with a pseudonymised user only: never an e-mail, IP, code or token.
"""

import hashlib
import logging
import secrets
from datetime import datetime, timedelta
from urllib.parse import urlencode

from django.conf import settings
from django.contrib import auth
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.db import IntegrityError, transaction
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from django.utils.crypto import constant_time_compare, salted_hmac
from django.utils.translation import gettext

from apps.core import jobs
from apps.core.logs import pseudonymise_user

from . import signals, throttling
from .managers import normalize_email_address
from .models import EmailChangeRequest, LoginChallenge

logger = logging.getLogger("apps.accounts.auth")

SEED_DOMAIN = "example.invalid"
ARTIST_COUNT = 10
INSTITUTION_COUNT = 5

CODE_DIGITS = 6


# --- helpers ---------------------------------------------------------------------------------


def _now(now: datetime | None) -> datetime:
    return now or timezone.now()


def _log(message: str, event: str, user=None, level: int = logging.INFO) -> None:
    extra = {"event": event}
    if user is not None:
        extra["user"] = pseudonymise_user(user.pk)
    logger.log(level, message, extra=extra)


def _active_user(email: str):
    user_model = get_user_model()
    return user_model.objects.filter(email=email, is_active=True).first()


def _token_hash(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def _code_hash(salt: str, code: str) -> str:
    return salted_hmac("accounts.login_code", f"{salt}:{code}").hexdigest()


# --- login -----------------------------------------------------------------------------------


def login_email_allowed(email: str, client_ip: str, *, now=None) -> bool:
    """True if a login e-mail for this address from this IP is within the sending limits.
    Counts nothing (registration checks this before it creates an account)."""
    now = _now(now)
    email = normalize_email_address(email)
    ip_key = throttling.ip_identifier(client_ip)
    return not (
        throttling.exceeded(throttling.EMAIL_PER_ADDRESS, email, now=now)
        or throttling.exceeded(throttling.EMAIL_PER_IP, ip_key, now=now)
    )


def request_login(
    email: str, client_ip: str, *, link_base: str, next_path: str = "", now=None
) -> bool:
    """Ask for a login e-mail. Returns False only when a sending limit is reached.

    The result is the same for known, unknown and inactive addresses (no enumeration): the
    limits count every request, and only an active user gets an e-mail. `link_base` is the
    site origin the link points to (e.g. ``https://host/``); `next_path` is an optional local
    path the link leads to after logging in (registration sends the wizard start).
    """
    now = _now(now)
    email = normalize_email_address(email)
    if not login_email_allowed(email, client_ip, now=now):
        _log("login e-mail rate limited", "login_rate_limited", level=logging.WARNING)
        return False
    throttling.hit(throttling.EMAIL_PER_ADDRESS, email, now=now)
    throttling.hit(throttling.EMAIL_PER_IP, throttling.ip_identifier(client_ip), now=now)

    user = _active_user(email)
    _log("login requested", "login_requested", user)
    if user is not None:
        from . import tasks  # tasks import this module

        jobs.enqueue(
            tasks.send_login_email,
            idempotency_key=f"accounts.login_email:{user.pk}",
            user_id=user.pk,
            link_base=link_base,
            next_path=next_path,
        )
    return True


def get_or_create_unconfirmed_user(email: str) -> tuple:
    """(user, created) for a registration. A new user has no password and stays
    "niepotwierdzone" (`email_confirmed_at` is None) until a link or code login. An existing
    user (any state) is returned untouched."""
    user_model = get_user_model()
    email = normalize_email_address(email)
    existing = user_model.objects.filter(email=email).first()
    if existing is not None:
        return existing, False
    try:
        with transaction.atomic():
            return user_model.objects.create_user(email=email), True
    except IntegrityError:  # the same address registered concurrently
        return user_model.objects.get(email=email), False


def confirm_email(user, *, now=None) -> bool:
    """Mark the address confirmed: the user just proved access to the mailbox. True only the
    first time (then `account_confirmed` is recorded); later logins change nothing."""
    from apps.analytics import services as analytics

    now = _now(now)
    updated = (
        get_user_model()
        .objects.filter(pk=user.pk, email_confirmed_at__isnull=True)
        .update(email_confirmed_at=now)
    )
    if not updated:
        return False
    user.email_confirmed_at = now
    analytics.track("account_confirmed", actor=user, obj=user)
    _log("account confirmed", "account_confirmed", user)
    signals.email_confirmed.send(sender=type(user), user=user)
    return True


def create_challenge(user, *, now=None) -> tuple[LoginChallenge, str, str]:
    """New challenge for `user`; earlier open challenges are closed (only the newest e-mail
    works). Returns (challenge, raw token, raw code); the raw values are never stored."""
    now = _now(now)
    LoginChallenge.objects.filter(user=user, consumed_at__isnull=True).update(consumed_at=now)
    token = secrets.token_urlsafe(32)
    code = f"{secrets.randbelow(10**CODE_DIGITS):0{CODE_DIGITS}d}"
    salt = secrets.token_hex(16)
    challenge = LoginChallenge.objects.create(
        user=user,
        token_hash=_token_hash(token),
        code_salt=salt,
        code_hash=_code_hash(salt, code),
        created_at=now,
        expires_at=now + timedelta(seconds=settings.LOGIN_CHALLENGE_TTL),
    )
    return challenge, token, code


def login_link(link_base: str, token: str, next_path: str = "") -> str:
    """Absolute link for the e-mail. The token is only ever in the query string (SECURITY.md).
    `next_path` must be a local path (``/...``); anything else is dropped."""
    query = {"t": token}
    if next_path.startswith("/") and not next_path.startswith("//"):
        query["next"] = next_path
    return f"{link_base.rstrip('/')}{reverse('accounts:login_link')}?{urlencode(query)}"


def send_login_email(user_id: int, link_base: str, next_path: str = "", *, now=None) -> bool:
    """Job body: create a challenge and e-mail its link and code. False if the user is gone
    or inactive (nothing is sent)."""
    user = get_user_model().objects.filter(pk=user_id, is_active=True).first()
    if user is None:
        return False
    _, token, code = create_challenge(user, now=now)
    minutes = settings.LOGIN_CHALLENGE_TTL // 60
    body = render_to_string(
        "accounts/email/login.txt",
        {"link": login_link(link_base, token, next_path), "code": code, "minutes": minutes},
    )
    send_mail(gettext("Logowanie do serwisu Artyści dla szkół"), body, None, [user.email])
    _log("login e-mail sent", "login_email_sent", user)
    return True


def _consume(challenge: LoginChallenge, now: datetime) -> bool:
    """Mark used; False if another request consumed it first (single use across workers)."""
    return (
        LoginChallenge.objects.filter(pk=challenge.pk, consumed_at__isnull=True).update(
            consumed_at=now
        )
        == 1
    )


def login_with_code(email: str, code: str, *, now=None):
    """The user for a correct, unexpired code, else None (one generic failure for every reason).

    After LOGIN_THROTTLE_LIMIT failures for one e-mail within the window, code login for that
    e-mail is locked and even a correct code is refused.
    """
    now = _now(now)
    email = normalize_email_address(email)
    code = (code or "").strip()
    if throttling.exceeded(throttling.CODE, email, now=now):
        _log("login refused, code login locked", "login_locked", level=logging.WARNING)
        return None

    user = _active_user(email)
    challenge = None
    if user is not None:
        challenge = (
            LoginChallenge.objects.filter(user=user, consumed_at__isnull=True, expires_at__gt=now)
            .order_by("-created_at")
            .first()
        )
    salt = challenge.code_salt if challenge else "-"
    expected = challenge.code_hash if challenge else ""
    matches = constant_time_compare(_code_hash(salt, code), expected)
    if not (matches and code.isdigit() and len(code) == CODE_DIGITS):
        failures = throttling.hit(throttling.CODE, email, now=now)
        _log("login code failed", "login_code_failed", user, level=logging.WARNING)
        if failures >= throttling.limit_for(throttling.CODE).limit:
            _log("code login locked", "login_locked", user, level=logging.WARNING)
        return None
    if not _consume(challenge, now):
        return None
    throttling.reset(throttling.CODE, email)
    confirm_email(user, now=now)
    return user


def check_link(token: str, *, now=None) -> bool:
    """True if the link could log in now (for the confirmation page; consumes nothing)."""
    challenge = _challenge_for_token(token)
    return challenge is not None and challenge.is_usable(_now(now)) and challenge.user.is_active


def _challenge_for_token(token: str) -> LoginChallenge | None:
    if not token:
        return None
    return (
        LoginChallenge.objects.select_related("user").filter(token_hash=_token_hash(token)).first()
    )


def login_with_link(token: str, *, now=None):
    """The user for an unused, unexpired link token, else None. Consumes the challenge."""
    now = _now(now)
    challenge = _challenge_for_token(token)
    if challenge is None or not challenge.is_usable(now) or not challenge.user.is_active:
        _log("login link refused", "login_link_failed")
        return None
    if not _consume(challenge, now):
        return None
    throttling.reset(throttling.CODE, challenge.user.email)
    confirm_email(challenge.user, now=now)
    return challenge.user


def start_session(request, user) -> None:
    """Log in: Django rotates the session key and stores the session in the database."""
    auth.login(request, user, backend="django.contrib.auth.backends.ModelBackend")
    _log("login succeeded", "login_succeeded", user)


def end_session(request) -> None:
    """Log out: the session row is deleted on the server (`flush`)."""
    user = request.user if request.user.is_authenticated else None
    auth.logout(request)
    if user is not None:
        _log("logout", "logout", user)


def purge_expired(*, now=None) -> dict[str, int]:
    """Housekeeping (daily job): old challenges, throttle events and expired sessions."""
    from django.contrib.sessions.models import Session

    now = _now(now)
    challenges, _ = LoginChallenge.objects.filter(expires_at__lte=now - timedelta(days=1)).delete()
    sessions, _ = Session.objects.filter(expire_date__lte=now).delete()
    changes, _ = EmailChangeRequest.objects.filter(created_at__lte=now - timedelta(days=1)).delete()
    return {
        "challenges": challenges,
        "email_changes": changes,
        "throttle_events": throttling.purge(now=now),
        "sessions": sessions,
    }


# --- account settings and e-mail change (US-1.6) ---------------------------------------------


def _artist_services():
    from apps.artists import services as artists  # artists imports this module

    return artists


def account_overview(user, *, now=None) -> dict:
    """What `/konto/` shows: the login e-mail, the names and whether a change is pending."""
    artist = _artist_services().artist_for(user)
    return {
        "email": user.email,
        "full_name": user.full_name,
        "is_artist": artist is not None,
        "artist_name": artist.name if artist else "",
        "change_pending": pending_email_change(user, now=now) is not None,
    }


def update_names(user, *, full_name: str, artist_name: str | None = None) -> None:
    """Store the person's name and, for an artist, the artist name (through `artists`).
    `artist_name` is ignored for accounts without an artist record."""
    user.full_name = full_name.strip()
    user.save(update_fields=["full_name"])
    if artist_name is not None:
        _artist_services().rename_artist(user, artist_name)
    _log("account names updated", "account_updated", user)


def _change_key(user) -> str:
    return str(user.pk)


def request_email_change(user, new_email: str, client_ip: str, *, link_base: str, now=None) -> bool:
    """Ask to move the login to `new_email`. False only when a limit is reached.

    The answer is the same whether the address is free or used by any account (no
    enumeration). The old address always gets a notice without a link (a missing notice would
    tell the user the address is taken). Only a free address gets the link and code, by the
    `send_email_change_email` job, which creates them. The account e-mail is unchanged until
    the change is confirmed.
    """
    from . import tasks  # tasks import this module

    now = _now(now)
    new_email = normalize_email_address(new_email)
    ip_key = throttling.ip_identifier(client_ip)
    if throttling.exceeded(
        throttling.CHANGE_PER_USER, _change_key(user), now=now
    ) or throttling.exceeded(throttling.EMAIL_PER_IP, ip_key, now=now):
        _log("e-mail change rate limited", "email_change_rate_limited", user, logging.WARNING)
        return False
    throttling.hit(throttling.CHANGE_PER_USER, _change_key(user), now=now)
    throttling.hit(throttling.EMAIL_PER_IP, ip_key, now=now)

    if get_user_model().objects.filter(email=new_email).exists():  # also the user's own address
        _log("e-mail change refused, address in use", "email_change_refused", user)
        jobs.enqueue(tasks.send_email_change_notice, user_id=user.pk)
        return True
    with transaction.atomic():
        EmailChangeRequest.objects.filter(user=user, consumed_at__isnull=True).update(
            consumed_at=now
        )
        change = EmailChangeRequest.objects.create(user=user, new_email=new_email, created_at=now)
    _log("e-mail change requested", "email_change_requested", user)
    jobs.enqueue(tasks.send_email_change_email, change_id=change.pk, link_base=link_base)
    return True


def email_change_link(link_base: str, token: str) -> str:
    """Absolute confirmation link; the token is only in the query string, as for login."""
    path = reverse("accounts:email_change_link")
    return f"{link_base.rstrip('/')}{path}?{urlencode({'t': token})}"


def _send_change_notice(user) -> None:
    body = render_to_string("accounts/email/email_change_notice.txt", {})
    send_mail(gettext("Prośba o zmianę adresu e-mail"), body, None, [user.email])


def send_email_change_email(change_id: int, link_base: str, *, now=None) -> bool:
    """Job body: give the request its link token and code, e-mail them to the new address and
    send the notice to the old one. False (nothing sent) if the request was replaced or used,
    or the user is inactive."""
    now = _now(now)
    change = (
        EmailChangeRequest.objects.select_related("user")
        .filter(pk=change_id, consumed_at__isnull=True, user__is_active=True)
        .first()
    )
    if change is None:
        return False
    token = secrets.token_urlsafe(32)
    code = f"{secrets.randbelow(10**CODE_DIGITS):0{CODE_DIGITS}d}"
    salt = secrets.token_hex(16)
    updated = EmailChangeRequest.objects.filter(pk=change.pk, consumed_at__isnull=True).update(
        token_hash=_token_hash(token),
        code_salt=salt,
        code_hash=_change_code_hash(salt, code),
        expires_at=now + timedelta(seconds=settings.LOGIN_CHALLENGE_TTL),
    )
    if not updated:  # replaced while this job ran
        return False
    body = render_to_string(
        "accounts/email/email_change.txt",
        {
            "link": email_change_link(link_base, token),
            "code": code,
            "minutes": settings.LOGIN_CHALLENGE_TTL // 60,
        },
    )
    send_mail(gettext("Potwierdź nowy adres e-mail"), body, None, [change.new_email])
    _send_change_notice(change.user)
    _log("e-mail change e-mails sent", "email_change_email_sent", change.user)
    return True


def send_email_change_notice(user_id: int) -> bool:
    """Job body: only the notice to the current address (the new one was in use)."""
    user = get_user_model().objects.filter(pk=user_id, is_active=True).first()
    if user is None:
        return False
    _send_change_notice(user)
    _log("e-mail change notice sent", "email_change_notice_sent", user)
    return True


def _change_code_hash(salt: str, code: str) -> str:
    return salted_hmac("accounts.email_change_code", f"{salt}:{code}").hexdigest()


def pending_email_change(user, *, now=None) -> EmailChangeRequest | None:
    """The open request of `user` (its e-mail may still be on the way), else None."""
    now = _now(now)
    change = (
        EmailChangeRequest.objects.filter(user=user, consumed_at__isnull=True)
        .order_by("-created_at")
        .first()
    )
    if change is None or (change.expires_at is not None and change.expires_at <= now):
        return None
    return change


def _refuse(user, reason: str) -> bool:
    _log(f"e-mail change refused, {reason}", "email_change_refused", user, logging.WARNING)
    return False


def confirm_email_change_code(user, code: str, *, now=None) -> bool:
    """Apply the newest open request of the logged-in `user` if `code` matches. False for every
    failure; after LOGIN_THROTTLE_LIMIT wrong codes within the window even a correct one is
    refused (a 6-digit code must not be guessable)."""
    now = _now(now)
    code = (code or "").strip()
    if throttling.exceeded(throttling.CHANGE_CODE, _change_key(user), now=now):
        return _refuse(user, "code entry locked")
    change = pending_email_change(user, now=now)
    usable = change is not None and change.is_usable(now)
    salt = change.code_salt if usable else "-"
    expected = change.code_hash if usable else ""
    matches = constant_time_compare(_change_code_hash(salt, code), expected)
    if not (usable and matches and code.isdigit() and len(code) == CODE_DIGITS):
        throttling.hit(throttling.CHANGE_CODE, _change_key(user), now=now)
        return _refuse(user, "wrong or expired code")
    return _apply_email_change(user, change, now)


def _change_for_token(token: str) -> EmailChangeRequest | None:
    if not token:
        return None
    return EmailChangeRequest.objects.filter(token_hash=_token_hash(token)).first()


def check_email_change_link(user, token: str, *, now=None) -> bool:
    """True if `user` could confirm with this link now (consumes nothing)."""
    change = _change_for_token(token)
    return change is not None and change.user_id == user.pk and change.is_usable(_now(now))


def confirm_email_change_link(user, token: str, *, now=None) -> bool:
    """Apply the request behind the link, only for the logged-in user who made it. A link
    opened by another account is refused and stays usable for its owner."""
    now = _now(now)
    change = _change_for_token(token)
    if change is None or not change.is_usable(now):
        return _refuse(user, "link invalid or expired")
    if change.user_id != user.pk:
        return _refuse(user, "link belongs to another account")
    return _apply_email_change(user, change, now)


def _apply_email_change(user, change: EmailChangeRequest, now) -> bool:
    """Consume the request and move the login to the new address (confirmed now). Open login
    links (sent to the old address) are closed. The caller keeps the current session with
    `keep_session_after_change()`; every other session stops authenticating because the
    session hash includes the e-mail (`User._get_session_auth_hash`)."""
    user_model = get_user_model()
    try:
        with transaction.atomic():
            consumed = EmailChangeRequest.objects.filter(
                pk=change.pk, consumed_at__isnull=True
            ).update(consumed_at=now)
            if not consumed:
                return _refuse(user, "already used")
            if user_model.objects.filter(email=change.new_email).exclude(pk=user.pk).exists():
                return _refuse(user, "address taken meanwhile")
            user_model.objects.filter(pk=user.pk).update(
                email=change.new_email, email_confirmed_at=now
            )
    except IntegrityError:  # taken concurrently
        return _refuse(user, "address taken meanwhile")
    user.email = change.new_email
    user.email_confirmed_at = now
    LoginChallenge.objects.filter(user=user, consumed_at__isnull=True).update(consumed_at=now)
    throttling.reset(throttling.CHANGE_CODE, _change_key(user))
    _log("e-mail change confirmed", "email_change_confirmed", user)
    return True


def keep_session_after_change(request, user) -> None:
    """New session key for this browser, still logged in with the new session hash."""
    auth.update_session_auth_hash(request, user)


# --- admin accounts (D37, D99) ----------------------------------------------------------------


class AdminRefused(Exception):
    """The address already belongs to an artist or institution account (one role per account)."""


def create_admin(email: str) -> tuple:
    """Make `email` an admin: the only way to set `is_staff`/`is_superuser` (run on the server
    with `manage.py create_admin`). Creates the account if needed, without a password: the admin
    logs in with the normal e-mail link or code. Idempotent. Returns (user, created)."""
    from .roles import Role, role_of

    user, created = get_or_create_unconfirmed_user(email)
    role = role_of(user)
    if role in (Role.ARTIST, Role.INSTITUTION):
        raise AdminRefused(role)
    if not (user.is_staff and user.is_superuser):
        user.is_staff = user.is_superuser = True
        user.save(update_fields=["is_staff", "is_superuser"])
        _log("admin role granted", "admin_granted", user)
    return user, created


# --- seed ------------------------------------------------------------------------------------


def seed_users() -> dict[str, int]:
    """Create synthetic artist and institution users (idempotent, no real data: D57).

    Every address is on the reserved ``example.invalid`` domain and the accounts have no usable
    password. Returns how many rows were created by this call.
    """
    user_model = get_user_model()
    created = {"artists": 0, "institutions": 0}
    specs = [
        ("artists", "artysta", "Artysta Testowy", ARTIST_COUNT),
        ("institutions", "szkola", "Szkoła Testowa", INSTITUTION_COUNT),
    ]
    for key, prefix, name, count in specs:
        for number in range(1, count + 1):
            user, was_created = user_model.objects.get_or_create(
                email=f"{prefix}{number:02d}@{SEED_DOMAIN}",
                defaults={"full_name": f"{name} {number:02d}"},
            )
            if was_created:
                user.set_unusable_password()
                user.save(update_fields=["password"])
                created[key] += 1
    return created
