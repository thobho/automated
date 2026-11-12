from django.http import JsonResponse
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET
from django.views.generic import TemplateView

from . import services


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


class HomeView(TemplateView):
    template_name = "core/home.html"
