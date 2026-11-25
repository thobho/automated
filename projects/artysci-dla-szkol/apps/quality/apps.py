"""Quality (E11): checks and scores for the content quality of artist pages."""

from django.apps import AppConfig


class QualityConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.quality"
    label = "quality"

    def ready(self):
        from . import reviewer  # noqa: F401  (registers the reviewer components, v0.1)
