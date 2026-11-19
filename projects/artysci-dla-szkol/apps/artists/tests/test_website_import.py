"""Import from the artist's own website (US-2.2). DNS and HTTP are faked (`FakeNet`), oEmbed
is faked, the upload path and the job queue are the real ones (in memory)."""

import io
import logging

import pytest
from django.test import Client
from PIL import Image

from apps.accounts.tests.conftest import make_artist, make_institution_member, run_worker
from apps.analytics.catalog import EVENT_CATALOG
from apps.analytics.models import Event
from apps.artists import services, tasks, website_import
from apps.artists.models import (
    Artist,
    ImportStatus,
    Material,
    MaterialKind,
    ScanStatus,
    WebsiteImport,
)
from apps.artists.tests.conftest import jobs_for
from apps.artists.tests.test_materials import (  # noqa: F401  (fixtures)
    BASICS,
    oembed,
    storage,
)
from apps.core import safefetch
from apps.core.safefetch import RawResponse
from apps.core.tests.test_safefetch import FakeNet
from apps.core.tests.test_uploads import make_jpeg_with_gps, read_stored
from apps.profiles.ai.scrub import scrub
from apps.trust import services as trust
from apps.trust.models import ArtistStatement

pytestmark = pytest.mark.django_db

FORM = "/artysta/profil/import/"
SITE = "http://teatr.example"
PUBLIC = "93.184.215.14"
OTHER = "85.128.1.1"
VALID_PESEL = "44051401359"
VALID_ID_CARD = "ABA300000"
YOUTUBE_ID = "dQw4w9WgXcQ"


def status_url(pk):
    return f"/artysta/profil/import/{pk}/"


# --- fixtures --------------------------------------------------------------------------------


@pytest.fixture
def wording(db):
    return trust.publish("material_rights", "Oświadczam, że mam prawa do materiałów.", True)


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
def net(monkeypatch):
    fake = FakeNet()
    fake.dns["teatr.example"] = [PUBLIC]
    fake.dns["www.teatr.example"] = [PUBLIC]
    fake.dns["obcy.example"] = [OTHER]
    monkeypatch.setattr(safefetch, "resolver", fake.resolver)
    monkeypatch.setattr(safefetch, "transport", fake.transport)
    return fake


def page(body: str, status=200, content_type="text/html; charset=utf-8", **headers):
    return RawResponse(status, {"content-type": content_type, **headers}, body.encode())


def image(data: bytes, content_type="image/jpeg"):
    return RawResponse(200, {"content-type": content_type}, data)


def html(title, body):
    return f"<html><head><title>{title}</title></head><body>{body}</body></html>"


def png() -> bytes:
    out = io.BytesIO()
    Image.new("RGB", (30, 30), "blue").save(out, "PNG")
    return out.getvalue()


def queued_import(artist, url=f"{SITE}/") -> WebsiteImport:
    return website_import.start_import(artist, url, rights_confirmed=True)


def run(artist, url=f"{SITE}/") -> WebsiteImport:
    record = queued_import(artist, url)
    website_import.run_import(record.pk)
    record.refresh_from_db()
    return record


# --- the form: rights checkbox and statement (AC 1) --------------------------------------------


def test_form_page_renders(web):
    response = web.get(FORM)
    assert response.status_code == 200
    body = response.content.decode()
    assert 'name="url"' in body and 'name="confirm"' in body
    assert "10 podstron" in body and "20 MB" in body


def test_without_the_checkbox_a_form_error_and_no_import(web, artist, wording, queue):
    response = web.post(FORM, {"url": f"{SITE}/"})
    assert response.status_code == 400
    assert "Zaznacz, że strona jest Twoja" in response.content.decode()
    assert WebsiteImport.objects.count() == 0
    assert ArtistStatement.objects.count() == 0
    assert jobs_for(queue, "artists.run_website_import") == []


def test_without_url_a_form_error(web, wording):
    response = web.post(FORM, {"confirm": "1"})
    assert response.status_code == 400
    assert "Podaj adres strony." in response.content.decode()


def test_ticked_records_the_statement_and_queues_the_import(web, artist, wording, queue):
    response = web.post(FORM, {"url": f"{SITE}/", "confirm": "1"})
    record = WebsiteImport.objects.get()
    assert response.status_code == 302 and response["Location"] == status_url(record.pk)
    statement = ArtistStatement.objects.get(artist=artist, kind="material_rights")
    assert record.rights_statement == statement and record.rights_confirmed_at
    assert record.url == f"{SITE}/" and record.status == ImportStatus.QUEUED
    [job] = jobs_for(queue, "artists.run_website_import")
    assert job["args"] == {"import_id": record.pk} and job["queue_name"] == "media"


def test_an_existing_statement_is_reused(artist, wording, net):
    existing = trust.make_statement(artist, "material_rights")
    first = run(artist)
    second = queued_import(artist)
    assert first.rights_statement == existing == second.rights_statement
    assert ArtistStatement.objects.filter(kind="material_rights").count() == 1


def test_no_published_wording_refuses(web, artist):
    response = web.post(FORM, {"url": f"{SITE}/", "confirm": "1"})
    assert response.status_code == 400
    assert "nie jest jeszcze dostępne" in response.content.decode()
    assert WebsiteImport.objects.count() == 0


def test_service_refuses_without_confirmation(artist, wording):
    with pytest.raises(website_import.ImportRefused) as caught:
        website_import.start_import(artist, f"{SITE}/", rights_confirmed=False)
    assert caught.value.code == "no_rights"


def test_one_import_at_a_time(web, artist, wording, queue):
    queued_import(artist)
    response = web.post(FORM, {"url": f"{SITE}/", "confirm": "1"})
    assert response.status_code == 400
    assert "już trwa" in response.content.decode()
    assert WebsiteImport.objects.count() == 1


def test_daily_limit(artist, wording, net, monkeypatch):
    monkeypatch.setattr(website_import, "MAX_PER_DAY", 2)
    run(artist)
    run(artist)
    with pytest.raises(website_import.ImportRefused) as caught:
        queued_import(artist)
    assert caught.value.code == "limit"


# --- crawling limits (AC 2, 5) -----------------------------------------------------------------


def test_twelve_pages_only_ten_fetched_and_never_another_host(artist, wording, net):
    links = "".join(f'<a href="/strona-{n}">Strona {n}</a>' for n in range(1, 13))
    links += '<a href="http://obcy.example/">Obcy</a><a href="https://obcy.example/x">x</a>'
    net.pages[f"{SITE}/"] = page(html("Start", f"<p>Teatr</p>{links}"))
    for n in range(1, 13):
        net.pages[f"{SITE}/strona-{n}"] = page(html(f"Strona {n}", f"<p>Tekst {n}</p>{links}"))
    record = run(artist)
    hosts = {c[0] for c in net.connections}
    assert hosts == {"teatr.example"}
    assert len(net.connections) == 10 and record.page_count == 10
    assert record.status == ImportStatus.DONE
    assert any("najwyżej 10 podstron" in s["why"] for s in record.skipped)


def test_www_and_bare_host_are_the_same_site(artist, wording, net):
    net.pages[f"{SITE}/"] = page(
        html("Start", '<p>Teatr</p><a href="http://www.teatr.example/o-nas#top">O nas</a>')
    )
    net.pages["http://www.teatr.example/o-nas"] = page(html("O nas", "<p>Zespół</p>"))
    record = run(artist)
    assert record.page_count == 2


def test_links_to_files_are_not_fetched_as_pages(artist, wording, net):
    net.pages[f"{SITE}/"] = page(
        html("Start", '<p>Teatr</p><a href="/oferta.pdf">PDF</a><a href="mailto:x@y.pl">m</a>')
    )
    run(artist)
    assert [c[2] for c in net.connections] == ["/"]


@pytest.mark.parametrize(
    "url",
    [
        "http://127.0.0.1/",
        "http://10.0.0.5/",
        "http://169.254.169.254/latest/meta-data/",
        "http://[::1]/",
        "http://[::ffff:127.0.0.1]/",
        "ftp://example.com/",
        "http://user:pass@example.com/",
    ],
)
def test_forbidden_urls_fail_with_a_message_and_no_connection(artist, wording, net, queue, url):
    record = queued_import(artist, url)
    assert record.status == ImportStatus.FAILED and record.message
    assert record.finished_at is not None
    assert jobs_for(queue, "artists.run_website_import") == []
    assert net.connections == [] and net.lookups == []


def test_public_name_resolving_to_a_private_address_fails(artist, wording, net):
    net.dns["teatr.example"] = ["10.0.0.8"]
    record = run(artist)
    assert record.status == ImportStatus.FAILED
    assert "sieć wewnętrzną" in record.message
    assert net.connections == []


def test_redirect_to_a_private_address_fails(artist, wording, net):
    net.pages[f"{SITE}/"] = page("", status=302, location="http://169.254.169.254/")
    record = run(artist)
    assert record.status == ImportStatus.FAILED and "sieć wewnętrzną" in record.message
    assert len(net.connections) == 1


def test_four_redirects_in_a_row_fail(artist, wording, net):
    for n in range(4):
        net.pages[f"{SITE}/{'' if n == 0 else n}"] = page("", status=301, location=f"/{n + 1}")
    net.pages[f"{SITE}/4"] = page(html("Koniec", "<p>tekst</p>"))
    record = run(artist)
    assert record.status == ImportStatus.FAILED
    assert "zbyt wiele razy" in record.message


def test_redirect_from_bare_to_www_is_followed_and_sets_the_site(artist, wording, net):
    net.pages[f"{SITE}/"] = page("", status=301, location="https://www.teatr.example/")
    net.pages["https://www.teatr.example/"] = page(
        html("Start", '<p>Teatr</p><a href="/kontakt">Kontakt</a>')
    )
    net.pages["https://www.teatr.example/kontakt"] = page(html("Kontakt", "<p>Pisz</p>"))
    record = run(artist)
    assert record.status == ImportStatus.DONE and record.page_count == 2


def test_slow_first_page_fails(artist, wording, net, monkeypatch):
    def slow(target, address, *, timeout, max_bytes):
        assert timeout == 30.0
        raise safefetch._error("timeout")

    monkeypatch.setattr(safefetch, "transport", slow)
    record = run(artist)
    assert record.status == ImportStatus.FAILED
    assert record.message == "Strona odpowiadała zbyt długo."


def test_slow_later_page_gives_a_partial_import(artist, wording, net, monkeypatch):
    net.pages[f"{SITE}/"] = page(html("Start", '<p>Teatr</p><a href="/wolna">Wolna</a>'))
    original = net.transport

    def transport(target, address, *, timeout, max_bytes):
        if target.path == "/wolna":
            raise safefetch._error("timeout")
        return original(target, address, timeout=timeout, max_bytes=max_bytes)

    monkeypatch.setattr(safefetch, "transport", transport)
    record = run(artist)
    assert record.status == ImportStatus.PARTIAL and record.page_count == 1
    assert record.skipped == [{"what": f"{SITE}/wolna", "why": "Strona odpowiadała zbyt długo."}]
    assert "Teatr" in record.text


def test_total_size_limit_stops_fetching(artist, wording, net, settings):
    settings.WEBSITE_IMPORT_MAX_BYTES = 5000
    filler = "x" * 1800
    links = "".join(f'<a href="/s{n}">s</a>' for n in range(5))
    net.pages[f"{SITE}/"] = page(html("Start", f"<p>{filler}</p>{links}"))
    for n in range(5):
        net.pages[f"{SITE}/s{n}"] = page(html(f"S{n}", f"<p>{filler}</p>"))
    record = run(artist)
    assert record.status == ImportStatus.PARTIAL
    assert "limit 4 MB" not in record.message and "Osiągnięto limit" in record.message
    assert record.page_count == 2 and record.bytes_fetched <= 5000


def test_first_page_over_the_total_fails(artist, wording, net, settings):
    settings.WEBSITE_IMPORT_MAX_BYTES = 100
    net.pages[f"{SITE}/"] = page(html("Start", "<p>" + "x" * 500 + "</p>"))
    record = run(artist)
    assert record.status == ImportStatus.FAILED and record.message == "Strona jest zbyt duża."
    assert record.bytes_fetched == 0


def test_first_page_404_fails(artist, wording, net):
    record = run(artist)
    assert record.status == ImportStatus.FAILED and "błędem 404" in record.message


def test_first_page_not_html_fails(artist, wording, net):
    net.pages[f"{SITE}/"] = page("{}", content_type="application/json")
    record = run(artist)
    assert record.status == ImportStatus.FAILED and "nie jest strona HTML" in record.message


def test_later_page_errors_and_non_html_are_skipped(artist, wording, net):
    net.pages[f"{SITE}/"] = page(
        html("Start", '<p>Teatr</p><a href="/brak">x</a><a href="/feed">y</a>')
    )
    net.pages[f"{SITE}/feed"] = page("<rss/>", content_type="application/rss+xml")
    record = run(artist)
    assert record.status == ImportStatus.PARTIAL
    assert {s["what"] for s in record.skipped} == {f"{SITE}/brak", f"{SITE}/feed"}


def test_javascript_only_site_fails_with_a_readable_message(artist, wording, net):
    net.pages[f"{SITE}/"] = page(
        html("App", '<div id="root"></div><script>render()</script><noscript>Włącz JS</noscript>')
    )
    record = run(artist)
    assert record.status == ImportStatus.FAILED
    assert "JavaScriptu" in record.message


# --- scrubbing (AC 6) --------------------------------------------------------------------------


def test_stored_text_has_placeholders_instead_of_numbers(artist, wording, net):
    body = (
        "<p>Wpłaty: 61 1090 1014 0000 0712 1981 2874</p>"
        "<p>IBAN PL61 1090 1014 0000 0712 1981 2874</p>"
        f"<p>PESEL {VALID_PESEL}, dowód {VALID_ID_CARD}</p>"
        "<p>Numer spektaklu 44051401358</p>"
        "<p>ul. Teatralna 5, 50-001 Wrocław</p>"
    )
    net.pages[f"{SITE}/"] = page(html("Teatr", body))
    record = run(artist)
    text = record.text
    for secret in ("1090 1014", VALID_PESEL, VALID_ID_CARD, "Teatralna"):
        assert secret not in text
    for placeholder in ("[iban]", "[pesel]", "[id_card]", "[address]"):
        assert placeholder in text
    assert "44051401358" in text  # wrong PESEL checksum: kept
    assert scrub(text) == text  # what reaches scrub() later has nothing left to remove
    assert record.contacts["addresses"] == ["ul. Teatralna 5, 50-001 Wrocław"]


# --- photos, links, contacts (AC 7, 8) ----------------------------------------------------------


@pytest.mark.usefixtures("storage")
def test_photos_links_and_contacts(artist, wording, net, oembed, queue):  # noqa: F811
    net.pages[f"{SITE}/"] = page(
        html(
            "Teatr Kwiatki",
            '<p>Spektakle dla dzieci. Rezerwacje: <a href="mailto:bilety@example.invalid">'
            "bilety@example.invalid</a>, tel. +48 601 234 567</p>"
            '<img src="/img/scena.jpg" alt=""><img src="https://cdn.example/foto.jpg">'
            f'<a href="https://www.youtube.com/watch?v={YOUTUBE_ID}">Film</a>'
            f'<iframe src="https://www.youtube.com/embed/{YOUTUBE_ID}"></iframe>'
            '<img src="/logo.svg">',
        )
    )
    net.dns["cdn.example"] = [OTHER]
    net.pages[f"{SITE}/img/scena.jpg"] = image(make_jpeg_with_gps())
    net.pages["https://cdn.example/foto.jpg"] = image(make_jpeg_with_gps())
    record = run(artist)

    photos = Material.objects.filter(artist=artist, kind=MaterialKind.PHOTO)
    assert photos.count() == 2 and record.photo_count == 2
    for photo in photos:
        assert photo.imported and photo.source_import == record
        assert photo.status == ScanStatus.PENDING and photo.content_type == "image/jpeg"
        with Image.open(io.BytesIO(read_stored("private", photo.storage_key))) as stored:
            assert not stored.getexif()  # EXIF incl. GPS stripped
    scans = jobs_for(queue, "artists.scan_material")
    assert sorted(j["args"]["material_id"] for j in scans) == sorted(p.pk for p in photos)

    [link] = Material.objects.filter(artist=artist, kind=MaterialKind.LINK)
    assert link.video_id == YOUTUBE_ID and link.imported and record.link_count == 1
    assert len(oembed.calls) == 1  # the embed of the same film is a duplicate, no 2nd call

    assert record.contacts["emails"] == ["bilety@example.invalid"]
    assert record.contacts["phones"] == ["+48 601 234 567"]
    assert "bilety@example.invalid" not in record.text and "601" not in record.text
    assert any("logo.svg" in s["what"] for s in record.skipped)
    assert record.status == ImportStatus.DONE


def test_contacts_are_shown_only_on_the_artists_status_page(web, artist, wording, net):
    net.pages[f"{SITE}/"] = page(html("T", "<p>Pisz: kontakt@example.invalid</p>"))
    record = run(artist)
    body = web.get(status_url(record.pk)).content.decode()
    assert "kontakt@example.invalid" in body and "Widzisz je tylko Ty" in body
    assert "kontakt@example.invalid" not in record.text


@pytest.mark.usefixtures("storage")
def test_photo_limit_imports_one_of_three(artist, wording, net):
    Material.objects.bulk_create(
        Material(artist=artist, kind=MaterialKind.PHOTO, status=ScanStatus.READY) for _ in range(39)
    )
    imgs = "".join(f'<img src="/f{n}.png">' for n in range(3))
    net.pages[f"{SITE}/"] = page(html("Galeria", f"<p>Zdjęcia</p>{imgs}"))
    for n in range(3):
        net.pages[f"{SITE}/f{n}.png"] = image(png(), "image/png")
    record = run(artist)
    assert record.photo_count == 1
    assert Material.objects.filter(artist=artist, kind=MaterialKind.PHOTO).count() == 40
    over = [s for s in record.skipped if "limit 40 zdjęć" in s["why"]]
    assert [s["what"] for s in over] == ["f1.png", "f2.png"]
    assert [c[2] for c in net.connections] == ["/", "/f0.png"]  # skipped ones not fetched


@pytest.mark.usefixtures("storage")
def test_bad_image_is_skipped_with_the_upload_message(artist, wording, net):
    net.pages[f"{SITE}/"] = page(html("G", '<p>x</p><img src="/zly.jpg"><img src="/brak.jpg">'))
    net.pages[f"{SITE}/zly.jpg"] = image(b"<html>not an image</html>", "image/jpeg")
    record = run(artist)
    assert record.photo_count == 0
    reasons = {s["what"]: s["why"] for s in record.skipped}
    assert reasons["zly.jpg"] == "Ten typ pliku nie jest dozwolony."
    assert reasons["brak.jpg"] == "Nie udało się pobrać zdjęcia."


@pytest.mark.usefixtures("storage")
def test_photo_over_the_remaining_total_stops_further_photos(artist, wording, net, settings):
    settings.WEBSITE_IMPORT_MAX_BYTES = 2000
    net.pages[f"{SITE}/"] = page(html("G", '<p>x</p><img src="/a.jpg"><img src="/b.jpg">'))
    net.pages[f"{SITE}/a.jpg"] = image(b"\xff\xd8\xff" + b"0" * 5000)
    net.pages[f"{SITE}/b.jpg"] = image(make_jpeg_with_gps())
    record = run(artist)
    assert record.status == ImportStatus.PARTIAL and record.photo_count == 0
    assert all("Osiągnięto limit" in s["why"] for s in record.skipped)
    assert record.bytes_fetched <= 2000


def test_video_not_found_is_reported(artist, wording, net, oembed):  # noqa: F811
    oembed.answer = (404, b"")
    net.pages[f"{SITE}/"] = page(
        html("T", f'<p>x</p><a href="https://youtu.be/{YOUTUBE_ID}">f</a>')
    )
    record = run(artist)
    assert record.link_count == 0
    assert record.skipped[0]["what"] == f"https://www.youtube.com/watch?v={YOUTUBE_ID}"


# --- events (AC 9), replacement, job ------------------------------------------------------------


def test_events_recorded_with_allowed_properties_only(artist, wording, net):
    net.pages[f"{SITE}/"] = page(html("T", "<p>Teatr</p>"))
    record = run(artist)
    started = Event.objects.get(name="website_import_started")
    finished = Event.objects.get(name="website_import_finished")
    assert started.properties == {}
    assert set(finished.properties) == EVENT_CATALOG["website_import_finished"]
    assert finished.properties["status"] == "done" and finished.properties["page_count"] == 1
    assert finished.properties["photo_count"] == 0 and finished.properties["duration_ms"] >= 0
    assert finished.object_id == str(record.pk)
    assert "teatr.example" not in repr(started.__dict__) + repr(finished.__dict__)


def test_failed_offline_import_records_both_events(artist, wording, net):
    queued_import(artist, "http://127.0.0.1/")
    finished = Event.objects.get(name="website_import_finished")
    assert finished.properties["status"] == "failed"
    assert Event.objects.filter(name="website_import_started").count() == 1


def test_a_new_import_replaces_the_text_of_the_previous_one(artist, wording, net):
    net.pages[f"{SITE}/"] = page(html("T", "<p>Stary opis</p><p>kontakt@example.invalid</p>"))
    first = run(artist)
    net.pages[f"{SITE}/"] = page(html("T", "<p>Nowy opis</p>"))
    second = run(artist)
    first.refresh_from_db()
    assert first.text == "" and first.contacts == {}
    assert "Nowy opis" in second.text
    assert website_import.import_text(artist) == second.text


def test_a_failed_import_keeps_the_previous_text(artist, wording, net):
    net.pages[f"{SITE}/"] = page(html("T", "<p>Opis</p>"))
    first = run(artist)
    del net.pages[f"{SITE}/"]
    run(artist)
    first.refresh_from_db()
    assert "Opis" in first.text and website_import.import_text(artist) == first.text


def test_run_import_runs_once(artist, wording, net):
    net.pages[f"{SITE}/"] = page(html("T", "<p>x</p>"))
    record = queued_import(artist)
    assert website_import.run_import(record.pk) == ImportStatus.DONE
    assert website_import.run_import(record.pk) == ""
    assert len(net.connections) == 1


def test_crash_ends_as_failed(artist, wording, net, monkeypatch, caplog):
    def boom(*args, **kwargs):
        raise RuntimeError("bug")

    monkeypatch.setattr(website_import, "_crawl", boom)
    with caplog.at_level(logging.ERROR, logger="apps.artists.website_import"):
        record = run(artist)
    assert record.status == ImportStatus.FAILED and "po naszej stronie" in record.message


@pytest.mark.django_db(transaction=True)
def test_the_worker_runs_the_job(artist, wording, net, queue):
    net.pages[f"{SITE}/"] = page(html("T", "<p>x</p>"))
    record = queued_import(artist)
    run_worker()
    record.refresh_from_db()
    assert record.status == ImportStatus.DONE
    assert tasks.run_website_import.name == "artists.run_website_import"


def test_log_lines_carry_no_url(artist, wording, net, caplog):
    with caplog.at_level(logging.INFO, logger="apps.artists.website_import"):
        run(artist, "http://169.254.169.254/latest/meta-data/")
    assert all("169.254" not in line.getMessage() for line in caplog.records)
    own = [r for r in caplog.records if r.name == "apps.artists.website_import"]
    assert own and all(getattr(r, "website_import", None) is not None for r in own)
    assert own[-1].code == "blocked"


def test_stale_running_import_does_not_block_a_new_one(artist, wording, net):
    from datetime import timedelta

    from django.utils import timezone

    record = queued_import(artist)
    WebsiteImport.objects.filter(pk=record.pk).update(
        status=ImportStatus.RUNNING, created_at=timezone.now() - timedelta(hours=2)
    )
    assert queued_import(artist).pk != record.pk


# --- status page (AC 10) and wizard -------------------------------------------------------------


def test_status_page_of_own_import(web, artist, wording, net):
    net.pages[f"{SITE}/"] = page(html("Teatr Kwiatki", "<p>x</p>"))
    record = run(artist)
    response = web.get(status_url(record.pk))
    body = response.content.decode()
    assert response.status_code == 200
    assert 'data-status="done"' in body and "Teatr Kwiatki" in body
    assert 'http-equiv="refresh"' not in body


def test_status_page_refreshes_while_queued(web, artist, wording):
    record = queued_import(artist)
    body = web.get(status_url(record.pk)).content.decode()
    assert 'http-equiv="refresh"' in body and "w kolejce" in body


def test_failed_import_page_links_to_manual_steps(web, artist, wording, net):
    record = queued_import(artist, "http://169.254.169.254/")
    body = web.get(status_url(record.pk)).content.decode()
    assert "sieć wewnętrzną" in body
    assert 'href="/artysta/profil/materialy/"' in body and 'href="/artysta/profil/dane/"' in body


def test_another_artists_import_is_404(web, wording):
    other = make_artist("inny.artysta@example.invalid")
    services.save_basics(other, BASICS)
    record = queued_import(Artist.objects.get(user=other))
    assert web.get(status_url(record.pk)).status_code == 404


def test_institution_user_gets_403(wording, artist):
    record = queued_import(artist)
    client = Client()
    client.force_login(make_institution_member())
    assert client.get(status_url(record.pk)).status_code == 403
    assert client.post(FORM, {"url": f"{SITE}/", "confirm": "1"}).status_code == 403


def test_form_page_lists_recent_imports(web, artist, wording):
    record = queued_import(artist)
    body = web.get(FORM).content.decode()
    assert f'data-import="{record.pk}"' in body


def test_wizard_step_done_after_a_finished_import(artist, wording, net):
    def done():
        return {s.step.key: s.done for s in services.wizard_steps(artist)}["import"]

    assert not done()
    net.pages[f"{SITE}/"] = page(html("T", "<p>x</p>"))
    run(artist)
    assert done()


# --- parsing helpers ----------------------------------------------------------------------------


def test_parse_page_keeps_visible_text_only():
    parsed = website_import.parse_page(
        "<html><head><title> Teatr  Kwiatki </title><style>p{}</style></head><body>"
        "<nav><a href='/a'>Menu</a></nav><div role='navigation'>Skróty</div>"
        "<h1>Witamy</h1><p>Gramy &amp; uczymy<br>od lat</p><script>alert(1)</script>"
        "<p>Bilety: <a href='tel:+48601234567'>zadzwoń</a></p><img data-src='/l.jpg'>"
        "<img srcset='/s.jpg 1x, /m.jpg 2x'><footer>Stopka</footer></body></html>"
    )
    assert parsed.title == "Teatr Kwiatki"
    assert parsed.text == "Witamy\nGramy & uczymy\nod lat\nBilety: zadzwoń\nStopka"
    assert parsed.links == ["/a"] and parsed.phones == ["+48601234567"]
    assert parsed.images == ["/l.jpg", "/s.jpg"]


def test_parse_page_tolerates_broken_markup():
    parsed = website_import.parse_page("<div><p>Jeden<div>Dwa</p></span><script>x")
    assert "Jeden" in parsed.text and "Dwa" in parsed.text and "x" not in parsed.text


@pytest.mark.parametrize(
    ("url", "expected"),
    [
        (f"https://www.youtube.com/embed/{YOUTUBE_ID}?rel=0", f"https://www.youtube.com/watch?v={YOUTUBE_ID}"),
        (f"https://www.youtube-nocookie.com/embed/{YOUTUBE_ID}", f"https://www.youtube.com/watch?v={YOUTUBE_ID}"),
        ("https://player.vimeo.com/video/123456", "https://vimeo.com/123456"),
        ("https://vimeo.com/123456", "https://vimeo.com/123456"),
        ("https://example.com/video", ""),
    ],
)  # fmt: skip
def test_video_url(url, expected):
    assert website_import.video_url(url) == expected


@pytest.mark.parametrize(
    ("body", "charset", "expected"),
    [
        ("Zażółć".encode("iso-8859-2"), "iso-8859-2", "Zażółć"),
        ("Zażółć".encode(), "", "Zażółć"),
        (b"<meta charset='cp1250'>" + "ż".encode("cp1250"), "", "<meta charset='cp1250'>ż"),
        ("ż".encode(), "no-such-charset", "ż"),
    ],
)  # fmt: skip
def test_decode(body, charset, expected):
    assert website_import.decode(body, charset) == expected


def test_absolute_drops_fragments_and_other_schemes():
    assert website_import.absolute(f"{SITE}/a/", "b#x") == f"{SITE}/a/b"
    assert website_import.absolute(f"{SITE}/", "javascript:alert(1)") == ""
    assert website_import.absolute(f"{SITE}/", "http://[::1") == ""
