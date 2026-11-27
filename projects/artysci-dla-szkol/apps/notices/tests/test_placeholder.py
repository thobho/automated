"""The notice placeholder of US-4.2 (until US-6.1): public, GET only, records the catalog click."""

import pytest
from django.test import Client

from apps.analytics.models import Event

pytestmark = pytest.mark.django_db

URL = "/ogloszenia/nowe/"


def test_placeholder_is_public_and_says_soon():
    response = Client().get(URL)
    assert response.status_code == 200
    assert "wkrótce" in response.content.decode()
    assert not Event.objects.exists()


def test_post_is_refused():
    assert Client().post(URL).status_code == 405


def test_click_from_the_catalog_is_recorded_with_the_filters():
    response = Client().get(URL + "?wojewodztwo=lodzkie&cena_max=100&zrodlo=katalog")
    assert response.status_code == 200
    (event,) = Event.objects.all()
    assert event.name == "catalog_notice_cta_clicked"
    assert event.properties == {"wojewodztwo": "lodzkie", "cena_max": 100}
    assert event.actor == ""


def test_bad_filter_values_are_dropped_and_not_echoed():
    response = Client().get(URL + "?wojewodztwo=xyz&cena_max=abc&zrodlo=katalog")
    body = response.content.decode()
    assert "xyz" not in body and "abc" not in body
    assert Event.objects.get().properties == {}


def test_other_source_is_not_recorded():
    Client().get(URL + "?zrodlo=inne")
    assert not Event.objects.exists()
