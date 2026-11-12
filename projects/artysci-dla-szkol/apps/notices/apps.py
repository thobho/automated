"""Notices: announcements institutions post so that artists can respond."""

from django.apps import AppConfig


class NoticesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.notices"
    label = "notices"
