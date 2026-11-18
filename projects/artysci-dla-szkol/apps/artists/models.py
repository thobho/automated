from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class Artist(models.Model):
    """An artist account's profile record: one account = one artist (D2).

    Minimal for registration (US-1.1); the profile wizard (US-2.1) adds type, region and
    audiences. `name` is a person, a band or a company, as typed in one field.
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="artist"
    )
    name = models.CharField(_("nazwa"), max_length=200)
    created_at = models.DateTimeField(_("utworzono"), default=timezone.now)

    class Meta:
        verbose_name = _("artysta")
        verbose_name_plural = _("artyści")

    def __str__(self) -> str:
        return f"Artist {self.pk}"
