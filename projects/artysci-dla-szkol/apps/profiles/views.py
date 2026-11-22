"""Owner-only preview of the public artist page (US-3.1). Publishing is a later story."""

from django.shortcuts import render
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET

from apps.accounts.permissions import role_required
from apps.artists import services as artists

from .content import page_content_for


@never_cache
@require_GET
@role_required("artist")
def preview(request):
    """The artist's own page rendered from `page_content_for`; not public, not indexed."""
    artist = artists.artist_for(request.user)
    content = page_content_for(artist)
    response = render(request, "profiles/page.html", {"content": content, "noindex": True})
    response["X-Robots-Tag"] = "noindex, nofollow"
    return response
