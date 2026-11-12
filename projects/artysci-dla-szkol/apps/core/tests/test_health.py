from unittest import mock

import pytest
from django.db import DatabaseError
from django.urls import reverse

from apps.core import services

pytestmark = pytest.mark.django_db


def test_healthz_ok(client):
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"db": "ok"}
    assert "no-cache" in response["Cache-Control"]


def test_healthz_db_down(client):
    with mock.patch("django.db.backends.utils.CursorWrapper.execute", side_effect=DatabaseError):
        response = client.get(reverse("core:healthz"))
    assert response.status_code == 503
    assert response.json() == {"db": "error"}


def test_healthz_rejects_post(client):
    assert client.post("/healthz").status_code == 405


def test_readyz_ok(client):
    response = client.get("/readyz")
    assert response.status_code == 200
    assert response.json() == {"db": "ok", "migrations": "ok"}


def test_readyz_db_down(client):
    with mock.patch.object(services, "check_database", return_value=services.ERROR):
        response = client.get("/readyz")
    assert response.status_code == 503
    assert response.json() == {"db": "error", "migrations": "error"}


def test_readyz_pending_migrations(client):
    with mock.patch(
        "django.db.migrations.executor.MigrationExecutor.migration_plan",
        return_value=[("fake", False)],
    ):
        response = client.get("/readyz")
    assert response.status_code == 503
    assert response.json() == {"db": "ok", "migrations": "pending"}


def test_check_migrations_db_error():
    with mock.patch(
        "django.db.migrations.executor.MigrationExecutor.__init__", side_effect=DatabaseError
    ):
        assert services.check_migrations() == services.ERROR


def test_home_page_polish_with_vendored_htmx(client):
    response = client.get("/")
    assert response.status_code == 200
    html = response.content.decode()
    assert '<html lang="pl">' in html
    assert "/static/vendor/htmx/htmx.min.js" in html
    assert "unpkg" not in html and "cdn" not in html.lower()
    assert "Artyści dla szkół" in html
