"""Registry-level check of the jobs admin; runs on SQLite too (no database access)."""

from django.contrib import admin
from procrastinate.contrib.django.models import ProcrastinateJob


def test_jobs_admin_has_no_actions_and_forbids_writes(rf):
    model_admin = admin.site._registry[ProcrastinateJob]
    request = rf.get("/")
    assert model_admin.get_actions(request) == {}
    assert not model_admin.has_add_permission(request)
    assert not model_admin.has_change_permission(request)
    assert not model_admin.has_delete_permission(request)
