"""`manage.py import_rspo <path>`: upsert the RSPO CSV export ("Pobierz CSV" on rspo.gov.pl)
into `RspoEntry` and run the domain rule. Prints counts only, never row content."""

from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from apps.institutions import services


class Command(BaseCommand):
    help = "Import the RSPO CSV export (upsert by RSPO number; safe to run again)."

    def add_arguments(self, parser):
        parser.add_argument("path", type=Path, help="CSV file exported from rspo.gov.pl")

    def handle(self, *args, path: Path, **options):
        try:
            data = path.read_bytes()
        except OSError as error:
            raise CommandError(f"cannot read {path}: {error.strerror}") from None
        try:
            report = services.import_rspo(data)
        except services.RspoImportError as error:
            raise CommandError(f"import_rspo: {error}") from None
        self.stdout.write(f"import_rspo: {report.summary()}")
        if not report.has_email_column:
            self.stdout.write("import_rspo: no e-mail column, the domain rule is off")
