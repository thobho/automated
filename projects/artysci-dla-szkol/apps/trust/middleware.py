"""Re-acceptance gate (US-8.1): a logged-in user with pending acceptances sees only the
acceptance page, the legal texts and a few technical endpoints until they accept."""

from urllib.parse import urlencode

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import Resolver404, resolve, reverse

from . import services

# URL names reachable without accepting. Names that do not exist yet (logout comes with E1)
# simply never match.
EXEMPT_URL_NAMES = frozenset(
    {
        "trust:terms",
        "trust:privacy",
        "trust:cookies",
        "trust:accept",
        "core:healthz",
        "core:readyz",
        "admin:logout",
        "accounts:logout",
    }
)


class LegalAcceptanceMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if self._must_accept(request):
            target = reverse("trust:accept")
            if request.method in ("GET", "HEAD"):
                target += "?" + urlencode({"next": request.path})
            if request.headers.get("HX-Request"):
                response = HttpResponse(status=204)
                response["HX-Redirect"] = target
                return response
            return redirect(target)
        return self.get_response(request)

    @staticmethod
    def _must_accept(request) -> bool:
        user = getattr(request, "user", None)
        if user is None or not user.is_authenticated:
            return False
        if request.path_info.startswith(settings.STATIC_URL):
            return False
        try:
            match = resolve(request.path_info)
        except Resolver404:
            return False  # let the 404 happen
        if match.view_name in EXEMPT_URL_NAMES:
            return False
        return bool(services.pending_acceptances(user))
