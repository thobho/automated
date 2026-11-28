"""Closed dictionaries managed by the admin (US-4.6, D17): topics and forms."""

from django.db import models
from django.utils.translation import gettext_lazy as _


class EntryKind(models.TextChoices):
    TOPIC = "topic", _("Tematyka")
    FORM = "form", _("Forma")


class DictionaryEntry(models.Model):
    """One entry of a closed dictionary. The slug is made once from the name and never changes,
    so filter URLs stay stable after a rename (US-4.2). Entries are never hidden by deleting:
    deactivate them (kept on the profiles that have them) or merge them into another entry."""

    kind = models.CharField(_("słownik"), max_length=16, choices=EntryKind.choices)
    name = models.CharField(_("nazwa"), max_length=80)
    slug = models.SlugField(_("identyfikator"), max_length=80)
    is_active = models.BooleanField(_("aktywna"), default=True)
    position = models.PositiveIntegerField(_("pozycja"), default=0)

    class Meta:
        verbose_name = _("pozycja słownika")
        verbose_name_plural = _("pozycje słowników")
        ordering = ("kind", "position", "name")
        constraints = [
            models.UniqueConstraint(fields=("kind", "slug"), name="catalog_entry_kind_slug_unique"),
            models.UniqueConstraint(fields=("kind", "name"), name="catalog_entry_kind_name_unique"),
        ]

    def __str__(self) -> str:
        return self.name


class ArtistEntry(models.Model):
    """An artist has an entry (a row per pair, like the child tables of D102)."""

    artist = models.ForeignKey(
        "artists.Artist", on_delete=models.CASCADE, related_name="catalog_entries"
    )
    # PROTECT: an entry with assignments is merged or deactivated, never deleted (US-4.6).
    entry = models.ForeignKey(DictionaryEntry, on_delete=models.PROTECT, related_name="assignments")

    class Meta:
        verbose_name = _("przypisanie pozycji")
        verbose_name_plural = _("przypisania pozycji")
        constraints = [
            models.UniqueConstraint(fields=("artist", "entry"), name="catalog_artist_entry_unique")
        ]
        indexes = [models.Index(fields=("entry",), name="catalog_artistentry_entry_idx")]

    def __str__(self) -> str:
        return f"{self.artist_id}: {self.entry_id}"


class CatalogEntry(models.Model):
    """The read model of the public catalog (US-4.1, D119): one row per publicly visible artist,
    copied from the publication snapshot by `listing.sync`. Nothing here is edited by hand; a row
    is written on publish and "Opublikuj zmiany", removed on withdrawal and deactivation, and
    `rebuild_catalog` makes all rows again. Lists are JSON so the same code runs on SQLite and
    PostgreSQL; the filters of US-4.2 can read `offers` and the lists from here."""

    artist = models.OneToOneField(
        "artists.Artist", on_delete=models.CASCADE, related_name="catalog_entry"
    )
    slug = models.SlugField(max_length=80, unique=True)
    name = models.CharField(max_length=200)
    artist_type = models.CharField(max_length=32, blank=True)
    voivodeships = models.JSONField(default=list)  # Voivodeship codes
    age_groups = models.JSONField(default=list)  # Audience codes
    topics = models.JSONField(default=list)  # [{"slug", "name"}]
    forms = models.JSONField(default=list)  # [{"slug", "name"}]
    main_photo_id = models.PositiveBigIntegerField(null=True, blank=True)
    main_photo_alt = models.CharField(max_length=200, blank=True)
    price_from = models.PositiveIntegerField(null=True, blank=True)  # whole zł; None = no price
    offers = models.JSONField(default=list)  # [{"price": int | None, "duration": int | None}]
    published_at = models.DateTimeField()  # the last publication of the snapshot
    # Profile completeness rounded down to tens (0-100), written with the row (US-4.4, D16).
    completeness_bucket = models.PositiveSmallIntegerField(default=0)
    # Text search (US-4.3, `search.py`): stems without Polish letters, space-separated and padded.
    search_name = models.TextField(blank=True, default="")
    search_other = models.TextField(blank=True, default="")  # offer titles and topic names
    search_fuzzy = models.TextField(blank=True, default="")  # one-letter deletions, for typos

    class Meta:
        verbose_name = _("wpis katalogu")
        verbose_name_plural = _("wpisy katalogu")
        indexes = [models.Index(fields=("-published_at", "-id"), name="catalog_entry_order_idx")]

    def __str__(self) -> str:
        return self.slug
