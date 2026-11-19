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


MAX_AGE = 99


class Offer(models.Model):
    """One show, concert or workshop of an artist (US-2.9). A theatre's repertoire is many
    offers in one profile (D2). Only `services` create, change, order and delete offers (D103).

    The price is either a whole-PLN amount or "na zapytanie" (exactly one, a DB constraint).
    `poster_key` is a key in the private storage (T06 upload path); it becomes public only with
    publication (US-2.8).
    """

    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, related_name="offers")
    title = models.CharField(_("tytuł"), max_length=200)
    description = models.TextField(_("opis"), max_length=5000)
    age_from = models.PositiveSmallIntegerField(_("wiek widzów od"), null=True, blank=True)
    age_to = models.PositiveSmallIntegerField(_("wiek widzów do"), null=True, blank=True)
    duration_minutes = models.PositiveIntegerField(_("czas trwania (min)"), null=True, blank=True)
    price_pln = models.PositiveIntegerField(_("cena (zł)"), null=True, blank=True)
    price_on_request = models.BooleanField(_("cena na zapytanie"), default=False)
    position = models.PositiveIntegerField(_("kolejność"), default=0)
    poster_key = models.CharField(_("plakat"), max_length=255, blank=True)
    created_at = models.DateTimeField(_("utworzono"), default=timezone.now)
    updated_at = models.DateTimeField(_("zmieniono"), default=timezone.now)

    class Meta:
        verbose_name = _("oferta")
        verbose_name_plural = _("oferty")
        ordering = ("position", "pk")
        indexes = [models.Index(fields=("artist", "position"), name="offer_artist_position")]
        constraints = [
            models.CheckConstraint(
                condition=(
                    models.Q(price_pln__isnull=False, price_on_request=False)
                    | models.Q(price_pln__isnull=True, price_on_request=True)
                ),
                name="offer_price_xor_on_request",
            ),
            models.CheckConstraint(
                condition=models.Q(age_from__isnull=True)
                | models.Q(age_to__isnull=True)
                | models.Q(age_from__lte=models.F("age_to")),
                name="offer_age_from_lte_to",
            ),
            models.CheckConstraint(
                condition=models.Q(age_from__isnull=True) | models.Q(age_from__lte=MAX_AGE),
                name="offer_age_from_max",
            ),
            models.CheckConstraint(
                condition=models.Q(age_to__isnull=True) | models.Q(age_to__lte=MAX_AGE),
                name="offer_age_to_max",
            ),
            models.CheckConstraint(
                condition=models.Q(duration_minutes__isnull=True)
                | models.Q(duration_minutes__gt=0),
                name="offer_duration_positive",
            ),
            models.CheckConstraint(
                condition=models.Q(price_pln__isnull=True) | models.Q(price_pln__gt=0),
                name="offer_price_positive",
            ),
        ]

    def __str__(self) -> str:
        return f"Offer {self.pk}"
