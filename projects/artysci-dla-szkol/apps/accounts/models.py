from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.utils.crypto import salted_hmac
from django.utils.translation import gettext_lazy as _

from .managers import UserManager, normalize_email_address


class User(AbstractBaseUser, PermissionsMixin):
    """A person who logs in with an email address. There is no username."""

    email = models.EmailField(_("adres e-mail"), unique=True)
    full_name = models.CharField(_("imię i nazwisko"), max_length=200, blank=True)
    is_active = models.BooleanField(_("aktywny"), default=True)
    is_staff = models.BooleanField(_("dostęp do panelu Django"), default=False)
    date_joined = models.DateTimeField(_("data rejestracji"), default=timezone.now)
    # None = "niepotwierdzone" (US-1.1): set by the first successful link or code login.
    email_confirmed_at = models.DateTimeField(_("e-mail potwierdzony"), null=True, blank=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS: list[str] = []

    class Meta:
        verbose_name = _("użytkownik")
        verbose_name_plural = _("użytkownicy")

    def __str__(self) -> str:
        return self.email

    @property
    def is_confirmed(self) -> bool:
        return self.email_confirmed_at is not None

    def clean(self) -> None:
        super().clean()
        self.email = normalize_email_address(self.email)

    def _get_session_auth_hash(self, secret=None):
        """Sessions stay valid only while the password field *and the e-mail* are unchanged.

        Django's default hashes only the password field, which never changes here (no
        passwords, D1). Including the login e-mail means a confirmed e-mail change ends every
        other session of the user (US-1.6); the session that made the change is kept with
        `update_session_auth_hash()`.
        """
        return salted_hmac(
            "apps.accounts.User.session_auth_hash",
            f"{self.password}\x00{self.email}",
            secret=secret,
            algorithm="sha256",
        ).hexdigest()


class LoginChallenge(models.Model):
    """One e-mail login: a link token and a 6-digit code, single use, short-lived (US-1.3).

    Only hashes are stored: SHA-256 of the high-entropy token (looked up by it) and an HMAC of
    the code keyed with SECRET_KEY and this row's salt (a 6-digit code alone is trivial to
    brute-force from a plain hash). Using either the link or the code consumes the challenge.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="login_challenges"
    )
    token_hash = models.CharField(max_length=64, unique=True)
    code_salt = models.CharField(max_length=32)
    code_hash = models.CharField(max_length=64)
    created_at = models.DateTimeField()
    expires_at = models.DateTimeField()
    consumed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [models.Index(fields=["user", "-created_at"], name="login_chal_user_created")]

    def __str__(self) -> str:
        return f"LoginChallenge {self.pk}"

    def is_usable(self, now) -> bool:
        return self.consumed_at is None and now < self.expires_at


class EmailChangeRequest(models.Model):
    """A requested new login e-mail, waiting for confirmation from that address (US-1.6).

    Created by the request (with the new address only); the e-mail job then sets the hashes
    and the expiry, so the raw link token and code exist only in the e-mail, as in
    `LoginChallenge`. Hashes stay empty until the e-mail is sent; an empty hash never matches.
    A newer request closes the older open ones (`consumed_at`), and so does using one.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="email_changes"
    )
    new_email = models.EmailField()
    token_hash = models.CharField(max_length=64, null=True, blank=True, unique=True)
    code_salt = models.CharField(max_length=32, blank=True)
    code_hash = models.CharField(max_length=64, blank=True)
    created_at = models.DateTimeField()
    expires_at = models.DateTimeField(null=True, blank=True)
    consumed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [models.Index(fields=["user", "-created_at"], name="email_change_user_created")]

    def __str__(self) -> str:
        return f"EmailChangeRequest {self.pk}"

    def is_usable(self, now) -> bool:
        return (
            self.consumed_at is None
            and self.expires_at is not None
            and bool(self.code_hash)
            and now < self.expires_at
        )


class ThrottleEvent(models.Model):
    """One counted event (a failed code, a login e-mail sent) for rate limits (US-1.3).

    Lives in PostgreSQL so every web worker sees the same counts (D96). `key_hash` is an HMAC
    of the normalised e-mail or IP: no raw identifier is stored.
    """

    scope = models.CharField(max_length=32)
    key_hash = models.CharField(max_length=64)
    created_at = models.DateTimeField()

    class Meta:
        indexes = [
            models.Index(fields=["scope", "key_hash", "created_at"], name="throttle_scope_key_at")
        ]

    def __str__(self) -> str:
        return f"{self.scope} {self.created_at:%Y-%m-%d %H:%M}"
