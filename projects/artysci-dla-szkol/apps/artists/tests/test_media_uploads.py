"""Video and audio materials (US-2.3B, D8): resumable uploads in chunks, the scan, the
ffprobe/ffmpeg processing job, the cleanup of expired sessions and delete. The scanner is the
fake backend. ffmpeg is mocked here, except the tests marked `needs_ffmpeg`, which make short
synthetic samples with the real ffmpeg (CI installs it; skipped locally without it)."""

import io
import uuid
from datetime import timedelta
from pathlib import Path

import pytest
from django.test import Client
from django.utils import timezone

from apps.accounts.tests.conftest import make_artist, make_institution_member
from apps.artists import materials, recordings, resumable, services
from apps.artists.models import (
    Artist,
    Material,
    ProcessingStatus,
    ScanStatus,
    UploadSession,
)
from apps.artists.tests.test_materials import (
    BASICS,
    PAGE,
    delete_url,
    run_media_worker,
    scan_jobs,
    stored_files,
)
from apps.core import ffmpeg
from apps.core.tests.test_ffmpeg import make_sample, needs_ffmpeg
from apps.core.uploads import MB
from config.settings.storage import build_storages

pytestmark = pytest.mark.django_db

CREATE = "/artysta/profil/materialy/wysylki/"
MP4 = b"\x00\x00\x00\x18ftypisom\x00\x00\x02\x00isomiso2" + bytes(range(256)) * 40
MP3 = b"ID3\x04\x00\x00\x00\x00\x00\x00" + b"\xff\xfb\x90\x00" * 2000


def chunk_url(session_id):
    return f"/artysta/profil/materialy/wysylki/{session_id}/"


def complete_url(session_id):
    return f"/artysta/profil/materialy/wysylki/{session_id}/zakoncz/"


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
    settings.MALWARE_SCANNER_FAKE_RESULT = "clean"
    return lambda result: setattr(settings, "MALWARE_SCANNER_FAKE_RESULT", result)


@pytest.fixture
def commit(django_capture_on_commit_callbacks):
    return lambda: django_capture_on_commit_callbacks(execute=True)


@pytest.fixture
def chunks(settings, tmp_path):
    """Temporary upload directory and a small chunk size, so files come in several chunks."""
    settings.UPLOAD_TEMP_DIR = tmp_path / "chunks"
    settings.UPLOAD_CHUNK_BYTES = 4096
    return tmp_path / "chunks"


def temp_files(root: Path) -> list:
    return sorted(root.glob("*")) if root.exists() else []


def open_session(web, kind="video", size=None, name="spektakl.mp4"):
    size = len(MP4) if size is None else size
    return web.post(CREATE, {"kind": kind, "size": str(size), "name": name})


def send(web, session_id, data, offset):
    return web.post(
        chunk_url(session_id),
        data=data,
        content_type="application/octet-stream",
        headers={"Upload-Offset": str(offset)},
    )


def send_all(web, session_id, data, size=4096, start=0):
    offset = start
    while offset < len(data):
        response = send(web, session_id, data[offset : offset + size], offset)
        assert response.status_code == 200, response.content
        offset = response.json()["offset"]
    return offset


def upload_file(web, data=MP4, kind="video", name="spektakl.mp4"):
    response = open_session(web, kind, len(data), name)
    assert response.status_code == 201, response.content
    session_id = response.json()["id"]
    send_all(web, session_id, data)
    response = web.post(complete_url(session_id))
    assert response.status_code == 201, response.content
    return Material.objects.get(pk=response.json()["material"])


@pytest.fixture
def fake_ffmpeg(monkeypatch):
    """Mocked probe/convert/thumbnail. `fake_ffmpeg.probe_result` is what ffprobe 'sees';
    set `fake_ffmpeg.error` to an FFmpegError raised by the conversion."""

    class Fake:
        probe_result = ffmpeg.Probe(frozenset({"mov", "mp4"}), 12.4, True, True, 1920, 1080)
        converted = ffmpeg.Probe(frozenset({"mov", "mp4"}), 12.4, True, True, 1280, 720)
        error = None
        probe_error = None
        calls: list = []

        def probe(self, path):
            self.calls.append(("probe", Path(path).name))
            if self.probe_error:
                raise self.probe_error
            return self.converted if Path(path).name == "converted.mp4" else self.probe_result

        def convert_video(self, source, target, *, max_seconds):
            self.calls.append(("convert", max_seconds))
            if self.error:
                raise self.error
            Path(target).write_bytes(b"\x00\x00\x00\x18ftypisom converted")

        def thumbnail(self, source, target, *, at_seconds):
            self.calls.append(("thumbnail", at_seconds))
            Path(target).write_bytes(b"\xff\xd8\xff thumbnail")

    fake = Fake()
    fake.calls = []
    monkeypatch.setattr(ffmpeg, "probe", fake.probe)
    monkeypatch.setattr(ffmpeg, "convert_video", fake.convert_video)
    monkeypatch.setattr(ffmpeg, "thumbnail", fake.thumbnail)
    return fake


def scanned(material):
    """Run the scan (fake: clean) so the material waits for processing."""
    materials.scan_material(material.pk)
    material.refresh_from_db()
    return material


# --- sessions and chunks ---------------------------------------------------------------------


def test_upload_in_several_chunks_creates_a_pending_material_and_removes_the_chunks(
    web, artist, storage, chunks, queue
):
    response = open_session(web)
    assert response.status_code == 201
    data = response.json()
    assert data["offset"] == 0 and data["size"] == len(MP4) and data["chunk_size"] == 4096
    assert data["url"] == chunk_url(data["id"]) and data["complete_url"] == complete_url(data["id"])
    assert len(temp_files(chunks)) == 1
    assert send_all(web, data["id"], MP4) == len(MP4)
    response = web.post(complete_url(data["id"]))
    assert response.status_code == 201 and response.json()["redirect"] == PAGE
    material = Material.objects.get(artist=artist)
    assert (material.kind, material.status) == ("video", ScanStatus.PENDING)
    assert material.storage_key.startswith("video/") and material.storage_key.endswith(".mp4")
    assert material.original_name == "spektakl.mp4" and material.size == len(MP4)
    assert storage.joinpath(material.storage_key).read_bytes() == MP4
    assert temp_files(chunks) == [] and not UploadSession.objects.exists()
    assert [j["args"] for j in scan_jobs(queue)] == [{"material_id": material.pk}]


def test_interrupted_upload_resumes_from_the_server_offset_and_is_byte_identical(
    web, artist, storage, chunks
):
    session_id = open_session(web).json()["id"]
    assert send(web, session_id, MP4[:4096], 0).status_code == 200
    # connection lost, page reloaded: the client asks where to continue
    state = web.get(chunk_url(session_id)).json()
    assert state["offset"] == 4096 and state["complete"] is False
    send_all(web, session_id, MP4, start=state["offset"])
    assert web.get(chunk_url(session_id)).json()["complete"] is True
    assert web.post(complete_url(session_id)).status_code == 201
    material = Material.objects.get(artist=artist)
    assert storage.joinpath(material.storage_key).read_bytes() == MP4


def test_wrong_offset_is_refused_with_the_server_offset_and_nothing_written(web, artist, chunks):
    session_id = open_session(web).json()["id"]
    send(web, session_id, MP4[:4096], 0)
    for offset in (0, 100, 8192):
        response = send(web, session_id, MP4[offset : offset + 10], offset)
        assert response.status_code == 409 and response.json()["offset"] == 4096
    assert resumable.temp_path(session_id).read_bytes() == MP4[:4096]


def test_bytes_beyond_the_declared_size_are_refused(web, artist, chunks):
    session_id = open_session(web, size=5000).json()["id"]
    assert send(web, session_id, MP4[:4096], 0).status_code == 200
    response = send(web, session_id, MP4[4096:8192], 4096)  # 4096 + 4096 > 5000
    assert response.status_code == 413
    assert UploadSession.objects.get(pk=session_id).received == 4096
    assert resumable.temp_path(session_id).stat().st_size == 4096


def test_a_chunk_larger_than_the_chunk_size_is_refused(web, artist, chunks):
    session_id = open_session(web).json()["id"]
    response = send(web, session_id, MP4[:4097], 0)
    assert response.status_code == 413
    assert resumable.temp_path(session_id).stat().st_size == 0


def test_short_or_malformed_chunk_requests_are_refused(artist, chunks):
    session = resumable.create_session(artist, "video", len(MP4), "a.mp4")
    with pytest.raises(resumable.UploadRefused) as exc:
        resumable.append_chunk(artist, session.pk, 0, 100, io.BytesIO(MP4[:50]))
    assert exc.value.code == "short"
    with pytest.raises(resumable.UploadRefused) as exc:
        resumable.append_chunk(artist, session.pk, "x", 100, io.BytesIO(MP4))
    assert exc.value.code == "bad_request"
    with pytest.raises(resumable.UploadRefused) as exc:
        resumable.append_chunk(artist, session.pk, 0, 0, io.BytesIO(b""))
    assert exc.value.code == "chunk_size"


def test_complete_before_the_last_byte_is_refused_and_the_session_stays(web, artist, chunks):
    session_id = open_session(web).json()["id"]
    send(web, session_id, MP4[:4096], 0)
    response = web.post(complete_url(session_id))
    assert response.status_code == 409 and response.json()["offset"] == 4096
    assert UploadSession.objects.filter(pk=session_id).exists()


def test_a_crashed_write_is_dropped_before_the_next_chunk(artist, chunks):
    session = resumable.create_session(artist, "video", len(MP4), "a.mp4")
    resumable.append_chunk(artist, session.pk, 0, 4096, io.BytesIO(MP4[:4096]))
    with resumable.temp_path(session.pk).open("ab") as file:
        file.write(b"garbage of a write that never committed")
    resumable.append_chunk(artist, session.pk, 4096, 4096, io.BytesIO(MP4[4096:8192]))
    assert resumable.temp_path(session.pk).read_bytes() == MP4[:8192]


def test_a_vanished_temp_file_is_a_gone_session(artist, chunks):
    session = resumable.create_session(artist, "video", len(MP4), "a.mp4")
    resumable.temp_path(session.pk).unlink()
    with pytest.raises(resumable.SessionGone):
        resumable.append_chunk(artist, session.pk, 0, 4096, io.BytesIO(MP4[:4096]))
    with pytest.raises(resumable.SessionGone):
        resumable.get_session(artist, "not-a-uuid")


# --- limits and type checks ------------------------------------------------------------------


@pytest.mark.parametrize("kind, size", [("video", 500 * MB + 1), ("audio", 50 * MB + 1)])
def test_declared_size_over_the_d8_limit_is_refused(web, artist, chunks, kind, size):
    response = open_session(web, kind, size)
    assert response.status_code == 413
    assert "Plik jest za duży" in response.json()["error"]
    assert not UploadSession.objects.exists() and temp_files(chunks) == []


@pytest.mark.parametrize(
    "fields, code",
    [
        ({"kind": "photo", "size": "10"}, 400),
        ({"kind": "video", "size": "abc"}, 400),
        ({"kind": "video", "size": "0"}, 400),
        ({"kind": "video"}, 400),
    ],
)
def test_bad_session_requests_are_refused(web, artist, chunks, fields, code):
    response = web.post(CREATE, fields)
    assert response.status_code == code and response.json()["error"]
    assert not UploadSession.objects.exists()


def test_sixth_video_is_refused_before_any_byte_and_the_page_shows_the_limit(
    web, artist, storage, chunks, settings
):
    settings.MATERIAL_MAX_VIDEOS = 2  # same code path as 5, fewer files
    for _ in range(2):
        upload_file(web)
    response = open_session(web)
    assert response.status_code == 400
    assert "Osiągnięto limit 2 filmów." in response.json()["error"]
    assert not UploadSession.objects.exists() and temp_files(chunks) == []
    body = web.get(PAGE).content.decode()
    assert 'data-resumable data-kind="video"' not in body  # no upload form, the limit message
    assert "Osiągnięto limit." in body and "Pozostało miejsc: 0." in body


def test_eleventh_audio_is_refused(web, artist, storage, chunks, settings):
    settings.MATERIAL_MAX_AUDIO = 1
    upload_file(web, MP3, "audio", "nagranie.mp3")
    response = open_session(web, "audio", len(MP3), "drugie.mp3")
    assert response.status_code == 400 and "Osiągnięto limit 1 nagrań." in response.json()["error"]


def test_default_limits_are_5_videos_and_10_audio(settings):
    assert (settings.MATERIAL_MAX_VIDEOS, settings.MATERIAL_MAX_AUDIO) == (5, 10)
    assert settings.MEDIA_MAX_DURATION_SECONDS == 600


def test_limit_reached_by_a_parallel_upload_refuses_the_completion(
    web, artist, storage, chunks, settings
):
    settings.MATERIAL_MAX_VIDEOS = 2
    upload_file(web)  # one place left, two uploads started in parallel
    first = open_session(web).json()["id"]
    second = open_session(web).json()["id"]
    send_all(web, first, MP4)
    send_all(web, second, MP4)
    assert web.post(complete_url(first)).status_code == 201
    response = web.post(complete_url(second))
    assert response.status_code == 400 and "Osiągnięto limit 2 filmów." in response.json()["error"]
    assert Material.objects.count() == 2 and len(stored_files(storage)) == 2
    assert temp_files(chunks) == []


def test_text_renamed_mp4_is_refused_on_the_first_chunk_and_nothing_stored(
    web, artist, storage, chunks
):
    text = b"To jest zwykly plik tekstowy, nie film.\n" * 100
    session_id = open_session(web, size=len(text), name="film.mp4").json()["id"]
    response = send(web, session_id, text[:4096], 0)
    assert response.status_code == 400
    assert response.json()["error"] == "Ten typ pliku nie jest dozwolony."
    assert not UploadSession.objects.exists() and temp_files(chunks) == []
    assert not Material.objects.exists() and stored_files(storage) == []
    assert web.get(chunk_url(session_id)).status_code == 404


def test_content_is_checked_again_on_completion(artist, storage, chunks, monkeypatch):
    session = resumable.create_session(artist, "video", len(MP4), "a.mp4")
    resumable.append_chunk(artist, session.pk, 0, 4096, io.BytesIO(MP4[:4096]))
    # the stored head is replaced behind the server's back: completion sniffs the file again
    session.refresh_from_db()
    data = b"%PDF-1.4 " + MP4[9:4096]
    resumable.temp_path(session.pk).write_bytes(data)
    UploadSession.objects.filter(pk=session.pk).update(declared_size=4096, received=4096)
    with pytest.raises(resumable.UploadRefused) as exc:
        resumable.complete(artist, session.pk)
    assert exc.value.code == "bad_type"
    assert stored_files(storage) == [] and temp_files(chunks) == []


def test_ogg_audio_is_refused_for_the_audio_kind(artist, storage, chunks):
    ogg = b"OggS" + b"\x00" * 100
    session = resumable.create_session(artist, "audio", len(ogg), "a.ogg")
    with pytest.raises(resumable.UploadRefused):
        resumable.append_chunk(artist, session.pk, 0, len(ogg), io.BytesIO(ogg))


def test_open_sessions_are_capped_by_replacing_the_oldest(artist, chunks, settings):
    settings.MATERIAL_MAX_VIDEOS = 2
    first = resumable.create_session(artist, "video", 100, "a.mp4")
    second = resumable.create_session(artist, "video", 100, "b.mp4")
    third = resumable.create_session(artist, "video", 100, "c.mp4")
    assert set(UploadSession.objects.values_list("pk", flat=True)) == {second.pk, third.pk}
    assert not resumable.temp_path(first.pk).exists()


def test_a_size_mismatch_on_disk_drops_the_session(artist, storage, chunks):
    session = resumable.create_session(artist, "video", len(MP4), "a.mp4")
    resumable.temp_path(session.pk).write_bytes(MP4)
    UploadSession.objects.filter(pk=session.pk).update(received=len(MP4))
    resumable.temp_path(session.pk).write_bytes(MP4[:10])
    with pytest.raises(resumable.UploadRefused) as exc:
        resumable.complete(artist, session.pk)
    assert exc.value.code == "size_mismatch" and not UploadSession.objects.exists()


# --- ownership, expiry, cleanup --------------------------------------------------------------


def other_artist():
    user = make_artist("inny.artysta@example.invalid")
    services.save_basics(user, BASICS)
    return Artist.objects.get(user=user)


def test_another_artists_session_is_404_everywhere(web, artist, chunks):
    session = resumable.create_session(other_artist(), "video", len(MP4), "a.mp4")
    assert web.get(chunk_url(session.pk)).status_code == 404
    assert send(web, session.pk, MP4[:4096], 0).status_code == 404
    assert web.post(complete_url(session.pk)).status_code == 404
    assert web.get(chunk_url(uuid.uuid4())).status_code == 404
    assert UploadSession.objects.get(pk=session.pk).received == 0


def test_institution_gets_403_on_the_upload_routes(chunks):
    client = Client()
    client.force_login(make_institution_member())
    session_id = uuid.uuid4()
    assert client.post(CREATE, {"kind": "video", "size": "10"}).status_code == 403
    assert client.get(chunk_url(session_id)).status_code == 403
    assert client.post(chunk_url(session_id), b"x", "application/octet-stream").status_code == 403
    assert client.post(complete_url(session_id)).status_code == 403


def test_upload_routes_need_complete_basics_and_post(chunks):
    client = Client()
    client.force_login(make_artist())
    response = client.post(CREATE, {"kind": "video", "size": "10"})
    assert response.status_code == 302 and response["Location"] == "/artysta/profil/dane/"


def test_create_and_complete_refuse_get(web, artist):
    assert web.get(CREATE).status_code == 405
    assert web.get(complete_url(uuid.uuid4())).status_code == 405


def test_expired_session_is_404_and_the_cleanup_removes_its_data(web, artist, chunks):
    session_id = open_session(web).json()["id"]
    send(web, session_id, MP4[:4096], 0)
    path = resumable.temp_path(session_id)
    assert path.exists()
    UploadSession.objects.filter(pk=session_id).update(
        expires_at=timezone.now() - timedelta(seconds=1)
    )
    assert web.get(chunk_url(session_id)).status_code == 404
    assert resumable.cleanup_expired() == 1
    assert not path.exists() and not UploadSession.objects.exists()


def test_cleanup_keeps_live_sessions_and_removes_stray_old_files(artist, chunks, settings):
    live = resumable.create_session(artist, "video", 100, "a.mp4")
    stray = chunks / f"{uuid.uuid4().hex}.part"
    stray.write_bytes(b"x")
    import os

    old = timezone.now().timestamp() - settings.UPLOAD_SESSION_TTL_HOURS * 3600 - 10
    os.utime(stray, (old, old))
    fresh_stray = chunks / f"{uuid.uuid4().hex}.part"
    fresh_stray.write_bytes(b"x")
    assert resumable.cleanup_expired() == 1
    assert resumable.temp_path(live.pk).exists() and fresh_stray.exists() and not stray.exists()
    assert resumable.cleanup_expired() == 0


def test_session_expiry_comes_from_the_setting(artist, chunks, settings):
    settings.UPLOAD_SESSION_TTL_HOURS = 2
    session = resumable.create_session(artist, "audio", 100, "a.mp3")
    assert session.expires_at - session.created_at == timedelta(hours=2)


@pytest.mark.django_db(transaction=True)
def test_periodic_cleanup_job_runs(artist, chunks, queue):
    from apps.artists import tasks

    session = resumable.create_session(artist, "video", 100, "a.mp4")
    UploadSession.objects.filter(pk=session.pk).update(expires_at=timezone.now())
    tasks.cleanup_upload_sessions(timestamp=0)
    assert not UploadSession.objects.exists()


# --- processing (ffmpeg mocked) --------------------------------------------------------------


def test_clean_scan_queues_processing_and_keeps_the_video_pending(
    web, artist, storage, chunks, queue
):
    material = scanned(upload_file(web))
    assert material.status == ScanStatus.PENDING
    assert material.processing_status == ProcessingStatus.PENDING
    jobs = scan_jobs(queue, "artists.process_media")
    assert [(j["args"], j["queue_name"]) for j in jobs] == [({"material_id": material.pk}, "media")]
    assert not materials.ready_materials(artist).exists()
    body = web.get(PAGE).content.decode()
    assert 'data-processing="pending"' in body and "przetwarzanie" in body


def test_video_is_converted_with_a_thumbnail_and_becomes_ready(
    web, artist, storage, chunks, fake_ffmpeg
):
    material = scanned(upload_file(web))
    assert recordings.process_media(material.pk) == ScanStatus.READY
    material.refresh_from_db()
    assert material.processing_status == ProcessingStatus.DONE
    assert (material.duration_seconds, material.width, material.height) == (12.4, 1280, 720)
    assert material.converted_key.startswith("converted/") and material.converted_key.endswith(
        ".mp4"
    )
    assert material.thumbnail_key.startswith("thumbnail/")
    for key in material.stored_keys():
        assert storage.joinpath(key).exists()
    assert ("convert", 600) in fake_ffmpeg.calls and ("thumbnail", 1.0) in fake_ffmpeg.calls
    assert list(materials.ready_materials(artist)) == [material]
    body = web.get(PAGE).content.decode()
    assert 'data-field="thumbnail"' in body and "(0:12, 1280×720)" in body
    assert body.count("/media/private/") >= 2  # signed links: MP4 and thumbnail


def test_mp3_is_ready_with_its_duration_and_no_conversion(
    web, artist, storage, chunks, fake_ffmpeg
):
    fake_ffmpeg.probe_result = ffmpeg.Probe(frozenset({"mp3"}), 95.0, False, True, None, None)
    material = scanned(upload_file(web, MP3, "audio", "piosenka.mp3"))
    assert recordings.process_media(material.pk) == ScanStatus.READY
    material.refresh_from_db()
    assert material.duration_seconds == 95.0 and material.converted_key == ""
    assert material.thumbnail_key == "" and material.content_type == "audio/mpeg"
    assert [c[0] for c in fake_ffmpeg.calls] == ["probe"]
    assert "(1:35)" in web.get(PAGE).content.decode()


def test_video_over_ten_minutes_is_rejected_and_its_file_deleted(
    web, artist, storage, chunks, fake_ffmpeg, commit
):
    fake_ffmpeg.probe_result = ffmpeg.Probe(frozenset({"mp4"}), 600.5, True, True, 640, 360)
    material = scanned(upload_file(web))
    with commit():
        assert recordings.process_media(material.pk) == ScanStatus.REJECTED
    material.refresh_from_db()
    assert material.processing_status == ProcessingStatus.FAILED
    assert material.processing_message.startswith("Film jest dłuższy niż 10 minut")
    assert material.storage_key == "" and stored_files(storage) == []
    assert materials.remaining(artist, "video") == 5  # a rejected file frees its slot
    body = web.get(PAGE).content.decode()
    assert "Film jest dłuższy niż 10 minut" in body and "złośliwe" not in body


@pytest.mark.parametrize(
    "probe, kind",
    [
        (ffmpeg.Probe(frozenset({"mp3"}), 10, False, True, None, None), "video"),  # wrong format
        (ffmpeg.Probe(frozenset({"mp4"}), 10, False, True, None, None), "video"),  # no picture
        (ffmpeg.Probe(frozenset({"mp4"}), None, True, True, 640, 360), "video"),  # no duration
        (ffmpeg.Probe(frozenset({"mp4"}), 10, True, True, 640, 360), "audio"),  # a video
        (ffmpeg.Probe(frozenset({"ogg"}), 10, False, True, None, None), "audio"),
    ],
)
def test_probe_results_outside_d8_are_unreadable(probe, kind):
    with pytest.raises(recordings.Rejected) as exc:
        recordings.check_probe(kind, probe)
    assert "Nie można odczytać" in str(exc.value.message)


def test_long_audio_is_fine(fake_ffmpeg):
    recordings.check_probe("audio", ffmpeg.Probe(frozenset({"wav"}), 3600, False, True, None, None))


def test_unreadable_file_is_rejected(web, artist, storage, chunks, fake_ffmpeg, commit):
    fake_ffmpeg.probe_error = ffmpeg.FFmpegError("failed", "Invalid data")
    material = scanned(upload_file(web))
    with commit():
        assert recordings.process_media(material.pk) == ScanStatus.REJECTED
    material.refresh_from_db()
    assert "Nie można odczytać tego pliku jako filmu" in material.processing_message
    assert stored_files(storage) == []


@pytest.mark.parametrize(
    "error, message",
    [
        (ffmpeg.FFmpegError("timeout", "900 s"), "Przetwarzanie trwało za długo"),
        (ffmpeg.FFmpegError("crash", "signal 9"), "Nie udało się przetworzyć pliku"),
        (ffmpeg.FFmpegError("missing", "ffmpeg"), "Nie udało się przetworzyć pliku"),
        (RuntimeError("unexpected"), "Nie udało się przetworzyć pliku"),
    ],
)
def test_ffmpeg_trouble_ends_as_a_readable_status(
    web, artist, storage, chunks, fake_ffmpeg, commit, error, message
):
    fake_ffmpeg.error = error
    material = scanned(upload_file(web))
    with commit():
        assert recordings.process_media(material.pk) == ScanStatus.REJECTED  # no exception
    material.refresh_from_db()
    assert material.processing_status == ProcessingStatus.FAILED
    assert material.processing_message.startswith(message)
    assert stored_files(storage) == []


@pytest.mark.django_db(transaction=True)
def test_worker_survives_an_ffmpeg_timeout(artist, storage, chunks, queue, fake_ffmpeg, settings):
    fake_ffmpeg.error = ffmpeg.FFmpegError("timeout", "0.01 s")
    session = resumable.create_session(artist, "video", len(MP4), "a.mp4")
    resumable.append_chunk(artist, session.pk, 0, 4096, io.BytesIO(MP4[:4096]))
    UploadSession.objects.filter(pk=session.pk).update(declared_size=4096)
    material = resumable.complete(artist, session.pk)
    run_media_worker()
    material.refresh_from_db()
    assert material.status == ScanStatus.REJECTED
    assert "Przetwarzanie trwało za długo" in material.processing_message
    statuses = {j["task_name"]: j["status"] for j in queue.jobs.values()}
    assert statuses == {"artists.scan_material": "succeeded", "artists.process_media": "succeeded"}


@pytest.mark.django_db(transaction=True)
def test_worker_scans_then_processes_a_video_to_ready(artist, storage, chunks, queue, fake_ffmpeg):
    session = resumable.create_session(artist, "video", 4096, "a.mp4")
    resumable.append_chunk(artist, session.pk, 0, 4096, io.BytesIO(MP4[:4096]))
    material = resumable.complete(artist, session.pk)
    run_media_worker()
    material.refresh_from_db()
    assert material.status == ScanStatus.READY and material.converted_key
    assert temp_files(chunks) == []


def test_processing_is_skipped_when_nothing_to_do(artist, storage, chunks, web):
    assert recordings.process_media(999999) == ""
    material = upload_file(web)  # not scanned yet
    assert recordings.process_media(material.pk) == ""


def test_material_deleted_during_processing_keeps_no_files(
    web, artist, storage, chunks, fake_ffmpeg, commit, monkeypatch
):
    material = scanned(upload_file(web))
    real_record = recordings._record

    def delete_first(material_id, outcome):
        Material.objects.filter(pk=material_id).delete()
        return real_record(material_id, outcome)

    monkeypatch.setattr(recordings, "_record", delete_first)
    with commit():
        assert recordings.process_media(material.pk) == ""
    assert not any("converted" in str(p) or "thumbnail" in str(p) for p in stored_files(storage))


def test_infected_video_is_rejected_without_processing(
    web, artist, storage, chunks, scanner, queue
):
    material = upload_file(web)
    scanner("infected")
    assert materials.scan_material(material.pk) == ScanStatus.REJECTED
    assert scan_jobs(queue, "artists.process_media") == []


def test_format_duration():
    assert materials.format_duration(None) == ""
    assert materials.format_duration(0.4) == "0:00"
    assert materials.format_duration(599.6) == "10:00"
    assert materials.format_duration(65) == "1:05"


# --- delete ----------------------------------------------------------------------------------


def test_deleting_a_video_removes_the_row_the_original_the_mp4_and_the_thumbnail(
    web, artist, storage, chunks, fake_ffmpeg, commit
):
    material = scanned(upload_file(web))
    recordings.process_media(material.pk)
    material.refresh_from_db()
    assert len(stored_files(storage)) == 3
    with commit():
        assert web.post(delete_url(material.pk)).status_code == 302
    assert not Material.objects.exists() and stored_files(storage) == []


def test_another_artists_video_cannot_be_deleted(web, artist, storage, chunks):
    other = other_artist()
    session = resumable.create_session(other, "video", 4096, "a.mp4")
    resumable.append_chunk(other, session.pk, 0, 4096, io.BytesIO(MP4[:4096]))
    material = resumable.complete(other, session.pk)
    assert web.post(delete_url(material.pk)).status_code == 404
    assert Material.objects.filter(pk=material.pk).exists()


# --- page ------------------------------------------------------------------------------------


def test_page_has_the_resumable_boxes_with_the_checks(web, artist):
    body = web.get(PAGE).content.decode()
    assert 'data-resumable data-kind="video"' in body and 'data-kind="audio"' in body
    assert f'data-max-bytes="{500 * MB}"' in body and f'data-max-bytes="{50 * MB}"' in body
    assert 'data-max-seconds="600"' in body and 'data-max-seconds="0"' in body
    assert 'accept="video/mp4,video/quicktime,video/webm,.mp4,.mov,.webm"' in body
    assert "Film może trwać najwyżej 10 minut." in body
    assert f'action="{CREATE}"' in body and "<script>" not in body


def test_csp_allows_blob_media_for_the_duration_check(web, artist):
    csp = web.get(PAGE)["Content-Security-Policy"]
    assert "media-src 'self' blob:" in csp and "script-src 'self' 'nonce-" in csp


# --- real ffmpeg on generated samples (CI) ---------------------------------------------------


@needs_ffmpeg
@pytest.mark.django_db(transaction=True)
def test_real_short_mp4_in_chunks_ends_ready_with_mp4_and_thumbnail(
    artist_user, artist, storage, chunks, queue, tmp_path, settings
):
    settings.UPLOAD_CHUNK_BYTES = 16 * 1024
    data = make_sample(tmp_path / "sample.mp4", seconds=2, size="1280x720").read_bytes()
    assert len(data) > 2 * settings.UPLOAD_CHUNK_BYTES  # several chunks
    client = Client()
    client.force_login(artist_user)
    material = upload_file(client, data, "video", "sample.mp4")
    assert temp_files(chunks) == []
    run_media_worker()
    material.refresh_from_db()
    assert material.status == ScanStatus.READY, material.processing_message
    assert (material.width, material.height) == (1280, 720)
    assert 1.5 < material.duration_seconds < 2.5
    converted = storage / material.converted_key
    assert ffmpeg.probe(converted).format_names & {"mp4", "mov"}
    assert (storage / material.thumbnail_key).read_bytes()[:3] == b"\xff\xd8\xff"
    assert (storage / material.storage_key).read_bytes() == data


@needs_ffmpeg
def test_real_mp3_is_ready_without_conversion(web, artist, storage, chunks, tmp_path):
    data = make_sample(tmp_path / "tone.mp3", seconds=3, audio_only=True).read_bytes()
    material = scanned(upload_file(web, data, "audio", "tone.mp3"))
    assert recordings.process_media(material.pk) == ScanStatus.READY
    material.refresh_from_db()
    assert 2.5 < material.duration_seconds < 3.5 and not material.converted_key


@needs_ffmpeg
def test_real_video_over_the_limit_is_rejected(web, artist, storage, chunks, tmp_path, settings,
                                               commit):  # fmt: skip
    settings.MEDIA_MAX_DURATION_SECONDS = 1  # a 2 s sample stands in for an 11-minute film
    data = make_sample(tmp_path / "long.mp4", seconds=2, size="320x240").read_bytes()
    material = scanned(upload_file(web, data))
    with commit():
        assert recordings.process_media(material.pk) == ScanStatus.REJECTED
    material.refresh_from_db()
    assert "dłuższy niż" in material.processing_message and stored_files(storage) == []


@needs_ffmpeg
def test_real_conversion_with_a_tiny_time_limit_is_a_readable_status(
    web, artist, storage, chunks, tmp_path, settings
):
    data = make_sample(tmp_path / "in.mp4", seconds=4, size="1920x1080").read_bytes()
    material = scanned(upload_file(web, data))
    settings.FFMPEG_TIMEOUT_SECONDS = 0.01
    assert recordings.process_media(material.pk) == ScanStatus.REJECTED
    material.refresh_from_db()
    assert material.processing_message.startswith("Przetwarzanie trwało za długo")
