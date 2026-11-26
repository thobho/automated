"""Screenshot review by a vision model (US-11.3B, D59, D60, D63).

    result = review_screenshots(package, {360: png, 1440: png}, artist_pk)

One call per package (purpose `page_screenshot_review`): two full-page screenshots, own
instructions and reply schema (reviewer components v0.1). It sees no generator reasoning and no
validator report. D59: in the MVP only screenshots of `synthetic` packages may go to AI; any other
origin is refused here, in code, before the adapter is reached. An invalid reply, an AI error or a
cost cap gives `brak oceny` with the reason; the other results of the package stay.
"""

import json
import logging
from dataclasses import dataclass, field
from functools import cache
from pathlib import Path

from django.conf import settings
from jsonschema import Draft202012Validator

from apps.profiles import ai

from .registry import Component, registry

logger = logging.getLogger("apps.quality.screenshots")

PURPOSE = "page_screenshot_review"
REVIEW_VERSION = "0.1"
VIEWPORTS = (360, 1440)
KINDS = ("empty_place", "cut_off_content", "overlapping_content")
OK = "ok"
PROBLEM = "problem"
MISSING = "brak oceny"

INSTRUCTIONS = registry.register(
    Component(
        "instructions",
        "page_screenshot_review",
        REVIEW_VERSION,
        files=("apps/quality/prompts/screenshot_review_instructions.md",),
    )
)
SCHEMA = registry.register(
    Component(
        "schema",
        "page_screenshot_review",
        REVIEW_VERSION,
        files=("apps/quality/schemas/screenshot_review.json",),
    )
)
COMPONENTS = (INSTRUCTIONS, SCHEMA)


class ScreenshotRefused(Exception):
    """The screenshots may not be sent (not a `synthetic` package, wrong set of images)."""


@dataclass
class ScreenshotReview:
    status: str  # OK or MISSING
    reason: str = ""
    viewports: dict = field(default_factory=dict)  # "360" -> {"verdict", "problems"}
    call_ids: list = field(default_factory=list)
    cost_usd: str = "0"


@cache
def review_schema() -> dict:
    path = Path(__file__).resolve().parent / "schemas" / "screenshot_review.json"
    return json.loads(path.read_text("utf-8"))


def build_messages(shots: dict[int, bytes]) -> list[dict]:
    """Instructions and the two images; nothing else reaches the model."""
    text = "Zrzuty ekranu strony: pierwszy 360 px, drugi 1440 px."
    parts = [{"type": "text", "text": text}]
    parts += [{"type": "image", "data": shots[width]} for width in VIEWPORTS]
    return [
        {"role": "system", "content": INSTRUCTIONS.text()},
        {"role": "user", "content": parts},
    ]


def schema_errors(data) -> list[str]:
    """Paths and rules only: never the reply's own text. A verdict must agree with its list."""
    validator = Draft202012Validator(review_schema())
    errors = [
        "$"
        + "".join(f"[{p}]" if isinstance(p, int) else f".{p}" for p in e.absolute_path)
        + f" ({e.validator})"
        for e in sorted(validator.iter_errors(data), key=lambda e: list(map(str, e.absolute_path)))
    ]
    if errors:
        return errors
    for width, viewport in data["viewports"].items():
        if (viewport["verdict"] == OK) != (not viewport["problems"]):
            errors.append(f"$.viewports.{width} (verdict does not match the problems)")
    return errors


def parse_reply(data) -> ScreenshotReview:
    errors = schema_errors(data)
    if errors:
        return ScreenshotReview(
            MISSING, "odpowiedź niezgodna ze schematem: " + "; ".join(errors[:5])
        )
    return ScreenshotReview(OK, viewports=data["viewports"])


def review_screenshots(package: dict, shots: dict[int, bytes], artist_pk) -> ScreenshotReview:
    """Raises `ScreenshotRefused` for a package that is not `synthetic` (nothing is sent)."""
    if package.get("origin") != "synthetic":
        raise ScreenshotRefused(
            "screenshots go to AI only for packages with origin 'synthetic' (D59)"
        )
    if set(shots) != set(VIEWPORTS):
        raise ScreenshotRefused("the review needs exactly the 360 px and 1440 px screenshots")
    try:
        result = ai.complete(
            build_messages(shots),
            schema=review_schema(),
            purpose=PURPOSE,
            max_cost_usd=settings.AI_PER_CALL_CAP_USD,
            user_ref=artist_pk,
            allow_images=True,
        )
    except ai.AICapExceeded:
        return ScreenshotReview(MISSING, "limit kosztów AI")
    except ai.AIDisabled:
        return ScreenshotReview(MISSING, "AI wyłączone")
    except ai.AIProviderError as exc:
        return ScreenshotReview(MISSING, f"błąd odpowiedzi AI ({exc.code})")
    except ai.AIError:
        return ScreenshotReview(MISSING, "nie udało się wywołać AI")
    except Exception:  # a dropped connection etc.: this package has no review, the run goes on
        logger.exception("screenshot review failed", extra={"event": "screenshot_review_failed"})
        return ScreenshotReview(MISSING, "nie udało się wywołać AI (błąd połączenia)")
    review = parse_reply(result.data)
    review.call_ids = [result.call_id]
    review.cost_usd = str(result.cost_usd)
    return review
