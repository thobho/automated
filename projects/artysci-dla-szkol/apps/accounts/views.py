"""E-mail login (US-1.3) and account settings (US-1.6) views. They parse the request, call
`services`, render a response."""

from django import forms
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils.translation import gettext_lazy as _
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_http_methods, require_POST

from . import services


class EmailForm(forms.Form):
    email = forms.EmailField(max_length=254)


def _safe_next(request) -> str:
    """`next` if it points to this host, else the default page."""
    target = request.POST.get("next") or request.GET.get("next") or ""
    if target and url_has_allowed_host_and_scheme(
        target, allowed_hosts={request.get_host()}, require_https=request.is_secure()
    ):
        return target
    return settings.LOGIN_REDIRECT_URL


def _render_code_step(request, email: str, *, status: int, rate_limited=False, error=False):
    context = {
        "email": email,
        "next": _safe_next(request),
        "rate_limited": rate_limited,
        "error": error,
    }
    return render(request, "accounts/login_code.html", context, status=status)


@never_cache
@require_http_methods(["GET", "HEAD", "POST"])
def login(request):
    """Step 1: e-mail. The answer is the same whether or not an account exists."""
    if request.method != "POST":
        return render(
            request, "accounts/login.html", {"form": EmailForm(), "next": _safe_next(request)}
        )
    form = EmailForm(request.POST)
    if not form.is_valid():
        context = {"form": form, "next": _safe_next(request)}
        return render(request, "accounts/login.html", context, status=400)
    email = form.cleaned_data["email"]
    accepted = services.request_login(
        email, request.META.get("REMOTE_ADDR", ""), link_base=request.build_absolute_uri("/")
    )
    if not accepted:
        return _render_code_step(request, email, status=429, rate_limited=True)
    return _render_code_step(request, email, status=200)


@never_cache
@require_POST
def login_code(request):
    """Step 2: the 6-digit code from the e-mail."""
    email = request.POST.get("email", "")[:254]
    user = services.login_with_code(email, request.POST.get("code", "")[:32])
    if user is None:
        return _render_code_step(request, email, status=400, error=True)
    services.start_session(request, user)
    return redirect(_safe_next(request))


@never_cache
@require_http_methods(["GET", "HEAD", "POST"])
def login_link(request):
    """The link from the e-mail. GET only shows a button (mail scanners open links); the POST
    logs in. The token comes in the query string, which no log line contains."""
    if request.method == "POST":
        user = services.login_with_link(request.POST.get("t", "")[:128])
        if user is not None:
            services.start_session(request, user)
            return redirect(_safe_next(request))
        return render(request, "accounts/login_link.html", {"valid": False}, status=400)
    token = request.GET.get("t", "")[:128]
    valid = services.check_link(token)
    context = {"valid": valid, "token": token if valid else "", "next": _safe_next(request)}
    return render(request, "accounts/login_link.html", context, status=200 if valid else 400)


@require_POST
def logout(request):
    """End the session on the server and ask the browser to drop cookies and storage."""
    services.end_session(request)
    response = redirect(settings.LOGOUT_REDIRECT_URL)
    response["Clear-Site-Data"] = '"cookies", "storage"'
    return response


# --- account settings (US-1.6) ---------------------------------------------------------------


class NamesForm(forms.Form):
    full_name = forms.CharField(max_length=200, required=False)
    artist_name = forms.CharField(max_length=200, required=False)


def _settings_page(request, *, names_form=None, email_form=None, status=200, **flags):
    overview = services.account_overview(request.user)
    if names_form is None:
        names_form = NamesForm(
            initial={"full_name": overview["full_name"], "artist_name": overview["artist_name"]}
        )
    context = {
        **overview,
        "names_form": names_form,
        "email_form": email_form or EmailForm(),
        **flags,
    }
    return render(request, "accounts/settings.html", context, status=status)


@never_cache
@login_required
@require_http_methods(["GET", "HEAD", "POST"])
def account_settings(request):
    """Names (POST saves them) and the current login e-mail."""
    if request.method != "POST":
        return _settings_page(request)
    form = NamesForm(request.POST)
    is_artist = services.account_overview(request.user)["is_artist"]
    if form.is_valid() and is_artist and not form.cleaned_data["artist_name"].strip():
        form.add_error("artist_name", _("Podaj nazwę artysty."))
    if not form.is_valid():
        return _settings_page(request, names_form=form, status=400)
    services.update_names(
        request.user,
        full_name=form.cleaned_data["full_name"],
        artist_name=form.cleaned_data["artist_name"] if is_artist else None,
    )
    messages.success(request, _("Zapisano zmiany."))
    return redirect("accounts:settings")


@never_cache
@login_required
@require_POST
def email_change(request):
    """Request a new login e-mail. Free and taken addresses get the same answer."""
    form = EmailForm(request.POST)
    if not form.is_valid():
        return _settings_page(request, email_form=form, status=400)
    accepted = services.request_email_change(
        request.user,
        form.cleaned_data["email"],
        request.META.get("REMOTE_ADDR", ""),
        link_base=request.build_absolute_uri("/"),
    )
    context = {"rate_limited": not accepted}
    return render(
        request, "accounts/email_change_sent.html", context, status=200 if accepted else 429
    )


@never_cache
@login_required
@require_POST
def email_change_code(request):
    """Confirm the change with the 6-digit code from the new address."""
    if services.confirm_email_change_code(request.user, request.POST.get("code", "")[:32]):
        services.keep_session_after_change(request, request.user)
        messages.success(request, _("Adres e-mail został zmieniony."))
        return redirect("accounts:settings")
    return render(request, "accounts/email_change_sent.html", {"error": True}, status=400)


@never_cache
@login_required
@require_http_methods(["GET", "HEAD", "POST"])
def email_change_link(request):
    """The link from the new address. GET only shows a button (mail scanners open links);
    the POST confirms, for the logged-in user who asked for the change only."""
    if request.method == "POST":
        token = request.POST.get("t", "")[:128]
        if services.confirm_email_change_link(request.user, token):
            services.keep_session_after_change(request, request.user)
            messages.success(request, _("Adres e-mail został zmieniony."))
            return redirect("accounts:settings")
        return render(request, "accounts/email_change_link.html", {"valid": False}, status=400)
    token = request.GET.get("t", "")[:128]
    valid = services.check_email_change_link(request.user, token)
    context = {"valid": valid, "token": token if valid else ""}
    return render(request, "accounts/email_change_link.html", context, status=200 if valid else 400)


@login_required
@require_http_methods(["GET", "HEAD"])
def data_export(request):
    """Placeholder: data export comes with US-8.6."""
    return render(request, "accounts/coming_later.html", {"title": _("Pobierz moje dane")})


@login_required
@require_http_methods(["GET", "HEAD"])
def delete_account(request):
    """Placeholder: account deletion comes with US-8.6."""
    return render(request, "accounts/coming_later.html", {"title": _("Usuń konto")})
