import pytest

from apps.trust import services
from apps.trust.models import LegalAcceptance, LegalDocument

pytestmark = pytest.mark.django_db

ADMIN = "/django-admin/trust/legaldocument/"


@pytest.fixture
def admin_client(client, staff):
    # Tests accept the published versions for `staff` so the gate stays out of the way.
    client.force_login(staff)
    return client


def _accept_all(user):
    services.record_acceptance(user, ["terms", "privacy"])


def test_admin_publishes_new_version(admin_client, staff):
    services.publish("terms", "Regulamin v1", material=True)
    services.publish("privacy", "Polityka v1", material=True)
    _accept_all(staff)
    response = admin_client.post(
        f"{ADMIN}add/", {"kind": "terms", "body": "Regulamin v2", "material": ""}
    )
    assert response.status_code == 302
    v2 = services.current("terms")
    assert (v2.version, v2.body, v2.material) == (2, "Regulamin v2", False)
    assert LegalDocument.objects.get(kind="terms", version=1).body == "Regulamin v1"


def test_admin_add_page_and_changelist(admin_client, staff):
    assert admin_client.get(f"{ADMIN}add/").status_code == 200
    services.seed_placeholders()
    _accept_all(staff)
    response = admin_client.get(ADMIN)
    assert response.status_code == 200
    assert "Regulamin" in response.content.decode()


def test_admin_refuses_editing_published_version(admin_client, staff):
    v1 = services.publish("terms", "Regulamin v1", material=True)
    services.publish("privacy", "Polityka v1", material=True)
    _accept_all(staff)
    url = f"{ADMIN}{v1.pk}/change/"
    view = admin_client.get(url)
    assert view.status_code == 200  # view-only page
    assert 'name="body"' not in view.content.decode()
    edit = admin_client.post(url, {"kind": "terms", "body": "Zmieniony", "material": "on"})
    assert edit.status_code == 403
    assert LegalDocument.objects.get(pk=v1.pk).body == "Regulamin v1"


def test_admin_refuses_delete(admin_client, staff):
    v1 = services.publish("terms", "Regulamin v1", material=True)
    services.publish("privacy", "Polityka v1", material=True)
    _accept_all(staff)
    assert admin_client.post(f"{ADMIN}{v1.pk}/delete/", {"post": "yes"}).status_code == 403
    assert LegalDocument.objects.filter(pk=v1.pk).exists()


def test_acceptances_admin_read_only(admin_client, staff):
    services.publish("terms", "Regulamin v1", material=True)
    services.publish("privacy", "Polityka v1", material=True)
    _accept_all(staff)
    row = LegalAcceptance.objects.filter(user=staff).first()
    base = "/django-admin/trust/legalacceptance/"
    assert admin_client.get(base).status_code == 200
    assert admin_client.get(f"{base}add/").status_code == 403
    assert admin_client.post(f"{base}{row.pk}/delete/", {"post": "yes"}).status_code == 403


def test_admin_not_for_regular_users(client, user):
    client.force_login(user)
    response = client.get(ADMIN)
    assert response.status_code == 302
    assert "/django-admin/login/" in response["Location"]


def test_staff_with_pending_is_sent_to_accept_page(admin_client):
    services.publish("terms", "Regulamin v1", material=True)
    response = admin_client.get(ADMIN)
    assert response.status_code == 302
    assert response["Location"].startswith("/akceptacja-dokumentow/")
