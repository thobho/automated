"""Artist registration (US-1.1) and the profile wizard (US-2.1). Views parse the request,
call `services`, render a response."""

from dataclasses import asdict

from django import forms
from django.contrib import messages
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_http_methods

from apps.accounts.permissions import role_required
from apps.core.regions import Voivodeship

from . import services
from .models import ArtistType, Audience
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


# --- profile wizard (US-2.1) -----------------------------------------------------------------


class BasicsForm(forms.Form):
    """Step 1. Choice fields refuse values outside the lists (tampered POST)."""

    artist_type = forms.ChoiceField(
        label=_("Rodzaj"),
        choices=ArtistType.choices,
        widget=forms.RadioSelect,
        error_messages={"required": _("Wybierz rodzaj.")},
    )
    name = forms.CharField(
        label=_("Nazwa (imię i nazwisko, zespół lub firma)"),
        max_length=200,
        error_messages={"required": _("Podaj nazwę.")},
    )
    city = forms.CharField(
        label=_("Miasto"), max_length=100, error_messages={"required": _("Podaj miasto.")}
    )
    voivodeships = forms.MultipleChoiceField(
        label=_("Województwa działania"),
        choices=Voivodeship.choices,
        widget=forms.CheckboxSelectMultiple,
        error_messages={"required": _("Wybierz co najmniej jedno województwo.")},
    )
    audiences = forms.MultipleChoiceField(
        label=_("Odbiorcy"),
        choices=Audience.choices,
        widget=forms.CheckboxSelectMultiple,
        error_messages={"required": _("Wybierz co najmniej jedną grupę odbiorców.")},
    )


def _artist(request):
    return services.artist_for(request.user)  # role_required("artist") => never None


@role_required("artist")
def start(request):
    """Wizard overview (`can_create_artist_profile`): step 1 is required, later steps open
    once it is done and can be skipped."""
    artist = _artist(request)
    context = {"steps": services.wizard_steps(artist), "artist": artist}
    return render(request, "artists/start.html", context)


@never_cache
@require_http_methods(["GET", "HEAD", "POST"])
@role_required("artist")
def basics(request):
    """Step 1, the basics; prefilled on every visit."""
    artist = _artist(request)
    if request.method != "POST":
        initial = asdict(services.basics_of(artist))
        form = BasicsForm(initial={k: v or None for k, v in initial.items()})
        return render(request, "artists/basics.html", {"form": form})
    form = BasicsForm(request.POST)
    if not form.is_valid():
        return render(request, "artists/basics.html", {"form": form}, status=400)
    services.save_basics(request.user, form.cleaned_data)
    messages.success(request, _("Zapisano dane podstawowe."))
    return redirect("artists:start")


def _later_step(key):
    step = services.LATER_STEPS[key]

    @role_required("artist")
    def view(request):
        if not services.basics_complete(_artist(request)):
            messages.info(request, _("Najpierw uzupełnij dane podstawowe."))
            return redirect("artists:basics")
        return render(request, "artists/later_step.html", {"step": step})

    view.__name__ = view.__qualname__ = key
    view.__doc__ = f"Wizard step {key!r}: a placeholder until its task lands."
    return view


offers = _later_step("offers")
statements = _later_step("statements")
materials = _later_step("materials")
