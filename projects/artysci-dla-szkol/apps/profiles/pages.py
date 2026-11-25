"""Stored page texts of an artist: versions, field edits and locks (US-2.6).

    version = record_generated(generation)       # a `gotowa` run creates the next version
    version = edit_field(artist, "about", text)  # an edit: new version, the field is locked
    unlock(artist, "about")                      # only removes the lock
    version = restore(artist, 3)                 # a new version with the content of version 3
    content = page_content(artist)               # PageContent for the preview

A version holds only the artist-editable texts (see `PageVersion`); the newest is the current one.
Regeneration (a whole run or one section) keeps every locked field as the artist wrote it
(`apply_locks`). At most `MAX_VERSIONS` stay; the current one is never deleted.
"""

import copy
import re

from django.db import transaction
from django.utils.translation import gettext as _
from django.utils.translation import gettext_lazy

from apps.artists.models import Artist
from apps.quality.models import Generation

from . import validator
from .content import FaqItem, PageContent, page_content_for
from .models import PageVersion

MAX_VERSIONS = 10
FACT_FIT = validator.FACT_MAX_CHARS

# Section key (what the artist regenerates) -> the content keys it owns.
SECTIONS = {
    "tagline": ("tagline",),
    "facts": ("facts",),
    "about": ("about",),
    "schools": ("for_schools",),
    "faq": ("faq",),
}
SECTION_LABELS = {
    "tagline": gettext_lazy("Hasło"),
    "facts": gettext_lazy("Informacje"),
    "about": gettext_lazy("O artyście"),
    "schools": gettext_lazy("Dla szkół i przedszkoli"),
    "faq": gettext_lazy("Pytania"),
}
_PATH = re.compile(r"^(tagline|about|for_schools|facts\.\d+|faq\.\d+\.(question|answer))$")


class InvalidEdit(ValueError):
    """An edit that is refused. `message` is shown to the artist (Polish)."""

    def __init__(self, message):
        super().__init__(str(message))
        self.message = message


def empty_content() -> dict:
    return {"tagline": "", "facts": [], "about": "", "for_schools": "", "faq": []}


# --- generated profile <-> page texts ----------------------------------------------------------


def content_from_profile(profile: dict) -> dict:
    """The page texts of a generated profile JSON."""
    facts = []
    for fact in profile.get("facts") or []:
        label, value = (fact.get("label") or "").strip(), (fact.get("value") or "").strip()
        joined = f"{label}: {value}" if label and value else (value or label)
        facts.append(joined if len(joined) <= FACT_FIT else (value or label))
    schools = profile.get("schools") or {}
    paragraphs = (profile.get("description") or {}).get("paragraphs") or []
    return {
        "tagline": ((profile.get("hero") or {}).get("headline") or "").strip(),
        "facts": facts,
        "about": "\n\n".join(p.strip() for p in paragraphs if p.strip()),
        "for_schools": "\n\n".join(p.strip() for p in schools.get("points") or [] if p.strip()),
        "faq": [
            {
                "question": (i.get("question") or "").strip(),
                "answer": (i.get("answer") or "").strip(),
            }
            for i in profile.get("faq") or []
        ],
    }


def _blocks(text: str) -> list[str]:
    return [b.strip() for b in re.split(r"\n\s*\n", text or "") if b.strip()]


def profile_for_validation(content: dict, base: dict | None = None) -> dict:
    """A profile JSON with `content`'s texts written into `base` (the validator's input)."""
    profile = copy.deepcopy(base) if base else {}
    profile.setdefault("hero", {})["headline"] = content.get("tagline", "")
    profile["facts"] = [{"label": "", "value": f} for f in content.get("facts", [])]
    profile.setdefault("description", {})["paragraphs"] = _blocks(content.get("about", ""))
    profile.setdefault("schools", {})["points"] = _blocks(content.get("for_schools", ""))
    profile["faq"] = [dict(i) for i in content.get("faq", [])]
    return profile


# --- locks ---------------------------------------------------------------------------------------

# Where each lockable path lives in the profile JSON (findings use these paths).
_PROFILE_PATHS = {
    "tagline": "$.hero.headline",
    "about": "$.description.paragraphs",
    "for_schools": "$.schools.points",
}


def profile_path(path: str) -> str:
    """The validator path of a lockable field path ("faq.1.answer" -> "$.faq[1].answer")."""
    if path in _PROFILE_PATHS:
        return _PROFILE_PATHS[path]
    parts = path.split(".")
    return "$." + parts[0] + "".join(f"[{p}]" if p.isdigit() else f".{p}" for p in parts[1:])


def apply_locks(new: dict, old: dict, locks) -> dict:
    """`new` with every locked field taken from `old` (returns a copy; lists are extended)."""
    result = copy.deepcopy(new)
    for path in locks:
        parts = path.split(".")
        if parts[0] in ("tagline", "about", "for_schools"):
            if parts[0] in old:
                result[parts[0]] = old[parts[0]]
        elif parts[0] == "facts":
            index, items, source = (
                int(parts[1]),
                result.setdefault("facts", []),
                old.get("facts", []),
            )
            if index >= len(source):
                continue
            while len(items) <= index:
                items.append(source[len(items)])
            items[index] = source[index]
        elif parts[0] == "faq":
            index, field = int(parts[1]), parts[2]
            items, source = result.setdefault("faq", []), old.get("faq", [])
            if index >= len(source):
                continue
            while len(items) <= index:
                items.append(dict(source[len(items)]))
            items[index] = {**items[index], field: source[index][field]}
    return result


def text_at(content: dict, path: str) -> str:
    """The text at a lockable path; raises `InvalidEdit` for an unknown or missing one."""
    if not _PATH.match(path):
        raise InvalidEdit(_("Nieznane pole."))
    parts = path.split(".")
    try:
        if len(parts) == 1:
            return content.get(path, "")
        if parts[0] == "facts":
            return content["facts"][int(parts[1])]
        return content["faq"][int(parts[1])][parts[2]]
    except (KeyError, IndexError):
        raise InvalidEdit(_("Nieznane pole.")) from None


def _with_text(content: dict, path: str, value: str) -> dict:
    result = copy.deepcopy(content)
    parts = path.split(".")
    if len(parts) == 1:
        result[path] = value
    elif parts[0] == "facts":
        result["facts"][int(parts[1])] = value
    else:
        result["faq"][int(parts[1])][parts[2]] = value
    return result


# --- versions ------------------------------------------------------------------------------------


def current_version(artist: Artist) -> PageVersion | None:
    return PageVersion.objects.filter(artist=artist).order_by("-number").first()


def versions_of(artist: Artist) -> list[PageVersion]:
    return list(PageVersion.objects.filter(artist=artist).order_by("-number")[:MAX_VERSIONS])


def current_content(artist: Artist) -> tuple[dict, list[str]]:
    """(content, locks) of the current version; empty content and no locks without one."""
    version = current_version(artist)
    if version is None:
        return empty_content(), []
    return {**empty_content(), **version.content}, list(version.locks)


def create_version(
    artist: Artist, content: dict, source: str, locks, generation: Generation | None = None
) -> PageVersion:
    """Save the next version and drop the oldest ones above `MAX_VERSIONS`."""
    with transaction.atomic():
        Artist.objects.select_for_update().filter(pk=artist.pk).first()  # one writer at a time
        last = PageVersion.objects.filter(artist=artist).order_by("-number").first()
        version = PageVersion.objects.create(
            artist=artist,
            number=(last.number + 1) if last else 1,
            source=source,
            content=content,
            locks=sorted(set(locks)),
            generation=generation,
        )
        stale = PageVersion.objects.filter(artist=artist).order_by("-number")[MAX_VERSIONS:]
        PageVersion.objects.filter(pk__in=[v.pk for v in stale]).delete()
    return version


def record_generated(generation: Generation) -> PageVersion | None:
    """The version of a finished `gotowa` run (None for any other status). Locked fields keep
    the artist's text. Safe to call twice for the same run."""
    if generation.status != Generation.Status.READY or not isinstance(generation.result, dict):
        return None
    existing = PageVersion.objects.filter(generation=generation).first()
    if existing is not None:
        return existing
    old, locks = current_content(generation.artist)
    new = apply_locks(content_from_profile(generation.result), old, locks)
    return create_version(
        generation.artist, new, PageVersion.Source.GENERATED, locks, generation=generation
    )


def check_text(path: str, value: str) -> None:
    """The hard rules that apply to the artist's own text: length limits, and for facts at most
    22 characters without brackets. Raises `InvalidEdit` with the Polish reason."""
    kind = path.split(".")[0]
    probe = {
        "tagline": {"hero": {"headline": value}},
        "about": {"description": {"paragraphs": _blocks(value)}},
        "for_schools": {"schools": {"points": _blocks(value)}},
        "facts": {"facts": [{"label": "", "value": value}]},
        "faq": {"faq": [{"question": value, "answer": ""} if path.endswith("question") else
                        {"question": "", "answer": value}]},
    }[kind]  # fmt: skip
    report = validator.validate_profile(probe, validator.Sources())
    wrong = [f for f in report.hard if f.rule in (validator.RULE_FACTS, validator.RULE_LENGTHS)]
    if wrong:
        raise InvalidEdit(wrong[0].message)


def edit_field(artist: Artist, path: str, value: str) -> PageVersion | None:
    """Save the artist's own text for one field as a new `edited` version and lock the field.
    Returns None when the text did not change. Raises `InvalidEdit`; then nothing is saved."""
    value = value.replace("\r\n", "\n").replace("\x00", "").strip()
    content, locks = current_content(artist)
    old = text_at(content, path)
    if path.split(".")[0] in ("facts", "faq") and not value:
        raise InvalidEdit(_("To pole nie może być puste."))
    check_text(path, value)
    if value == old:
        return None
    return create_version(
        artist, _with_text(content, path, value), PageVersion.Source.EDITED, [*locks, path]
    )


def unlock(artist: Artist, path: str) -> bool:
    """Remove a lock from the current version (no new version). False when it was not locked."""
    version = current_version(artist)
    if version is None or path not in version.locks:
        return False
    version.locks = [p for p in version.locks if p != path]
    version.save(update_fields=["locks"])
    return True


def restore(artist: Artist, number: int) -> PageVersion:
    """A new `restored` version with the content of version `number`, keeping the current locks.
    Raises `PageVersion.DoesNotExist` for a number the artist does not have."""
    old = PageVersion.objects.get(artist=artist, number=number)
    locks = current_content(artist)[1]
    return create_version(artist, copy.deepcopy(old.content), PageVersion.Source.RESTORED, locks)


# --- preview -------------------------------------------------------------------------------------


def page_content(artist: Artist) -> PageContent:
    """The builder output with the texts of the current version laid over it."""
    page = page_content_for(artist)
    version = current_version(artist)
    if version is not None:
        overlay_texts(page, version.content)
    return page


def overlay_texts(page, content: dict) -> None:
    """Write the stored texts (`content` of a version or of a snapshot) into `page`."""
    data = {**empty_content(), **content}
    page.hero.tagline = data["tagline"]
    page.facts = list(data["facts"])
    page.about = data["about"]
    page.for_schools = data["for_schools"]
    page.faq = [FaqItem(i.get("question", ""), i.get("answer", "")) for i in data["faq"]]


def editor_sections(artist: Artist) -> list[dict]:
    """The editable fields grouped by section, for the editor next to the preview."""
    content, locks = current_content(artist)

    def field(path, label, kind="line"):
        return {
            "path": path,
            "label": label,
            "value": text_at(content, path),
            "locked": path in locks,
            "multiline": kind == "text",
        }

    facts = [
        field(f"facts.{i}", _("Informacja %(n)d") % {"n": i + 1})
        for i in range(len(content["facts"]))
    ]
    faq = []
    for i in range(len(content["faq"])):
        faq.append(field(f"faq.{i}.question", _("Pytanie %(n)d") % {"n": i + 1}))
        faq.append(field(f"faq.{i}.answer", _("Odpowiedź %(n)d") % {"n": i + 1}, "text"))
    groups = {
        "tagline": [field("tagline", _("Hasło pod nazwą"))],
        "facts": facts,
        "about": [field("about", _("Tekst „O artyście”"), "text")],
        "schools": [field("for_schools", _("Tekst „Dla szkół i przedszkoli”"), "text")],
        "faq": faq,
    }
    return [{"key": k, "label": SECTION_LABELS[k], "fields": groups[k]} for k in SECTIONS]
