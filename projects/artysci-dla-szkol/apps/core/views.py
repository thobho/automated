from django.core.exceptions import SuspiciousOperation
from django.http import FileResponse, Http404, HttpResponse, JsonResponse
from django.views.decorators.cache import cache_control, never_cache
from django.views.decorators.http import require_GET
from django.views.generic import TemplateView

from . import media, services


def _json(result: dict[str, str]) -> JsonResponse:
    return JsonResponse(result, status=200 if services.all_ok(result) else 503)


@never_cache
@require_GET
def healthz(request):
    return _json(services.health())


@never_cache
@require_GET
def readyz(request):
    return _json(services.readiness())


@cache_control(public=True, max_age=3600)
@require_GET
def robots_txt(request):
    """`/robots.txt` (US-3.4): public pages are open, the panel, admin and preview links are not
    (they also send `noindex`); the sitemap is named with its absolute URL."""
    return HttpResponse(services.robots_txt(), content_type="text/plain; charset=utf-8")


@never_cache
@require_GET
def private_media(request, token: str):
    """Serve a private file (filesystem backend) for a valid, unexpired signed token."""
    try:
        key = media.resolve_token(token)
        handle = media.private_storage().open(key, "rb")
    except (media.SignedURLInvalid, FileNotFoundError, SuspiciousOperation) as exc:
        raise Http404 from exc
    response = FileResponse(handle, as_attachment=True, filename=key.rsplit("/", 1)[-1])
    response["X-Content-Type-Options"] = "nosniff"
    response["Content-Security-Policy"] = "sandbox; default-src 'none'"
    return response


class HomeView(TemplateView):
    template_name = "core/home.html"
