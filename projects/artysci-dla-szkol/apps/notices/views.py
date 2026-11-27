from django.shortcuts import render
from django.views.decorators.cache import cache_control
from django.views.decorators.http import require_GET

from apps.catalog import filters as catalog_filters


# Placeholder until US-6.1 (D23): public, GET only. When it is opened from the empty results of the
# catalog (`zrodlo=katalog`), the click is recorded; the filters are checked like in the catalog.
@cache_control(no_cache=True)
@require_GET
def new_notice(request):
    filters = catalog_filters.parse(request.GET)
    if request.GET.get("zrodlo") == catalog_filters.NOTICE_SOURCE:
        catalog_filters.record_notice_click(filters)
    return render(request, "notices/soon.html", {"back_url": filters.url()})
