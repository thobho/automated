"""Trust: verification, references and reports that make artists trustworthy."""

from django.apps import AppConfig


class TrustConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.trust"
    label = "trust"
