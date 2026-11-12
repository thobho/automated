"""Jobs admin: Procrastinate's admin, made truly read-only.

Procrastinate's `ProcrastinateJobAdmin` forbids add/change/delete but ships retry, cancel and
abort bulk actions. We re-register it without actions. This module is autodiscovered after
`procrastinate.contrib.django` (INSTALLED_APPS order), so the original is already registered.
"""

from django.contrib import admin
from procrastinate.contrib.django.admin import ProcrastinateJobAdmin
from procrastinate.contrib.django.models import ProcrastinateJob


class ReadOnlyJobAdmin(ProcrastinateJobAdmin):
    actions = None

    def get_actions(self, request):
        return {}


if admin.site.is_registered(ProcrastinateJob):
    admin.site.unregister(ProcrastinateJob)
admin.site.register(ProcrastinateJob, ReadOnlyJobAdmin)
