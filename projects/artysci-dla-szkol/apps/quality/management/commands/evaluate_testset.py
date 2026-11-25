import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.test import override_settings

from apps.profiles.management.commands.ai_smoke import key_from_file
from apps.quality import evaluation, testset


class Command(BaseCommand):
    help = (
        "Run the generator on the test set and evaluate every package: validator result, "
        "expectations and an independent AI review (6 dimensions, 1-5). Prints one line per "
        "package and a summary. Needs QUALITY_LAB_ENABLED; synthetic packages only. With "
        "--key-file it uses the real OpenRouter client (spends money); otherwise AI_CLIENT."
    )

    def add_arguments(self, parser):
        parser.add_argument("--package", action="append", default=[], help="slug (repeatable)")
        parser.add_argument("--level", choices=testset.LEVELS, help="only packages of this level")
        parser.add_argument("--output", type=Path, help="write the JSON report to this file")
        parser.add_argument("--resume", type=int, metavar="RUN_ID", help="finish an incomplete run")
        parser.add_argument("--key-file", type=Path, help="dotenv file with OPENROUTER_API_KEY")

    def handle(self, *args, **options):
        if options["resume"] and (options["package"] or options["level"]):
            raise CommandError("--resume takes no --package or --level: the run has its own.")
        overrides = {}
        if options["key_file"]:
            overrides = {
                "AI_CLIENT": "openrouter",
                "OPENROUTER_API_KEY": key_from_file(options["key_file"]),
            }
        try:
            testset.require_enabled()
            with override_settings(**overrides):
                if options["resume"]:
                    run = evaluation.resume(options["resume"])
                else:
                    run = evaluation.start_run(options["package"], options["level"] or "")
                    run = evaluation.evaluate(run)
        except (testset.LabDisabled, testset.PackageError, evaluation.EvaluationRefused) as exc:
            raise CommandError(str(exc)) from None
        self._print(run)
        if options["output"]:
            options["output"].write_text(
                json.dumps(evaluation.report(run), ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            self.stdout.write(f"report: {options['output']}")

    def _print(self, run):
        for row in run.evaluations.order_by("slug"):
            self.stdout.write(evaluation.package_line(row))
        data = evaluation.summary(run)
        self.stdout.write(f"run {run.pk}: {run.get_status_display()} {run.note}".rstrip())
        self.stdout.write(
            f"packages: {data['packages']}/{data['expected_packages']}, hard rules passed: "
            f"{data['hard_pass']}/{data['packages']}, failed expectations: "
            f"{data['expectations_failed']}, reviews missing: {data['unscored']}, "
            f"unverified quotes: {data['unverified_quotes']}"
        )
        self.stdout.write("mean per dimension (scored packages): " + _means(data["means"]))
        for level, means in data["means_by_level"].items():
            self.stdout.write(f"  {level}: " + _means(means))
        self.stdout.write(f"cost: {data['cost_usd']} USD")


def _means(means: dict) -> str:
    return " ".join(
        f"{name}={'-' if item['mean'] is None else item['mean']}({item['scored']})"
        for name, item in means.items()
    )
