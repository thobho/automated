from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("", include("apps.core.urls")),
    path("django-admin/", admin.site.urls),
]
