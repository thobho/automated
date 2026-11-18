"""View guards (US-1.5): `role_required(...)` for function views, `RoleRequiredMixin` for class
views. Anonymous visitors go to the login page with `next` = the requested path; a logged-in
account with another role gets the Polish 403 page and one `permission denied` log line."""

from functools import wraps

from django.contrib.auth.views import redirect_to_login
from django.shortcuts import render

from .roles import Role, log_denied, role_of


def _roles(roles) -> frozenset[Role]:
    if not roles:
        raise ValueError("role_required needs at least one role")
    return frozenset(Role(r) for r in roles)


def forbidden(request):
    """The 403 page (also Django's default for `PermissionDenied`: templates/403.html)."""
    return render(request, "403.html", status=403)


def check_role(request, required: frozenset[Role]):
    """None when the request may go on, else the response to return instead."""
    user = request.user
    role = role_of(user)
    if role is Role.ANONYMOUS:
        if Role.ANONYMOUS in required:
            return None
        return redirect_to_login(request.get_full_path())  # local path only
    if role in required:
        return None
    match = request.resolver_match
    log_denied(user, role, match.view_name if match else "-", required)
    return forbidden(request)


def role_required(*roles):
    """Allow only the given roles (``"artist"``, ``"institution"``, ``"admin"``)."""
    required = _roles(roles)

    def decorator(view):
        @wraps(view)
        def wrapped(request, *args, **kwargs):
            denied = check_role(request, required)
            return denied if denied is not None else view(request, *args, **kwargs)

        wrapped.required_roles = required
        return wrapped

    return decorator


class RoleRequiredMixin:
    """Class-view guard: set ``required_roles = ("institution",)``."""

    required_roles: tuple[str, ...] = ()

    def dispatch(self, request, *args, **kwargs):
        denied = check_role(request, _roles(self.required_roles))
        if denied is not None:
            return denied
        return super().dispatch(request, *args, **kwargs)
