"""Artist panel: profile generation status (US-2.5A) and the owner-only page preview (US-3.1).

There is no id in the URLs: an artist only ever sees the status of their own latest run.
"""

from django.contrib import messages
from django.http import Http404
from django.shortcuts import redirect, render
from django.utils.translation import gettext_lazy as _
from django.views.decorators.cache import cache_control, never_cache
from django.views.decorators.http import require_GET, require_http_methods, require_POST

from apps.accounts.permissions import role_required
from apps.artists import services as artist_services
from apps.quality.models import Generation

from . import completeness, pages, publication, sections, services
from . import generation as generations
from .models import PageVersion
from .themes import Theme


def _context(request) -> dict:
    artist = artist_services.artist_for(request.user)
    record = generations.latest_generation(artist)
    return {
        "generation": record,
        "running": record is not None and record.status == Generation.Status.RUNNING,
        "ready": record is not None and record.status == Generation.Status.READY,
        # Not checked yet: the page says only that it waits, never what was generated.
        "in_review": record is not None and record.status == Generation.Status.REVIEW,
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
def gaps(request):
    """The artist's own missing items as a task list with the completeness percentage."""
    artist = artist_services.artist_for(request.user)
    context = {
        "tasks": completeness.task_list(artist),
        "percent": completeness.completeness_percent(artist),
    }
    return render(request, "profiles/gaps.html", context)


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


def _section_context(artist) -> dict:
    """Status of the latest one-section run: running (poll) or a Polish reason after a failure
    that is newer than the current version."""
    record = generations.latest_generation(artist)
    if record is None or record.trigger != Generation.Trigger.SECTION:
        return {"section_running": False, "section_error": ""}
    running = record.status == Generation.Status.RUNNING
    error = ""
    if record.status == Generation.Status.ERROR and record.warnings:
        version = pages.current_version(artist)
        if version is None or record.finished_at > version.created_at:
            error = record.warnings[0]
    return {"section_running": running, "section_error": error}


@never_cache
@require_GET
@role_required("artist")
def preview(request):
    """The artist's own page (current version of the texts); not public, not indexed."""
    artist = artist_services.artist_for(request.user)
    content = pages.page_content(artist)
    locks = pages.current_content(artist)[1]
    context = {
        "content": content,
        "noindex": True,
        "theme_switch": True,
        "theme_choices": Theme.choices,
        "editor": pages.editor_sections(artist),
        "locks": locks,
        "versions": pages.versions_of(artist),
        **_section_context(artist),
    }
    response = render(request, "profiles/page.html", context)
    response["X-Robots-Tag"] = "noindex, nofollow"
    return response


@never_cache
@require_GET
@role_required("artist")
def section_status(request):
    """The regeneration status block (HTMX polls it); a finished run reloads the whole page."""
    artist = artist_services.artist_for(request.user)
    context = _section_context(artist)
    response = render(request, "profiles/_section_status.html", context)
    if not context["section_running"]:
        response["HX-Refresh"] = "true"
    return response


@never_cache
@role_required("artist")
@require_POST
def edit_field(request):
    """Save the artist's own text of one field (new version, the field gets locked)."""
    artist = artist_services.artist_for(request.user)
    try:
        version = pages.edit_field(
            artist, request.POST.get("path", ""), request.POST.get("value", "")
        )
    except pages.InvalidEdit as exc:
        messages.error(request, exc.message)
    else:
        if version is None:
            messages.info(request, _("Tekst bez zmian."))
        else:
            messages.success(
                request, _("Zapisaliśmy tekst. Pole jest zablokowane przed ponownym generowaniem.")
            )
    return redirect("profiles:preview")


@never_cache
@role_required("artist")
@require_POST
def unlock_field(request):
    artist = artist_services.artist_for(request.user)
    if pages.unlock(artist, request.POST.get("path", "")):
        messages.success(request, _("Pole odblokowane. Kolejne generowanie może je zmienić."))
    else:
        messages.error(request, _("Nieznane pole."))
    return redirect("profiles:preview")


@never_cache
@role_required("artist")
@require_POST
def regenerate_section(request):
    artist = artist_services.artist_for(request.user)
    try:
        sections.request_section(artist, request.POST.get("section", ""))
    except generations.GenerationRefused as exc:
        messages.error(request, exc.message)
    else:
        messages.success(
            request, _("Generujemy sekcję od nowa. Pola zablokowane zostaną bez zmian.")
        )
    return redirect("profiles:preview")


@never_cache
@role_required("artist")
@require_POST
def restore_version(request):
    artist = artist_services.artist_for(request.user)
    try:
        number = int(request.POST.get("number", ""))
    except ValueError:
        raise Http404 from None
    try:
        version = pages.restore(artist, number)
    except PageVersion.DoesNotExist:
        raise Http404 from None
    messages.success(
        request,
        _("Przywrócono wersję %(old)d jako nową wersję %(new)d.")
        % {"old": number, "new": version.number},
    )
    return redirect("profiles:preview")


@never_cache
@role_required("artist")
@require_POST
def theme(request):
    """Save the artist's own theme choice (owner only: the artist is the logged-in user)."""
    artist = artist_services.artist_for(request.user)
    try:
        services.set_theme(artist, request.POST.get("theme", ""))
    except services.InvalidTheme:
        messages.error(request, _("Nieznany motyw."))
    else:
        messages.success(request, _("Zapisaliśmy motyw strony."))
    return redirect("profiles:preview")


# --- publication (US-2.8) ------------------------------------------------------------------------


@never_cache
@require_http_methods(["GET", "HEAD"])
@role_required("artist")
def publication_page(request):
    artist = artist_services.artist_for(request.user)
    context = {
        "artist": artist,
        "blockers": publication.publication_blockers(artist),
        "unpublished_changes": publication.has_unpublished_changes(artist),
        "materials_hidden": publication.materials_hidden(artist),
    }
    return render(request, "profiles/publication.html", context)


@never_cache
@require_http_methods(["GET", "HEAD"])
@role_required("artist")
def withdraw_confirm(request):
    """Asks before the page is taken down; the action itself is the POST below."""
    artist = artist_services.artist_for(request.user)
    return render(request, "profiles/withdraw_confirm.html", {"artist": artist})


def _run(request, action, success):
    artist = artist_services.artist_for(request.user)
    try:
        action(artist)
    except publication.PublicationRefused as exc:
        messages.error(request, exc.message)
    else:
        messages.success(request, success)
    return redirect("profiles:publication")


@never_cache
@role_required("artist")
@require_POST
def publish(request):
    return _run(
        request,
        lambda artist: publication.publish(artist, actor=request.user),
        _("Strona jest opublikowana."),
    )


@never_cache
@role_required("artist")
@require_POST
def publish_changes(request):
    return _run(request, publication.update_published, _("Opublikowaliśmy zmiany."))


@never_cache
@role_required("artist")
@require_POST
def withdraw(request):
    return _run(
        request,
        lambda artist: publication.withdraw(artist, actor=request.user),
        _("Strona została wycofana i nie jest już dostępna."),
    )


# `no-cache`: a cache may keep the page but must ask the server first, so a withdrawal is seen
# at once. A draft, withdrawn or unknown slug gives the same 404.
@cache_control(no_cache=True)
@require_GET
def public_page(request, slug):
    content = publication.public_page(slug)
    if content is None:
        raise Http404
    return render(request, "profiles/page.html", {"content": content, "noindex": False})
