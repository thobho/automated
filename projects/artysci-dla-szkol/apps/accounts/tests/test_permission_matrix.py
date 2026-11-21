"""Permission matrix (US-1.5, D61, D65): every URL name in `config.urls` and the expected answer
to a GET for each role. A route missing from MATRIX fails `test_every_route_is_in_the_matrix`
with its name; adding a route means adding a row here.

Expected values:
- ``200``, ``400``, ``404``, ``405``: that status code;
- ``login``: 302 to ``/logowanie/?next=<path>``;
- ``403``: the Polish 403 page from a permission check (one `permission denied` log line);
- ``home``: 302 somewhere other than the login page (e.g. back to ``/``).
"""

from urllib.parse import quote

import pytest
from django.urls import URLPattern, URLResolver, get_resolver, reverse

ROLES = ("anonymous", "artist", "institution", "admin")

# Not in the matrix, on purpose (path prefix or URL name -> why).
EXCLUDED = {
    "admin": "/django-admin/: Django's admin, staff only by Django itself",
    "core:healthz": "health check for the load balancer, public by design, no data",
    "core:readyz": "readiness check for the load balancer, public by design, no data",
}

# Arguments for routes that need them (URL name -> kwargs).
ARGUMENTS = {
    "core:private-media": {"token": "not-a-real-token"},
    "artists:offer_edit": {"offer_id": 999999},
    "artists:offer_delete": {"offer_id": 999999},
    "artists:offer_move": {"offer_id": 999999},
    "artists:material_delete": {"material_id": 999999},
    "artists:frame_delete": {"frame_id": 999999},
    "artists:upload_chunk": {"session_id": "00000000-0000-4000-8000-000000000000"},
    "artists:upload_complete": {"session_id": "00000000-0000-4000-8000-000000000000"},
    "artists:website_import_status": {"import_id": 999999},
}

#: URL name -> expected answer for (anonymous, artist, institution, admin)
MATRIX = {
    "core:home": ("200", "200", "200", "200"),
    "core:private-media": ("404", "404", "404", "404"),  # signed token is the permission
    "trust:terms": ("200", "200", "200", "200"),
    "trust:privacy": ("200", "200", "200", "200"),
    "trust:cookies": ("200", "200", "200", "200"),
    "trust:accept": ("login", "home", "home", "home"),  # nothing pending -> back to next
    "accounts:login": ("200", "200", "200", "200"),
    "accounts:login_code": ("405", "405", "405", "405"),  # POST only
    "accounts:login_link": ("400", "400", "400", "400"),  # no token -> "link invalid"
    "accounts:logout": ("405", "405", "405", "405"),  # POST only
    "accounts:settings": ("login", "200", "200", "200"),
    "accounts:email_change": ("login", "405", "405", "405"),  # POST only
    "accounts:email_change_code": ("login", "405", "405", "405"),  # POST only
    "accounts:email_change_link": ("login", "400", "400", "400"),  # no token -> "link invalid"
    "accounts:data_export": ("login", "200", "200", "200"),  # placeholder (US-8.6)
    "accounts:delete_account": ("login", "200", "200", "200"),  # placeholder (US-8.6)
    "artists:register": ("200", "200", "200", "200"),
    "artists:start": ("login", "200", "403", "403"),
    "profiles:preview": ("login", "200", "403", "403"),
    "artists:basics": ("login", "200", "403", "403"),
    # later wizard steps: the matrix artist has empty basics -> redirected to step 1
    "artists:offers": ("login", "home", "403", "403"),
    "artists:offer_add": ("login", "home", "403", "403"),
    "artists:offer_edit": ("login", "home", "403", "403"),
    "artists:offer_delete": ("login", "home", "403", "403"),
    "artists:offer_move": ("login", "405", "403", "403"),  # POST only
    "artists:statements": ("login", "home", "403", "403"),
    "artists:materials": ("login", "home", "403", "403"),
    "artists:materials_photos": ("login", "405", "403", "403"),  # POST only
    "artists:materials_pdfs": ("login", "405", "403", "403"),  # POST only
    "artists:materials_link": ("login", "405", "403", "403"),  # POST only
    "artists:material_delete": ("login", "405", "403", "403"),  # POST only
    "artists:frame_delete": ("login", "405", "403", "403"),  # POST only
    "artists:upload_create": ("login", "405", "403", "403"),  # POST only
    "artists:upload_chunk": ("login", "home", "403", "403"),  # GET = offset, POST = chunk
    "artists:upload_complete": ("login", "405", "403", "403"),  # POST only
    "artists:questionnaire": ("login", "home", "403", "403"),
    "artists:website_import": ("login", "home", "403", "403"),
    "artists:website_import_status": ("login", "home", "403", "403"),
    "profiles:generation": ("login", "200", "403", "403"),
    "profiles:generation_status": ("login", "200", "403", "403"),
    "profiles:generation_start": ("login", "405", "403", "403"),  # POST only
    "institutions:register": ("200", "200", "200", "200"),
    "institutions:rspo_suggestions": ("200", "200", "200", "200"),
    "institutions:start": ("login", "403", "200", "403"),
}


def url_names(urlconf=None) -> set[str]:
    """Every named route (``namespace:name``) except the EXCLUDED ones."""

    def walk(patterns, namespace=""):
        for pattern in patterns:
            if isinstance(pattern, URLResolver):
                if pattern.namespace in EXCLUDED:
                    continue
                inner = pattern.namespace or namespace
                yield from walk(pattern.url_patterns, inner)
            elif isinstance(pattern, URLPattern) and pattern.name:
                yield f"{namespace}:{pattern.name}" if namespace else pattern.name

    return {name for name in walk(get_resolver(urlconf).url_patterns) if name not in EXCLUDED}


def missing_from_matrix(urlconf=None) -> list[str]:
    return sorted(url_names(urlconf) - MATRIX.keys())


def check(response, expected: str, path: str) -> str | None:
    """None if `response` matches `expected`, else a short description of the mismatch."""
    status, location = response.status_code, response.get("Location", "")
    if expected == "login":
        ok = status == 302 and location == f"/logowanie/?next={quote(path)}"
    elif expected == "home":
        ok = status == 302 and not location.startswith("/logowanie/")
    elif expected == "403":
        ok = status == 403 and "Brak dostępu" in response.content.decode()
    else:
        ok = status == int(expected)
    return None if ok else f"expected {expected}, got {status} {location}".strip()


# --- the matrix ------------------------------------------------------------------------------


def test_every_route_is_in_the_matrix():
    assert missing_from_matrix() == [], "add these URL names to MATRIX"


def test_matrix_has_no_stale_rows():
    assert sorted(MATRIX.keys() - url_names()) == []


def test_matrix_covers_more_than_zero_routes():
    assert len(MATRIX) > 0 and len(url_names()) == len(MATRIX)


@pytest.mark.parametrize("name", sorted(MATRIX))
def test_permission_matrix(name, role_clients):
    path = reverse(name, kwargs=ARGUMENTS.get(name))
    problems = {}
    for role, expected in zip(ROLES, MATRIX[name], strict=True):
        problem = check(role_clients[role].get(path), expected, path)
        if problem:
            problems[role] = problem
    assert problems == {}, f"{name} ({path})"


def test_a_new_route_without_a_row_fails_and_is_named(settings):
    settings.ROOT_URLCONF = "apps.accounts.tests.matrix_urls"
    assert missing_from_matrix() == ["accounts:brand-new", "accounts:institution-only"]
