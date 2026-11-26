import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.test import override_settings

from apps.profiles.management.commands.ai_smoke import key_from_file
from apps.quality import evaluation, pagemetrics, testset
from apps.quality.models import EvaluationRun


class Command(BaseCommand):
    help = (
        "Measure the owner preview of every test-set package at 360 and 1440 px: screenshots, "
        "axe violations, a Lighthouse mobile score with LCP and a screenshot review by a vision "
        "model. Needs a running server on the same database (--base-url), QUALITY_LAB_ENABLED "
        "and Playwright. With --run the metrics are stored for that evaluation run. Exits "
        "non-zero when a package has no axe or Lighthouse result or a critical axe violation. "
        "With --key-file the review uses the real OpenRouter client (spends money)."
    )

    def add_arguments(self, parser):
        parser.add_argument("--base-url", default="http://127.0.0.1:8000")
        parser.add_argument("--run", type=int, metavar="RUN_ID", help="an evaluation run")
        parser.add_argument("--package", action="append", default=[], help="slug (repeatable)")
        parser.add_argument("--level", choices=testset.LEVELS, help="only packages of this level")
        parser.add_argument("--output", type=Path, default=Path("page-metrics"))
        parser.add_argument(
            "--no-review", action="store_true", help="skip the AI screenshot review"
        )
        parser.add_argument("--key-file", type=Path, help="dotenv file with OPENROUTER_API_KEY")

    def handle(self, *args, **options):
        overrides = {}
        if options["key_file"]:
            overrides = {
                "AI_CLIENT": "openrouter",
                "OPENROUTER_API_KEY": key_from_file(options["key_file"]),
            }
        run = None
        try:
            testset.require_enabled()
            if options["run"]:
                run = EvaluationRun.objects.filter(pk=options["run"]).first()
                if run is None:
                    raise CommandError(f"run {options['run']}: no such run")
            slugs = options["package"] or (run.slugs if run else [])
            level = options["level"] or ""
            packages = evaluation.select_packages(slugs, level)
            with override_settings(**overrides):
                results = pagemetrics.measure(
                    packages,
                    options["base_url"].rstrip("/"),
                    options["output"],
                    run=run,
                    review=not options["no_review"],
                )
        except (
            testset.LabDisabled,
            testset.PackageError,
            evaluation.EvaluationRefused,
            pagemetrics.MeasureRefused,
        ) as exc:
            raise CommandError(str(exc)) from None
        self._write(results, run, options["output"])

    def _write(self, results, run, output: Path):
        report = pagemetrics.report(results, run)
        (output / "page-metrics.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        table = pagemetrics.markdown_table(results)
        (output / "summary.md").write_text(table, encoding="utf-8")
        if run is not None:
            (output / "evaluation-report.json").write_text(
                json.dumps(evaluation.report(run), ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
        self.stdout.write(table)
        self.stdout.write(f"report: {output / 'page-metrics.json'}")
        problems = report["failures"]
        for line in problems:
            self.stderr.write(line)
        if problems:
            raise CommandError(f"{len(problems)} measurement problem(s)")
