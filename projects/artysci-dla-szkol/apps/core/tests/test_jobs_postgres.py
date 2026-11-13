"""Jobs against a real PostgreSQL (skipped on the SQLite fallback; CI sets DATABASE_URL)."""

import pytest
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.db import connection
from procrastinate.contrib.django.models import ProcrastinateJob

from apps.core import jobs, tasks
from apps.core.models import PingRecord

pytestmark = [
    pytest.mark.skipif(connection.vendor != "postgresql", reason="needs PostgreSQL"),
    pytest.mark.django_db(transaction=True),
]


def run_worker():
    call_command("worker", "--once")


def test_ping_end_to_end_and_idempotency():
    assert jobs.enqueue(tasks.ping, idempotency_key="pg-1", token="pg") is not None
    assert jobs.enqueue(tasks.ping, idempotency_key="pg-1", token="pg") is None
    run_worker()
    assert PingRecord.objects.filter(token="pg").count() == 1
    assert list(ProcrastinateJob.objects.values_list("status", flat=True)) == ["succeeded"]


def test_jobs_admin_page_lists_jobs(client):
    jobs.enqueue(tasks.ping, token="adm")
    admin = get_user_model().objects.create_superuser(email="a@example.invalid", password="x")
    client.force_login(admin)
    response = client.get("/django-admin/procrastinate/procrastinatejob/")
    assert response.status_code == 200
    assert "core.ping" in response.content.decode()
