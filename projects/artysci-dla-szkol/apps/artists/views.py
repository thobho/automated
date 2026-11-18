"""Artist registration (US-1.1) and the wizard start placeholder. Views parse the request,
call `services`, render a response."""

from django import forms
from django.shortcuts import render
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_http_methods

from apps.accounts.permissions import role_required

from . import services
from .services import Registration


class ArtistRegistrationForm(forms.Form):
    email = forms.EmailField(label=_("Adres e-mail"), max_length=254)
    name = forms.CharField(label=_("Nazwa"), max_length=200)
    accept = forms.BooleanField(
        required=True,
        error_messages={
            "required": _("Aby założyć konto, zaakceptuj regulamin i politykę prywatności.")
        },
    )


def _form_page(request, form, *, status=200, unavailable=False):
    context = {"form": form, "unavailable": unavailable}
    return render(request, "artists/register.html", context, status=status)


@never_cache
@require_http_methods(["GET", "HEAD", "POST"])
def register(request):
    """The registration form. The answer to a valid form is the same for a new and an
    existing address (no enumeration)."""
    if request.method != "POST":
        return _form_page(request, ArtistRegistrationForm())
    form = ArtistRegistrationForm(request.POST)
    if not form.is_valid():
        return _form_page(request, form, status=400)
    email = form.cleaned_data["email"]
    result = services.register_artist(
        email,
        form.cleaned_data["name"],
        request.META.get("REMOTE_ADDR", ""),
        link_base=request.build_absolute_uri("/"),
    )
    if result is Registration.UNAVAILABLE:
        return _form_page(request, form, status=503, unavailable=True)
    context = {
        "email": email,
        "next": reverse("artists:start"),
        "rate_limited": result is Registration.RATE_LIMITED,
    }
    status = 429 if result is Registration.RATE_LIMITED else 200
    return render(request, "artists/register_sent.html", context, status=status)


@role_required("artist")
def start(request):
    """Profile wizard start (`can_create_artist_profile`): a placeholder until US-2.1."""
    return render(request, "artists/start.html")
