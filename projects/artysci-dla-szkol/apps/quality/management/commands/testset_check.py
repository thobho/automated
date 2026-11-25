from django.core.management.base import BaseCommand, CommandError

from apps.quality import testset


class Command(BaseCommand):
    help = (
        "Validate every package of the generator test set and print a table (slug, level, "
        "type, expectations). Exits non-zero and names the package and the problem when one "
        "is invalid. Needs QUALITY_LAB_ENABLED."
    )

    def handle(self, *args, **options):
        try:
            testset.require_enabled()
        except testset.LabDisabled as exc:
            raise CommandError(str(exc)) from None
        report = testset.check_all()
        rows = [("slug", "origin", "level", "type", "expectations")]
        failures = []
        for folder, package, problems in report:
            if problems:
                failures += [f"{folder}: {problem}" for problem in problems]
            if package is not None and not problems:
                rows.append(
                    (
                        package["slug"],
                        package["origin"],
                        package["level"],
                        package["artist"]["type"],
                        str(len(package["expectations"])),
                    )
                )
        widths = [max(len(row[i]) for row in rows) for i in range(len(rows[0]))]
        for row in rows:
            self.stdout.write(
                "  ".join(
                    cell.ljust(width) for cell, width in zip(row, widths, strict=True)
                ).rstrip()
            )
        valid = len(rows) - 1
        self.stdout.write(f"{valid} valid package(s) of {len(report)}")
        if failures:
            raise CommandError("invalid package(s):\n" + "\n".join(failures))
