"""Artist panel: start a profile generation and watch its status (US-2.5A).

There is no id in the URLs: an artist only ever sees the status of their own latest run.
"""

from django.contrib import messages
from django.shortcuts import redirect, render
from django.utils.translation import gettext_lazy as _
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_http_methods, require_POST

from apps.accounts.permissions import role_required
from apps.artists import services as artist_services
from apps.quality.models import Generation

from . import generation as generations


def _context(request) -> dict:
    artist = artist_services.artist_for(request.user)
    record = generations.latest_generation(artist)
    return {
        "generation": record,
        "running": record is not None and record.status == Generation.Status.RUNNING,
        "ready": record is not None
        and record.status in (Generation.Status.READY, Generation.Status.REVIEW),
        "failed": record is not None and record.status == Generation.Status.ERROR,
    }


@never_cache
@require_http_methods(["GET", "HEAD"])
@role_required("artist")
def generation_page(request):
    """The status of the latest generation and the button to start one."""
    return render(request, "profiles/generation.html", _context(request))


@never_cache
@require_http_methods(["GET", "HEAD"])
@role_required("artist")
def generation_status(request):
    """The status block alone (HTMX polls this while a run is going)."""
    return render(request, "profiles/_generation_status.html", _context(request))


@never_cache
@role_required("artist")
@require_POST
def generation_start(request):
    artist = artist_services.artist_for(request.user)
    try:
        generations.request_generation(artist, Generation.Trigger.MANUAL)
    except generations.GenerationRefused as exc:
        messages.error(request, exc.message)
    else:
        messages.success(request, _("Zaczęliśmy generować profil."))
    return redirect("profiles:generation")
