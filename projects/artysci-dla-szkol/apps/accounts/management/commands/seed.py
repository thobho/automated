from django.core.management.base import BaseCommand

from apps.accounts import services
from apps.trust import services as trust_services


class Command(BaseCommand):
    help = "Load synthetic demo data (safe to run repeatedly)."

    def handle(self, *args, **options):
        created = services.seed_users()
        documents = trust_services.seed_placeholders()
        self.stdout.write(
            f"seed: created {created['artists']} artists, {created['institutions']} institutions, "
            f"{documents} placeholder legal documents (offers: no model yet)"
        )
