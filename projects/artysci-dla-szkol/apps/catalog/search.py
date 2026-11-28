"""Polish text search of the catalog (US-4.3, D129): inflection, diacritics, one typo.

    terms = index_terms(name, offer_titles, topic_names)   # written into the read model
    entries = search(entries, "spektakl o hejcie")          # matching rows, best match first

No external service and no extension is needed to *match* (D91): the words of the read model are
reduced to light stems without Polish letters, and the query is reduced the same way.

* Inflection: `stem()` strips the common noun/adjective endings and undoes the usual stem change
  (hejcie -> hejt, teatrze -> teatr), so "hejcie" and "hejtu" meet at "hejt".
* Diacritics: letters are folded to ASCII (ł -> l, ą -> a), on both sides.
* One typo (words of 5+ letters): every indexed word is stored with its one-letter deletions, and a
  query word is looked up with its own deletions (the "symmetric delete" idea): a substitution, a
  missing or extra letter or a swapped pair all share a variant with the right word.
* Function words ("o", "w", "na", "dla", "i" ...) and one-letter tokens are dropped.

The three text columns hold the words separated and surrounded by spaces, so a word is found by
`contains " word "`; on PostgreSQL a `pg_trgm` GIN index makes that an index lookup (migration
0004).
Ranking is done on the few matching rows: a word in the name beats a word in an offer or topic,
which beats a typo-only match. The typed text is only ever used to build the query: it is never
logged or stored.
"""

import re
import unicodedata

from django.db.models import Q

MAX_QUERY_LENGTH = 100
MAX_WORDS = 8  # more words than this in a query add nothing, and each one costs a SQL condition
TYPO_MIN_LENGTH = 5  # a word this long (as typed) may contain one typo
_MIN_VARIANT = 3  # a deletion variant shorter than this matches far too much

STOP_WORDS = frozenset(
    ["o", "w", "we", "na", "dla", "i", "a", "z", "ze", "do", "od", "po", "za", "u", "to"]
    + ["się", "czy", "oraz", "lub", "albo", "przy", "pod", "nad", "bez", "że", "jak"]
)

_TOKEN = re.compile(r"[a-z0-9]+")
_FOLD = str.maketrans({"ł": "l", "Ł": "l"})

# Stem changes of the locative/dative that hide the stem: hejcie -> hejt, teatrze -> teatr.
_ALTERNATIONS = (("dzie", "d"), ("cie", "t"), ("rze", "r"))
# Endings, longest first; a stem keeps at least `_MIN_STEM` letters.
_ENDINGS = tuple(
    sorted(
        ["iach", "ami", "ach", "iem", "owi", "ego", "emu", "ych", "ich", "ymi", "imi"]
        + ["ia", "ie", "ii", "iu", "om", "ow", "ej", "ym", "im", "y", "i", "a", "e", "u", "o"],
        key=len,
        reverse=True,
    )
)
_MIN_STEM = 3


def fold(text: str) -> str:
    """Lower case without Polish letters or other accents."""
    text = text.lower().translate(_FOLD)
    return "".join(c for c in unicodedata.normalize("NFKD", text) if not unicodedata.combining(c))


def words(text: str) -> list[str]:
    """The folded words of a text, function words and single letters removed."""
    stop = {fold(w) for w in STOP_WORDS}
    return [w for w in _TOKEN.findall(fold(text)) if len(w) > 1 and w not in stop]


def stem(word: str) -> str:
    for old, new in _ALTERNATIONS:
        if word.endswith(old) and len(word) - len(old) >= 2:
            return word[: -len(old)] + new
    for ending in _ENDINGS:
        if word.endswith(ending) and len(word) - len(ending) >= _MIN_STEM:
            return word[: -len(ending)]
    return word


def variants(stemmed: str) -> set[str]:
    """The stem and its one-letter deletions (those that are still long enough)."""
    found = {stemmed}
    found.update(stemmed[:i] + stemmed[i + 1 :] for i in range(len(stemmed)))
    return {v for v in found if len(v) >= _MIN_VARIANT}


def _pack(items) -> str:
    items = sorted(set(items))
    return f" {' '.join(items)} " if items else ""


def index_terms(name: str, offer_titles: list[str], topic_names: list[str]) -> dict[str, str]:
    """The three search columns of a catalog row."""
    name_stems = {stem(w) for w in words(name)}
    other_stems = {stem(w) for t in [*offer_titles, *topic_names] for w in words(t)}
    fuzzy = set()
    for text in (name, *offer_titles, *topic_names):
        for w in words(text):
            if len(w) >= TYPO_MIN_LENGTH:
                fuzzy |= variants(stem(w))
    return {
        "search_name": _pack(name_stems),
        "search_other": _pack(other_stems),
        "search_fuzzy": _pack(fuzzy),
    }


def clean(raw: str | None) -> str:
    """The query as used and shown: trimmed, at most 100 characters, single spaces."""
    return " ".join((raw or "").split())[:MAX_QUERY_LENGTH].strip()


class Query:
    """A parsed query: for each word its stem and (for words of 5+ letters) the typo variants."""

    def __init__(self, text: str):
        self.terms: list[tuple[str, set[str]]] = []
        seen = set()
        for w in words(text):
            s = stem(w)
            if s in seen:
                continue
            seen.add(s)
            self.terms.append((s, variants(s) if len(w) >= TYPO_MIN_LENGTH else set()))
            if len(self.terms) == MAX_WORDS:
                break

    @property
    def word_count(self) -> int:
        return len(self.terms)

    def condition(self) -> Q:
        cond = Q()
        for s, typo in self.terms:
            token = f" {s} "
            cond |= Q(search_name__contains=token) | Q(search_other__contains=token)
            for v in typo:
                cond |= Q(search_fuzzy__contains=f" {v} ")
        return cond

    def score(self, entry) -> int:
        """Name match 100, offer or topic match 10, typo-only match 1, per word."""
        total = 0
        for s, typo in self.terms:
            token = f" {s} "
            if token in entry.search_name:
                total += 100
            elif token in entry.search_other:
                total += 10
            elif any(f" {v} " in entry.search_fuzzy for v in typo):
                total += 1
        return total


def search(entries, text: str) -> list | None:
    """Rows of the queryset matching any word of `text`, best first; ties keep the queryset order.
    None when the text has no searchable word (empty, or only function words): no search then."""
    query = Query(text)
    if not query.terms:
        return None
    matched = list(entries.filter(query.condition()))
    matched.sort(key=query.score, reverse=True)  # stable: ties keep the order of #205
    return matched
