"""URLconf used only by test_security.py: the home page plus a POST endpoint behind CSRF."""

from django.http import HttpResponse
from django.urls import include, path
from django.views.decorators.http import require_POST

from apps.core.views import HomeView


@require_POST
def echo(request):
    return HttpResponse("ok")


urlpatterns = [
    path("", HomeView.as_view()),
    path("echo", echo),
    path("", include("apps.trust.urls")),  # base.html links the legal pages
    path("", include("apps.accounts.urls")),  # ... and login / logout
]
