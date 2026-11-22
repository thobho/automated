"""Profile generation (US-2.5A): request, background run and status.

    generation = request_generation(artist, "manual")   # a `trwa` row + a job on the AI queue
    run_generation(generation.pk)                       # the job: AI call, schema check, finish

`request_generation` records the run through `quality.start_generation` right away (so the artist
sees `trwa` at once and a second request is refused), the job calls the AI only through
`apps.profiles.ai`, checks the reply against the JSON Schema and closes the run with
`finish_generation`: ``gotowa`` or ``błąd`` with a readable reason. Hard validator findings go
through up to 2 repair rounds (`repair.py`); what is still not clean ends as ``do przeglądu``
(manual admin review), never as ``gotowa``. No other retries. Reasons, logs and
the database never hold prompt or reply text, e-mails or tokens.
"""

import json
import logging
import time
from datetime import timedelta

from django.conf import settings
from django.db import transaction
from django.utils import timezone
from django.utils.translation import gettext as _

from apps.artists.models import Artist
from apps.core import jobs
from apps.core.logs import pseudonymise_user
from apps.quality import services as quality
from apps.quality.models import Generation

from . import ai, inputs, pages, repair, validation, validator
from .generator_components import COMPONENTS, INSTRUCTIONS

logger = logging.getLogger("apps.profiles.generation")

PURPOSE = "profile_draft"


class GenerationRefused(Exception):
    """A generation cannot be started now. `message` is shown to the artist (Polish)."""

    def __init__(self, message):
        super().__init__(str(message))
        self.message = message


def _log(event: str, generation: Generation, **extra) -> None:
    logger.info(
        event.replace("_", " "),
        extra={
            "event": event,
            "user": pseudonymise_user(generation.artist.user_id),
            "generation": generation.pk,
            **extra,
        },
    )


def latest_generation(artist: Artist) -> Generation | None:
    return Generation.objects.filter(artist=artist).order_by("-started_at", "-pk").first()


def _fail(generation: Generation, reason, *, code: str, started: float) -> Generation:
    finished = quality.finish_generation(
        generation, None, [str(reason)], 0, Generation.Status.ERROR
    )
    _log("generation_failed", finished, code=code, duration_ms=_elapsed_ms(started))
    return finished


def _elapsed_ms(started: float) -> int:
    return int((time.monotonic() - started) * 1000)


def close_stale(artist: Artist) -> None:
    """Finish a run that never ended (worker killed) so it cannot block new requests."""
    limit = timezone.now() - timedelta(seconds=settings.GENERATION_STALE_SECONDS)
    for generation in Generation.objects.filter(
        artist=artist, status=Generation.Status.RUNNING, started_at__lt=limit
    ):
        _fail(
            generation,
            _("Generowanie zostało przerwane. Spróbuj ponownie."),
            code="stale",
            started=time.monotonic(),
        )


def request_generation(artist: Artist, trigger: str, *, section: str = "") -> Generation:
    """Record a running generation and queue its job (the one-section job when `section` is
    given, US-2.6). Raises `GenerationRefused` while another one is running for this artist
    (nothing is queued then)."""
    from . import tasks  # tasks import this module

    close_stale(artist)
    with transaction.atomic():
        Artist.objects.select_for_update().filter(pk=artist.pk).first()  # one request at a time
        if Generation.objects.filter(artist=artist, status=Generation.Status.RUNNING).exists():
            raise GenerationRefused(_("Generowanie profilu już trwa. Poczekaj na wynik."))
        generation = quality.start_generation(artist, trigger, COMPONENTS)
    # After the commit, so the job always finds the row.
    try:
        if section:
            jobs.enqueue(tasks.regenerate_section, generation_id=generation.pk, section=section)
        else:
            jobs.enqueue(tasks.generate_profile, generation_id=generation.pk)
    except Exception:
        logger.exception("profile generation job could not be queued")
        _fail(
            generation,
            _("Nie udało się zlecić generowania. Spróbuj ponownie."),
            code="enqueue",
            started=time.monotonic(),
        )
        raise GenerationRefused(_("Nie udało się zlecić generowania. Spróbuj ponownie.")) from None
    _log("generation_requested", generation, trigger=trigger, section=section)
    return generation


def _messages(data: dict) -> list[dict]:
    return [
        {"role": "system", "content": INSTRUCTIONS.text()},
        {"role": "user", "content": json.dumps(data, ensure_ascii=False)},
    ]


def run_generation(generation_id: int) -> Generation | None:
    """The job body. Returns the finished generation (None when it is missing or finished)."""
    generation = Generation.objects.select_related("artist").filter(pk=generation_id).first()
    if generation is None or generation.finished:
        return None
    started = time.monotonic()
    try:
        data = inputs.build_input(generation.artist)
        result = ai.complete(
            _messages(data),
            schema=validation.profile_schema(),
            purpose=PURPOSE,
            max_cost_usd=settings.AI_PER_CALL_CAP_USD,
            user_ref=generation.artist_id,
            generation=generation,
        )
    except ai.AICapExceeded:
        return _fail(
            generation,
            _("Limit kosztów AI został osiągnięty. Spróbuj ponownie później."),
            code="cost_cap",
            started=started,
        )
    except ai.AIDisabled:
        return _fail(
            generation, _("Generowanie przez AI jest wyłączone."), code="disabled", started=started
        )
    except ai.AIProviderError as exc:
        if exc.code == "invalid_json":
            reason = _("Odpowiedź AI nie jest poprawnym JSON-em.")
        else:
            reason = _("Usługa AI zwróciła błąd. Spróbuj ponownie.")
        return _fail(generation, reason, code=exc.code, started=started)
    except ai.AIError:
        return _fail(generation, _("Nie udało się wywołać AI."), code="ai_error", started=started)
    except Exception:
        logger.exception("profile generation crashed", extra={"generation": generation.pk})
        return _fail(
            generation, _("Nieoczekiwany błąd generowania."), code="unexpected", started=started
        )

    errors = validation.schema_errors(result.data)
    if errors:
        reason = _("Odpowiedź AI nie pasuje do schematu profilu (%(where)s).") % {
            "where": "; ".join(errors[:5])
        }
        return _fail(generation, reason, code="schema", started=started)
    try:
        sources = inputs.collect_sources(generation.artist, data)
        report = validator.validate_profile(result.data, sources)
    except Exception:
        logger.exception("profile validation crashed", extra={"generation": generation.pk})
        return _fail(
            generation, _("Nieoczekiwany błąd generowania."), code="validator", started=started
        )
    profile, rounds, stopped = result.data, 0, ""
    if not report.ok:
        # Hard violations: up to 2 repair rounds, then manual review (US-2.5C). Soft ones never.
        outcome = repair.repair_profile(generation, data, sources, profile, report)
        profile, report, rounds, stopped = (
            outcome.result,
            outcome.report,
            outcome.rounds,
            outcome.stopped,
        )
    status = Generation.Status.READY if report.ok else Generation.Status.REVIEW
    warnings = [finding.line() for finding in report.soft]
    report_data = report.as_dict()
    if rounds or stopped:
        report_data["repair"] = {"rounds": rounds, "stopped": stopped}
    if stopped and not report.ok:
        warnings.append(
            _("Poprawki przerwane: %(reason)s") % {"reason": repair.STOP_REASONS[stopped]}
        )
    finished = quality.finish_generation(
        generation, profile, warnings, rounds, status, report=report_data
    )
    _log(
        "generation_ready" if report.ok else "generation_needs_review",
        finished,
        duration_ms=_elapsed_ms(started),
        hard=len(report.hard),
        soft=len(report.soft),
        repair_rounds=rounds,
        repair_stopped=stopped,
    )
    if finished.status == Generation.Status.READY:
        pages.record_generated(finished)  # a held (`do przeglądu`) run saves no version
    return finished
