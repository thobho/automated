"""Regenerate one section of the page (US-2.6, D5, D46, D59, D63).

    generation = request_section(artist, "about")   # a `trwa` run (trigger `section`) + a job
    run_section(generation.pk, "about")             # the job: one AI call, validator, repair

The AI gets the same source input as the full run plus the current texts and the locked fields of
the section as fixed text. Only the section's fields are taken from the reply; locked fields are
put back as the artist wrote them. At most `repair.MAX_ROUNDS` repair rounds, only for hard
findings inside the section (not for locked text, which is the artist's own). On failure or a
reached cost cap nothing is saved: the current version stays and the run ends as `błąd` with a
Polish reason. Success creates a `regenerated` version. No prompt or reply text is stored.
"""

import json
import logging
import time

from django.conf import settings
from django.utils.translation import gettext as _

from apps.quality import services as quality
from apps.quality.models import Generation

from . import ai, inputs, pages, repair, validation, validator
from . import generation as generations
from .generator_components import INSTRUCTIONS
from .models import PageVersion

logger = logging.getLogger("apps.profiles.sections")

PURPOSE = "profile_section"

# Where a section lives in the profile JSON: findings outside it are not this run's business.
SECTION_PATHS = {
    "tagline": "$.hero.headline",
    "facts": "$.facts",
    "about": "$.description",
    "schools": "$.schools.points",
    "faq": "$.faq",
}


def request_section(artist, section: str) -> Generation:
    """Queue the regeneration of one section. Raises `GenerationRefused` (Polish message) for an
    unknown section or while another run of this artist is going."""
    if section not in pages.SECTIONS:
        raise generations.GenerationRefused(_("Nieznana sekcja."))
    return generations.request_generation(artist, Generation.Trigger.SECTION, section=section)


def _section_locks(locks, section: str) -> list[str]:
    owned = pages.SECTIONS[section]
    return [p for p in locks if p.split(".")[0] in owned]


def _messages(section, current, fixed, data) -> list[dict]:
    payload = {"task": "section", "section": section, "current": current, "fixed": fixed}
    payload["input"] = data
    return [
        {"role": "system", "content": INSTRUCTIONS.text()},
        {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
    ]


def _merge(section: str, reply_profile: dict, current: dict, locks) -> dict:
    """`current` with the section's texts from the reply, locked fields kept."""
    fresh = pages.content_from_profile(reply_profile)
    merged = dict(current)
    for key in pages.SECTIONS[section]:
        merged[key] = fresh[key]
    return pages.apply_locks(merged, current, locks)


def _section_report(section: str, profile: dict, sources, locks) -> validator.ValidationReport:
    """The validator's report limited to this section and without the artist's locked text."""
    full = validator.validate_profile(profile, sources)
    prefix = SECTION_PATHS[section]
    skip = tuple(pages.profile_path(p) for p in _section_locks(locks, section))
    hard = [
        f for f in full.hard if f.path.startswith(prefix) and not (skip and f.path.startswith(skip))
    ]
    return validator.ValidationReport(hard=hard, soft=[])


class _Failed(Exception):
    def __init__(self, reason, code):
        super().__init__(code)
        self.reason, self.code = reason, code


def _call(messages, generation, purpose) -> dict:
    """One AI call; a profile dict or `_Failed` with a Polish reason."""
    try:
        reply = ai.complete(
            messages,
            schema=validation.profile_schema(),
            purpose=purpose,
            max_cost_usd=settings.AI_PER_CALL_CAP_USD,
            user_ref=generation.artist_id,
            generation=generation,
        )
    except ai.AICapExceeded:
        raise _Failed(
            _("Limit kosztów AI został osiągnięty. Spróbuj ponownie później."), "cost_cap"
        ) from None
    except ai.AIDisabled:
        raise _Failed(_("Generowanie przez AI jest wyłączone."), "disabled") from None
    except ai.AIProviderError as exc:
        if exc.code == "invalid_json":
            raise _Failed(_("Odpowiedź AI nie jest poprawnym JSON-em."), exc.code) from None
        raise _Failed(_("Usługa AI zwróciła błąd. Spróbuj ponownie."), exc.code) from None
    except ai.AIError:
        raise _Failed(_("Nie udało się wywołać AI."), "ai_error") from None
    if validation.schema_errors(reply.data):
        raise _Failed(_("Odpowiedź AI nie pasuje do schematu profilu."), "schema")
    return reply.data


def run_section(generation_id: int, section: str) -> Generation | None:
    """The job body. Returns the finished run (None when it is missing or already finished)."""
    generation = Generation.objects.select_related("artist").filter(pk=generation_id).first()
    if generation is None or generation.finished:
        return None
    started = time.monotonic()
    artist = generation.artist
    try:
        if section not in pages.SECTIONS:
            raise _Failed(_("Nieznana sekcja."), "section")
        current, locks = pages.current_content(artist)
        data = inputs.build_input(artist)
        sources = inputs.collect_sources(artist, data)
        fixed = {p: pages.text_at(current, p) for p in _section_locks(locks, section)}
        profile = _call(_messages(section, current, fixed, data), generation, PURPOSE)
        rounds = 0
        merged = _merge(section, profile, current, locks)
        checked = pages.profile_for_validation(merged, profile)
        report = _section_report(section, checked, sources, locks)
        while not report.ok and rounds < repair.MAX_ROUNDS:
            rounds += 1
            profile = _call(
                repair.repair_messages(data, checked, report), generation, repair.PURPOSE
            )
            merged = _merge(section, profile, current, locks)
            checked = pages.profile_for_validation(merged, profile)
            report = _section_report(section, checked, sources, locks)
        if not report.ok:
            raise _Failed(
                _("Nowy tekst nie spełnia zasad nawet po poprawkach. Zostawiliśmy obecną wersję."),
                "invalid",
            )
    except _Failed as failed:
        return _fail(generation, failed, started)
    except Exception:
        logger.exception("section regeneration crashed", extra={"generation": generation.pk})
        return _fail(
            generation, _Failed(_("Nieoczekiwany błąd generowania."), "unexpected"), started
        )

    finished = quality.finish_generation(
        generation, checked, [], rounds, Generation.Status.READY, report=report.as_dict()
    )
    # The version is built from the newest content: an edit made while the job ran is kept.
    latest, latest_locks = pages.current_content(artist)
    new = pages.apply_locks(
        {**latest, **{k: merged[k] for k in pages.SECTIONS[section]}}, latest, latest_locks
    )
    pages.create_version(
        artist, new, PageVersion.Source.REGENERATED, latest_locks, generation=finished
    )
    logger.info(
        "section regenerated",
        extra={"event": "section_ready", "generation": finished.pk, "section": section},
    )
    return finished


def _fail(generation, failed: _Failed, started: float) -> Generation:
    finished = quality.finish_generation(
        generation, None, [str(failed.reason)], 0, Generation.Status.ERROR
    )
    logger.info(
        "section regeneration failed",
        extra={
            "event": "section_failed",
            "generation": finished.pk,
            "code": failed.code,
            "duration_ms": int((time.monotonic() - started) * 1000),
        },
    )
    return finished
