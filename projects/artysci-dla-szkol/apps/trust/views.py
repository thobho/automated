from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_GET, require_http_methods

from . import services


@require_GET
def document(request, kind: str):
    """Public page with the current version of one legal document."""
    current = services.current(kind)
    if current is None:
        raise Http404
    return render(request, "trust/document.html", {"document": current})


def _safe_next(request) -> str:
    target = request.POST.get("next") or request.GET.get("next") or ""
    if target and url_has_allowed_host_and_scheme(
        target, allowed_hosts={request.get_host()}, require_https=request.is_secure()
    ):
        return target
    return "/"


@login_required
@require_http_methods(["GET", "HEAD", "POST"])
def accept(request):
    """Re-acceptance page: lists the pending versions, one checkbox, submit."""
    next_url = _safe_next(request)
    error = False
    if request.method == "POST":
        shown = [int(v) for v in request.POST.getlist("document") if v.isdigit()]
        if request.POST.get("confirm") == "1" and services.accept_pending(request.user, shown):
            return redirect(next_url)
        error = True
    items = services.pending(request.user)
    if not items:
        return redirect(next_url)
    return render(
        request,
        "trust/accept.html",
        {"items": items, "next": next_url, "error": error},
        status=400 if error else 200,
    )
