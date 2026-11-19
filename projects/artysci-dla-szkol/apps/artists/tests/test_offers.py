"""Wizard step "Oferty" (US-2.9, D2, D6, D103): services, views, poster storage cleanup."""

import io
import logging

import pytest
from django.core.files.storage import storages
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client
from PIL import Image

from apps.accounts.tests.conftest import make_artist, make_institution_member
from apps.artists import services
from apps.artists.models import Artist, Offer
from apps.artists.services import InvalidOffer
from apps.core.tests.test_uploads import make_jpeg_with_gps
from apps.core.uploads import MB, UploadRejected
from config.settings.storage import build_storages

pytestmark = pytest.mark.django_db

OFFERS = "/artysta/profil/oferty/"
ADD = "/artysta/profil/oferty/nowa/"
BASICS_URL = "/artysta/profil/dane/"

BASICS = {
    "artist_type": "theatre",
    "name": "Teatr Testowy Kwiatki",
    "city": "Wrocław",
    "voivodeships": ["dolnoslaskie"],
    "audiences": ["grades_0_3"],
}

OFFER = {
    "title": "Kot w butach",
    "description": "Spektakl o kocie.\nDruga linia.",
    "age_from": 7,
    "age_to": 10,
    "duration_minutes": 45,
    "price_pln": 1200,
    "price_on_request": False,
}


def edit_url(pk):
    return f"/artysta/profil/oferty/{pk}/edycja/"


def delete_url(pk):
    return f"/artysta/profil/oferty/{pk}/usun/"


def move_url(pk):
    return f"/artysta/profil/oferty/{pk}/przesun/"


def form_data(**changes):
    data = {**OFFER, **changes}
    if not data.pop("price_on_request"):
        data.pop("price_on_request", None)
    else:
        data["price_on_request"] = "on"
    return {k: ("" if v is None else v) for k, v in data.items()}


@pytest.fixture
def storage(settings, tmp_path):
    """Filesystem storages in a temporary folder; returns the private root."""
    settings.STORAGE_BACKEND = "filesystem"
    settings.STORAGES = build_storages(
        "filesystem",
        public_base_url="http://media.test:8101/",
        private_root=tmp_path / "private",
        public_root=tmp_path / "public",
        signed_url_ttl=settings.MEDIA_SIGNED_URL_TTL,
    )
    return tmp_path / "private"


@pytest.fixture
def commit(django_capture_on_commit_callbacks):
    """Run on-commit callbacks (poster deletion) of the block: the test DB never commits."""
    return lambda: django_capture_on_commit_callbacks(execute=True)


@pytest.fixture
def artist_user():
    user = make_artist()
    services.save_basics(user, BASICS)
    return user


@pytest.fixture
def artist(artist_user):
    return Artist.objects.get(user=artist_user)


@pytest.fixture
def web(artist_user):
    client = Client()
    client.force_login(artist_user)
    return client


@pytest.fixture
def other_artist():
    user = make_artist("inny.artysta@example.invalid")
    services.save_basics(user, BASICS)
    return Artist.objects.get(user=user)


def jpeg(name="plakat.jpg", data=None):
    return SimpleUploadedFile(name, data or make_jpeg_with_gps(), content_type="image/jpeg")


def pdf_as_jpg():
    return SimpleUploadedFile("plakat.jpg", b"%PDF-1.7\n" + b"x" * 200, content_type="image/jpeg")


def too_large():
    return SimpleUploadedFile(
        "duzy.jpg", b"\xff\xd8\xff\xe0" + b"\0" * (15 * MB), content_type="image/jpeg"
    )


def exists(key):
    return storages["private"].exists(key)


def titles(artist):
    return list(services.offers_for(artist).values_list("title", flat=True))


def make_offers(artist, n):
    return [
        services.create_offer(artist, {**OFFER, "title": f"Oferta {i}"}) for i in range(1, n + 1)
    ]


# --- services --------------------------------------------------------------------------------


def test_create_offer_stores_values(artist):
    offer = services.create_offer(artist, OFFER)
    offer.refresh_from_db()
    assert services.offer_data(offer) == {**OFFER, "description": OFFER["description"]}
    assert offer.poster_key == "" and services.poster_url(offer) == ""
    assert services.has_offers(artist)


def test_create_offer_on_request_and_optional_fields(artist):
    data = {"title": " Warsztaty ", "description": " Opis ", "price_on_request": True}
    offer = services.create_offer(artist, data)
    assert (offer.title, offer.description) == ("Warsztaty", "Opis")
    assert offer.price_pln is None and offer.price_on_request
    assert offer.age_from is None and offer.age_to is None and offer.duration_minutes is None


@pytest.mark.parametrize(
    "changes, field",
    [
        ({"price_on_request": True}, "price_pln"),  # amount and "na zapytanie"
        ({"price_pln": None}, "price_pln"),  # neither
        ({"price_pln": ""}, "price_pln"),
        ({"age_from": 10, "age_to": 7}, "age_to"),
        ({"age_from": 100}, "age_from"),
        ({"age_to": -1}, "age_to"),
        ({"age_from": "siedem"}, "age_from"),
        ({"duration_minutes": 0}, "duration_minutes"),
        ({"price_pln": 0}, "price_pln"),
        ({"title": "  "}, "title"),
        ({"title": "x" * 201}, "title"),
        ({"description": ""}, "description"),
        ({"description": "x" * 5001}, "description"),
    ],
)
def test_invalid_offer_is_refused_and_nothing_saved(artist, changes, field):
    with pytest.raises(InvalidOffer) as error:
        services.create_offer(artist, {**OFFER, **changes})
    assert field in error.value.errors
    assert not Offer.objects.exists()
    assert not services.has_offers(artist)


def test_age_bounds_are_inclusive(artist):
    offer = services.create_offer(artist, {**OFFER, "age_from": 0, "age_to": 99})
    assert (offer.age_from, offer.age_to) == (0, 99)
    offer = services.create_offer(artist, {**OFFER, "age_from": 5, "age_to": 5})
    assert offer.age_from == offer.age_to == 5


def test_update_title_changes_nothing_else(artist):
    offer = services.create_offer(artist, OFFER)
    services.update_offer(artist, offer.pk, {**OFFER, "title": "Nowy tytuł"})
    offer.refresh_from_db()
    assert services.offer_data(offer) == {**OFFER, "title": "Nowy tytuł"}
    assert offer.position == 0


def test_update_invalid_changes_nothing(artist):
    offer = services.create_offer(artist, OFFER)
    with pytest.raises(InvalidOffer):
        services.update_offer(artist, offer.pk, {**OFFER, "title": "X", "price_pln": None})
    offer.refresh_from_db()
    assert offer.title == OFFER["title"]


def test_new_offers_go_to_the_end(artist):
    make_offers(artist, 3)
    assert titles(artist) == ["Oferta 1", "Oferta 2", "Oferta 3"]
    assert list(services.offers_for(artist).values_list("position", flat=True)) == [0, 1, 2]


def test_move_third_up_gives_1_3_2(artist):
    first, second, third = make_offers(artist, 3)
    services.move_offer(artist, third.pk, "up")
    assert titles(artist) == ["Oferta 1", "Oferta 3", "Oferta 2"]
    services.move_offer(artist, first.pk, "down")
    assert titles(artist) == ["Oferta 3", "Oferta 1", "Oferta 2"]


def test_move_at_the_ends_is_a_no_op(artist):
    first, _second, third = make_offers(artist, 3)
    services.move_offer(artist, first.pk, "up")
    services.move_offer(artist, third.pk, "down")
    assert titles(artist) == ["Oferta 1", "Oferta 2", "Oferta 3"]


def test_move_refuses_bad_direction_and_foreign_offer(artist, other_artist):
    (offer,) = make_offers(artist, 1)
    with pytest.raises(ValueError):
        services.move_offer(artist, offer.pk, "left")
    with pytest.raises(Offer.DoesNotExist):
        services.move_offer(other_artist, offer.pk, "up")


def test_order_survives_a_deleted_offer(artist):
    first, second, third = make_offers(artist, 3)
    services.delete_offer(artist, second.pk)
    services.move_offer(artist, third.pk, "up")
    assert titles(artist) == ["Oferta 3", "Oferta 1"]


def test_reorder_offers(artist, other_artist):
    a, b, c = make_offers(artist, 3)
    services.reorder_offers(artist, [c.pk, a.pk, b.pk])
    assert titles(artist) == ["Oferta 3", "Oferta 1", "Oferta 2"]
    (foreign,) = make_offers(other_artist, 1)
    for bad in ([a.pk, b.pk], [a.pk, b.pk, c.pk, foreign.pk], [a.pk, a.pk, b.pk]):
        with pytest.raises(ValueError):
            services.reorder_offers(artist, bad)
    assert titles(artist) == ["Oferta 3", "Oferta 1", "Oferta 2"]


def test_offers_of_another_artist_are_not_reachable(artist, other_artist):
    (offer,) = make_offers(other_artist, 1)
    with pytest.raises(Offer.DoesNotExist):
        services.get_offer(artist, offer.pk)
    with pytest.raises(Offer.DoesNotExist):
        services.update_offer(artist, offer.pk, {**OFFER, "title": "Przejęta"})
    with pytest.raises(Offer.DoesNotExist):
        services.delete_offer(artist, offer.pk)
    offer.refresh_from_db()
    assert offer.title == "Oferta 1"
    assert services.offers_for(artist).count() == 0


def test_has_offers(artist):
    assert not services.has_offers(None)
    assert not services.has_offers(artist)
    (offer,) = make_offers(artist, 1)
    assert services.has_offers(artist)
    services.delete_offer(artist, offer.pk)
    assert not services.has_offers(artist)


def test_offers_step_is_done_with_one_offer(artist):
    def offers_done():
        return {s.step.key: s.done for s in services.wizard_steps(artist)}["offers"]

    assert not offers_done()
    make_offers(artist, 1)
    assert offers_done()


def test_offer_str(artist):
    (offer,) = make_offers(artist, 1)
    assert str(offer) == f"Offer {offer.pk}"


# --- poster storage --------------------------------------------------------------------------


def test_poster_is_private_and_has_no_exif(artist, storage, client):
    offer = services.create_offer(artist, OFFER, poster=jpeg())
    assert offer.poster_key.startswith("photo/") and exists(offer.poster_key)
    assert (storage / offer.poster_key).is_file()
    with storages["private"].open(offer.poster_key, "rb") as handle:
        data = handle.read()
    image = Image.open(io.BytesIO(data))
    assert not image.getexif() and b"TestCam" not in data
    url = services.poster_url(offer)
    assert url.startswith("/media/private/")
    assert client.get(url).status_code == 200


def test_replacing_the_poster_deletes_the_old_file(artist, storage, commit):
    offer = services.create_offer(artist, OFFER, poster=jpeg())
    old = offer.poster_key
    with commit():
        offer = services.update_offer(artist, offer.pk, OFFER, poster=jpeg())
    assert offer.poster_key != old and exists(offer.poster_key)
    assert not exists(old)


def test_removing_the_poster_deletes_the_file(artist, storage, commit):
    offer = services.create_offer(artist, OFFER, poster=jpeg())
    old = offer.poster_key
    with commit():
        offer = services.update_offer(artist, offer.pk, OFFER, remove_poster=True)
    assert offer.poster_key == "" and not exists(old)
    assert list(storage.rglob("*.jpg")) == []


def test_editing_without_a_new_poster_keeps_it(artist, storage, commit):
    offer = services.create_offer(artist, OFFER, poster=jpeg())
    with commit():
        updated = services.update_offer(artist, offer.pk, {**OFFER, "title": "Inny"})
    assert updated.poster_key == offer.poster_key and exists(offer.poster_key)


def test_deleting_the_offer_deletes_the_poster(artist, storage, commit):
    offer = services.create_offer(artist, OFFER, poster=jpeg())
    with commit():
        services.delete_offer(artist, offer.pk)
    assert not Offer.objects.exists()
    assert not exists(offer.poster_key)
    assert list(storage.rglob("*.jpg")) == []


@pytest.mark.parametrize("make_file, code", [(pdf_as_jpg, "bad_type"), (too_large, "too_large")])
def test_rejected_poster_saves_nothing(artist, storage, make_file, code):
    with pytest.raises(UploadRejected) as error:
        services.create_offer(artist, OFFER, poster=make_file())
    assert error.value.code == code
    assert not Offer.objects.exists()
    offer = services.create_offer(artist, OFFER, poster=jpeg())
    with pytest.raises(UploadRejected):
        services.update_offer(artist, offer.pk, {**OFFER, "title": "Nie"}, poster=make_file())
    offer.refresh_from_db()
    assert offer.title == OFFER["title"] and exists(offer.poster_key)
    assert len(list(storage.rglob("*.*"))) == 1


def test_failed_insert_removes_the_new_poster(artist, storage, monkeypatch):
    def boom(**kwargs):
        raise RuntimeError("db down")

    monkeypatch.setattr(Offer.objects, "create", boom)
    with pytest.raises(RuntimeError):
        services.create_offer(artist, OFFER, poster=jpeg())
    assert list(storage.rglob("*.*")) == []


def test_failed_update_removes_the_new_poster(artist, storage, monkeypatch):
    offer = services.create_offer(artist, OFFER, poster=jpeg())

    def boom(self, *args, **kwargs):
        raise RuntimeError("db down")

    monkeypatch.setattr(Offer, "save", boom)
    with pytest.raises(RuntimeError):
        services.update_offer(artist, offer.pk, OFFER, poster=jpeg())
    assert [p.name for p in storage.rglob("*.*")] == [offer.poster_key.split("/")[1]]


def test_storage_failure_on_delete_is_logged(artist, storage, monkeypatch, caplog, commit):
    offer = services.create_offer(artist, OFFER, poster=jpeg())

    def broken(key):
        raise OSError("storage down")

    monkeypatch.setattr(storages["private"], "delete", broken)
    with caplog.at_level(logging.WARNING, "apps.artists.profile"), commit():
        services.delete_offer(artist, offer.pk)
    assert not Offer.objects.exists()
    assert any(getattr(r, "event", "") == "offer_poster_orphan" for r in caplog.records)
    assert offer.poster_key not in caplog.text


# --- views -----------------------------------------------------------------------------------


def test_add_offer_and_list_it(web, artist):
    response = web.post(ADD, form_data(), follow=True)
    assert response.redirect_chain == [(OFFERS, 302)]
    body = response.content.decode()
    assert "Dodano ofertę." in body
    assert "Kot w butach" in body and "Spektakl o kocie.<br>Druga linia." in body
    assert '<dd data-field="age">7–10 lat</dd>' in body
    assert '<dd data-field="duration">45 min</dd>' in body
    assert '<dd data-field="price">1200 zł</dd>' in body
    (offer,) = services.offers_for(artist)
    assert services.offer_data(offer) == OFFER


def test_add_offer_on_request_is_listed(web, artist):
    web.post(ADD, form_data(price_pln=None, price_on_request=True))
    body = web.get(OFFERS).content.decode()
    assert '<dd data-field="price">na zapytanie</dd>' in body


@pytest.mark.parametrize(
    "changes, field, message",
    [
        ({"price_on_request": True}, "price_pln", "jedno z dwóch"),
        ({"price_pln": None}, "price_pln", "jedno z dwóch"),
        ({"age_from": 10, "age_to": 7}, "age_to", "nie może być mniejszy"),
        ({"title": ""}, "title", "Podaj tytuł."),
        ({"description": ""}, "description", "Podaj opis."),
        ({"duration_minutes": 0}, "duration_minutes", ""),
        ({"age_from": 120}, "age_from", ""),
    ],
)
def test_add_invalid_offer_shows_form_error(web, changes, field, message):
    response = web.post(ADD, form_data(**changes))
    body = response.content.decode()
    assert response.status_code == 400
    assert f'id="{field}-error"' in body and message in body
    assert not Offer.objects.exists()


def test_add_form_page(web):
    response = web.get(ADD)
    body = response.content.decode()
    assert response.status_code == 200
    assert 'enctype="multipart/form-data"' in body and 'name="poster"' in body
    assert 'name="remove_poster"' not in body  # nothing to remove yet


def test_edit_title_lists_new_title_and_nothing_else_changes(web, artist):
    offer = services.create_offer(artist, OFFER)
    page = web.get(edit_url(offer.pk)).content.decode()
    assert 'value="Kot w butach"' in page and 'value="1200"' in page and 'value="45"' in page
    response = web.post(edit_url(offer.pk), form_data(title="Kot w kaloszach"), follow=True)
    assert response.redirect_chain == [(OFFERS, 302)]
    assert "Kot w kaloszach" in response.content.decode()
    offer.refresh_from_db()
    assert services.offer_data(offer) == {**OFFER, "title": "Kot w kaloszach"}


def test_edit_invalid_shows_error_and_changes_nothing(web, artist):
    offer = services.create_offer(artist, OFFER)
    response = web.post(edit_url(offer.pk), form_data(title="Zmiana", age_from=10, age_to=7))
    assert response.status_code == 400 and 'id="age_to-error"' in response.content.decode()
    offer.refresh_from_db()
    assert offer.title == OFFER["title"]


def test_move_third_up_and_reload(web, artist):
    _first, _second, third = make_offers(artist, 3)
    response = web.post(move_url(third.pk), {"direction": "up"})
    assert response.status_code == 302
    assert response["Location"] == f"{OFFERS}#offer-{third.pk}"
    body = web.get(OFFERS).content.decode()
    positions = [body.index(f"<h2>Oferta {n}</h2>") for n in (1, 3, 2)]
    assert positions == sorted(positions)
    assert titles(artist) == ["Oferta 1", "Oferta 3", "Oferta 2"]


def test_move_needs_a_valid_direction_and_post(web, artist):
    (offer,) = make_offers(artist, 1)
    assert web.post(move_url(offer.pk), {"direction": "sideways"}).status_code == 400
    assert web.post(move_url(offer.pk)).status_code == 400
    assert web.get(move_url(offer.pk)).status_code == 405


def test_list_has_move_buttons_only_where_they_move(web, artist):
    make_offers(artist, 2)
    body = web.get(OFFERS).content.decode()
    assert body.count('value="up"') == 1 and body.count('value="down"') == 1


def test_twenty_offers_listed_in_order_on_one_page(web, artist):
    make_offers(artist, 20)
    response = web.get(OFFERS)
    body = response.content.decode()
    assert response.status_code == 200
    assert 'data-count="20"' in body
    positions = [body.index(f"<h2>Oferta {n}</h2>") for n in range(1, 21)]
    assert positions == sorted(positions)


def test_empty_list(web):
    response = web.get(OFFERS)
    assert response.status_code == 200
    assert "Nie masz jeszcze żadnej oferty." in response.content.decode()


def test_delete_asks_then_deletes_offer_and_poster(web, artist, storage, commit):
    offer = services.create_offer(artist, OFFER, poster=jpeg())
    page = web.get(delete_url(offer.pk))
    assert page.status_code == 200 and "Tak, usuń ofertę" in page.content.decode()
    assert Offer.objects.filter(pk=offer.pk).exists()  # GET changes nothing
    with commit():
        response = web.post(delete_url(offer.pk), follow=True)
    assert response.redirect_chain == [(OFFERS, 302)]
    assert "Usunięto ofertę." in response.content.decode()
    assert not Offer.objects.exists() and not exists(offer.poster_key)


def test_add_with_poster_via_form(web, artist, storage):
    response = web.post(ADD, {**form_data(), "poster": jpeg()})
    assert response.status_code == 302
    (offer,) = services.offers_for(artist)
    assert exists(offer.poster_key)
    data = (storage / offer.poster_key).read_bytes()
    assert not Image.open(io.BytesIO(data)).getexif()
    body = web.get(OFFERS).content.decode()
    assert 'data-field="poster"' in body and "/media/private/" in body
    edit = web.get(edit_url(offer.pk)).content.decode()
    assert "Obecny plakat" in edit and 'name="remove_poster"' in edit


def test_replace_and_remove_poster_via_form(web, artist, storage, commit):
    offer = services.create_offer(artist, OFFER, poster=jpeg())
    old = offer.poster_key
    with commit():
        web.post(edit_url(offer.pk), {**form_data(), "poster": jpeg()})
    offer.refresh_from_db()
    assert offer.poster_key != old and not exists(old) and exists(offer.poster_key)
    current = offer.poster_key
    with commit():
        web.post(edit_url(offer.pk), {**form_data(), "remove_poster": "on"})
    offer.refresh_from_db()
    assert offer.poster_key == "" and not exists(current)


@pytest.mark.parametrize(
    "make_file, message",
    [(pdf_as_jpg, "Ten typ pliku nie jest dozwolony."), (too_large, "Plik jest za duży")],
)
def test_rejected_poster_via_form(web, artist, storage, make_file, message):
    response = web.post(ADD, {**form_data(), "poster": make_file()})
    body = response.content.decode()
    assert response.status_code == 400
    assert message in body and 'id="poster-error"' in body
    assert not Offer.objects.exists()
    offer = services.create_offer(artist, OFFER)
    response = web.post(edit_url(offer.pk), {**form_data(title="Nie"), "poster": make_file()})
    assert response.status_code == 400 and message in response.content.decode()
    offer.refresh_from_db()
    assert offer.title == OFFER["title"] and offer.poster_key == ""


def test_service_race_error_is_shown(web, artist, monkeypatch):
    def refuse(*args, **kwargs):
        raise InvalidOffer({"title": "Zmieniono w międzyczasie."})

    monkeypatch.setattr(services, "create_offer", refuse)
    response = web.post(ADD, form_data())
    assert response.status_code == 400 and "Zmieniono w międzyczasie." in response.content.decode()


def test_script_in_title_is_escaped(web, artist):
    services.create_offer(
        artist, {**OFFER, "title": "<script>alert(1)</script>", "description": "<b>x</b>"}
    )
    body = web.get(OFFERS).content.decode()
    assert "<script>alert(1)</script>" not in body and "<b>x</b>" not in body
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in body and "&lt;b&gt;x&lt;/b&gt;" in body


def test_other_artists_offer_is_404_and_unchanged(web, other_artist):
    (offer,) = make_offers(other_artist, 1)
    for url in (edit_url(offer.pk), delete_url(offer.pk)):
        assert web.get(url).status_code == 404
    assert web.post(edit_url(offer.pk), form_data(title="Przejęta")).status_code == 404
    assert web.post(delete_url(offer.pk)).status_code == 404
    assert web.post(move_url(offer.pk), {"direction": "up"}).status_code == 404
    offer.refresh_from_db()
    assert offer.title == "Oferta 1"
    # a missing id looks the same as a foreign one
    assert web.get(edit_url(999999)).status_code == 404


def test_institution_gets_403_and_nothing_changes(artist):
    (offer,) = make_offers(artist, 1)
    client = Client()
    client.force_login(make_institution_member())
    for url in (OFFERS, ADD, edit_url(offer.pk), delete_url(offer.pk)):
        assert client.get(url).status_code == 403
    assert client.post(delete_url(offer.pk)).status_code == 403
    assert client.post(move_url(offer.pk), {"direction": "down"}).status_code == 403
    assert client.post(ADD, form_data()).status_code == 403
    assert Offer.objects.count() == 1


@pytest.mark.parametrize("path", [OFFERS, ADD, edit_url(1), delete_url(1)])
def test_offer_pages_need_complete_basics(path):
    client = Client()
    client.force_login(make_artist())  # empty basics
    response = client.get(path, follow=True)
    assert response.redirect_chain == [(BASICS_URL, 302)]


def test_anonymous_goes_to_login():
    response = Client().get(ADD)
    assert response.status_code == 302 and response["Location"] == f"/logowanie/?next={ADD}"


def test_overview_marks_offers_done(web, artist):
    make_offers(artist, 1)
    body = web.get("/artysta/kreator/").content.decode()
    assert 'data-step="offers"\n          data-status="done"' in body


# --- seed ------------------------------------------------------------------------------------


def test_seed_gives_one_artist_a_20_offer_repertoire_idempotently():
    from django.core.management import call_command

    call_command("seed")
    artist = Artist.objects.get(user__email="artysta01@example.invalid")
    first = list(services.offers_for(artist).values_list("title", "position", "price_pln"))
    assert len(first) == 20
    assert first[0][0] == "Spektakl testowy 01" and first[-1][0] == "Spektakl testowy 20"
    assert Offer.objects.count() == 20
    assert services.offers_for(artist).filter(price_on_request=True).count() == 4
    call_command("seed")
    assert list(services.offers_for(artist).values_list("title", "position", "price_pln")) == first
    assert Offer.objects.count() == 20
    assert not Offer.objects.exclude(poster_key="").exists()
