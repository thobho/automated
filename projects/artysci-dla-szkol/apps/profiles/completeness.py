"""Missing items as a task list and the completeness percentage (US-2.7).

Nothing is stored: the list and the percentage are recomputed from the artist's data on every
call, so filling an item on its target screen removes it (no "done" flag).

- `CHECKLIST` is the fixed list the percentage counts (it holds the D6 publication minimum:
  name and region, description, at least one offer, child-protection statement). The percentage
  is the share of satisfied items, a whole number 0-100.
- `GAP_KINDS` is the closed mapping from the generator's `gaps[].code` (T29 schema) to a target
  screen and a check that tells whether the data now exists. An unknown code is listed without a
  button, with the generator's own message; only the `gotowa` run's gaps are read, never a held
  (`do przeglądu`) one.
- `completeness_percent(artist)` is the function the "published" analytics event (US-2.8) uses.
"""

from collections.abc import Callable
from dataclasses import dataclass

from django.utils.translation import gettext_lazy as _

from apps.artists import checks, materials
from apps.artists import services as artist_services
from apps.artists.models import Artist
from apps.quality.models import Generation
from apps.trust import services as trust

from . import pages

MESSAGE_LIMIT = 200  # an unknown gap shows the generator's text, cut to this length


@dataclass(frozen=True)
class Kind:
    key: str
    text: str  # Polish task text (lazy)
    url_name: str  # target screen; "" = no button
    done: Callable[[Artist], bool]
    button: str = ""


def _basics(artist: Artist) -> bool:
    return artist_services.basics_complete(artist)


def _description(artist: Artist) -> bool:
    return bool(pages.page_content(artist).about.strip())


def _offers(artist: Artist) -> bool:
    return artist_services.has_offers(artist)


def _statement(artist: Artist) -> bool:
    return trust.has_child_protection_statement(artist)


def _photo(artist: Artist) -> bool:
    return bool(checks.main_photo_candidates(artist))


def _questionnaire(artist: Artist) -> bool:
    return materials.questionnaire_filled(artist)


def _price(artist: Artist) -> bool:
    if artist.q_price_from_pln is not None or artist.q_price_on_request:
        return True
    return (
        artist.offers.filter(price_pln__isnull=False).exists()
        or artist.offers.filter(price_on_request=True).exists()
    )


def _max_audience(artist: Artist) -> bool:
    return artist.q_max_audience is not None


def _duration(artist: Artist) -> bool:
    return (
        artist.q_duration_minutes is not None
        or artist.offers.filter(duration_minutes__isnull=False).exists()
    )


def _age_range(artist: Artist) -> bool:
    return artist.q_age_from is not None or artist.q_age_to is not None


def _tech(artist: Artist) -> bool:
    return bool(artist.q_tech_room or artist.q_tech_power or artist.q_tech_sound)


BASICS = Kind("basics", _("Uzupełnij dane podstawowe"), "artists:basics", _basics)
DESCRIPTION = Kind("description", _("Wygeneruj opis artysty"), "profiles:generation", _description)
OFFERS = Kind("offers", _("Dodaj co najmniej jedną ofertę"), "artists:offers", _offers)
STATEMENT = Kind(
    "child_protection",
    _("Złóż oświadczenie o standardach ochrony małoletnich"),
    "artists:statements",
    _statement,
)
PHOTO = Kind("main_photo", _("Dodaj zdjęcie ze sceny"), "artists:materials_photos", _photo)
QUESTIONNAIRE = Kind(
    "questionnaire",
    _("Wypełnij kwestionariusz dla szkół"),
    "artists:questionnaire",
    _questionnaire,
)

# The fixed checklist behind the percentage (documented in the README).
CHECKLIST: tuple[Kind, ...] = (BASICS, DESCRIPTION, OFFERS, STATEMENT, PHOTO, QUESTIONNAIRE)

# Rule-based items shown even without a generation (cheap to compute from existing data).
RULE_ITEMS: tuple[Kind, ...] = (BASICS, OFFERS, STATEMENT, PHOTO, QUESTIONNAIRE, DESCRIPTION)

_PRICE = Kind("price", _("Podaj cenę lub zaznacz „cena na zapytanie”"), "artists:offers", _price)
_AUDIENCE = Kind(
    "max_audience",
    _("Podaj maksymalną liczbę widzów"),
    "artists:questionnaire",
    _max_audience,
)
_DURATION = Kind("duration", _("Podaj czas trwania"), "artists:questionnaire", _duration)
_AGE = Kind("age_range", _("Podaj wiek widzów"), "artists:questionnaire", _age_range)
_TECH = Kind("tech", _("Opisz wymagania techniczne"), "artists:questionnaire", _tech)

# Closed mapping: generator `gaps[].code` -> kind (target screen + check). Anything else is
# unknown and gets no button.
GAP_KINDS: dict[str, Kind] = {
    "no_photo": PHOTO,
    "no_main_photo": PHOTO,
    "no_stage_photo": PHOTO,
    "no_offers": OFFERS,
    "no_offer": OFFERS,
    "no_price": _PRICE,
    "no_max_audience": _AUDIENCE,
    "no_audience_size": _AUDIENCE,
    "no_duration": _DURATION,
    "no_age_range": _AGE,
    "no_age": _AGE,
    "no_tech_requirements": _TECH,
    "no_tech": _TECH,
    "no_questionnaire": QUESTIONNAIRE,
    "no_child_protection": STATEMENT,
    "no_basics": BASICS,
}


@dataclass(frozen=True)
class Task:
    key: str
    text: str
    url_name: str = ""  # empty: shown without a button

    @property
    def has_button(self) -> bool:
        return bool(self.url_name)


def _gaps(artist: Artist) -> list[dict]:
    """The `gaps` of the latest finished run, only when it is `gotowa` (a held one is hidden)."""
    record = (
        Generation.objects.filter(
            artist=artist, status__in=[Generation.Status.READY, Generation.Status.REVIEW]
        )
        .order_by("-started_at", "-pk")
        .first()
    )
    if record is None or record.status != Generation.Status.READY:
        return []
    gaps = record.result.get("gaps") if isinstance(record.result, dict) else None
    if not isinstance(gaps, list):
        return []
    return [g for g in gaps if isinstance(g, dict)]


def task_list(artist: Artist) -> list[Task]:
    """What is still missing: generator gaps first, then the rule-based items. Each kind shows
    once; an item whose data exists is dropped."""
    tasks: list[Task] = []
    seen: set[str] = set()
    for gap in _gaps(artist):
        code, message = gap.get("code"), gap.get("message")
        kind = GAP_KINDS.get(code) if isinstance(code, str) else None
        if kind is not None:
            if kind.key in seen or kind.done(artist):
                continue
            seen.add(kind.key)
            tasks.append(Task(kind.key, str(kind.text), kind.url_name))
        elif isinstance(message, str) and message.strip():
            text = message.strip()[:MESSAGE_LIMIT]
            if text not in seen:
                seen.add(text)
                tasks.append(Task(f"gap:{text}", text))
    for kind in RULE_ITEMS:
        if kind.key not in seen and not kind.done(artist):
            seen.add(kind.key)
            tasks.append(Task(kind.key, str(kind.text), kind.url_name))
    return tasks


def completeness_percent(artist: Artist) -> int:
    """Whole percent of `CHECKLIST` satisfied, 0-100."""
    satisfied = sum(1 for kind in CHECKLIST if kind.done(artist))
    return max(0, min(100, round(100 * satisfied / len(CHECKLIST))))
