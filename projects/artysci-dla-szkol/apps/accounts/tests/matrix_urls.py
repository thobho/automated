"""Test-only URLconf: the real routes plus one route the permission matrix does not list, and
a test view behind `RoleRequiredMixin`."""

from django.http import HttpResponse
from django.urls import include, path
from django.views import View

from apps.accounts.permissions import RoleRequiredMixin
from config.urls import urlpatterns as real_patterns


def brand_new(request):
    return HttpResponse("new")


class InstitutionOnly(RoleRequiredMixin, View):
    required_roles = ("institution",)

    def get(self, request):
        return HttpResponse("ok")


extra = (
    [
        path("nowa-strona/", brand_new, name="brand-new"),
        path("tylko-placowka/", InstitutionOnly.as_view(), name="institution-only"),
    ],
    "accounts",
)

urlpatterns = [*real_patterns, path("test/", include(extra))]
