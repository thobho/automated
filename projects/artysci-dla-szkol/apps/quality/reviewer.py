"""Independent AI reviewer of a finished profile (US-11.3A, D13, D46, D59, D60, D63).

    result = review(artist, profile)       # one AI call through apps.profiles.ai, no retries

The reviewer is a separate call with its own instructions and reply schema (registered here, kinds
`instructions` and `schema`, but not in the generator's `COMPONENTS`). It receives only the source
input (`build_input`) and the finished profile without its `claims_audit`: never the generator
instructions, the validator findings or the repair history. The reply is checked against the
review schema; a missing dimension, a score outside 1 to 5 or invalid JSON gives no scores, never
an invented one. A quote that is not a verbatim substring of the profile's public texts (after
whitespace normalisation) is kept and marked `unverified`.
"""

import json
import re
from dataclasses import dataclass, field
from functools import cache
from pathlib import Path

from django.conf import settings
from jsonschema import Draft202012Validator

from apps.artists.models import Artist
from apps.profiles import ai, inputs

from .registry import Component, registry

PURPOSE = "profile_review"
REVIEW_VERSION = "0.1"
DIMENSIONS = ("wiernosc", "kompletnosc", "przydatnosc", "jezyk", "ton", "uczciwosc")
DIMENSION_LABELS = {
    "wiernosc": "wierność",
    "kompletnosc": "kompletność",
    "przydatnosc": "przydatność",
    "jezyk": "język",
    "ton": "ton",
    "uczciwosc": "uczciwość wobec braków",
}
OK = "ok"
MISSING = "brak oceny"  # the stored review status when there is no score

INSTRUCTIONS = registry.register(
    Component(
        "instructions",
        "profile_review",
        REVIEW_VERSION,
        files=("apps/quality/prompts/review_instructions.md",),
    )
)
SCHEMA = registry.register(
    Component(
        "schema", "profile_review", REVIEW_VERSION, files=("apps/quality/schemas/review.json",)
    )
)
COMPONENTS = (INSTRUCTIONS, SCHEMA)


class ReviewStop(Exception):
    """The AI is off or a cost cap is reached: the run must stop (nothing invented)."""


@dataclass
class ReviewResult:
    status: str  # OK or MISSING
    reason: str = ""  # why there is no score (a short code or sentence, never reply text)
    scores: dict = field(default_factory=dict)
    problems: list = field(default_factory=list)


@cache
def review_schema() -> dict:
    return json.loads(
        (Path(__file__).resolve().parent / "schemas" / "review.json").read_text("utf-8")
    )


def normalise(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def build_messages(input_data: dict, profile: dict) -> list[dict]:
    """The only thing the reviewer sees. No `claims_audit`, no findings, no history."""
    shown = {key: value for key, value in profile.items() if key != "claims_audit"}
    payload = {"source_input": input_data, "profile": shown}
    return [
        {"role": "system", "content": INSTRUCTIONS.text()},
        {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
    ]


def schema_errors(data) -> list[str]:
    """Where the reply breaks the schema (paths and rules only: never the reply's own text)."""
    validator = Draft202012Validator(review_schema())
    errors = sorted(validator.iter_errors(data), key=lambda e: list(map(str, e.absolute_path)))
    return [
        "$"
        + "".join(f"[{p}]" if isinstance(p, int) else f".{p}" for p in e.absolute_path)
        + f" ({e.validator})"
        for e in errors
    ]


def mark_quotes(problems: list[dict], profile: dict) -> list[dict]:
    """Each problem with `unverified` set when its quote is not in the public texts."""
    from .testset import all_public_texts  # testset imports models

    haystack = [normalise(text) for _, text in all_public_texts(profile)]
    marked = []
    for problem in problems:
        quote = normalise(problem["quote"])
        unverified = bool(quote) and not any(quote in text for text in haystack)
        marked.append({**problem, "quote": quote, "unverified": unverified})
    return marked


def parse_reply(data, profile: dict) -> ReviewResult:
    errors = schema_errors(data)
    if errors:
        reason = "odpowiedź recenzenta niezgodna ze schematem: " + "; ".join(errors[:5])
        return ReviewResult(MISSING, reason)
    scores = {name: data["scores"][name] for name in DIMENSIONS}
    return ReviewResult(OK, scores=scores, problems=mark_quotes(data["problems"], profile))


def review(artist: Artist, profile: dict) -> ReviewResult:
    """One review call. Raises `ReviewStop` on the kill switch or a cost cap; any other failure is
    a `MISSING` result with the reason."""
    messages = build_messages(inputs.build_input(artist), profile)
    try:
        result = ai.complete(
            messages,
            schema=review_schema(),
            purpose=PURPOSE,
            max_cost_usd=settings.AI_PER_CALL_CAP_USD,
            user_ref=artist.pk,
        )
    except (ai.AICapExceeded, ai.AIDisabled) as exc:
        raise ReviewStop(type(exc).__name__) from None
    except ai.AIProviderError as exc:
        return ReviewResult(MISSING, f"błąd odpowiedzi AI ({exc.code})")
    except ai.AIError:
        return ReviewResult(MISSING, "nie udało się wywołać AI")
    return parse_reply(result.data, profile)
