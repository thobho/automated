from django.conf import settings
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.static import serve

urlpatterns = [
    path("", include("apps.core.urls")),
    path("", include("apps.trust.urls")),
    path("django-admin/", admin.site.urls),
]

if getattr(settings, "SERVE_STATIC", False):  # only config.settings.pirx (no proxy in front)
    urlpatterns += [
        re_path(
            rf"^{settings.STATIC_URL.lstrip('/')}(?P<path>.*)$",
            serve,
            {"document_root": settings.STATIC_ROOT},
        )
    ]
