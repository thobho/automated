from django.core.management.base import BaseCommand, CommandError

from apps.quality import registry


class Command(BaseCommand):
    help = (
        "Check the registered generator components against components.json; with --write, "
        "add new versions to it (a recorded version is never rewritten: bump the version)."
    )

    def add_arguments(self, parser):
        parser.add_argument("--write", action="store_true", help="Record new versions.")

    def handle(self, *args, write, **options):
        components = registry.registry.all()
        manifest = registry.load_manifest()
        if write:
            try:
                updated = registry.updated_manifest(components, manifest)
            except registry.RegistryError as exc:
                raise CommandError(str(exc)) from None
            registry.write_manifest(updated)
            self.stdout.write(f"components.json: {len(components)} component(s) recorded.")
            return
        errors = registry.manifest_errors(components, manifest)
        if errors:
            raise CommandError("\n".join(errors))
        self.stdout.write(f"components.json matches {len(components)} component(s).")
