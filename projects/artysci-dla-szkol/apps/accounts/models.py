from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .managers import UserManager, normalize_email_address


class User(AbstractBaseUser, PermissionsMixin):
    """A person who logs in with an email address. There is no username."""

    email = models.EmailField(_("adres e-mail"), unique=True)
    full_name = models.CharField(_("imię i nazwisko"), max_length=200, blank=True)
    is_active = models.BooleanField(_("aktywny"), default=True)
    is_staff = models.BooleanField(_("dostęp do panelu Django"), default=False)
    date_joined = models.DateTimeField(_("data rejestracji"), default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = "email"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS: list[str] = []

    class Meta:
        verbose_name = _("użytkownik")
        verbose_name_plural = _("użytkownicy")

    def __str__(self) -> str:
        return self.email

    def clean(self) -> None:
        super().clean()
        self.email = normalize_email_address(self.email)
