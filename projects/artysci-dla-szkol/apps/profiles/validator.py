"""Hard-rule validator of a generated profile (US-2.5B, D5, D59).

    sources = inputs.collect_sources(artist)
    report = validate_profile(result_json, sources)   # ValidationReport: .hard, .soft, .ok

Deterministic: no AI, no network, no database (the sources are collected beforehand). Every
finding has a rule code, a JSON path and a Polish message the repair step (US-2.5C) can hand
back to the model. This file is the generator's `validator` component (`generator_components.py`):
change it only together with a version bump there.

Rules are listed in the README ("Walidator twardych reguł"); to add one, write a function
`_rule_x(profile, sources) -> list[Finding]`, add it to `HARD_RULES` or `SOFT_RULES`, give the
code a named constant and add a passing and a failing test.
"""

import re
from collections.abc import Callable, Iterator
from dataclasses import dataclass, field

# --- rule codes -----------------------------------------------------------------------------
RULE_NUMBERS = "liczby i ceny tylko ze źródła"
RULE_QUOTES = "opinie dosłownie"
RULE_MEDIA = "zdjęcia i filmy tylko z materiałów artysty"
RULE_PHRASES = "bez języka procesu i bez dodanych obietnic"
RULE_FACTS = "fakty"
RULE_LENGTHS = "limity długości"
RULE_PUPIL = "opinie tylko od dorosłych i instytucji"  # D125: never a child's opinion
RULE_HEDGE = "zastrzeżenie ze źródła"  # soft: "około 200" must not become "200" (D125)
SOFT_VAGUE = "mało konkretny opis"
SOFT_MISSING = "brak sekcji"

# --- thresholds and phrase lists (named constants; changing one needs a version bump) -------
FACT_MAX_CHARS = 22
# Maximum characters per field (a value one over the limit is a hard finding).
LENGTH_LIMITS = {
    "hero.headline": 70,
    "hero.subheadline": 160,
    "hero.button_label": 30,
    "description.paragraph": 800,
    "description.total": 2500,
    "schools.headline": 80,
    "schools.point": 160,
    "schools.age_range": 40,
    "schools.requirement": 160,
    "offers.tagline": 120,
    "gallery.alt": 140,
    "faq.question": 120,
    "faq.answer": 500,
    "seo.title": 60,
    "seo.description": 160,
}
# Process language: the text talks about the source material instead of the artist.
BANNED_PROCESS_PHRASES = (
    "w materiałach",
    "w przesłanych materiałach",
    "z przesłanych materiałów",
    "na podstawie przesłanych",
    "na podstawie materiałów",
    "na podstawie podanych informacji",
    "według materiałów",
    "w źródłach",
    "w kwestionariuszu",
    "w ankiecie",
    "jako model językowy",
)
# Promises the artist never made.
PROMISE_PHRASES = (
    "gwarantujemy",
    "gwarantuję",
    "gwarantowan",
    "gwarancja",
    "zagwarantowan",
    "100% satysfakcji",
    "100% gwarancji",
    "zwrot pieniędzy",
    "bez ryzyka",
    "na pewno się spodoba",
)
# An author that is a child or pupil: a pupil word ("uczeń", "uczniowie", "Samorząd Uczniowski"),
# a class ("klasa 3", "klasy II", "kl. 3") or a trailing class mark (", 3b").
PUPIL_AUTHOR = re.compile(
    r"\bucze[nń]|\buczni|\bdziec[koi]|\bprzedszkolak|\bzerówk|\bklas[aęy]\b|\bkl\.|"
    r"(?:^|[,\s])\d{1,2}\s?[a-z]\s*$",
    re.I,
)
# An adult role wins over a pupil word ("wychowawczyni klasy 3b", "Rada Rodziców Uczniów").
# Institutions ("SP 5 w Gdyni", "Przedszkole nr 4") have no pupil word and need no marker.
ADULT_AUTHOR = re.compile(
    r"nauczyciel|wychowaw|dyrektor|pedagog|organizator|rodzic|\brad[aay]\b|opiekun|koordynator|"
    r"terapeut|bibliotekarz|animator|instruktor",
    re.I,
)
# A hedge in front of a number: the page must keep the same one ("około 200" is neither "200"
# nor "ponad 200"). Each word maps to its meaning, so "ok." keeps "około".
HEDGE_WORDS = {
    "około": "około",
    "ok.": "około",
    "ponad": "ponad",
    "prawie": "prawie",
    "niemal": "prawie",
    "blisko": "blisko",
}
HEDGE_LOOKBACK_CHARS = 14  # how far before a number a hedge word may stand
VALUE_PREVIEW_CHARS = 120  # an offending value is cut to this length in a finding
VAGUE_MIN_CHARS = 80  # a description shorter than this is vague by itself


@dataclass(frozen=True)
class Finding:
    rule: str
    path: str  # JSON path such as `$.faq[1].answer`
    message: str  # Polish, usable as a repair instruction
    value: str = ""

    def as_dict(self) -> dict:
        return {"rule": self.rule, "path": self.path, "message": self.message, "value": self.value}

    def line(self) -> str:
        return f"[{self.rule}] {self.path}: {self.message}"


@dataclass
class ValidationReport:
    hard: list[Finding] = field(default_factory=list)
    soft: list[Finding] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.hard

    def as_dict(self) -> dict:
        return {
            "ok": self.ok,
            "hard": [f.as_dict() for f in self.hard],
            "soft": [f.as_dict() for f in self.soft],
        }


@dataclass(frozen=True)
class Sources:
    """What the profile may be built from (see `inputs.collect_sources`)."""

    texts: tuple[str, ...] = ()  # site text, PDF text, video titles, questionnaire, offers, basics
    photo_ids: frozenset = frozenset()  # ready photos and video frames of the artist
    video_ids: frozenset = frozenset()  # ready video and link materials of the artist
    material_ids: frozenset = frozenset()  # every ready material of the artist
    offer_ids: frozenset = frozenset()
    links: frozenset = frozenset()  # (provider, video id) of the artist's own links
    anchors: tuple[str, ...] = ()  # offer titles, city, name: "concrete" words for the soft rule


def _preview(value) -> str:
    text = str(value)
    return text if len(text) <= VALUE_PREVIEW_CHARS else text[:VALUE_PREVIEW_CHARS] + "…"


def _squash(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _path(*parts) -> str:
    return "$" + "".join(f"[{p}]" if isinstance(p, int) else f".{p}" for p in parts)


# --- walking the profile ----------------------------------------------------------------------


def public_texts(profile: dict) -> Iterator[tuple[str, str]]:
    """(path, text) of every text the public page shows, except testimonial quotes."""
    hero = profile.get("hero") or {}
    for key in ("headline", "subheadline", "button_label"):
        yield _path("hero", key), hero.get(key) or ""
    for i, fact in enumerate(profile.get("facts") or []):
        yield _path("facts", i, "label"), fact.get("label") or ""
        yield _path("facts", i, "value"), fact.get("value") or ""
    for i, text in enumerate((profile.get("description") or {}).get("paragraphs") or []):
        yield _path("description", "paragraphs", i), text
    schools = profile.get("schools") or {}
    yield _path("schools", "headline"), schools.get("headline") or ""
    yield _path("schools", "age_range"), schools.get("age_range") or ""
    for key in ("points", "requirements"):
        for i, text in enumerate(schools.get(key) or []):
            yield _path("schools", key, i), text
    for i, offer in enumerate(profile.get("offers") or []):
        yield _path("offers", i, "tagline"), offer.get("tagline") or ""
    for i, caption in enumerate((profile.get("gallery") or {}).get("captions") or []):
        yield _path("gallery", "captions", i, "alt"), caption.get("alt") or ""
    for i, item in enumerate(profile.get("faq") or []):
        yield _path("faq", i, "question"), item.get("question") or ""
        yield _path("faq", i, "answer"), item.get("answer") or ""
    seo = profile.get("seo") or {}
    yield _path("seo", "title"), seo.get("title") or ""
    yield _path("seo", "description"), seo.get("description") or ""
    for i, item in enumerate(profile.get("testimonials") or []):
        yield _path("testimonials", i, "author"), item.get("author") or ""


# --- numbers ---------------------------------------------------------------------------------

# A number not glued to a preceding letter: "1 200", "1.200,50", "45", "4–9" gives 4 and 9.
_NUMBER = re.compile(r"(?<![^\W\d_])\d+(?:[   .,]\d{3}(?!\d))*(?:[.,]\d+)?")


def normalise_number(raw: str) -> str:
    """ "1 200", "1.200" and "1200,00" all give "1200"; "1,5" gives "1.5"."""
    text = re.sub(r"[   ]", "", raw)
    if re.fullmatch(r"\d{1,3}([.,]\d{3})+", text):  # thousands separators only
        text = re.sub(r"[.,]", "", text)
    else:
        match = re.fullmatch(r"(\d{1,3}(?:[.,]\d{3})+)[.,](\d+)", text)  # 1.200,50
        if match:
            text = re.sub(r"[.,]", "", match.group(1)) + "." + match.group(2)
        text = text.replace(",", ".")
    whole, _, fraction = text.partition(".")
    whole = whole.lstrip("0") or "0"
    fraction = fraction.rstrip("0")
    return f"{whole}.{fraction}" if fraction else whole


def numbers_in(text: str) -> set[str]:
    return {normalise_number(match.group()) for match in _NUMBER.finditer(text)}


def _rule_numbers(profile: dict, sources: Sources) -> list[Finding]:
    allowed = set()
    for text in sources.texts:
        allowed |= numbers_in(text)
    findings = []
    for path, text in public_texts(profile):
        for match in _NUMBER.finditer(_LINK.sub(" ", text)):  # ids inside links are not numbers
            number = normalise_number(match.group())
            if number in allowed:
                continue
            findings.append(
                Finding(
                    RULE_NUMBERS,
                    path,
                    f"Liczba „{match.group()}” nie występuje w materiałach artysty. "
                    "Usuń ją albo użyj liczby ze źródła.",
                    _preview(match.group()),
                )
            )
    return findings


# --- testimonials ------------------------------------------------------------------------------


def _rule_quotes(profile: dict, sources: Sources) -> list[Finding]:
    haystacks = [_squash(t) for t in sources.texts]
    findings = []
    for i, item in enumerate(profile.get("testimonials") or []):
        quote = _squash(item.get("quote") or "")
        if quote and not any(quote in haystack for haystack in haystacks):
            findings.append(
                Finding(
                    RULE_QUOTES,
                    _path("testimonials", i, "quote"),
                    "Opinia musi być cytatem dosłownie ze źródła. Przepisz ją bez zmian albo usuń.",
                    _preview(quote),
                )
            )
    return findings


def _rule_pupil(profile: dict, sources: Sources) -> list[Finding]:
    findings = []
    for i, item in enumerate(profile.get("testimonials") or []):
        author = item.get("author") or ""
        if PUPIL_AUTHOR.search(author) and not ADULT_AUTHOR.search(author):
            findings.append(
                Finding(
                    RULE_PUPIL,
                    _path("testimonials", i, "author"),
                    "Opinia pochodzi od dziecka lub ucznia. Na stronie są tylko opinie dorosłych "
                    "i instytucji (nauczyciel, dyrekcja, organizator). Usuń tę opinię.",
                    _preview(author),
                )
            )
    return findings


# --- hedges kept from the source (soft) -------------------------------------------------------


def _hedges_before(text: str, start: int) -> set[str]:
    """The meanings of the hedge words just before a number (empty: stated exactly)."""
    before = text[max(0, start - HEDGE_LOOKBACK_CHARS) : start].lower()
    return {meaning for word, meaning in HEDGE_WORDS.items() if word in before}


def _rule_hedge(profile: dict, sources: Sources) -> list[Finding]:
    """A number the source gives only with a hedge ("około 200") is written without it."""
    hedged: dict[str, set[str]] = {}  # number -> the hedges the source uses with it
    plain: set[str] = set()
    for text in sources.texts:
        for match in _NUMBER.finditer(text):
            number = normalise_number(match.group())
            if hedges := _hedges_before(text, match.start()):
                hedged.setdefault(number, set()).update(hedges)
            else:
                plain.add(number)
    for number in plain:  # the source also states it exactly somewhere
        hedged.pop(number, None)
    findings = []
    for path, text in public_texts(profile):
        flat = _LINK.sub(" ", text)
        for match in _NUMBER.finditer(flat):
            source_hedges = hedged.get(normalise_number(match.group()))
            if source_hedges and not source_hedges & _hedges_before(flat, match.start()):
                findings.append(
                    Finding(
                        RULE_HEDGE,
                        path,
                        f"Źródło podaje „{match.group()}” z zastrzeżeniem (np. „około”). "
                        "Zachowaj to samo zastrzeżenie jak w źródle albo pomiń to twierdzenie.",
                        _preview(match.group()),
                    )
                )
    return findings


# --- photos, videos, links ----------------------------------------------------------------------

_LINK = re.compile(
    r"(?:https?://)?(?:[\w-]+\.)*(?:youtube\.com|youtu\.be|vimeo\.com)[^\s\"'<>)]*", re.I
)
_YOUTUBE_ID = re.compile(r"(?:youtu\.be/|[?&]v=|/embed/|/shorts/|/live/)([\w-]{6,})", re.I)
_VIMEO_ID = re.compile(r"vimeo\.com/(?:[\w/]*/)?(\d+)", re.I)


def link_identity(url: str) -> tuple[str, str] | None:
    """(provider, video id) of a YouTube or Vimeo link, None when no id can be read."""
    if re.search(r"vimeo\.com", url, re.I):
        match = _VIMEO_ID.search(url)
        return ("vimeo", match.group(1)) if match else None
    match = _YOUTUBE_ID.search(url)
    return ("youtube", match.group(1)) if match else None


def _ids(profile: dict) -> Iterator[tuple[str, object, str]]:
    """(path, id, what it must be): `photo`, `video`, `material`, `offer`."""
    main = (profile.get("hero") or {}).get("main_photo_id")
    if main is not None:
        yield _path("hero", "main_photo_id"), main, "photo"
    gallery = profile.get("gallery") or {}
    for i, value in enumerate(gallery.get("photo_ids") or []):
        yield _path("gallery", "photo_ids", i), value, "photo"
    for i, value in enumerate(gallery.get("video_ids") or []):
        yield _path("gallery", "video_ids", i), value, "video"
    for i, caption in enumerate(gallery.get("captions") or []):
        yield _path("gallery", "captions", i, "material_id"), caption.get("material_id"), "material"
    for i, item in enumerate(profile.get("testimonials") or []):
        if item.get("source_material_id") is not None:
            yield (
                _path("testimonials", i, "source_material_id"),
                item["source_material_id"],
                ("material"),
            )
    for i, offer in enumerate(profile.get("offers") or []):
        yield _path("offers", i, "offer_id"), offer.get("offer_id"), "offer"


def _rule_media(profile: dict, sources: Sources) -> list[Finding]:
    allowed = {
        "photo": sources.photo_ids,
        "video": sources.video_ids,
        "material": sources.material_ids | sources.photo_ids,
        "offer": sources.offer_ids,
    }
    names = {"photo": "zdjęcie", "video": "film", "material": "materiał", "offer": "oferta"}
    findings = []
    for path, value, kind in _ids(profile):
        if value not in allowed[kind]:
            findings.append(
                Finding(
                    RULE_MEDIA,
                    path,
                    f"Id {value}: {names[kind]} nie należy do gotowych materiałów artysty. "
                    "Użyj tylko identyfikatorów z danych wejściowych.",
                    _preview(value),
                )
            )
    texts = list(public_texts(profile))
    texts += [
        (_path("testimonials", i, "quote"), item.get("quote") or "")
        for i, item in enumerate(profile.get("testimonials") or [])
    ]
    for path, text in texts:
        for match in _LINK.finditer(text):
            identity = link_identity(match.group())
            if identity is None or identity not in sources.links:
                findings.append(
                    Finding(
                        RULE_MEDIA,
                        path,
                        "Link do YouTube lub Vimeo nie pochodzi z linków artysty. Usuń go.",
                        _preview(match.group()),
                    )
                )
    return findings


# --- process language and promises --------------------------------------------------------------


def _rule_phrases(profile: dict, sources: Sources) -> list[Finding]:
    findings = []
    for path, text in public_texts(profile):
        lowered = _squash(text).lower()
        for phrase in (*BANNED_PROCESS_PHRASES, *PROMISE_PHRASES):
            if phrase in lowered:
                kind = "język procesu" if phrase in BANNED_PROCESS_PHRASES else "obietnica"
                findings.append(
                    Finding(
                        RULE_PHRASES,
                        path,
                        f"Zwrot „{phrase}” jest niedozwolony ({kind}). Napisz to inaczej, "
                        "bez odwołań do materiałów i bez obietnic.",
                        phrase,
                    )
                )
    return findings


# --- facts and lengths ---------------------------------------------------------------------------


def _rule_facts(profile: dict, sources: Sources) -> list[Finding]:
    findings = []
    for i, fact in enumerate(profile.get("facts") or []):
        for key in ("label", "value"):
            text = fact.get(key) or ""
            path = _path("facts", i, key)
            if len(text) > FACT_MAX_CHARS:
                findings.append(
                    Finding(
                        RULE_FACTS,
                        path,
                        f"Fakt ma {len(text)} znaków, dozwolone jest {FACT_MAX_CHARS}. Skróć go.",
                        _preview(text),
                    )
                )
            if "(" in text or ")" in text:
                findings.append(
                    Finding(RULE_FACTS, path, "Fakt nie może zawierać nawiasów.", _preview(text))
                )
    return findings


def _length_checks(profile: dict) -> Iterator[tuple[str, str, str]]:
    """(limit key, path, text)."""
    hero = profile.get("hero") or {}
    for key in ("headline", "subheadline", "button_label"):
        yield f"hero.{key}", _path("hero", key), hero.get(key) or ""
    paragraphs = (profile.get("description") or {}).get("paragraphs") or []
    for i, text in enumerate(paragraphs):
        yield "description.paragraph", _path("description", "paragraphs", i), text
    yield "description.total", _path("description", "paragraphs"), "".join(paragraphs)
    schools = profile.get("schools") or {}
    yield "schools.headline", _path("schools", "headline"), schools.get("headline") or ""
    yield "schools.age_range", _path("schools", "age_range"), schools.get("age_range") or ""
    for i, text in enumerate(schools.get("points") or []):
        yield "schools.point", _path("schools", "points", i), text
    for i, text in enumerate(schools.get("requirements") or []):
        yield "schools.requirement", _path("schools", "requirements", i), text
    for i, offer in enumerate(profile.get("offers") or []):
        yield "offers.tagline", _path("offers", i, "tagline"), offer.get("tagline") or ""
    for i, caption in enumerate((profile.get("gallery") or {}).get("captions") or []):
        yield "gallery.alt", _path("gallery", "captions", i, "alt"), caption.get("alt") or ""
    for i, item in enumerate(profile.get("faq") or []):
        yield "faq.question", _path("faq", i, "question"), item.get("question") or ""
        yield "faq.answer", _path("faq", i, "answer"), item.get("answer") or ""
    seo = profile.get("seo") or {}
    yield "seo.title", _path("seo", "title"), seo.get("title") or ""
    yield "seo.description", _path("seo", "description"), seo.get("description") or ""


def _rule_lengths(profile: dict, sources: Sources) -> list[Finding]:
    findings = []
    for key, path, text in _length_checks(profile):
        limit = LENGTH_LIMITS[key]
        if len(text) > limit:
            findings.append(
                Finding(
                    RULE_LENGTHS,
                    path,
                    f"Tekst ma {len(text)} znaków, limit to {limit}. Skróć go.",
                    _preview(text),
                )
            )
    return findings


# --- soft rules ------------------------------------------------------------------------------


def _rule_vague(profile: dict, sources: Sources) -> list[Finding]:
    paragraphs = (profile.get("description") or {}).get("paragraphs") or []
    text = " ".join(paragraphs)
    if not text.strip():
        return []  # a missing description is a missing section, not a vague one
    lowered = text.lower()
    concrete = (
        re.search(r"\d", text) or any(a and a.lower() in lowered for a in sources.anchors)
    ) and len(text) >= VAGUE_MIN_CHARS
    if concrete:
        return []
    return [
        Finding(
            SOFT_VAGUE,
            _path("description", "paragraphs"),
            "Opis jest mało konkretny: brak liczby, miejsca lub nazwy oferty.",
        )
    ]


def _rule_missing(profile: dict, sources: Sources) -> list[Finding]:
    gallery = profile.get("gallery") or {}
    checks = (
        ("facts", profile.get("facts"), "fakty"),
        ("description", (profile.get("description") or {}).get("paragraphs"), "opis"),
        ("schools", (profile.get("schools") or {}).get("points"), "sekcja dla szkół"),
        ("gallery", gallery.get("photo_ids"), "zdjęcia w galerii"),
        ("testimonials", profile.get("testimonials"), "opinie"),
        ("faq", profile.get("faq"), "FAQ"),
    )
    return [
        Finding(SOFT_MISSING, _path(key), f"Brak sekcji: {label}.")
        for key, value, label in checks
        if not value
    ]


HARD_RULES: tuple[Callable[[dict, Sources], list[Finding]], ...] = (
    _rule_numbers,
    _rule_quotes,
    _rule_pupil,
    _rule_media,
    _rule_phrases,
    _rule_facts,
    _rule_lengths,
)
SOFT_RULES: tuple[Callable[[dict, Sources], list[Finding]], ...] = (
    _rule_vague,
    _rule_missing,
    _rule_hedge,
)


def validate_profile(result_json: dict, sources: Sources) -> ValidationReport:
    """Check a profile that already matches the JSON Schema against the hard and soft rules."""
    report = ValidationReport()
    for rule in HARD_RULES:
        report.hard.extend(rule(result_json, sources))
    for rule in SOFT_RULES:
        report.soft.extend(rule(result_json, sources))
    return report
