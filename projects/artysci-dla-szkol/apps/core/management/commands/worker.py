from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError

from apps.core.jobs import QUEUES


class Command(BaseCommand):
    help = "Run the Procrastinate job worker on all queues (default, ai, media, email)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--once",
            action="store_true",
            help="Process the jobs that are due, then exit (no waiting).",
        )
        parser.add_argument("--concurrency", type=int, default=2)

    def handle(self, *args, **options):
        if options["concurrency"] < 1:
            raise CommandError("--concurrency must be at least 1")
        self.stdout.write("worker: started, queues=" + ",".join(QUEUES))
        call_command(
            "procrastinate",
            "worker",
            "--queues",
            ",".join(QUEUES),
            "--concurrency",
            str(options["concurrency"]),
            *(["--one-shot"] if options["once"] else []),
        )
