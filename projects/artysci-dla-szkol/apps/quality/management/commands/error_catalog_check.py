from django.core.management.base import BaseCommand, CommandError

from apps.quality import catalog, testset


class Command(BaseCommand):
    help = (
        "Check the error catalog (US-11.7): schema, rule codes and instruction anchors, every "
        "regression case. One line per entry; exits non-zero and names the entry on any error. "
        "Needs QUALITY_LAB_ENABLED (validator cases load synthetic packages)."
    )

    def handle(self, *args, **options):
        try:
            testset.require_enabled()
        except testset.LabDisabled as exc:
            raise CommandError(str(exc)) from None
        try:
            results = catalog.check()
        except catalog.CatalogError as exc:
            raise CommandError("error catalog:\n" + "\n".join(exc.problems)) from None
        for result in results:
            self.stdout.write(result.line())
        failed = [r for r in results if not r.ok]
        self.stdout.write(f"{len(results) - len(failed)} of {len(results)} entries ok")
        if failed:
            raise CommandError(
                f"{len(failed)} entry(ies) failed:\n" + "\n".join(r.line() for r in failed)
            )
