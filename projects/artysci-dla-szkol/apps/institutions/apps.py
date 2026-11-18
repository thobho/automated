"""Institutions: schools, kindergartens and cultural centres that invite artists."""

from django.apps import AppConfig


class InstitutionsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.institutions"
    label = "institutions"

    def ready(self) -> None:
        from . import receivers

        receivers.connect()
