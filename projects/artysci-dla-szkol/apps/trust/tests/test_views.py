import pytest
from django.urls import reverse

from apps.trust import services
from apps.trust.models import LegalAcceptance

pytestmark = pytest.mark.django_db

ACCEPT = "/akceptacja-dokumentow/"


@pytest.fixture
def accepted_v1(client, user):
    """A logged-in user who accepted terms v1 and privacy v1."""
    services.publish("terms", "Regulamin v1", material=True)
    services.publish("privacy", "Polityka v1", material=True)
    services.record_acceptance(user, ["terms", "privacy"])
    client.force_login(user)
    return user


@pytest.mark.parametrize(
    ("url", "kind"),
    [("/regulamin/", "terms"), ("/polityka-prywatnosci/", "privacy"), ("/ciasteczka/", "cookies")],
)
def test_public_page_shows_current_version(client, url, kind):
    services.publish(kind, "Stara treść", material=True)
    services.publish(kind, "Akapit pierwszy.\n\nAkapit drugi.", material=False)
    response = client.get(url)
    assert response.status_code == 200
    html = response.content.decode()
    assert "Wersja 2" in html
    assert "<p>Akapit pierwszy.</p>" in html and "<p>Akapit drugi.</p>" in html
    assert "Stara treść" not in html
    assert "datetime=" in html


@pytest.mark.parametrize("url", ["/regulamin/", "/polityka-prywatnosci/", "/ciasteczka/"])
def test_public_page_404_without_version(client, url):
    assert client.get(url).status_code == 404


def test_public_page_rejects_post(client):
    services.publish("terms", "t", material=True)
    assert client.post("/regulamin/").status_code == 405


def test_body_html_is_escaped(client):
    services.publish("terms", "<script>alert(1)</script> <b>x</b>", material=True)
    html = client.get("/regulamin/").content.decode()
    assert "<script>alert(1)</script>" not in html
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in html
    assert "<b>x</b>" not in html


def test_footer_links_legal_pages(client):
    html = client.get("/").content.decode()
    for url in ("/regulamin/", "/polityka-prywatnosci/", "/ciasteczka/"):
        assert f'href="{url}"' in html


def test_material_change_redirects_until_accepted(client, accepted_v1):
    assert client.get("/").status_code == 200
    v2 = services.publish("terms", "Regulamin v2", material=True)

    response = client.get("/")
    assert response.status_code == 302
    assert response["Location"] == f"{ACCEPT}?next=%2F"

    page = client.get(response["Location"])
    assert page.status_code == 200
    html = page.content.decode()
    assert "nowa wersja 2" in html and "wcześniej zaakceptowana wersja 1" in html
    assert 'href="/regulamin/"' in html
    assert 'type="checkbox"' in html

    done = client.post(ACCEPT, {"confirm": "1", "document": [v2.pk], "next": "/"})
    assert done.status_code == 302 and done["Location"] == "/"
    assert LegalAcceptance.objects.filter(user=accepted_v1, document=v2).exists()
    assert client.get("/").status_code == 200


def test_non_material_change_does_not_redirect(client, accepted_v1):
    services.publish("terms", "Regulamin v2, literówka", material=False)
    assert client.get("/").status_code == 200


@pytest.mark.parametrize(
    "url", ["/regulamin/", "/polityka-prywatnosci/", "/ciasteczka/", "/healthz", "/readyz"]
)
def test_exempt_pages_reachable_with_pending(client, accepted_v1, url):
    for kind in ("terms", "privacy", "cookies"):
        services.publish(kind, f"{kind} v2", material=True)
    assert client.get(url).status_code == 200


def test_logout_reachable_with_pending(client, staff):
    # The only logout today is the admin's (staff); E1's `accounts:logout` is exempt by name too.
    services.publish("terms", "v1", material=True)
    client.force_login(staff)
    assert client.get("/").status_code == 302  # pending
    response = client.post(reverse("admin:logout"))
    assert not response.get("Location", "").startswith(ACCEPT)
    assert "_auth_user_id" not in client.session  # logout went through


def test_static_and_unknown_urls_not_redirected(client, accepted_v1):
    services.publish("terms", "v2", material=True)
    assert client.get("/static/vendor/htmx/htmx.min.js").status_code == 404  # no static serving
    assert client.get("/nie-ma-takiej-strony/").status_code == 404


def test_htmx_request_gets_hx_redirect(client, accepted_v1):
    services.publish("terms", "v2", material=True)
    response = client.get("/", headers={"HX-Request": "true"})
    assert response.status_code == 204
    assert response["HX-Redirect"].startswith(ACCEPT)


def test_post_elsewhere_redirects_without_next(client, accepted_v1):
    services.publish("terms", "v2", material=True)
    response = client.post("/")
    assert response.status_code == 302
    assert response["Location"] == ACCEPT


def test_anonymous_is_never_gated(client):
    services.publish("terms", "t1", material=True)
    assert client.get("/").status_code == 200


def test_accept_page_requires_login(client):
    response = client.get(ACCEPT)
    assert response.status_code == 302
    assert "login" in response["Location"]


def test_accept_page_without_pending_redirects_to_next(client, accepted_v1):
    response = client.get(ACCEPT, {"next": "/regulamin/"})
    assert response.status_code == 302 and response["Location"] == "/regulamin/"


def test_accept_page_rejects_foreign_next(client, accepted_v1):
    v2 = services.publish("terms", "v2", material=True)
    response = client.post(
        ACCEPT, {"confirm": "1", "document": [v2.pk], "next": "https://evil.example/"}
    )
    assert response.status_code == 302 and response["Location"] == "/"


def test_accept_without_checkbox_is_refused(client, accepted_v1):
    v2 = services.publish("terms", "v2", material=True)
    response = client.post(ACCEPT, {"document": [v2.pk]})
    assert response.status_code == 400
    assert 'role="alert"' in response.content.decode()
    assert not LegalAcceptance.objects.filter(document=v2).exists()


def test_accept_stale_page_is_refused(client, accepted_v1):
    v2 = services.publish("terms", "v2", material=True)
    v3 = services.publish("terms", "v3", material=True)
    response = client.post(ACCEPT, {"confirm": "1", "document": [v2.pk, "x"]})
    assert response.status_code == 400
    assert "nowa wersja 3" in response.content.decode()
    assert not LegalAcceptance.objects.filter(document__in=[v2, v3]).exists()


def test_accept_page_rejects_put(client, accepted_v1):
    services.publish("terms", "v2", material=True)
    assert client.put(ACCEPT).status_code == 405
