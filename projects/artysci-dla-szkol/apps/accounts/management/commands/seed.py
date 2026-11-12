from django.core.management.base import BaseCommand

from apps.accounts import services


class Command(BaseCommand):
    help = "Load synthetic demo data (safe to run repeatedly)."

    def handle(self, *args, **options):
        created = services.seed_users()
        self.stdout.write(
            f"seed: created {created['artists']} artists, {created['institutions']} institutions "
            f"(offers: no model yet)"
        )
