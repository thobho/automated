from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError
from django.core.validators import validate_email

from apps.accounts import services


class Command(BaseCommand):
    help = (
        "Give an e-mail address the admin role (D37). Server only: no form or view can do it. "
        "The admin logs in with the normal e-mail link or code."
    )

    def add_arguments(self, parser):
        parser.add_argument("email")

    def handle(self, *args, email, **options):
        try:
            validate_email(email)
        except ValidationError as exc:
            raise CommandError("not a valid e-mail address") from exc
        try:
            user, created = services.create_admin(email)
        except services.AdminRefused as exc:
            raise CommandError(
                f"this account already has the {exc.args[0]} role; one account = one role"
            ) from exc
        self.stdout.write(f"admin {'created' if created else 'updated'}: user id {user.pk}")
