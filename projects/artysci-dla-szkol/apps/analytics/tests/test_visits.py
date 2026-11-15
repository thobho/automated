from datetime import date, timedelta
from unittest import mock

import pytest
from django.http import HttpResponse
from django.test import RequestFactory

from apps.analytics import services
from apps.analytics.middleware import VisitMiddleware
from apps.analytics.models import DailySalt, Visit

pytestmark = pytest.mark.django_db

UA = "Mozilla/5.0 (X11; Linux x86_64) Firefox/130.0"


def get(client, path="/", ua=UA, ip="203.0.113.5"):
    return client.get(path, HTTP_USER_AGENT=ua, REMOTE_ADDR=ip)


def test_page_view_counted_without_cookie(client):
    response = get(client)
    assert response.status_code == 200
    visit = Visit.objects.get()
    assert visit.path == "/" and visit.views == 1 and len(visit.visitor) == 32
    assert "203.0.113.5" not in visit.visitor


def test_same_client_same_day_is_one_unique_visitor(client):
    get(client)
    get(client)
    assert Visit.objects.count() == 1
    assert Visit.objects.get().views == 2


def test_different_clients_are_different_visitors(client):
    get(client)
    get(client, ip="203.0.113.6")
    assert Visit.objects.values("visitor").distinct().count() == 2


def test_hash_differs_next_day_and_old_salt_is_deleted(client):
    today = date(2026, 3, 1)
    h1 = services.visitor_hash("203.0.113.5", UA, today)
    assert services.visitor_hash("203.0.113.5", UA, today) == h1
    h2 = services.visitor_hash("203.0.113.5", UA, today + timedelta(days=1))
    assert h1 != h2
    assert list(DailySalt.objects.values_list("day", flat=True)) == [today + timedelta(days=1)]


@pytest.mark.parametrize(
    "path,ua",
    [
        ("/healthz", UA),
        ("/readyz", UA),
        ("/static/vendor/htmx/htmx.min.js", UA),
        ("/", "Googlebot/2.1 (+http://www.google.com/bot.html)"),
        ("/", "curl/8.5.0"),
        ("/", ""),
    ],
)
def test_excluded_requests_not_counted(client, path, ua):
    get(client, path=path, ua=ua)
    assert Visit.objects.count() == 0


def test_non_html_and_errors_not_counted(client):
    get(client, "/does-not-exist")
    client.post("/", HTTP_USER_AGENT=UA)
    assert Visit.objects.count() == 0


def test_analytics_failure_does_not_break_page(client):
    with mock.patch.object(services, "record_visit", side_effect=RuntimeError):
        assert get(client).status_code == 200


def test_middleware_sets_no_cookie():
    request = RequestFactory().get("/", HTTP_USER_AGENT=UA)
    response = VisitMiddleware(lambda r: HttpResponse("<p>x</p>"))(request)
    assert not response.cookies
    assert "Set-Cookie" not in response.headers
    assert Visit.objects.count() == 1


def test_long_path_truncated():
    services.record_visit("/" + "a" * 500, "203.0.113.5", UA)
    assert len(Visit.objects.get().path) == services.MAX_PATH
