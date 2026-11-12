"""Admin panel: staff tools for moderation and support (separate from Django admin)."""

from django.apps import AppConfig


class AdminpanelConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.adminpanel"
    label = "adminpanel"
