"""Backfill of the quality checks (US-2.4): checks every ready photo and video that has no result
of the current `CHECKS_VERSION`. Idempotent: a second run finds nothing to do.

    python manage.py check_materials [--force]
"""

from django.core.management.base import BaseCommand

from apps.artists import checks


class Command(BaseCommand):
    help = "Run the quality checks on ready photos and videos that have no current result."

    def add_arguments(self, parser):
        parser.add_argument(
            "--force", action="store_true", help="check every ready photo and video again"
        )

    def handle(self, *args, **options):
        counts = checks.backfill(force=options["force"])
        self.stdout.write(
            f"checked: {counts['checked']}, skipped: {counts['skipped']} "
            f"(checks version {checks.CHECKS_VERSION})"
        )
