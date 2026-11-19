from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.core.regions import Voivodeship


class ArtistType(models.TextChoices):
    """What the artist does (US-2.1), one choice."""

    THEATRE = "theatre", _("teatr")
    ILLUSION = "illusion", _("iluzja")
    MUSIC = "music", _("muzyka")
    SCIENCE_SHOW = "science_show", _("pokaz naukowy")
    ANIMAL_SHOW = "animal_show", _("pokaz ze zwierzętami")
    WORKSHOPS = "workshops", _("warsztaty")
    OTHER = "other", _("inne")


class Audience(models.TextChoices):
    """Who the artist performs for (US-2.1), one or more."""

    KINDERGARTEN = "kindergarten", _("przedszkola")
    GRADES_0_3 = "grades_0_3", _("klasy 0–3")
    GRADES_4_6 = "grades_4_6", _("klasy 4–6")
    GRADES_7_8 = "grades_7_8", _("klasy 7–8")
    SECONDARY = "secondary", _("szkoły ponadpodstawowe")
    FAMILIES = "families", _("rodziny")


class Artist(models.Model):
    """An artist account's profile record: one account = one artist (D2).

    `name` is a person, a band or a company, as typed in one field (D97); only
    `services.rename_artist()` changes it. The basics (US-2.1) are `artist_type`, `city` and the
    `voivodeships` / `audiences` child rows (D102); `services.save_basics()` writes them all.
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="artist"
    )
    name = models.CharField(_("nazwa"), max_length=200)
    artist_type = models.CharField(
        _("rodzaj"), max_length=32, choices=ArtistType.choices, blank=True
    )
    city = models.CharField(_("miasto"), max_length=100, blank=True)
    created_at = models.DateTimeField(_("utworzono"), default=timezone.now)

    class Meta:
        verbose_name = _("artysta")
        verbose_name_plural = _("artyści")

    def __str__(self) -> str:
        return f"Artist {self.pk}"


class ArtistVoivodeship(models.Model):
    """One voivodeship the artist works in (a row per value: works on SQLite and PostgreSQL
    and the catalog can filter with a join, D102)."""

    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, related_name="voivodeships")
    voivodeship = models.CharField(_("województwo"), max_length=32, choices=Voivodeship.choices)

    class Meta:
        verbose_name = _("województwo działania")
        verbose_name_plural = _("województwa działania")
        constraints = [
            models.UniqueConstraint(
                fields=("artist", "voivodeship"), name="artist_voivodeship_unique"
            )
        ]

    def __str__(self) -> str:
        return self.voivodeship


class ArtistAudience(models.Model):
    """One audience of the artist (a row per value, D102)."""

    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, related_name="audiences")
    audience = models.CharField(_("odbiorcy"), max_length=32, choices=Audience.choices)

    class Meta:
        verbose_name = _("odbiorcy")
        verbose_name_plural = _("odbiorcy")
        constraints = [
            models.UniqueConstraint(fields=("artist", "audience"), name="artist_audience_unique")
        ]

    def __str__(self) -> str:
        return self.audience
