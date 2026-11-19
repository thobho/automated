"""Wizard step "Materiały" (US-2.3A, D8, D62): photos, PDFs, YouTube/Vimeo links, the malware
scan and PDF text jobs, the school questionnaire. The scanner is the fake backend, oEmbed is
mocked (no network), PDFs are generated here."""

import asyncio
import io
import json
import logging

import pytest
from django.core.files.storage import storages
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client
from PIL import Image
from procrastinate.contrib.django import app
from pypdf import PdfWriter

from apps.accounts.tests.conftest import (
    make_admin,
    make_artist,
    make_institution_member,
    run_worker,
)
from apps.artists import materials, services
from apps.artists.materials import MaterialRejected, ScanNotFinished
from apps.artists.models import Artist, Material, Offer, ScanStatus, TextStatus
from apps.core.tests.test_uploads import make_jpeg_with_gps
from apps.core.uploads import MB, UploadRejected
from config.settings.storage import build_storages

pytestmark = pytest.mark.django_db

PAGE = "/artysta/profil/materialy/"
PHOTOS = "/artysta/profil/materialy/zdjecia/"
PDFS = "/artysta/profil/materialy/pdf/"
LINK = "/artysta/profil/materialy/film/"
QUESTIONNAIRE = "/artysta/profil/kwestionariusz/"
YOUTUBE_ID = "dQw4w9WgXcQ"

BASICS = {
    "artist_type": "theatre",
    "name": "Teatr Testowy Kwiatki",
    "city": "Wrocław",
    "voivodeships": ["dolnoslaskie"],
    "audiences": ["grades_0_3"],
}


def delete_url(pk):
    return f"/artysta/profil/materialy/{pk}/usun/"


# --- fixtures and file builders --------------------------------------------------------------


@pytest.fixture
def storage(settings, tmp_path):
    settings.STORAGE_BACKEND = "filesystem"
    settings.STORAGES = build_storages(
        "filesystem",
        public_base_url="http://media.test:8101/",
        private_root=tmp_path / "private",
        public_root=tmp_path / "public",
        signed_url_ttl=settings.MEDIA_SIGNED_URL_TTL,
    )
    return tmp_path / "private"


def stored_files(root) -> list:
    return sorted(p for p in root.rglob("*") if p.is_file()) if root.exists() else []


@pytest.fixture
def commit(django_capture_on_commit_callbacks):
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
def scanner(settings):
    """Set the fake scanner's answer: scanner("infected")."""

    def set_result(result):
        settings.MALWARE_SCANNER_FAKE_RESULT = result

    set_result("clean")
    return set_result


@pytest.fixture
def oembed(monkeypatch):
    """Replace the transport; `oembed.answer = (status, body)`; `oembed.calls` lists URLs."""

    class Fake:
        calls: list = []
        answer = (200, json.dumps({"title": "Spektakl testowy", "type": "video"}).encode())

        def __call__(self, url, timeout):
            self.calls.append((url, timeout))
            if isinstance(self.answer, Exception):
                raise self.answer
            return self.answer

    fake = Fake()
    fake.calls = []
    monkeypatch.setattr(materials, "transport", fake)
    return fake


def jpeg(name="zdjecie.jpg", data=None):
    return SimpleUploadedFile(name, data or make_jpeg_with_gps(), content_type="image/jpeg")


def make_pdf(*pages: str) -> bytes:
    """A minimal valid PDF with one text line per page (Helvetica, ASCII)."""
    count = len(pages)
    kids = " ".join(f"{4 + 2 * i} 0 R" for i in range(count))
    objects = {
        1: b"<< /Type /Catalog /Pages 2 0 R >>",
        2: f"<< /Type /Pages /Kids [{kids}] /Count {count} >>".encode(),
        3: b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    }
    for i, text in enumerate(pages):
        stream = f"BT /F1 12 Tf 72 720 Td ({text}) Tj ET".encode("latin-1")
        objects[4 + 2 * i] = (
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
            f"/Resources << /Font << /F1 3 0 R >> >> /Contents {5 + 2 * i} 0 R >>"
        ).encode()
        objects[5 + 2 * i] = b"<< /Length %d >>\nstream\n" % len(stream) + stream + b"\nendstream"
    out, offsets = b"%PDF-1.4\n", {}
    for number in sorted(objects):
        offsets[number] = len(out)
        out += f"{number} 0 obj\n".encode() + objects[number] + b"\nendobj\n"
    xref, size = len(out), len(objects) + 1
    out += f"xref\n0 {size}\n0000000000 65535 f \n".encode()
    for number in sorted(objects):
        out += f"{offsets[number]:010d} 00000 n \n".encode()
    out += f"trailer\n<< /Size {size} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode()
    return out


def encrypted_pdf() -> bytes:
    writer = PdfWriter(clone_from=io.BytesIO(make_pdf("Tajny tekst")))
    writer.encrypt("haslo", algorithm="RC4-128")
    out = io.BytesIO()
    writer.write(out)
    return out.getvalue()


BROKEN_PDF = b"%PDF-1.7\n" + b"\x00\xff garbage, no objects, no xref " * 20


def pdf(name="opis.pdf", data=None):
    return SimpleUploadedFile(name, data or make_pdf("Czas trwania 45 minut"), "application/pdf")


def upload(artist, kind="photo", file=None):
    return materials.add_file(artist, kind, file or (jpeg() if kind == "photo" else pdf()))


def run_media_worker():
    """Run queued jobs once. Without LISTEN/NOTIFY: the in-memory connector cannot notify
    itself when a job defers another job (the scan defers the text extraction)."""
    asyncio.run(
        app.run_worker_async(wait=False, install_signal_handlers=False, listen_notify=False)
    )


def scan_jobs(queue, name="artists.scan_material"):
    return [j for j in queue.jobs.values() if j["task_name"] == name]


# --- photos ----------------------------------------------------------------------------------


def test_photo_with_gps_is_stored_without_exif_and_ready_after_a_clean_scan(
    web, artist, storage, scanner, queue
):
    response = web.post(PHOTOS, {"files": jpeg()})
    assert response.status_code == 302 and response["Location"] == PAGE
    material = Material.objects.get(artist=artist)
    assert (material.kind, material.status) == ("photo", ScanStatus.PENDING)
    assert material.content_type == "image/jpeg" and material.original_name == "zdjecie.jpg"
    assert material.storage_key.startswith("photo/")
    with storages["private"].open(material.storage_key, "rb") as stored:
        image = Image.open(stored)
        assert not image.getexif() and "exif" not in image.info
    jobs = scan_jobs(queue)
    assert len(jobs) == 1 and jobs[0]["queue_name"] == "media"
    assert jobs[0]["args"] == {"material_id": material.pk}
    assert materials.scan_material(material.pk) == ScanStatus.READY
    material.refresh_from_db()
    assert material.status == ScanStatus.READY and material.scanned_at is not None
    assert list(materials.ready_materials(artist)) == [material]


def test_41st_photo_is_refused_and_nothing_is_stored(web, artist, storage, settings):
    settings.MATERIAL_MAX_PHOTOS = 3  # same code path as 40, fewer files to make
    for _ in range(3):
        upload(artist)
    before = stored_files(storage)
    response = web.post(PHOTOS, {"files": jpeg()})
    assert response.status_code == 400
    assert "Osiągnięto limit 3 zdjęć." in response.content.decode()
    assert Material.objects.filter(artist=artist).count() == 3
    assert stored_files(storage) == before
    with pytest.raises(MaterialRejected):
        upload(artist)


def test_default_limits_are_40_photos_and_10_pdfs(settings):
    assert (settings.MATERIAL_MAX_PHOTOS, settings.MATERIAL_MAX_PDFS) == (40, 10)


def test_page_shows_the_limit_and_the_checks_before_sending(web, artist, storage, settings):
    settings.MATERIAL_MAX_PHOTOS = 2
    upload(artist)
    body = web.get(PAGE).content.decode()
    assert 'data-remaining="1"' in body and "Pozostało miejsc: 1." in body
    assert f'data-max-bytes="{15 * MB}"' in body and f'data-max-bytes="{20 * MB}"' in body
    assert 'accept="image/jpeg,image/png,image/webp,.jpg,.jpeg,.png,.webp"' in body
    assert 'accept="application/pdf,.pdf"' in body
    assert "/static/js/materials.js" in body and "<script>" not in body
    upload(artist)
    body = web.get(PAGE).content.decode()
    assert "Osiągnięto limit." in body and 'action="/artysta/profil/materialy/zdjecia/"' not in body


def test_too_many_files_in_one_send_store_nothing(web, artist, storage, settings):
    settings.MATERIAL_MAX_PHOTOS = 2
    response = web.post(PHOTOS, {"files": [jpeg("a.jpg"), jpeg("b.jpg"), jpeg("c.jpg")]})
    assert response.status_code == 400
    assert not Material.objects.exists() and stored_files(storage) == []


def test_several_photos_in_one_send(web, artist, storage):
    response = web.post(PHOTOS, {"files": [jpeg("a.jpg"), jpeg("b.jpg")]})
    assert response.status_code == 302
    assert Material.objects.filter(artist=artist, kind="photo").count() == 2


def test_16_mb_photo_is_refused_and_nothing_stored(web, artist, storage):
    big = SimpleUploadedFile("duze.jpg", b"\xff\xd8\xff" + b"0" * (16 * MB), "image/jpeg")
    response = web.post(PHOTOS, {"files": big})
    assert response.status_code == 400
    assert "Plik jest za duży (maksymalnie 15 MB)." in response.content.decode()
    assert not Material.objects.exists() and stored_files(storage) == []


def test_pdf_renamed_jpg_is_refused_with_the_upload_message(web, artist, storage):
    fake = SimpleUploadedFile("zdjecie.jpg", make_pdf("x"), content_type="image/jpeg")
    response = web.post(PHOTOS, {"files": fake})
    assert response.status_code == 400
    assert "zdjecie.jpg: Ten typ pliku nie jest dozwolony." in response.content.decode()
    assert not Material.objects.exists() and stored_files(storage) == []


def test_one_bad_file_does_not_stop_the_good_one(web, artist, storage):
    bad = SimpleUploadedFile("zly.jpg", make_pdf("x"), content_type="image/jpeg")
    response = web.post(PHOTOS, {"files": [jpeg("dobry.jpg"), bad]})
    assert response.status_code == 400
    assert list(Material.objects.values_list("original_name", flat=True)) == ["dobry.jpg"]


def test_upload_without_a_file_is_an_error(web, storage):
    response = web.post(PHOTOS, {})
    assert response.status_code == 400 and "Wybierz plik." in response.content.decode()


def test_rejected_materials_do_not_use_up_the_limit(artist, storage, settings, scanner):
    settings.MATERIAL_MAX_PHOTOS = 1
    material = upload(artist)
    scanner("infected")
    materials.scan_material(material.pk)
    assert materials.remaining(artist, "photo") == 1


def test_a_failed_database_write_removes_the_stored_file(artist, storage, monkeypatch):
    def fail(**kwargs):
        raise RuntimeError("db down")

    monkeypatch.setattr(Material.objects, "create", fail)
    with pytest.raises(RuntimeError):
        upload(artist)
    assert stored_files(storage) == []


def test_file_names_are_cleaned():
    assert materials.clean_name("C:\\Users\\x\\zdj\u0007ecie.jpg") == "zdjecie.jpg"
    assert materials.clean_name("a/" + "b" * 300) == "b" * 200
    assert materials.clean_name(None) == ""


def test_add_file_refuses_a_link_kind(artist):
    with pytest.raises(ValueError):
        materials.add_file(artist, "link", jpeg())


# --- malware scan ----------------------------------------------------------------------------


def test_infected_file_is_removed_and_rejected_and_the_artist_sees_why(
    web, artist, storage, scanner, commit
):
    material = upload(artist)
    assert stored_files(storage)
    scanner("infected")
    with commit():
        assert materials.scan_material(material.pk) == ScanStatus.REJECTED
    material.refresh_from_db()
    assert material.status == ScanStatus.REJECTED and material.storage_key == ""
    assert stored_files(storage) == []
    assert not materials.ready_materials(artist).exists()
    body = web.get(PAGE).content.decode()
    assert 'data-status="rejected"' in body and "skaner wykrył złośliwe oprogramowanie" in body


def test_scanner_error_keeps_the_material_pending_and_not_ready(artist, storage, scanner):
    material = upload(artist)
    scanner("error")
    with pytest.raises(ScanNotFinished):
        materials.scan_material(material.pk)
    material.refresh_from_db()
    assert material.status == ScanStatus.PENDING and material.storage_key
    assert not materials.ready_materials(artist).exists()
    assert not materials.has_ready_materials(artist)


@pytest.mark.django_db(transaction=True)
def test_worker_retries_a_scanner_error_and_leaves_the_file_pending(
    artist, storage, scanner, queue
):
    material = upload(artist)
    scanner("error")
    run_worker()
    job = scan_jobs(queue)[0]
    assert job["status"] == "todo" and job["attempts"] == 1  # retry scheduled later
    material.refresh_from_db()
    assert material.status == ScanStatus.PENDING


@pytest.mark.django_db(transaction=True)
def test_worker_scans_a_pdf_and_then_extracts_its_text(artist, storage, scanner, queue):
    material = upload(artist, "pdf")
    run_media_worker()
    material.refresh_from_db()
    assert material.status == ScanStatus.READY
    assert material.text_status == TextStatus.DONE
    assert "Czas trwania 45 minut" in material.text
    names = sorted(j["task_name"] for j in queue.jobs.values())
    assert names == ["artists.extract_pdf_text", "artists.scan_material"]
    assert {j["status"] for j in queue.jobs.values()} == {"succeeded"}


def test_scan_twice_is_harmless(artist, storage):
    material = upload(artist)
    materials.scan_material(material.pk)
    assert materials.scan_material(material.pk) == ScanStatus.READY
    assert materials.scan_material(999999) == ""


def test_none_scanner_marks_the_file_unscanned_in_the_log(artist, storage, settings, caplog):
    settings.MALWARE_SCANNER = "none"
    material = upload(artist)
    with caplog.at_level(logging.INFO):
        assert materials.scan_material(material.pk) == ScanStatus.READY
    events = [getattr(r, "event", "") for r in caplog.records]
    assert "upload_unscanned" in events and "material_scan_clean" in events


# --- offer posters go through the same scan --------------------------------------------------


def _offer(artist, poster=None):
    data = {"title": "Spektakl", "description": "Opis", "price_pln": 900}
    return services.create_offer(artist, data, poster=poster)


def test_offer_poster_is_scanned_and_an_infected_one_removed(
    artist, storage, scanner, queue, commit, web
):
    offer = _offer(artist, poster=jpeg("plakat.jpg"))
    assert offer.poster_status == ScanStatus.PENDING
    job = scan_jobs(queue, "artists.scan_poster")[0]
    assert job["args"] == {"offer_id": offer.pk, "key": offer.poster_key}
    scanner("infected")
    with commit():
        assert materials.scan_poster(offer.pk, offer.poster_key) == ScanStatus.REJECTED
    offer.refresh_from_db()
    assert offer.poster_key == "" and offer.poster_status == ScanStatus.REJECTED
    assert stored_files(storage) == []
    assert "Plakat odrzucony" in web.get("/artysta/profil/oferty/").content.decode()


def test_clean_poster_is_ready_and_a_replaced_poster_is_not_touched(artist, storage, scanner):
    offer = _offer(artist, poster=jpeg())
    old_key = offer.poster_key
    services.update_offer(artist, offer.pk, services.offer_data(offer), poster=jpeg("nowy.jpg"))
    assert materials.scan_poster(offer.pk, old_key) == ""  # queued for the old poster
    offer.refresh_from_db()
    assert materials.scan_poster(offer.pk, offer.poster_key) == ScanStatus.READY
    scanner("error")
    services.update_offer(artist, offer.pk, services.offer_data(offer), poster=jpeg())
    offer.refresh_from_db()
    with pytest.raises(ScanNotFinished):
        materials.scan_poster(offer.pk, offer.poster_key)


def test_removing_the_poster_clears_its_status(artist, storage):
    offer = _offer(artist, poster=jpeg())
    services.update_offer(artist, offer.pk, services.offer_data(offer), remove_poster=True)
    assert Offer.objects.get(pk=offer.pk).poster_status == ""


# --- PDFs and their text ---------------------------------------------------------------------


def test_pdf_upload_then_text_extraction(web, artist, storage, queue):
    assert web.post(PDFS, {"files": pdf()}).status_code == 302
    material = Material.objects.get(artist=artist, kind="pdf")
    assert material.content_type == "application/pdf"
    materials.scan_material(material.pk)
    assert [j["args"] for j in scan_jobs(queue, "artists.extract_pdf_text")] == [
        {"material_id": material.pk}
    ]
    assert materials.extract_pdf_text(material.pk) == TextStatus.DONE
    material.refresh_from_db()
    assert "Czas trwania 45 minut" in material.text


@pytest.mark.parametrize(
    "data, status",
    [(encrypted_pdf(), TextStatus.ENCRYPTED), (BROKEN_PDF, TextStatus.BROKEN)],
)
def test_encrypted_or_broken_pdf_gets_a_readable_status(web, artist, storage, data, status):
    material = upload(artist, "pdf", pdf(data=data))
    materials.scan_material(material.pk)
    assert materials.extract_pdf_text(material.pk) == status  # no exception
    material.refresh_from_db()
    assert material.text == "" and material.text_status == status
    assert str(status.label) in web.get(PAGE).content.decode()


def test_text_limits_pages_and_characters():
    data = make_pdf("Strona pierwsza", "Strona druga", "Strona trzecia")
    result = materials.extract_text(io.BytesIO(data), max_pages=2, max_chars=1000, max_seconds=30)
    assert result.status == TextStatus.TRUNCATED
    assert "Strona druga" in result.text and "trzecia" not in result.text
    result = materials.extract_text(io.BytesIO(data), max_pages=10, max_chars=10, max_seconds=30)
    assert result.status == TextStatus.TRUNCATED and len(result.text) == 10


def test_text_time_limit_stops_between_pages():
    data = make_pdf("Pierwsza", "Druga")
    result = materials.extract_text(io.BytesIO(data), max_pages=10, max_chars=1000, max_seconds=-1)
    assert result.status == TextStatus.EMPTY  # stopped before the first page


def test_pdf_without_text_is_empty():
    result = materials.extract_text(
        io.BytesIO(make_pdf("")), max_pages=5, max_chars=100, max_seconds=5
    )
    assert result == materials.Extracted("", TextStatus.EMPTY)


def test_extraction_skips_photos_pending_and_missing(artist, storage):
    photo = upload(artist)
    pending_pdf = upload(artist, "pdf")
    assert materials.extract_pdf_text(photo.pk) == ""
    assert materials.extract_pdf_text(pending_pdf.pk) == ""
    assert materials.extract_pdf_text(999999) == ""


def test_extraction_of_a_vanished_file_is_broken(artist, storage):
    material = upload(artist, "pdf")
    materials.scan_material(material.pk)
    storages["private"].delete(material.storage_key)
    assert materials.extract_pdf_text(material.pk) == TextStatus.BROKEN


# --- YouTube / Vimeo links -------------------------------------------------------------------


@pytest.mark.parametrize(
    "url, provider, video_id",
    [
        (f"https://youtu.be/{YOUTUBE_ID}", "youtube", YOUTUBE_ID),
        (f"https://www.youtube.com/watch?v={YOUTUBE_ID}&t=10", "youtube", YOUTUBE_ID),
        (f"http://youtube.com/watch?feature=x&v={YOUTUBE_ID}", "youtube", YOUTUBE_ID),
        (f"https://m.youtube.com/watch?v={YOUTUBE_ID}", "youtube", YOUTUBE_ID),
        (f"https://www.youtube.com/shorts/{YOUTUBE_ID}", "youtube", YOUTUBE_ID),
        ("https://vimeo.com/76979871", "vimeo", "76979871"),
        ("https://www.vimeo.com/76979871/", "vimeo", "76979871"),
    ],
)
def test_supported_video_urls_are_parsed(url, provider, video_id):
    ref = materials.parse_video_url(url)
    assert (ref.provider, ref.video_id) == (provider, video_id)


@pytest.mark.parametrize(
    "url",
    [
        "https://example.com/watch?v=x",
        "http://127.0.0.1/",
        f"https://youtube.com.evil.example/watch?v={YOUTUBE_ID}",
        f"https://www.youtube.com:8443/watch?v={YOUTUBE_ID}",
        f"https://user@www.youtube.com/watch?v={YOUTUBE_ID}",
        f"javascript://youtu.be/{YOUTUBE_ID}",
        f"ftp://youtu.be/{YOUTUBE_ID}",
        "https://www.youtube.com/watch?v=short",
        "https://www.youtube.com/channel/abc",
        "https://vimeo.com/channels/staffpicks",
        "https://vimeo.com/123/456",
        "https://[::1",
        "",
        "x" * 600,
    ],
)
def test_other_urls_are_refused_without_a_request(web, artist, oembed, url):
    assert materials.parse_video_url(url) is None
    response = web.post(LINK, {"url": url})
    assert response.status_code == 400
    assert "Podaj link do filmu na YouTube" in response.content.decode()
    assert oembed.calls == [] and not Material.objects.exists()


def test_youtube_link_with_oembed_200_creates_a_link_material(web, artist, oembed):
    response = web.post(LINK, {"url": f"https://youtu.be/{YOUTUBE_ID}"})
    assert response.status_code == 302
    material = Material.objects.get(artist=artist)
    assert (material.kind, material.status) == ("link", ScanStatus.READY)
    assert (material.provider, material.video_id) == ("youtube", YOUTUBE_ID)
    assert material.canonical_url == f"https://www.youtube.com/watch?v={YOUTUBE_ID}"
    assert material.title == "Spektakl testowy"
    ((url, timeout),) = oembed.calls
    assert url.startswith("https://www.youtube.com/oembed?url=https%3A%2F%2Fwww.youtube.com")
    assert url.endswith("&format=json") and timeout == 5.0
    assert "Spektakl testowy" in web.get(PAGE).content.decode()


def test_vimeo_link_uses_the_vimeo_endpoint(artist, oembed):
    material = materials.add_link(artist, "https://vimeo.com/76979871")
    assert material.provider == "vimeo"
    assert oembed.calls[0][0].startswith("https://vimeo.com/api/oembed.json?url=")


@pytest.mark.parametrize("status", [404, 401, 403])
def test_missing_or_private_video_is_a_form_error_and_no_material(web, artist, oembed, status):
    oembed.answer = (status, b"")
    response = web.post(LINK, {"url": f"https://youtu.be/{YOUTUBE_ID}"})
    assert response.status_code == 400
    assert "Nie znaleziono tego filmu albo jest prywatny." in response.content.decode()
    assert f'value="https://youtu.be/{YOUTUBE_ID}"' in response.content.decode()
    assert not Material.objects.exists()


@pytest.mark.parametrize(
    "answer",
    [(500, b""), (200, b"not json"), (200, b"[]"), (200, b'{"title": 5}'), TimeoutError()],
)
def test_provider_trouble_is_a_retry_later_error(artist, oembed, answer):
    oembed.answer = answer
    with pytest.raises(MaterialRejected) as exc:
        materials.add_link(artist, f"https://youtu.be/{YOUTUBE_ID}")
    assert exc.value.code == "unavailable" and not Material.objects.exists()


def test_the_same_video_twice_is_refused(artist, oembed):
    materials.add_link(artist, f"https://youtu.be/{YOUTUBE_ID}")
    with pytest.raises(MaterialRejected) as exc:
        materials.add_link(artist, f"https://www.youtube.com/watch?v={YOUTUBE_ID}")
    assert exc.value.code == "duplicate" and len(oembed.calls) == 1


def test_real_transport_only_calls_the_fixed_endpoints():
    with pytest.raises(ValueError):
        materials.urllib_transport("http://127.0.0.1/oembed", 1)
    with pytest.raises(ValueError):
        materials.urllib_transport("https://www.youtube.com.evil.example/oembed", 1)


def test_link_is_a_ready_material_and_completes_the_step(artist, oembed):
    assert not services.wizard_steps(artist)[3].done
    materials.add_link(artist, f"https://youtu.be/{YOUTUBE_ID}")
    step = services.wizard_steps(artist)[3]
    assert step.step.key == "materials" and step.done


# --- delete ----------------------------------------------------------------------------------


def test_delete_removes_the_row_and_the_file(web, artist, storage, commit):
    material = upload(artist)
    with commit():
        response = web.post(delete_url(material.pk))
    assert response.status_code == 302 and response["Location"] == PAGE
    assert not Material.objects.exists() and stored_files(storage) == []


def test_delete_a_link(web, artist, oembed):
    material = materials.add_link(artist, f"https://youtu.be/{YOUTUBE_ID}")
    assert web.post(delete_url(material.pk)).status_code == 302
    assert not Material.objects.exists()


def test_another_artists_material_is_404_and_stays(web, storage):
    other = make_artist("inny.artysta@example.invalid")
    services.save_basics(other, BASICS)
    material = upload(Artist.objects.get(user=other))
    assert web.post(delete_url(material.pk)).status_code == 404
    assert web.post(delete_url(999999)).status_code == 404
    assert Material.objects.filter(pk=material.pk).exists()


def test_delete_needs_post(web, artist, storage):
    material = upload(artist)
    assert web.get(delete_url(material.pk)).status_code == 405


def test_storage_failure_on_delete_is_only_logged(artist, storage, monkeypatch, caplog):
    material = upload(artist)

    def broken(key):
        raise OSError("disk")

    monkeypatch.setattr(storages["private"], "delete", broken)
    with caplog.at_level(logging.WARNING):
        materials._delete_file(material.storage_key)
    assert "material file could not be deleted" in caplog.text


# --- page and permissions --------------------------------------------------------------------


def test_page_lists_materials_with_status_and_a_signed_link(web, artist, storage):
    photo = upload(artist)
    materials.scan_material(photo.pk)
    upload(artist, "pdf")
    body = web.get(PAGE).content.decode()
    assert 'data-status="ready"' in body and 'data-status="pending"' in body
    assert "oczekuje na skan" in body and "/media/private/" in body


@pytest.mark.parametrize("path", [PAGE, QUESTIONNAIRE])
def test_institution_and_admin_get_403_on_the_step(path):
    for user in (make_institution_member(), make_admin()):
        client = Client()
        client.force_login(user)
        assert client.get(path).status_code == 403
    response = Client().get(path)
    assert response.status_code == 302 and response["Location"].startswith("/logowanie/")


@pytest.mark.parametrize("path", [PHOTOS, PDFS, LINK, delete_url(1)])
def test_institution_cannot_post_to_the_step(path):
    client = Client()
    client.force_login(make_institution_member())
    assert client.post(path, {}).status_code == 403


@pytest.mark.parametrize("path", [PAGE, QUESTIONNAIRE])
def test_step_needs_complete_basics(path):
    client = Client()
    client.force_login(make_artist())
    response = client.get(path)
    assert response.status_code == 302 and response["Location"] == "/artysta/profil/dane/"


@pytest.mark.parametrize("path", [PHOTOS, PDFS, LINK])
def test_post_only_routes_refuse_get(web, path):
    assert web.get(path).status_code == 405


# --- school questionnaire --------------------------------------------------------------------

FILLED = {
    "q_age_from": "6",
    "q_age_to": "10",
    "q_duration_minutes": "45",
    "q_max_audience": "120",
    "q_tech_room": "Sala gimnastyczna",
    "q_tech_power": "Gniazdo 230 V",
    "q_tech_sound": "",
    "q_price_from_pln": "800",
    "q_price_to_pln": "1500",
}


def test_questionnaire_is_stored_and_prefilled(web, artist):
    assert web.get(QUESTIONNAIRE).status_code == 200
    response = web.post(QUESTIONNAIRE, FILLED)
    assert response.status_code == 302 and response["Location"] == PAGE
    artist.refresh_from_db()
    assert (artist.q_price_from_pln, artist.q_price_to_pln) == (800, 1500)
    assert (artist.q_age_from, artist.q_age_to) == (6, 10)
    assert (artist.q_duration_minutes, artist.q_max_audience) == (45, 120)
    assert artist.q_tech_room == "Sala gimnastyczna" and artist.q_price_on_request is False
    body = web.get(QUESTIONNAIRE).content.decode()
    for value in ("800", "1500", "45", "120", "Sala gimnastyczna"):
        assert f'value="{value}"' in body
    assert "Edytuj kwestionariusz" in web.get(PAGE).content.decode()


def test_empty_questionnaire_is_valid(web, artist):
    assert web.post(QUESTIONNAIRE, {}).status_code == 302
    assert not materials.questionnaire_filled(Artist.objects.get(pk=artist.pk))


def test_price_on_request_alone_is_valid(artist):
    saved = materials.save_questionnaire(artist, {"q_price_on_request": True})
    assert saved.q_price_on_request and saved.q_price_from_pln is None


@pytest.mark.parametrize(
    "changes, field, message",
    [
        ({"q_price_from_pln": "1600"}, "q_price_to_pln", "Cena „do” nie może być mniejsza"),
        ({"q_price_on_request": "on"}, "q_price_on_request", "jedno z dwóch"),
        ({"q_age_from": "12"}, "q_age_to", "Wiek „do” nie może być mniejszy"),
        ({"q_max_audience": "0"}, "q_max_audience", ""),
        ({"q_tech_room": "x" * 501}, "q_tech_room", ""),
    ],
)
def test_questionnaire_errors(web, artist, changes, field, message):
    response = web.post(QUESTIONNAIRE, {**FILLED, **changes})
    assert response.status_code == 400
    body = response.content.decode()
    assert f'id="{field}-error"' in body and message in body
    artist.refresh_from_db()
    assert artist.q_price_from_pln is None  # nothing saved


def test_service_validates_again(artist):
    with pytest.raises(materials.InvalidQuestionnaire) as exc:
        materials.save_questionnaire(
            artist, {"q_price_from_pln": 900, "q_price_to_pln": 100, "q_age_from": "x"}
        )
    assert set(exc.value.errors) == {"q_price_to_pln", "q_age_from"}
    with pytest.raises(materials.InvalidQuestionnaire):
        materials.save_questionnaire(artist, {"q_tech_sound": "y" * 501})


def test_questionnaire_rejects_other_methods(web):
    assert web.put(QUESTIONNAIRE).status_code == 405


def test_upload_kinds_raise_upload_rejected_through_the_service(artist, storage):
    with pytest.raises(UploadRejected):
        materials.add_file(artist, "pdf", jpeg("a.pdf"))
