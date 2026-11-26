"""Catalog dictionaries (US-4.6, D17, D102): the admin adds, renames, deactivates and merges
entries; artists pick from the active ones. Everything that writes goes through here."""

from django.db import IntegrityError, transaction
from django.db.models import Max
from django.utils.translation import gettext as _

from apps.profiles.publication import slugify_name

from .models import ArtistEntry, DictionaryEntry, EntryKind  # noqa: F401 (EntryKind re-exported)


class EntryError(Exception):
    """A refused dictionary change; the message is Polish and fit for the admin."""


def active_entries(kind: str) -> list[DictionaryEntry]:
    """Active entries of one kind in position order."""
    return list(DictionaryEntry.objects.filter(kind=kind, is_active=True))


def clean_name(name: str) -> str:
    name = " ".join((name or "").split())
    if not name or not any(ch.isalnum() for ch in name):
        raise EntryError(_("Podaj nazwę pozycji."))
    return name


def _check_kind(kind: str) -> None:
    if kind not in EntryKind.values:
        raise EntryError(_("Nieznany słownik."))


def check_name_free(entry, kind: str, name: str) -> None:
    """Refuse a name (or a name with the same slug) another entry of the kind already has."""
    others = DictionaryEntry.objects.filter(kind=kind).exclude(pk=entry.pk)
    if others.filter(name__iexact=name).exists() or (
        entry.pk is None and others.filter(slug=slugify_name(name)).exists()
    ):
        raise EntryError(_("Taka pozycja już istnieje w tym słowniku."))


def slug_for(kind: str, name: str) -> str:
    """The slug of a new entry (D119 rule: ASCII, Polish letters transliterated)."""
    _check_kind(kind)
    return slugify_name(clean_name(name))


def add_entry(kind: str, name: str, position: int | None = None) -> DictionaryEntry:
    """Create an entry; the slug comes from the name now and stays for good."""
    _check_kind(kind)
    name = clean_name(name)
    check_name_free(DictionaryEntry(), kind, name)
    if position is None:
        last = DictionaryEntry.objects.filter(kind=kind).aggregate(m=Max("position"))["m"]
        position = 0 if last is None else last + 1
    try:
        with transaction.atomic():
            return DictionaryEntry.objects.create(
                kind=kind, name=name, slug=slugify_name(name), position=position
            )
    except IntegrityError:
        raise EntryError(_("Taka pozycja już istnieje w tym słowniku.")) from None


def rename_entry(entry: DictionaryEntry, name: str) -> DictionaryEntry:
    """Change the name only; the slug never changes."""
    name = clean_name(name)
    check_name_free(entry, entry.kind, name)
    entry.name = name
    entry.save(update_fields=["name"])
    return entry


def deactivate_entry(entry: DictionaryEntry) -> DictionaryEntry:
    """Stop offering the entry; profiles keep it until the artist saves step 1 again."""
    if entry.is_active:
        entry.is_active = False
        entry.save(update_fields=["is_active"])
    return entry


def profiles_to_move(source: DictionaryEntry) -> int:
    return ArtistEntry.objects.filter(entry=source).count()


def merge_entries(source: DictionaryEntry, target: DictionaryEntry) -> int:
    """Move every assignment of `source` to `target` (no duplicate for an artist who has both),
    then delete `source`, in one transaction. Same kind only. Returns how many profiles had
    the source."""
    if source.pk == target.pk:
        raise EntryError(_("Nie można połączyć pozycji z nią samą."))
    if source.kind != target.kind:
        raise EntryError(_("Można łączyć tylko pozycje z tego samego słownika."))
    with transaction.atomic():
        source, target = (
            DictionaryEntry.objects.select_for_update().get(pk=pk) for pk in (source.pk, target.pk)
        )
        moving = ArtistEntry.objects.filter(entry=source)
        count = moving.count()
        already = ArtistEntry.objects.filter(entry=target).values("artist_id")
        moving.filter(artist_id__in=already).delete()
        moving.update(entry=target)
        source.delete()
    return count


def entries_of(artist, kind: str) -> list[DictionaryEntry]:
    """Entries the artist has, including inactive ones, in position order."""
    return list(DictionaryEntry.objects.filter(kind=kind, assignments__artist=artist))


def set_artist_entries(artist, kind: str, entries) -> None:
    """Replace the artist's entries of `kind` by `entries`. Refuses inactive entries and entries
    of another kind; an inactive entry the artist still has is dropped when it is not in `entries`
    (it is not offered again, so saving step 1 removes it)."""
    _check_kind(kind)
    wanted = {entry.pk: entry for entry in entries}
    with transaction.atomic():
        for entry in wanted.values():
            if entry.kind != kind:
                raise EntryError(_("Pozycja należy do innego słownika."))
            if not entry.is_active:
                raise EntryError(_("Pozycja jest nieaktywna."))
        current = set(
            ArtistEntry.objects.filter(artist=artist, entry__kind=kind).values_list(
                "entry_id", flat=True
            )
        )
        ArtistEntry.objects.filter(artist=artist, entry__kind=kind).exclude(
            entry_id__in=wanted
        ).delete()
        ArtistEntry.objects.bulk_create(
            ArtistEntry(artist=artist, entry=entry)
            for pk, entry in wanted.items()
            if pk not in current
        )
