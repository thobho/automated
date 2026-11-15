"""Security response headers Django 5.2 does not set itself: CSP (with a nonce) and
Permissions-Policy.

Django's SecurityMiddleware already sends X-Content-Type-Options, Referrer-Policy,
Cross-Origin-Opener-Policy and (in prod) HSTS; XFrameOptionsMiddleware sends X-Frame-Options.
The policies live in settings (`CSP_DIRECTIVES`, `PERMISSIONS_POLICY`), see config/settings/base.py.
"""

import secrets

from django.conf import settings

NONCE_PLACEHOLDER = "{nonce}"


def build_csp(directives: dict[str, list[str]], nonce: str) -> str:
    """Render a CSP header value; `{nonce}` in a source list becomes `'nonce-<value>'`."""
    parts = []
    for name, sources in directives.items():
        rendered = [f"'nonce-{nonce}'" if src == NONCE_PLACEHOLDER else src for src in sources]
        parts.append(" ".join([name, *rendered]))
    return "; ".join(parts)


def build_permissions_policy(features: list[str]) -> str:
    """Every listed feature is disabled for all origins: `camera=()`."""
    return ", ".join(f"{feature}=()" for feature in features)


class SecurityHeadersMiddleware:
    """Adds a per-request CSP nonce (`request.csp_nonce`) and the CSP/Permissions-Policy headers.

    A view that sets its own Content-Security-Policy keeps it.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.permissions_policy = build_permissions_policy(settings.PERMISSIONS_POLICY)

    def __call__(self, request):
        nonce = secrets.token_urlsafe(16)
        request.csp_nonce = nonce
        response = self.get_response(request)
        if "Content-Security-Policy" not in response:
            response["Content-Security-Policy"] = build_csp(settings.CSP_DIRECTIVES, nonce)
        response.setdefault("Permissions-Policy", self.permissions_policy)
        return response


def csp_nonce(request) -> dict[str, str]:
    """Template context processor: `<script nonce="{{ csp_nonce }}">` for the rare inline case."""
    return {"csp_nonce": getattr(request, "csp_nonce", "")}
