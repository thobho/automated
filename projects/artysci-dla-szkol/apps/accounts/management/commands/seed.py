from django.core.management.base import BaseCommand

from apps.accounts import services
from apps.artists import services as artist_services
from apps.institutions import services as institution_services
from apps.trust import services as trust_services


class Command(BaseCommand):
    help = "Load synthetic demo data (safe to run repeatedly)."

    def handle(self, *args, **options):
        created = services.seed_users()
        documents = trust_services.seed_placeholders()
        rspo = institution_services.seed_rspo()
        artists = artist_services.seed_artists()
        members = institution_services.seed_members()
        self.stdout.write(
            f"seed: created {created['artists']} artists, {created['institutions']} institutions, "
            f"{documents} placeholder legal documents, {rspo} synthetic RSPO entries, "
            f"{artists} artist profiles, {members} institution members "
            "(offers: no model yet)"
        )
