"""Automatic repair of a generated profile (US-2.5C, D5, D46, D59, D63).

    outcome = repair_profile(generation, data, sources, result, report)

When the validator found hard violations, the model gets the previous result, the findings (rule
code, path, message; never the offending text) and the same source input, and answers with a
corrected profile. At most `MAX_ROUNDS` rounds. The loop ends at the first clean result, after the
last round, or early with a `stopped` code when the cost cap is reached, the AI is off or fails,
or a reply is invalid. It never raises for those: the caller sends an unclean outcome to manual
review (`do przeglądu`), never to `gotowa`. Soft findings never start a repair.

Every round is one `AICall` linked to the generation (through `ai.complete(generation=)`). No
prompt or reply text is stored.
"""

import json
import logging
from dataclasses import dataclass

from django.conf import settings
from django.utils.translation import gettext_lazy as _

from . import ai, validation, validator
from .generator_components import INSTRUCTIONS

logger = logging.getLogger("apps.profiles.repair")

PURPOSE = "profile_repair"
MAX_ROUNDS = 2

STOP_COST_CAP = "cost_cap"
STOP_DISABLED = "disabled"
STOP_INVALID_JSON = "invalid_json"
STOP_SCHEMA = "schema"
STOP_PROVIDER = "provider"
STOP_VALIDATOR = "validator"

STOP_REASONS = {
    STOP_COST_CAP: _("Limit kosztów AI został osiągnięty."),
    STOP_DISABLED: _("Generowanie przez AI jest wyłączone."),
    STOP_INVALID_JSON: _("Odpowiedź poprawki nie jest poprawnym JSON-em."),
    STOP_SCHEMA: _("Odpowiedź poprawki nie pasuje do schematu profilu."),
    STOP_PROVIDER: _("Usługa AI zwróciła błąd podczas poprawki."),
    STOP_VALIDATOR: _("Nieoczekiwany błąd walidatora podczas poprawki."),
}


@dataclass
class RepairOutcome:
    result: dict  # the last valid profile (the repaired one when a round succeeded)
    report: validator.ValidationReport  # its validation
    rounds: int  # repair calls made
    stopped: str = ""  # a STOP_* code when the loop ended early

    @property
    def clean(self) -> bool:
        return self.report.ok


def findings_payload(report: validator.ValidationReport) -> list[dict]:
    """What the model is told: rule, path and message. The offending value is left out."""
    return [{"rule": f.rule, "path": f.path, "message": f.message} for f in report.hard]


def repair_messages(data: dict, result: dict, report: validator.ValidationReport) -> list[dict]:
    payload = {
        "task": "repair",
        "previous_result": result,
        "findings": findings_payload(report),
        "input": data,
    }
    return [
        {"role": "system", "content": INSTRUCTIONS.text()},
        {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
    ]


def _round(generation, data, sources, result, report):
    """One repair call. Returns (result, report) or raises `_Stop`."""
    try:
        reply = ai.complete(
            repair_messages(data, result, report),
            schema=validation.profile_schema(),
            purpose=PURPOSE,
            max_cost_usd=settings.AI_PER_CALL_CAP_USD,
            user_ref=generation.artist_id,
            generation=generation,
        )
    except ai.AICapExceeded:
        raise _Stop(STOP_COST_CAP, called=False) from None
    except ai.AIDisabled:
        raise _Stop(STOP_DISABLED, called=False) from None
    except ai.AIProviderError as exc:
        raise _Stop(STOP_INVALID_JSON if exc.code == "invalid_json" else STOP_PROVIDER) from None
    except ai.AIError:
        raise _Stop(STOP_PROVIDER) from None
    if validation.schema_errors(reply.data):
        raise _Stop(STOP_SCHEMA)
    try:
        return reply.data, validator.validate_profile(reply.data, sources)
    except Exception:
        logger.exception(
            "profile validation crashed in repair", extra={"generation": generation.pk}
        )
        raise _Stop(STOP_VALIDATOR) from None


class _Stop(Exception):
    def __init__(self, code: str, *, called: bool = True):
        super().__init__(code)
        self.code = code
        self.called = called


def repair_profile(generation, data, sources, result, report) -> RepairOutcome:
    """Repair `result` until the validator finds no hard violation or the rounds run out."""
    outcome = RepairOutcome(result, report, 0)
    while not outcome.clean and outcome.rounds < MAX_ROUNDS:
        try:
            outcome.result, outcome.report = _round(
                generation, data, sources, outcome.result, outcome.report
            )
        except _Stop as stop:
            outcome.rounds += 1 if stop.called else 0
            outcome.stopped = stop.code
            break
        outcome.rounds += 1
    return outcome
