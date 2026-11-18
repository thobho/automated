"""Institution registration (US-1.2), the RSPO suggestion fragment and the institution start
placeholder. Views parse the request, call `services`, render a response."""

from django import forms
from django.shortcuts import render
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET, require_http_methods

from apps.accounts.permissions import role_required

from . import services
from .models import InstitutionType, MemberFunction, Voivodeship
from .services import InstitutionDetails, Registration

TYPED_FIELDS = ("institution_type", "name", "locality", "voivodeship")


class InstitutionRegistrationForm(forms.Form):
    email = forms.EmailField(label=_("Adres e-mail"), max_length=254)
    # Only required when no RSPO suggestion is chosen (see clean()).
    institution_type = forms.ChoiceField(
        label=_("Typ placówki"), choices=InstitutionType.choices, required=False
    )
    name = forms.CharField(label=_("Nazwa placówki"), max_length=200, required=False)
    locality = forms.CharField(label=_("Miejscowość"), max_length=100, required=False)
    voivodeship = forms.ChoiceField(
        label=_("Województwo"), choices=Voivodeship.choices, required=False
    )
    rspo_number = forms.IntegerField(min_value=1, required=False)
    function = forms.ChoiceField(label=_("Twoja funkcja"), choices=MemberFunction.choices)
    accept = forms.BooleanField(
        required=True,
        error_messages={
            "required": _("Aby założyć konto, zaakceptuj regulamin i politykę prywatności.")
        },
    )

    def clean_rspo_number(self):
        number = self.cleaned_data.get("rspo_number")
        if number and services.rspo_entry(number) is None:
            raise forms.ValidationError(_("Nie znaleziono placówki w RSPO. Wpisz dane ręcznie."))
        return number

    def clean(self):
        data = super().clean()
        if not data.get("rspo_number") and "rspo_number" not in self.errors:
            for field in TYPED_FIELDS:
                if field not in self.errors and not (data.get(field) or "").strip():
                    self.add_error(field, forms.ValidationError("", code="required"))
        return data


def _form_page(request, form, *, status=200, unavailable=False):
    # Keep a chosen suggestion selected when the form comes back with an error.
    chosen = services.rspo_entry(form.cleaned_data.get("rspo_number")) if form.is_bound else None
    context = {
        "form": form,
        "unavailable": unavailable,
        "suggestions": [chosen] if chosen else [],
        "chosen": chosen.rspo_number if chosen else None,
        "types": InstitutionType.choices,
        "voivodeships": Voivodeship.choices,
        "functions": MemberFunction.choices,
    }
    return render(request, "institutions/register.html", context, status=status)


@never_cache
@require_http_methods(["GET", "HEAD", "POST"])
def register(request):
    """The registration form. The answer to a valid form is the same for a new and an
    existing address (no enumeration)."""
    if request.method != "POST":
        return _form_page(request, InstitutionRegistrationForm())
    form = InstitutionRegistrationForm(request.POST)
    if not form.is_valid():
        return _form_page(request, form, status=400)
    data = form.cleaned_data
    email = data["email"]
    result = services.register_institution(
        email,
        InstitutionDetails(**{field: data[field] for field in TYPED_FIELDS}),
        data["function"],
        request.META.get("REMOTE_ADDR", ""),
        rspo_number=data["rspo_number"],
        link_base=request.build_absolute_uri("/"),
    )
    if result is Registration.UNAVAILABLE:
        return _form_page(request, form, status=503, unavailable=True)
    context = {
        "email": email,
        "next": reverse("institutions:start"),
        "rate_limited": result is Registration.RATE_LIMITED,
    }
    status = 429 if result is Registration.RATE_LIMITED else 200
    return render(request, "institutions/register_sent.html", context, status=status)


@require_GET
def rspo_suggestions(request):
    """HTMX fragment: public RSPO rows matching the typed name (and locality). Anonymous,
    read-only; empty below 3 characters."""
    entries = services.suggest_rspo(request.GET.get("name", ""), request.GET.get("locality", ""))
    return render(
        request,
        "institutions/rspo_suggestions.html",
        {"suggestions": entries, "chosen": None},
    )


@role_required("institution")
def start(request):
    """Institution start: a placeholder until the catalog and inquiries (M2)."""
    member = services.member_for(request.user)
    return render(request, "institutions/start.html", {"member": member})
