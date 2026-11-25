from django.core.management.base import BaseCommand, CommandError

from apps.artists.models import Material, Offer
from apps.quality import services, testset


class Command(BaseCommand):
    help = (
        "Create or update the synthetic artist of one test-set package (--package <slug>) or of "
        "every package. Loading an unchanged package again changes nothing. Needs "
        "QUALITY_LAB_ENABLED; synthetic packages only."
    )

    def add_arguments(self, parser):
        parser.add_argument("--package", help="slug of one package (default: all)")

    def handle(self, *args, **options):
        try:
            testset.require_enabled()
            slugs = (
                [options["package"]]
                if options["package"]
                else [folder for folder, _, _ in testset.check_all()]
            )
            for slug in slugs:
                result = testset.load(slug)
                artist = result.artist
                self.stdout.write(
                    f"{slug}: {'loaded' if result.changed else 'unchanged'} "
                    f"artist={artist.pk} email={testset.artist_email(slug)} "
                    f"materials={Material.objects.filter(artist=artist).count()} "
                    f"offers={Offer.objects.filter(artist=artist).count()} "
                    f"fingerprint={services.input_fingerprint(artist)[:16]}"
                )
        except (testset.LabDisabled, testset.PackageError) as exc:
            raise CommandError(str(exc)) from None
