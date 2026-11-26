from django.http import Http404
from django.shortcuts import render
from django.views.decorators.cache import cache_control
from django.views.decorators.http import require_safe

from . import listing


# `no-cache` like the profile page: a cache must ask first, so a withdrawal shows at once.
@cache_control(no_cache=True)
@require_safe
def catalog_list(request):
    page = listing.cards_page(request.GET.get("strona"))
    if page is None:
        raise Http404
    return render(request, "catalog/list.html", {"page": page})
