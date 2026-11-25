"""Automatic evaluation of the generator test set, part 1 (US-11.3A, D13).

    run = start_run(slugs)                  # a `trwa` run with the versions and models
    finish = evaluate(run)                  # every package: generate, validate, check, review
    summary(run)                            # the numbers printed and written in the report
    report(run)                             # the JSON report (format `evaluation-report/1`)

Each package goes through the same code path as the background job (`profiles.generation.
run_generation`: first call, validator, up to 2 repair rounds), run in the foreground, and then
through the independent reviewer (`reviewer.py`, one call, no retries). A package whose review
fails keeps its other results with the review status `brak oceny` and the reason. When the AI is
switched off or a cost cap is reached the run stops, is marked `niekompletny`, and `resume`
evaluates only the missing packages (refused when a component, a model or a package changed).

Needs `QUALITY_LAB_ENABLED`; synthetic packages only (D12, D57). No prompt, instruction or reply
text is stored here or written to the report.
"""

import logging
import time
from collections import defaultdict
from datetime import timedelta
from decimal import Decimal

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from apps.profiles import generation as profile_generation
from apps.profiles.ai import budget
from apps.profiles.ai.errors import AICapExceeded, AIDisabled
from apps.profiles.generator_components import COMPONENTS as GENERATOR_COMPONENTS
from apps.profiles.models import AICall
from apps.quality import reviewer, services, testset
from apps.quality.models import EvaluationRun, Generation, PackageEvaluation

logger = logging.getLogger("apps.quality.evaluation")

REPORT_FORMAT = "evaluation-report/1"
SCORE_FIELDS = {name: f"score_{name}" for name in reviewer.DIMENSIONS}


class EvaluationRefused(Exception):
    """The run cannot start or resume. The message says why."""


class _Stop(Exception):
    """The AI is off or a cost cap is reached: stop the run, mark it incomplete. `cost` is the
    cost of a generation already paid for whose package is left for `--resume`."""

    def __init__(self, cost: Decimal = Decimal(0)):
        super().__init__()
        self.cost = cost


def _versions(components) -> dict:
    return {c.key: {"version": c.version, "content_hash": c.content_hash} for c in components}


def _selected(slugs, level) -> list[dict]:
    """The packages of the run, in slug order. Refuses an unknown, invalid or `consented` one."""
    available = {folder: package for folder, package, _ in testset.check_all() if package}
    chosen = list(slugs) if slugs else sorted(available)
    packages = []
    for slug in sorted(set(chosen)):
        if slug not in available:
            raise EvaluationRefused(f"{slug}: no such package")
        package = available[slug]
        if level and package["level"] != level:
            continue
        if package.get("origin") == "consented":
            raise EvaluationRefused(
                f"{slug}: origin 'consented' is not evaluated yet: the service has no consent "
                "record for the test set (D12)"
            )
        problems = testset.check_package(package, folder=slug)
        if problems:
            raise EvaluationRefused(f"{slug}: {problems[0]}")
        packages.append(package)
    if not packages:
        raise EvaluationRefused("no package selected")
    return packages


def package_set_hash(packages: list[dict]) -> str:
    digests = sorted((p["slug"], testset.package_digest(p)) for p in packages)
    return testset.package_digest({"packages": digests})


def start_run(slugs=(), level="") -> EvaluationRun:
    testset.require_enabled()
    packages = _selected(slugs, level)
    return EvaluationRun.objects.create(
        generator_components=_versions(GENERATOR_COMPONENTS),
        reviewer_components=_versions(reviewer.COMPONENTS),
        generator_model=settings.AI_MODEL,
        reviewer_model=settings.AI_MODEL,
        ai_client=settings.AI_CLIENT,
        package_set_hash=package_set_hash(packages),
        slugs=[p["slug"] for p in packages],
        level=level or "",
        started_at=timezone.now(),
    )


def _is_stale(run: EvaluationRun) -> bool:
    """A `trwa` run with no activity for `GENERATION_STALE_SECONDS`: its process was killed."""
    last = run.evaluations.order_by("-created_at").values_list("created_at", flat=True).first()
    limit = timezone.now() - timedelta(seconds=settings.GENERATION_STALE_SECONDS)
    return (last or run.started_at) < limit


def _can_resume(run: EvaluationRun) -> bool:
    if run.status == EvaluationRun.Status.RUNNING:
        return _is_stale(run)
    return run.status == EvaluationRun.Status.INCOMPLETE


def _check_resumable(run: EvaluationRun) -> list[dict]:
    if not _can_resume(run):
        raise EvaluationRefused(f"run {run.pk} is {run.get_status_display()}, not incomplete")
    changed = []
    if run.ai_client != settings.AI_CLIENT:
        changed.append("the AI client")
    if run.generator_components != _versions(GENERATOR_COMPONENTS):
        changed.append("a generator component")
    if run.reviewer_components != _versions(reviewer.COMPONENTS):
        changed.append("a reviewer component")
    if run.generator_model != settings.AI_MODEL or run.reviewer_model != settings.AI_MODEL:
        changed.append("the AI model")
    packages = _selected(run.slugs, "")
    if package_set_hash(packages) != run.package_set_hash:
        changed.append("a package")
    if changed:
        raise EvaluationRefused(
            f"run {run.pk} cannot be resumed: {', '.join(changed)} changed since it started"
        )
    return packages


def _cap_reached() -> bool:
    """True when the next AI call would be refused (kill switch or daily cap)."""
    try:
        budget.check_kill_switch()
        budget.check_daily_cap(Decimal(str(settings.AI_PER_CALL_CAP_USD)))
    except (AICapExceeded, AIDisabled):
        return True
    return False


def _validator_summary(generation: Generation) -> dict:
    report = generation.report or {}
    return {
        "ok": bool(report.get("ok")) if generation.report is not None else False,
        "hard": report.get("hard", []),
        "soft": report.get("soft", []),
        "repair_rounds": generation.repair_rounds,
        "repair_stopped": (report.get("repair") or {}).get("stopped", ""),
    }


def _evaluate_package(run: EvaluationRun, package: dict) -> PackageEvaluation:
    """Raises `_Stop` (nothing stored) when the AI cannot be called any more."""
    slug = package["slug"]
    started = time.monotonic()
    if _cap_reached():
        raise _Stop
    artist = testset.load_package(slug)
    record = services.start_generation(artist, Generation.Trigger.MANUAL, GENERATOR_COMPONENTS)
    generation = profile_generation.run_generation(record.pk)
    if (
        generation.status == Generation.Status.ERROR
        and not AICall.objects.filter(profile_generation=generation).exists()
        and _cap_reached()
    ):
        raise _Stop  # the first call was refused by the cap: not a result of this package

    expectations = []
    if generation.result is not None:
        expectations = [
            {"kind": r.kind, "detail": r.detail, "passed": r.passed, "message": r.message}
            for r in testset.check_expectations(package, generation.result)
        ]
    if generation.status == Generation.Status.ERROR:
        outcome = reviewer.ReviewResult(reviewer.MISSING, "generacja zakończyła się błędem")
        call_ids = []
    else:
        last_call = AICall.objects.order_by("-pk").values_list("pk", flat=True).first() or 0
        try:
            outcome = reviewer.review(artist, generation.result)
        except reviewer.ReviewStop:
            raise _Stop(generation.cost_usd or Decimal(0)) from None
        finally:
            call_ids = list(
                AICall.objects.filter(pk__gt=last_call, purpose=reviewer.PURPOSE)
                .order_by("pk")
                .values_list("pk", flat=True)
            )
    review_cost = sum(
        AICall.objects.filter(pk__in=call_ids).values_list("cost_usd", flat=True), Decimal(0)
    )
    scores = {SCORE_FIELDS[name]: outcome.scores.get(name) for name in reviewer.DIMENSIONS}
    return PackageEvaluation.objects.create(
        run=run,
        slug=slug,
        level=package["level"],
        package_hash=testset.package_digest(package),
        generation=generation,
        generation_status=generation.status,
        hard_pass=generation.status == Generation.Status.READY,
        validator=_validator_summary(generation),
        expectations=expectations,
        problems=outcome.problems,
        review_status=(
            PackageEvaluation.ReviewStatus.OK
            if outcome.status == reviewer.OK
            else PackageEvaluation.ReviewStatus.MISSING
        ),
        review_reason=outcome.reason[:300],
        review_call_ids=call_ids,
        cost_usd=(generation.cost_usd or Decimal(0)) + review_cost,
        duration_ms=int((time.monotonic() - started) * 1000),
        created_at=timezone.now(),
        **scores,
    )


def _close(run: EvaluationRun, status: str, note: str = "") -> EvaluationRun:
    total = sum((e.cost_usd for e in run.evaluations.all()), run.abandoned_cost_usd)
    run.status = status
    run.cost_usd = total
    run.note = note
    run.finished_at = timezone.now()
    run.save()
    return run


def evaluate(run: EvaluationRun, packages: list[dict] | None = None) -> EvaluationRun:
    """Evaluate the packages of `run` that have no result yet, then close the run as
    `zakończony`, or as `niekompletny` when the AI stopped (kill switch, cost cap)."""
    testset.require_enabled()
    if run.status not in (EvaluationRun.Status.RUNNING, EvaluationRun.Status.INCOMPLETE):
        raise EvaluationRefused(f"run {run.pk} is already finished")
    packages = packages or _selected(run.slugs, "")
    done = set(run.evaluations.values_list("slug", flat=True))
    for package in packages:
        if package["slug"] in done:
            continue
        try:
            _evaluate_package(run, package)
        except _Stop as stop:
            logger.warning("evaluation stopped", extra={"event": "evaluation_stopped"})
            run.abandoned_cost_usd += stop.cost
            return _close(run, EvaluationRun.Status.INCOMPLETE, "AI wyłączone lub limit kosztów")
        except BaseException:  # a crash or Ctrl-C: keep the run resumable, then fail loudly
            logger.exception("evaluation failed", extra={"event": "evaluation_failed"})
            _close(run, EvaluationRun.Status.INCOMPLETE, "przerwano błędem")
            raise
    return _close(run, EvaluationRun.Status.COMPLETE)


def resume(run_id: int) -> EvaluationRun:
    testset.require_enabled()
    run = EvaluationRun.objects.filter(pk=run_id).first()
    if run is None:
        raise EvaluationRefused(f"run {run_id}: no such run")
    packages = _check_resumable(run)
    with transaction.atomic():
        locked = EvaluationRun.objects.select_for_update().get(pk=run.pk)
        if not _can_resume(locked):
            raise EvaluationRefused(f"run {run_id} is not incomplete")
        locked.status = EvaluationRun.Status.RUNNING
        locked.finished_at = None
        locked.save()
    return evaluate(locked, packages)


# --- numbers and the report --------------------------------------------------------------------


def _mean(values: list[int]) -> float | None:
    return round(sum(values) / len(values), 2) if values else None


def _scores_of(evaluation: PackageEvaluation) -> dict:
    return {name: getattr(evaluation, field) for name, field in SCORE_FIELDS.items()}


def summary(run: EvaluationRun) -> dict:
    """Packages, hard-rule pass share, failed expectations, means per dimension (overall and per
    level; missing scores are left out and counted) and cost."""
    rows = list(run.evaluations.order_by("slug"))
    by_level = defaultdict(list)
    for row in rows:
        by_level[row.level].append(row)

    def means(group):
        out = {}
        for name in reviewer.DIMENSIONS:
            values = [s for s in (_scores_of(r)[name] for r in group) if s is not None]
            out[name] = {"mean": _mean(values), "scored": len(values)}
        return out

    failed = [
        {"slug": r.slug, "message": e["message"]}
        for r in rows
        for e in r.expectations
        if not e["passed"]
    ]
    return {
        "status": run.status,
        "packages": len(rows),
        "expected_packages": len(run.slugs),
        "hard_pass": sum(1 for r in rows if r.hard_pass),
        "hard_pass_share": round(sum(1 for r in rows if r.hard_pass) / len(rows), 2)
        if rows
        else None,
        "expectations_failed": len(failed),
        "expectations_failed_list": failed,
        "unscored": sum(1 for r in rows if r.review_status != PackageEvaluation.ReviewStatus.OK),
        "unverified_quotes": sum(
            1 for r in rows for problem in r.problems if problem.get("unverified")
        ),
        "means": means(rows),
        "means_by_level": {level: means(group) for level, group in sorted(by_level.items())},
        "cost_usd": str(run.cost_usd),
    }


def package_line(evaluation: PackageEvaluation) -> str:
    """One line per package for the command output."""
    failed = sum(1 for e in evaluation.expectations if not e["passed"])
    if evaluation.review_status == PackageEvaluation.ReviewStatus.OK:
        scores = " ".join(
            f"{name}={getattr(evaluation, field)}" for name, field in SCORE_FIELDS.items()
        )
    else:
        scores = f"brak oceny ({evaluation.review_reason})"
    unverified = sum(1 for p in evaluation.problems if p.get("unverified"))
    return (
        f"{evaluation.slug} [{evaluation.level}] generation={evaluation.generation_id} "
        f"{evaluation.generation_status} hard={'ok' if evaluation.hard_pass else 'FAIL'} "
        f"expectations_failed={failed} {scores} problems={len(evaluation.problems)} "
        f"unverified={unverified} cost={evaluation.cost_usd}"
    )


def report(run: EvaluationRun) -> dict:
    """The JSON report, format `evaluation-report/1` (see README). Synthetic data only; no key,
    prompt or instruction text."""
    packages = []
    for row in run.evaluations.select_related("generation").order_by("slug"):
        generation = row.generation
        packages.append(
            {
                "slug": row.slug,
                "level": row.level,
                "package_hash": row.package_hash,
                "generation": {
                    "id": row.generation_id,
                    "status": row.generation_status,
                    "repair_rounds": generation.repair_rounds if generation else 0,
                    "duration_ms": generation.duration_ms if generation else None,
                    "cost_usd": str(generation.cost_usd) if generation else None,
                },
                "hard_pass": row.hard_pass,
                "validator": row.validator,
                "expectations": row.expectations,
                "review": {
                    "status": row.review_status,
                    "reason": row.review_reason,
                    "scores": _scores_of(row),
                    "problems": row.problems,
                },
                "profile": generation.result if generation else None,
                "cost_usd": str(row.cost_usd),
                "duration_ms": row.duration_ms,
            }
        )
    return {
        "format": REPORT_FORMAT,
        "run": {
            "id": run.pk,
            "status": run.status,
            "note": run.note,
            "level": run.level,
            "started_at": run.started_at.isoformat(),
            "finished_at": run.finished_at.isoformat() if run.finished_at else None,
            "generator_components": run.generator_components,
            "reviewer_components": run.reviewer_components,
            "generator_model": run.generator_model,
            "reviewer_model": run.reviewer_model,
            "ai_client": run.ai_client,
            "package_set_hash": run.package_set_hash,
            "packages": run.slugs,
            "cost_usd": str(run.cost_usd),
        },
        "summary": summary(run),
        "packages": packages,
    }
