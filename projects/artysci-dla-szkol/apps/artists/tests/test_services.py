import pytest
from django.contrib.auth import get_user_model

from apps.analytics.models import Event
from apps.artists import services
from apps.artists.models import Artist
from apps.artists.services import Registration
from apps.trust import services as trust
from apps.trust.errors import NoPublishedVersion
from apps.trust.models import LegalAcceptance

from .conftest import IP, NAME, NEW_EMAIL, jobs_for

pytestmark = pytest.mark.django_db

BASE = "http://testserver/"


def test_register_new_artist(documents, queue, clock):
    assert services.register_artist(NEW_EMAIL, f"  {NAME} ", IP, link_base=BASE) is (
        Registration.SENT
    )
    artist = Artist.objects.select_related("user").get()
    assert artist.name == NAME and artist.user.email == NEW_EMAIL
    assert LegalAcceptance.objects.filter(user=artist.user).count() == 2
    assert Event.objects.filter(name="artist_registered").count() == 1
    assert len(jobs_for(queue)) == 1


def test_register_existing_address_changes_nothing(documents, queue, clock):
    user = get_user_model().objects.create_user(email=NEW_EMAIL)
    assert services.register_artist(NEW_EMAIL, NAME, IP, link_base=BASE) is Registration.SENT
    assert not Artist.objects.exists()
    assert not LegalAcceptance.objects.exists()
    assert not Event.objects.exists()
    (job,) = jobs_for(queue)
    assert job["args"]["user_id"] == user.pk


def test_register_unavailable_without_documents(db, queue, clock):
    trust.publish("terms", "Regulamin", material=True)
    assert services.register_artist(NEW_EMAIL, NAME, IP, link_base=BASE) is (
        Registration.UNAVAILABLE
    )
    assert not get_user_model().objects.exists()


def test_document_withdrawn_mid_registration_rolls_back(documents, queue, clock, monkeypatch):
    def gone(user, kinds):
        raise NoPublishedVersion("terms")

    monkeypatch.setattr(trust, "record_acceptance", gone)
    assert services.register_artist(NEW_EMAIL, NAME, IP, link_base=BASE) is (
        Registration.UNAVAILABLE
    )
    assert not get_user_model().objects.exists() and not Artist.objects.exists()
    assert jobs_for(queue) == []


def test_register_rate_limited(documents, queue, clock, settings):
    settings.LOGIN_EMAIL_LIMIT_PER_ADDRESS = 0
    assert services.register_artist(NEW_EMAIL, NAME, IP, link_base=BASE) is (
        Registration.RATE_LIMITED
    )
    assert not get_user_model().objects.exists()


def test_rate_limit_reached_between_check_and_send(documents, queue, clock, monkeypatch):
    monkeypatch.setattr(services.accounts, "request_login", lambda *a, **k: False)
    assert services.register_artist(NEW_EMAIL, NAME, IP, link_base=BASE) is (
        Registration.RATE_LIMITED
    )


def test_documents_published(db):
    assert not services.documents_published()
    trust.publish("terms", "R", material=True)
    assert not services.documents_published()
    trust.publish("privacy", "P", material=True)
    assert services.documents_published()


def test_artist_for(documents, queue, clock):
    from django.contrib.auth.models import AnonymousUser

    services.register_artist(NEW_EMAIL, NAME, IP, link_base=BASE)
    user = get_user_model().objects.get()
    assert services.artist_for(user) == user.artist
    assert services.artist_for(AnonymousUser()) is None
    assert str(user.artist) == f"Artist {user.artist.pk}"
