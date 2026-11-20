import json

from django.core.management.base import BaseCommand, CommandError

from apps.quality import services
from apps.quality.models import Generation


class Command(BaseCommand):
    help = (
        "Print one profile generation as JSON: component versions, input fingerprint, status, "
        "warnings, repair rounds, duration and cost (no prompt or reply text)."
    )

    def add_arguments(self, parser):
        parser.add_argument("generation_id", type=int)

    def handle(self, *args, generation_id, **options):
        try:
            generation = Generation.objects.get(pk=generation_id)
        except Generation.DoesNotExist:
            raise CommandError(f"No generation {generation_id}.") from None
        summary = services.generation_summary(generation)
        self.stdout.write(json.dumps(summary, indent=2, ensure_ascii=False))
