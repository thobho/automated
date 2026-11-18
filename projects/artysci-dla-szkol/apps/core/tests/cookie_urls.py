"""URLconf used only by test_cookies.py: views that set cookies, to prove the check catches them."""

from django.contrib import messages
from django.http import HttpResponse
from django.urls import path


def promo(request):
    response = HttpResponse("ok")
    response.set_cookie("promo", "1")
    return response


def flash(request):
    messages.success(request, "zapisano")
    return HttpResponse("ok")


def clean(request):
    return HttpResponse("ok")


urlpatterns = [
    path("promo", promo),
    path("flash", flash),
    path("clean", clean),
]
