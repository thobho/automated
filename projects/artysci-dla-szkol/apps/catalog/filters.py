"""Catalog filters that live in the URL (US-4.2, D17, D102, D127).

    filters = parse(request.GET)      # unknown or malformed values are dropped, never an error
    entries = apply(entries, filters)  # AND of the set filters, on the read model only
    filters.url(page=2)                # the same filters in a link

One value per filter. The values are always checked against closed lists (voivodeships, artist
types, age groups, active dictionary entries) or parsed as whole numbers, so nothing the visitor
typed is ever echoed into the page.
"""

from dataclasses import dataclass, fields
from urllib.parse import urlencode

from django.urls import reverse
from django.utils.translation import gettext as _

from apps.artists.models import ArtistType, Audience
from apps.core.regions import Voivodeship

from . import search, services
from .models import EntryKind

MAX_NUMBER_DIGITS = 6  # a price in złoty or a time in minutes never needs more


@dataclass(frozen=True)
class Filters:
    wojewodztwo: str = ""
    rodzaj: str = ""
    wiek: str = ""
    tematyka: str = ""
    forma: str = ""
    cena_max: int | None = None
    czas_max: int | None = None
    q: str = ""  # free text (US-4.3): kept in links, never in events or logs

    def active(self) -> dict[str, str | int]:
        """The set filters in a fixed order: URL parameter -> value."""
        values = {f.name: getattr(self, f.name) for f in fields(self)}
        return {name: value for name, value in values.items() if value not in ("", None)}

    def without(self, name: str) -> "Filters":
        return Filters(**{**self.active(), name: Filters.__dataclass_fields__[name].default})

    def query(self, **extra) -> str:
        params = {**self.active(), **{k: v for k, v in extra.items() if v not in ("", None)}}
        return urlencode(params)

    def url(self, page: int | None = None, base: str | None = None, **extra) -> str:
        """`/artysci/?...` with the filters; page 1 has no `strona`."""
        query = self.query(strona=page if page and page > 1 else None, **extra)
        path = base or reverse("catalog:list")
        return f"{path}?{query}" if query else path

    def event_properties(self) -> dict[str, str | int]:
        """Names and closed-list values, numbers for price and time (no free text can get in)."""
        return {k: v for k, v in self.active().items() if k != "q"}


def _number(raw: str | None) -> int | None:
    if raw is None or not (raw.isascii() and raw.isdigit() and len(raw) <= MAX_NUMBER_DIGITS):
        return None
    value = int(raw)
    return value or None  # 0 matches nothing useful: same as "dowolny"


def _choice(raw: str | None, allowed) -> str:
    return raw if raw in allowed else ""


def parse(params) -> Filters:
    """The filters of a query string (`request.GET`)."""
    topics = {e.slug for e in services.active_entries(EntryKind.TOPIC)}
    forms = {e.slug for e in services.active_entries(EntryKind.FORM)}
    return Filters(
        wojewodztwo=_choice(params.get("wojewodztwo"), Voivodeship.values),
        rodzaj=_choice(params.get("rodzaj"), ArtistType.values),
        wiek=_choice(params.get("wiek"), Audience.values),
        tematyka=_choice(params.get("tematyka"), topics),
        forma=_choice(params.get("forma"), forms),
        cena_max=_number(params.get("cena_max")),
        czas_max=_number(params.get("czas_max")),
        q=search.clean(params.get("q")),
    )


# --- matching ------------------------------------------------------------------------------------


def offer_matches(offers: list[dict], price_max: int | None, minutes_max: int | None) -> bool:
    """At least one offer fits both limits. An offer "na zapytanie" (no price) does not fit a
    price filter, an offer without duration does not fit a duration filter."""
    if price_max is None and minutes_max is None:
        return True
    for offer in offers:
        price, duration = offer.get("price"), offer.get("duration")
        if price_max is not None and (price is None or price > price_max):
            continue
        if minutes_max is not None and (duration is None or duration > minutes_max):
            continue
        return True
    return False


def _row_matches(row, filters: Filters) -> bool:
    _pk, voivodeships, age_groups, topics, forms, offers = row
    if filters.wojewodztwo and filters.wojewodztwo not in voivodeships:
        return False
    if filters.wiek and filters.wiek not in age_groups:
        return False
    if filters.tematyka and filters.tematyka not in {t.get("slug") for t in topics}:
        return False
    if filters.forma and filters.forma not in {f.get("slug") for f in forms}:
        return False
    return offer_matches(offers, filters.cena_max, filters.czas_max)


def apply(entries, filters: Filters):
    """Narrow a `CatalogEntry` queryset. The artist type is a column; the lists and offers are
    JSON (portable across SQLite and PostgreSQL), so they are matched in Python on the already
    narrowed rows. US-4.7 revisits this if the load test asks for it."""
    if filters.rodzaj:
        entries = entries.filter(artist_type=filters.rodzaj)
    if not any((filters.wojewodztwo, filters.wiek, filters.tematyka, filters.forma)) and (
        filters.cena_max is None and filters.czas_max is None
    ):
        return entries
    rows = entries.values_list("pk", "voivodeships", "age_groups", "topics", "forms", "offers")
    return entries.filter(pk__in=[row[0] for row in rows if _row_matches(row, filters)])


# --- what the page shows -------------------------------------------------------------------------


@dataclass(frozen=True)
class Option:
    value: str
    label: str
    selected: bool = False


def options(filters: Filters) -> dict[str, list[Option]]:
    """The choices of every select, with the current one marked. "dowolny" is the empty value."""

    def build(choices, current):
        return [Option(str(v), str(label), v == current) for v, label in choices]

    return {
        "wojewodztwo": build(Voivodeship.choices, filters.wojewodztwo),
        "rodzaj": build(ArtistType.choices, filters.rodzaj),
        "wiek": build(Audience.choices, filters.wiek),
        "tematyka": build(
            [(e.slug, e.name) for e in services.active_entries(EntryKind.TOPIC)], filters.tematyka
        ),
        "forma": build(
            [(e.slug, e.name) for e in services.active_entries(EntryKind.FORM)], filters.forma
        ),
    }


def _label(filters: Filters, name: str) -> str:
    value = getattr(filters, name)
    opts = options(filters)
    if name in opts:
        shown = next((o.label for o in opts[name] if o.value == value), "")
    elif name == "q":
        return _("szukaj: %(text)s") % {"text": value}
    elif name == "cena_max":
        return _("cena do %(n)s zł") % {"n": value}
    else:
        return _("czas do %(n)s min") % {"n": value}
    titles = {
        "wojewodztwo": _("województwo"),
        "rodzaj": _("rodzaj"),
        "wiek": _("grupa wiekowa"),
        "tematyka": _("tematyka"),
        "forma": _("forma"),
    }
    return f"{titles[name]}: {shown}"


def active_links(filters: Filters) -> list[dict]:
    """One entry per set filter: its label and a link that drops only that filter."""
    return [
        {"label": _label(filters, name), "url": filters.without(name).url()}
        for name in filters.active()
    ]


def found_text(count: int) -> str:
    """ "Znaleziono N artystów" with the Polish form: 1 artystę, otherwise artystów."""
    if count == 1:
        return _("Znaleziono 1 artystę")
    return _("Znaleziono %(n)s artystów") % {"n": count}


def notice_url(filters: Filters) -> str:
    """The "Opublikuj ogłoszenie" button: the notice page with the filters and the marker that
    tells the page it was opened from empty results (`catalog_notice_cta_clicked`)."""
    # The typed text may be personal data: it does not travel into another page's URL.
    return filters.without("q").url(base="/ogloszenia/nowe/", zrodlo=NOTICE_SOURCE)


NOTICE_SOURCE = "katalog"


# --- analytics (US-4.2, D127): server side, no cookie, no personal data --------------------------


def record_search(filters: Filters, total: int, page_number: int) -> None:
    """`catalog_searched` for a filtered list, plus `catalog_no_results` when it is empty."""
    from apps.analytics import services as analytics

    if not filters.active():
        return
    props = filters.event_properties()
    # The typed text itself is never recorded: only whether there was one and how many words.
    text = (
        {"text_query": True, "word_count": search.Query(filters.q).word_count} if filters.q else {}
    )
    analytics.track("catalog_searched", result_count=total, page=page_number, **props, **text)
    if total == 0:
        analytics.track("catalog_no_results", **props)


def record_notice_click(filters: Filters) -> None:
    """`catalog_notice_cta_clicked`: the notice page was opened from the empty-results button."""
    from apps.analytics import services as analytics

    analytics.track("catalog_notice_cta_clicked", **filters.event_properties())
