"""Inquiries: requests institutions send to artists about a visit."""

from django.apps import AppConfig


class InquiriesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.inquiries"
    label = "inquiries"
