import re

import pytest
from django.test import Client

from apps.core.security import build_csp, build_permissions_policy, csp_nonce

pytestmark = pytest.mark.django_db


@pytest.fixture
def home(client):
    return client.get("/")


def test_csp_is_strict(home):
    csp = home["Content-Security-Policy"]
    directives = dict(d.split(" ", 1) for d in csp.split("; "))
    assert directives["default-src"] == "'self'"
    assert re.fullmatch(r"'self' 'nonce-[\w-]{20,}'", directives["script-src"])
    assert directives["frame-ancestors"] == "'none'"
    assert directives["object-src"] == "'none'"
    assert "unsafe-inline" not in csp and "unsafe-eval" not in csp


def test_nonce_changes_per_request(client):
    first = client.get("/")["Content-Security-Policy"]
    second = client.get("/")["Content-Security-Policy"]
    assert first != second


def test_other_security_headers(home):
    assert home["X-Content-Type-Options"] == "nosniff"
    assert home["Referrer-Policy"] == "strict-origin-when-cross-origin"
    assert home["X-Frame-Options"] == "DENY"
    assert home["Cross-Origin-Opener-Policy"] == "same-origin"
    assert "camera=()" in home["Permissions-Policy"]
    assert "geolocation=()" in home["Permissions-Policy"]


def test_no_hsts_outside_prod(home):
    assert "Strict-Transport-Security" not in home


def test_headers_also_on_json_and_errors(client):
    for response in (client.get("/healthz"), client.get("/no-such-page")):
        assert "frame-ancestors 'none'" in response["Content-Security-Policy"]
        assert response["X-Content-Type-Options"] == "nosniff"


def test_page_has_no_inline_script(home):
    html = home.content.decode()
    for tag in re.findall(r"<script\b[^>]*>", html):
        assert "src=" in tag, f"inline script without src: {tag}"
    assert "<style" not in html
    assert '"allowEval": false' in html  # HTMX told not to eval (CSP has no unsafe-eval)


def test_view_can_set_its_own_csp(rf):
    from apps.core.security import SecurityHeadersMiddleware

    def view(request):
        from django.http import HttpResponse

        response = HttpResponse()
        response["Content-Security-Policy"] = "default-src 'none'"
        return response

    response = SecurityHeadersMiddleware(view)(rf.get("/"))
    assert response["Content-Security-Policy"] == "default-src 'none'"


def test_builders():
    assert (
        build_csp({"script-src": ["'self'", "{nonce}"]}, "abc") == "script-src 'self' 'nonce-abc'"
    )
    assert build_permissions_policy(["camera", "usb"]) == "camera=(), usb=()"


def test_csp_nonce_context_processor(rf):
    request = rf.get("/")
    assert csp_nonce(request) == {"csp_nonce": ""}
    request.csp_nonce = "n"
    assert csp_nonce(request) == {"csp_nonce": "n"}


def test_cookies_httponly_and_lax(settings):
    assert settings.SESSION_COOKIE_HTTPONLY and settings.CSRF_COOKIE_HTTPONLY
    assert settings.SESSION_COOKIE_SAMESITE == settings.CSRF_COOKIE_SAMESITE == "Lax"


@pytest.mark.urls("apps.core.tests.csrf_urls")
class TestCsrfOnHtmx:
    def _token(self, client):
        html = client.get("/").content.decode()
        return re.search(r'"X-CSRFToken": "([^"]+)"', html).group(1)

    def test_htmx_post_without_token_is_rejected(self):
        client = Client(enforce_csrf_checks=True)
        client.get("/")
        assert client.post("/echo", headers={"HX-Request": "true"}).status_code == 403

    def test_htmx_post_with_header_token_passes(self):
        client = Client(enforce_csrf_checks=True)
        token = self._token(client)
        response = client.post("/echo", headers={"HX-Request": "true", "X-CSRFToken": token})
        assert response.status_code == 200

    def test_csrf_cookie_flags(self):
        client = Client(enforce_csrf_checks=True)
        response = client.get("/")
        cookie = response.cookies["csrftoken"]
        assert cookie["httponly"] and cookie["samesite"] == "Lax"

    def test_wrong_token_is_rejected(self):
        client = Client(enforce_csrf_checks=True)
        self._token(client)
        response = client.post("/echo", headers={"X-CSRFToken": "x" * 64})
        assert response.status_code == 403
