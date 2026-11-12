"""The `jobs` admin page: Procrastinate's built-in read-only admin, served at
/django-admin/procrastinate/procrastinatejob/. Needs PostgreSQL (skipped on the SQLite fallback).
"""

import pytest
from django.contrib.auth import get_user_model
from django.db import connection
from django.urls import reverse
from procrastinate.contrib.django.models import ProcrastinateJob

from apps.core import jobs, tasks

pytestmark = [
    pytest.mark.skipif(connection.vendor != "postgresql", reason="needs PostgreSQL"),
    pytest.mark.django_db(transaction=True),
]

LIST_URL = "/django-admin/procrastinate/procrastinatejob/"


@pytest.fixture
def superuser(client):
    user = get_user_model().objects.create_superuser(email="root@example.invalid", password="x")
    client.force_login(user)
    return user


def test_anonymous_is_redirected_to_login(client):
    response = client.get(LIST_URL)
    assert response.status_code == 302
    assert "login" in response["Location"]


def test_non_staff_user_is_denied(client):
    user = get_user_model().objects.create_user(email="user@example.invalid", password="x")
    client.force_login(user)
    response = client.get(LIST_URL)
    assert response.status_code == 302  # admin sends non-staff to its login page
    assert "login" in response["Location"]


def test_staff_without_permissions_gets_403(client):
    user = get_user_model().objects.create_user(
        email="staff@example.invalid", password="x", is_staff=True
    )
    client.force_login(user)
    assert client.get(LIST_URL).status_code == 403


def test_superuser_sees_jobs_with_status_and_queue_filters(client, superuser):
    jobs.enqueue(tasks.ping, token="adm")
    page = client.get(LIST_URL).content.decode()
    assert "core.ping" in page or "c.ping" in page
    assert "Todo" in page
    assert client.get(LIST_URL + "?status=failed").status_code == 200
    assert client.get(LIST_URL + "?queue_name=default").status_code == 200


def test_page_is_read_only(client, superuser):
    job_id = jobs.enqueue(tasks.ping, token="ro")
    assert client.get(LIST_URL + "add/").status_code == 403
    detail = LIST_URL + f"{job_id}/change/"
    assert client.get(detail).status_code == 200  # view-only detail
    assert client.post(detail, {"queue_name": "x"}).status_code == 403
    delete = reverse("admin:procrastinate_procrastinatejob_delete", args=[job_id])
    assert client.post(delete, {"post": "yes"}).status_code == 403
    assert ProcrastinateJob.objects.filter(pk=job_id).exists()


@pytest.mark.parametrize("action", ["cancel", "retry", "abort"])
def test_bulk_actions_are_not_available(client, superuser, action):
    job_id = jobs.enqueue(tasks.ping, token=f"act-{action}")
    page = client.get(LIST_URL).content.decode()
    assert 'name="action"' not in page
    client.post(LIST_URL, {"action": action, "_selected_action": [job_id]})
    assert ProcrastinateJob.objects.get(pk=job_id).status == "todo"
