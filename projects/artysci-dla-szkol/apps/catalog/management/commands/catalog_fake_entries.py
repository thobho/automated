from django.core.management.base import BaseCommand, CommandError

from apps.catalog import fake


class Command(BaseCommand):
    help = (
        "Fill the catalog read model with synthetic published artists for load tests "
        "(dev/test settings only)."
    )

    def add_arguments(self, parser):
        parser.add_argument("--count", type=int, default=10000, help="How many rows to create.")
        parser.add_argument(
            "--seed", type=int, default=0, help="Random seed: same seed, same rows."
        )
        parser.add_argument(
            "--delete",
            action="store_true",
            help="Remove the synthetic fake-*@example.invalid users and their rows only.",
        )

    def handle(self, *args, **options):
        if options["delete"]:
            count = fake.delete_fake_entries()
            self.stdout.write(f"Removed {count} fake users and their catalog rows.")
            return

        try:
            count = fake.create_fake_entries(options["count"], seed=options["seed"])
        except fake.FakeEntriesRefused as error:
            self.stderr.write(str(error))
            raise CommandError(str(error)) from error
        except fake.FakeEntriesError as error:
            raise CommandError(str(error)) from error
        self.stdout.write(f"Created {count} fake catalog rows (seed={options['seed']}).")
