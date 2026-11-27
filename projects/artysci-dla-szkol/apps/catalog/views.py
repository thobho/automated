from django.http import Http404
from django.shortcuts import render
from django.views.decorators.cache import cache_control
from django.views.decorators.http import require_safe

from . import filters as filters_module
from . import listing


# `no-cache` like the profile page: a cache must ask first, so a withdrawal shows at once.
@cache_control(no_cache=True)
@require_safe
def catalog_list(request):
    filters = filters_module.parse(request.GET)
    page = listing.cards_page(request.GET.get("strona"), filters)
    if page is None:
        raise Http404
    if request.method == "GET":
        filters_module.record_search(filters, page.total, page.number)
    context = {
        "page": page,
        "filters": filters,
        "options": filters_module.options(filters),
        "found": filters_module.found_text(page.total),
        "filtered": bool(filters.active()),
    }
    if not page.cards and context["filtered"]:
        context["active_links"] = filters_module.active_links(filters)
        context["notice_url"] = filters_module.notice_url(filters)
    return render(request, "catalog/list.html", context)
