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
