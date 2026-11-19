"""US-8.8 / D32: the site sets only the essential session and CSRF cookies."""

import pytest
from django.test import Client
from django.urls import NoReverseMatch, URLPattern, URLResolver, get_resolver, reverse

from apps.core.cookies import essential_cookie_names

pytestmark = pytest.mark.django_db

# Routes with arguments cannot be walked automatically. Extend this list when a feature adds
# one (path -> why it is listed). Every entry is requested like a walked route.
ROUTES_WITH_ARGUMENTS = {
    "/media/private/not-a-real-token": "core:private-media (signed token)",
}

# Never requested: staff only, Django's own cookies are the same session/CSRF ones.
EXCLUDED_PREFIXES = ("/django-admin/",)


def _walk(patterns, prefix=""):
    """Yield (path, name) for every pattern that reverses without arguments."""
    for p in patterns:
        if isinstance(p, URLResolver):
            ns = p.namespace
            for path, name in _walk(p.url_patterns, prefix + str(p.pattern)):
                yield path, (f"{ns}:{name}" if ns and name else name)
        elif isinstance(p, URLPattern):
            yield prefix + str(p.pattern), p.name


def reversible_paths(urlconf=None) -> list[str]:
    found = []
    for _path, name in _walk(get_resolver(urlconf).url_patterns):
        if not name:
            continue
        try:
            url = reverse(name, urlconf=urlconf)
        except NoReverseMatch:  # needs arguments: see ROUTES_WITH_ARGUMENTS
            continue
        if not url.startswith(EXCLUDED_PREFIXES):
            found.append(url)
    return sorted(set(found))


def cookie_violations(client: Client, paths) -> list[str]:
    """GET each path; describe every Set-Cookie outside the allowlist or without its flags."""
    allowed = essential_cookie_names()
    problems = []
    for path in paths:
        response = client.get(path)
        for name, morsel in response.cookies.items():
            if name not in allowed:
                problems.append(f"{path}: cookie {name!r} is not essential")
            elif morsel["samesite"] != "Lax":
                problems.append(f"{path}: cookie {name!r} lacks SameSite=Lax")
            elif not morsel["httponly"]:
                problems.append(f"{path}: cookie {name!r} lacks HttpOnly")
    return problems


@pytest.fixture
def user(django_user_model):
    return django_user_model.objects.create_user(email="ala@example.invalid")


def test_every_reversible_route_sets_only_essential_cookies(user, capsys):
    paths = reversible_paths() + sorted(ROUTES_WITH_ARGUMENTS)
    assert len(paths) >= 8, f"route walker found only {len(paths)} routes"
    anonymous = cookie_violations(Client(), paths)
    logged_in = Client()
    logged_in.force_login(user)
    authenticated = cookie_violations(logged_in, paths)
    with capsys.disabled():
        print(f"\ncookie check: {len(paths)} routes x (anonymous, logged in)")
    assert anonymous == []
    assert authenticated == []


def test_walker_finds_known_routes():
    paths = reversible_paths()
    for expected in ("/", "/healthz", "/logowanie/", "/ciasteczka/", "/konto/", "/konto/email/"):
        assert expected in paths
    for wizard in ("/artysta/kreator/", "/artysta/profil/dane/", "/artysta/profil/oferty/"):
        assert wizard in paths  # US-2.1 wizard routes (no arguments: walked automatically)
    assert not any(p.startswith("/django-admin/") for p in paths)


def test_check_catches_a_non_essential_cookie(settings):
    settings.ROOT_URLCONF = "apps.core.tests.cookie_urls"
    problems = cookie_violations(Client(), ["/promo", "/clean"])
    assert problems == ["/promo: cookie 'promo' is not essential"]


def test_flash_messages_set_no_messages_cookie(settings):
    settings.ROOT_URLCONF = "apps.core.tests.cookie_urls"
    client = Client()
    response = client.get("/flash")
    assert "messages" not in response.cookies
    assert cookie_violations(client, ["/flash"]) == []


def test_no_language_switcher_route():
    # LocaleMiddleware only reads the language cookie; only the set_language view writes it.
    assert not any("setlang" in p or "i18n" in p for p in reversible_paths())


def test_prod_allowlist_is_host_prefixed(monkeypatch):
    import importlib
    import sys

    for key, value in {
        "DJANGO_SECRET_KEY": "x" * 60,
        "DJANGO_ALLOWED_HOSTS": "example.invalid",
        "DATABASE_URL": "sqlite://:memory:",
        "MEDIA_PUBLIC_BASE_URL": "https://media.example.invalid/",
    }.items():
        monkeypatch.setenv(key, value)
    monkeypatch.delitem(sys.modules, "config.settings.prod", raising=False)
    prod = importlib.import_module("config.settings.prod")
    assert {prod.SESSION_COOKIE_NAME, prod.CSRF_COOKIE_NAME} == {
        "__Host-sessionid",
        "__Host-csrftoken",
    }
    assert prod.MESSAGE_STORAGE.endswith("session.SessionStorage")


def test_allowlist_follows_settings(settings):
    settings.SESSION_COOKIE_NAME = "__Host-sessionid"
    settings.CSRF_COOKIE_NAME = "__Host-csrftoken"
    assert essential_cookie_names() == {"__Host-sessionid", "__Host-csrftoken"}
