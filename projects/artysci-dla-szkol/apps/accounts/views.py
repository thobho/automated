"""E-mail login views (US-1.3). They parse the request, call `services`, render a response."""

from django import forms
from django.conf import settings
from django.shortcuts import redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
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
    context = {"valid": valid, "token": token if valid else ""}
    return render(request, "accounts/login_link.html", context, status=200 if valid else 400)


@require_POST
def logout(request):
    """End the session on the server and ask the browser to drop cookies and storage."""
    services.end_session(request)
    response = redirect(settings.LOGOUT_REDIRECT_URL)
    response["Clear-Site-Data"] = '"cookies", "storage"'
    return response
