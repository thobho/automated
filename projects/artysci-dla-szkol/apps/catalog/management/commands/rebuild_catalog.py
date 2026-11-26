from django.core.management.base import BaseCommand

from apps.catalog import listing


class Command(BaseCommand):
    help = "Rebuild every row of the public catalog from the publication snapshots (idempotent)."

    def handle(self, *args, **options):
        count = listing.rebuild_all()
        self.stdout.write(f"Catalog rebuilt: {count} rows.")
