import uuid

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

    # School questionnaire (US-2.3A): all optional; only `services.save_questionnaire()`
    # writes them. Price: an amount range in whole PLN or "na zapytanie", never both.
    q_age_from = models.PositiveSmallIntegerField(_("wiek widzów od"), null=True, blank=True)
    q_age_to = models.PositiveSmallIntegerField(_("wiek widzów do"), null=True, blank=True)
    q_duration_minutes = models.PositiveIntegerField(_("czas trwania (min)"), null=True, blank=True)
    q_max_audience = models.PositiveIntegerField(_("maks. liczba widzów"), null=True, blank=True)
    q_tech_room = models.CharField(_("wymagania: sala"), max_length=500, blank=True)
    q_tech_power = models.CharField(_("wymagania: prąd"), max_length=500, blank=True)
    q_tech_sound = models.CharField(_("wymagania: nagłośnienie"), max_length=500, blank=True)
    q_price_from_pln = models.PositiveIntegerField(_("cena od (zł)"), null=True, blank=True)
    q_price_to_pln = models.PositiveIntegerField(_("cena do (zł)"), null=True, blank=True)
    q_price_on_request = models.BooleanField(_("cena na zapytanie"), default=False)

    class Meta:
        verbose_name = _("artysta")
        verbose_name_plural = _("artyści")
        constraints = [
            models.CheckConstraint(
                condition=models.Q(q_price_on_request=False)
                | models.Q(q_price_from_pln__isnull=True, q_price_to_pln__isnull=True),
                name="artist_q_price_xor_on_request",
            ),
            models.CheckConstraint(
                condition=models.Q(q_price_from_pln__isnull=True)
                | models.Q(q_price_to_pln__isnull=True)
                | models.Q(q_price_from_pln__lte=models.F("q_price_to_pln")),
                name="artist_q_price_from_lte_to",
            ),
            models.CheckConstraint(
                condition=models.Q(q_age_from__isnull=True)
                | models.Q(q_age_to__isnull=True)
                | models.Q(q_age_from__lte=models.F("q_age_to")),
                name="artist_q_age_from_lte_to",
            ),
        ]

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


class ScanStatus(models.TextChoices):
    """Malware-scan state of an uploaded file (materials and offer posters)."""

    PENDING = "pending", _("oczekuje na skan")
    READY = "ready", _("gotowy")
    REJECTED = "rejected", _("odrzucony")


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
    # Malware scan of the poster (US-2.3A); only a READY poster may be published (US-2.8).
    poster_status = models.CharField(
        _("status plakatu"), max_length=10, choices=ScanStatus.choices, blank=True
    )
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


class MaterialKind(models.TextChoices):
    PHOTO = "photo", _("zdjęcie")
    PDF = "pdf", _("PDF")
    LINK = "link", _("film (link)")
    VIDEO = "video", _("film")
    AUDIO = "audio", _("nagranie")


class ProcessingStatus(models.TextChoices):
    """ffprobe / ffmpeg work on a video or audio file (US-2.3B), after a clean scan."""

    NONE = "", _("—")
    PENDING = "pending", _("przetwarzanie")
    DONE = "done", _("przetworzony")
    FAILED = "failed", _("nie udało się przetworzyć")


class VideoProvider(models.TextChoices):
    YOUTUBE = "youtube", "YouTube"
    VIMEO = "vimeo", "Vimeo"


class TextStatus(models.TextChoices):
    """PDF text extraction (runs after a clean scan)."""

    NONE = "", _("—")
    PENDING = "pending", _("czeka na odczyt tekstu")
    DONE = "done", _("tekst odczytany")
    TRUNCATED = "truncated", _("tekst odczytany częściowo (limit)")
    EMPTY = "empty", _("brak tekstu (np. skan bez warstwy tekstowej)")
    ENCRYPTED = "encrypted", _("PDF zaszyfrowany: nie można odczytać tekstu")
    BROKEN = "broken", _("PDF uszkodzony: nie można odczytać tekstu")


class Material(models.Model):
    """A source material of an artist (US-2.3A): a photo, a PDF or a YouTube/Vimeo link.

    Files sit in the private storage under `storage_key` (T06 upload path) and count only when
    `status` is READY, which the malware-scan job sets (`apps/core/scanning.py`). Links are
    READY on creation (no file). A PDF's text (`text`) is source material for US-2.5a.
    Video and audio (US-2.3B) become READY only after the scan and the ffprobe/ffmpeg job
    (`processing_status`); a video then also has `converted_key` (MP4) and `thumbnail_key`.
    Only `artists.materials` creates, changes and deletes materials.
    """

    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, related_name="materials")
    kind = models.CharField(_("rodzaj"), max_length=8, choices=MaterialKind.choices)
    status = models.CharField(
        _("status"), max_length=10, choices=ScanStatus.choices, default=ScanStatus.PENDING
    )
    storage_key = models.CharField(_("klucz pliku"), max_length=255, blank=True)
    content_type = models.CharField(_("typ zawartości"), max_length=100, blank=True)
    size = models.PositiveIntegerField(_("rozmiar (B)"), default=0)
    original_name = models.CharField(_("nazwa pliku"), max_length=200, blank=True)
    # links
    provider = models.CharField(
        _("serwis"), max_length=10, choices=VideoProvider.choices, blank=True
    )
    video_id = models.CharField(_("id filmu"), max_length=32, blank=True)
    canonical_url = models.URLField(_("adres filmu"), max_length=200, blank=True)
    title = models.CharField(_("tytuł"), max_length=300, blank=True)
    # PDFs
    text = models.TextField(_("tekst z PDF"), blank=True)
    text_status = models.CharField(
        _("odczyt tekstu"), max_length=10, choices=TextStatus.choices, blank=True
    )
    # video and audio (US-2.3B): filled by the processing job; keys are in the private storage
    duration_seconds = models.FloatField(_("czas trwania (s)"), null=True, blank=True)
    width = models.PositiveIntegerField(_("szerokość"), null=True, blank=True)
    height = models.PositiveIntegerField(_("wysokość"), null=True, blank=True)
    converted_key = models.CharField(_("klucz pliku MP4"), max_length=255, blank=True)
    thumbnail_key = models.CharField(_("klucz miniatury"), max_length=255, blank=True)
    processing_status = models.CharField(
        _("przetwarzanie"), max_length=10, choices=ProcessingStatus.choices, blank=True
    )
    processing_message = models.CharField(_("komunikat"), max_length=300, blank=True)
    created_at = models.DateTimeField(_("utworzono"), default=timezone.now)
    scanned_at = models.DateTimeField(_("zeskanowano"), null=True, blank=True)

    class Meta:
        verbose_name = _("materiał")
        verbose_name_plural = _("materiały")
        ordering = ("created_at", "pk")
        indexes = [models.Index(fields=("artist", "kind"), name="material_artist_kind")]
        constraints = [
            models.UniqueConstraint(
                fields=("artist", "provider", "video_id"),
                condition=models.Q(kind="link"),
                name="material_link_unique",
            )
        ]

    def __str__(self) -> str:
        return f"Material {self.pk}"

    def stored_keys(self) -> list[str]:
        """Every storage key of this material (original, converted file, thumbnail)."""
        return [k for k in (self.storage_key, self.converted_key, self.thumbnail_key) if k]


class UploadSession(models.Model):
    """A resumable upload of one video or audio file (US-2.3B). The bytes received so far sit
    in a temporary file named after `id` under `UPLOAD_TEMP_DIR` (never in a storage that is
    served); `received` is how many. Only `artists.resumable` creates, changes and deletes
    sessions; an expired one is removed with its data by a periodic job."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, related_name="upload_sessions")
    kind = models.CharField(_("rodzaj"), max_length=8, choices=MaterialKind.choices)
    declared_size = models.PositiveIntegerField(_("deklarowany rozmiar (B)"))
    received = models.PositiveIntegerField(_("odebrano (B)"), default=0)
    original_name = models.CharField(_("nazwa pliku"), max_length=200, blank=True)
    created_at = models.DateTimeField(_("utworzono"), default=timezone.now)
    expires_at = models.DateTimeField(_("wygasa"))

    class Meta:
        verbose_name = _("wysyłka pliku")
        verbose_name_plural = _("wysyłki plików")
        indexes = [models.Index(fields=("expires_at",), name="upload_session_expires")]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(received__lte=models.F("declared_size")),
                name="upload_session_received_lte_declared",
            )
        ]

    def __str__(self) -> str:
        return f"UploadSession {self.pk}"
