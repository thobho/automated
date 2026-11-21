import json
import re

import pytest
from django.test import Client

from apps.accounts.tests.conftest import make_admin, make_institution_member
from apps.profiles import ai, generation
from apps.quality.models import Generation

from .factories import make_seed_artist, valid_profile

pytestmark = pytest.mark.django_db

PAGE = "/artysta/profil/generowanie/"
STATUS = PAGE + "status/"
START = PAGE + "start/"


@pytest.fixture(autouse=True)
def fake_ai(monkeypatch):
    fake = ai.FakeClient(reply=json.dumps(valid_profile()), cost_usd="0.001")
    monkeypatch.setattr(ai, "get_client", lambda: fake)
    return fake


@pytest.fixture
def artist():
    return make_seed_artist()


@pytest.fixture
def web(artist):
    client = Client()
    client.force_login(artist.user)
    return client


def test_no_generation_yet(web):
    response = web.get(PAGE)
    assert response.status_code == 200
    assert "Profil nie był jeszcze generowany" in response.content.decode()


def test_start_shows_running_and_polls_without_inline_script(web, queue):
    response = web.post(START, follow=True)
    body = response.content.decode()
    assert response.status_code == 200
    assert 'data-status="running"' in body and "trwa" in body
    assert 'hx-trigger="every 3s"' in body
    assert not re.search(r"<script(?![^>]*\bsrc=)", body)  # no inline script
    assert "disabled" in body
    assert len(queue.jobs) == 1


def test_second_start_is_refused_with_a_message(web, queue):
    web.post(START)
    response = web.post(START, follow=True)
    assert "już trwa" in response.content.decode()
    assert Generation.objects.count() == 1 and len(queue.jobs) == 1


def test_ready_status(web, artist):
    generation.run_generation(generation.request_generation(artist, "manual").pk)
    body = web.get(STATUS).content.decode()
    assert "gotowa" in body and 'data-status="ready"' in body and "hx-get" not in body


def test_error_status_shows_the_reason(web, artist, fake_ai):
    fake_ai.reply = "nie json"
    generation.run_generation(generation.request_generation(artist, "manual").pk)
    body = web.get(PAGE).content.decode()
    assert "błąd" in body and "JSON" in body and 'role="alert"' in body


def test_only_the_owners_generation_is_shown(web, artist):
    other = make_seed_artist("inny.artysta@example.invalid")
    generation.run_generation(generation.request_generation(other, "manual").pk)
    assert "Profil nie był jeszcze generowany" in web.get(STATUS).content.decode()


def test_start_needs_post(web):
    assert web.get(START).status_code == 405


@pytest.mark.parametrize("url", [PAGE, STATUS])
def test_anonymous_goes_to_login(url):
    response = Client().get(url)
    assert response.status_code == 302 and response["Location"].startswith("/logowanie/")
    assert Client().post(START).status_code == 302


def test_institution_and_admin_get_403():
    for user in (make_institution_member(), make_admin()):
        client = Client()
        client.force_login(user)
        for url in (PAGE, STATUS):
            assert client.get(url).status_code == 403
        assert client.post(START).status_code == 403
    assert Generation.objects.count() == 0
