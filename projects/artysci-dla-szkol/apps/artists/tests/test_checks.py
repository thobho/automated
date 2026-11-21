"""Quality checks of photos and videos and frames as main-photo candidates (US-2.4, D59, D109).
Photos are generated with Pillow; the scanner is the fake backend; ffmpeg is mocked, except the
tests marked `needs_ffmpeg` (real samples, CI installs ffmpeg)."""

import io
from pathlib import Path

import pytest
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.test import Client
from PIL import Image, ImageDraw, ImageFont

from apps.accounts.tests.conftest import make_artist
from apps.artists import checks, materials, recordings, services
from apps.artists.checks import Flag
from apps.artists.models import (
    Artist,
    Material,
    MaterialKind,
    ProcessingStatus,
    ScanStatus,
    VideoFrame,
)
from apps.artists.tests.test_materials import BASICS, PAGE, stored_files
from apps.core import ffmpeg, media
from apps.core.tests.test_ffmpeg import make_sample, needs_ffmpeg
from config.settings.storage import build_storages

pytestmark = pytest.mark.django_db


# --- fixtures and builders -------------------------------------------------------------------


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


@pytest.fixture(autouse=True)
def scanner(settings):
    settings.MALWARE_SCANNER_FAKE_RESULT = "clean"


def photo_like(width=1500, height=1000, seed_size=10) -> Image.Image:
    """Smooth coloured blobs: like a photo, not like a flat graphic."""
    noise = Image.effect_noise((width // seed_size, height // seed_size), 90).convert("RGB")
    return noise.resize((width, height), Image.Resampling.BICUBIC)


def other_photo(width=1500, height=1000) -> Image.Image:
    """A different photo-like image (other blobs, mirrored layout)."""
    return photo_like(width, height, seed_size=7).transpose(Image.Transpose.FLIP_LEFT_RIGHT)


def poster_image(width=800, height=1100) -> Image.Image:
    img = Image.new("RGB", (width, height), (250, 220, 40))
    draw = ImageDraw.Draw(img)
    big = ImageFont.load_default(size=200)
    draw.text((30, 80), "KON", fill=(20, 20, 20), font=big)
    draw.text((30, 380), "CERT", fill=(20, 20, 20), font=big)
    draw.text((30, 800), "12 maja", fill=(200, 30, 30), font=ImageFont.load_default(size=120))
    return img


def encode(img: Image.Image, fmt="JPEG", **kwargs) -> bytes:
    out = io.BytesIO()
    img.save(out, fmt, **kwargs)
    return out.getvalue()


def upload(artist, data, name="a.jpg", content_type="image/jpeg") -> Material:
    return materials.add_file(
        artist, MaterialKind.PHOTO, SimpleUploadedFile(name, data, content_type=content_type)
    )


def checked(artist, data, **kwargs) -> Material:
    """Upload through the real path, scan (clean) and run the check job."""
    material = upload(artist, data, **kwargs)
    materials.scan_material(material.pk)
    assert checks.check_material(material.pk) == "checked"
    material.refresh_from_db()
    return material


def ready_photo(artist, **fields) -> Material:
    """A ready, already checked photo row without a file (for rules that read only the row)."""
    values = {
        "kind": MaterialKind.PHOTO, "status": ScanStatus.READY, "width": 3000, "height": 2000,
        "checks_version": checks.CHECKS_VERSION, "flags": [], "storage_key": "photo/x.jpg",
    }  # fmt: skip
    return Material.objects.create(artist=artist, **{**values, **fields})


def exif(**tags) -> Image.Exif:
    value = Image.Exif()
    for tag, content in tags.items():
        value[int(tag.removeprefix("t"), 16)] = content
    return value


def xmp(body: str) -> bytes:
    return (
        '<x:xmpmeta xmlns:x="adobe:ns:meta/"><rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/'
        f'22-rdf-syntax-ns#"><rdf:Description>{body}</rdf:Description></rdf:RDF></x:xmpmeta>'
    ).encode()


# --- flag list and hints ---------------------------------------------------------------------


def test_every_flag_has_a_label_and_a_hint():
    for flag in Flag:
        assert flag.label and checks.hint_for(flag.value)
        assert checks.hint_for(flag.value, MaterialKind.VIDEO)


def test_hints_name_the_thresholds_and_flag_items_are_ordered_and_closed():
    assert "1200 px" in checks.hint_for(Flag.LOW_RESOLUTION)
    assert "720" in checks.hint_for(Flag.LOW_RESOLUTION, MaterialKind.VIDEO)
    assert "15 s" in checks.hint_for(Flag.TOO_SHORT, MaterialKind.VIDEO)
    items = checks.flag_items(["poster", "unknown", "low_resolution", "poster"])
    assert [i["code"] for i in items] == ["low_resolution", "poster"]
    assert items[0]["label"] == "niska rozdzielczość"
    assert checks.flag_items(None) == []


# --- photo flags: units ----------------------------------------------------------------------


@pytest.mark.parametrize(
    ("size", "low"),
    [
        ((1199, 800), True),
        ((1200, 800), False),
        ((800, 1199), True),
        ((800, 1200), False),
        ((1000, 800), True),
    ],  # fmt: skip
)
def test_low_resolution_is_the_longer_side_below_1200(size, low):
    flags = checks.image_flags(*size, poster=False, duplicate=False, camera_metadata=True)
    assert (Flag.LOW_RESOLUTION in flags) is low


def test_orientation():
    assert checks.orientation_of(1000, 800) == "landscape"
    assert checks.orientation_of(800, 1000) == "portrait"
    assert checks.orientation_of(900, 900) == "square"


@pytest.mark.parametrize(("quality", "flagged"), [(20, True), (59, True), (60, False), (90, False)])
def test_heavy_compression_threshold_on_the_original_quality(quality, flagged):
    from apps.core.imagemeta import ImageOrigin

    flags = checks.origin_flags(ImageOrigin(jpeg_quality=quality))
    assert (Flag.HEAVY_COMPRESSION in flags) is flagged
    assert checks.origin_flags(ImageOrigin(jpeg_quality=None)) == []
    assert checks.origin_flags(None) == []


def test_origin_flags_for_stock_and_ai():
    from apps.core.imagemeta import ImageOrigin

    assert checks.origin_flags(ImageOrigin(stock=True)) == [Flag.STOCK]
    assert checks.origin_flags(ImageOrigin(ai=True)) == [Flag.SCREENSHOT_OR_AI]


@pytest.mark.parametrize(
    ("size", "camera", "flagged"),
    [
        ((1920, 1080), False, True),
        ((1080, 1920), False, True),  # a phone screenshot
        ((1920, 1080), True, False),  # same size from a camera
        ((1920, 1080), None, False),  # unknown (older photos): never guessed
        ((1921, 1080), False, False),  # near the size
        ((1900, 1080), False, False),
    ],
)
def test_screenshot_needs_a_screen_size_and_no_camera_data(size, camera, flagged):
    flags = checks.image_flags(*size, poster=False, duplicate=False, camera_metadata=camera)
    assert (Flag.SCREENSHOT_OR_AI in flags) is flagged


@pytest.mark.parametrize(("other", "duplicate"), [(0, True), (5, True), (6, False)])
def test_duplicate_hash_distance_threshold(other, duplicate):
    base = "00000000000000ff"
    other_hash = f"{int(base, 16) ^ ((1 << other) - 1):016x}"
    assert checks.hash_distance(base, other_hash) == other
    assert checks._is_duplicate(base, [other_hash]) is duplicate
    assert checks._is_duplicate(base, ["", None]) is False


def test_perceptual_hash_is_stable_under_resize_and_recompression():
    img = photo_like(1200, 800)
    small = Image.open(io.BytesIO(encode(img.resize((600, 400)), quality=70)))
    assert checks.hash_distance(checks.perceptual_hash(img), checks.perceptual_hash(small)) <= 5
    assert (
        checks.hash_distance(checks.perceptual_hash(img), checks.perceptual_hash(other_photo())) > 5
    )


def test_poster_fixture_is_a_poster_and_photo_like_fixture_is_not():
    assert checks.looks_like_poster(poster_image())
    assert not checks.looks_like_poster(photo_like())
    assert not checks.looks_like_poster(Image.new("RGB", (800, 600), "white"))  # flat, no text
    assert not checks.looks_like_poster(Image.new("RGB", (4, 4), "white"))  # tiny


def test_a_photo_with_plain_shapes_but_no_lettering_is_not_a_poster():
    scene = Image.new("RGB", (1200, 800), (120, 170, 230))
    draw = ImageDraw.Draw(scene)
    draw.rectangle((100, 500, 400, 800), fill=(30, 30, 30))
    draw.rectangle((700, 450, 800, 800), fill=(40, 40, 40))
    assert not checks.looks_like_poster(scene)


# --- video flags: units ----------------------------------------------------------------------


def test_ten_second_vertical_480p_video_has_three_flags():
    flags = checks.video_flags(10, 480, 854)
    assert set(flags) == {Flag.TOO_SHORT, Flag.VERTICAL, Flag.LOW_RESOLUTION}


@pytest.mark.parametrize(
    ("args", "expected"),
    [
        ((14.9, 1280, 720), {Flag.TOO_SHORT}),
        ((15, 1280, 720), set()),
        ((60, 1280, 719), {Flag.LOW_RESOLUTION}),
        ((60, 720, 720), set()),  # square is not vertical
        ((60, 720, 1280), {Flag.VERTICAL}),  # portrait 720p: shorter side is 720
        ((None, None, None), set()),
    ],
)
def test_video_flag_thresholds(args, expected):
    assert set(checks.video_flags(*args)) == expected


# --- photo checks through the upload path and the job ----------------------------------------


def test_1000x800_photo_gets_size_orientation_flag_and_the_hint_in_the_list(artist, web, storage):
    material = checked(artist, encode(photo_like(1000, 800)))
    assert (material.width, material.height, material.orientation) == (1000, 800, "landscape")
    assert material.flags == [Flag.LOW_RESOLUTION]
    assert material.checks_version == checks.CHECKS_VERSION
    page = web.get(PAGE)
    assert page.status_code == 200
    html = page.content.decode()
    assert "niska rozdzielczość" in html
    assert "Wgraj zdjęcie o dłuższym boku co najmniej 1200 px" in html
    assert "1000×800" in html


def test_quality_20_has_heavy_compression_and_quality_90_does_not(artist, storage):
    img = photo_like()
    low = checked(artist, encode(img, quality=20))
    high = checked(artist, encode(other_photo(), quality=90))
    assert Flag.HEAVY_COMPRESSION in low.flags
    assert Flag.HEAVY_COMPRESSION not in high.flags


def test_second_copy_of_a_photo_resized_is_a_duplicate_the_first_is_not(artist, storage):
    img = photo_like(1500, 1000)
    first = checked(artist, encode(img))
    second = checked(artist, encode(img.resize((1300, 867)), quality=80))
    assert Flag.DUPLICATE not in first.flags
    assert Flag.DUPLICATE in second.flags
    # re-running the first check later does not flag it: only the older photo counts
    assert checks.check_material(first.pk, force=True) == "checked"
    first.refresh_from_db()
    assert Flag.DUPLICATE not in first.flags


def test_duplicates_are_per_artist(artist, storage):
    other = Artist.objects.get(user=make_artist(email="inny@example.invalid"))
    img = photo_like()
    checked(other, encode(img))
    mine = checked(artist, encode(img))
    assert Flag.DUPLICATE not in mine.flags


@pytest.mark.parametrize(
    "tags",
    [{"exif": exif(t8298="© Shutterstock")}, {"exif": exif(t8298="Getty Images")},
     {"xmp": xmp("<photoshop:Credit>iStock by Getty</photoshop:Credit>")}],
)  # fmt: skip
def test_stock_metadata_flags_and_the_stored_file_has_no_metadata(artist, storage, tags):
    material = checked(artist, encode(photo_like(), **tags))
    assert Flag.STOCK in material.flags
    saved = (storage / material.storage_key).read_bytes()
    assert b"getty" not in saved.lower() and b"shutterstock" not in saved.lower()
    assert not Image.open(io.BytesIO(saved)).getexif()
    assert "origin" not in {f.name for f in Material._meta.get_fields()}  # nothing raw kept


def test_1920x1080_png_without_camera_data_is_a_screenshot(artist, storage):
    material = checked(
        artist, encode(photo_like(1920, 1080), "PNG"), name="s.png", content_type="image/png"
    )
    assert Flag.SCREENSHOT_OR_AI in material.flags
    assert material.camera_metadata is False


def test_same_size_photo_with_camera_data_is_not_a_screenshot(artist, storage):
    data = encode(photo_like(1920, 1080), exif=exif(t010F="Canon", t0110="EOS"))
    material = checked(artist, data)
    assert material.camera_metadata is True
    assert Flag.SCREENSHOT_OR_AI not in material.flags


def test_ai_source_type_marker_flags_even_at_a_camera_size(artist, storage):
    body = (
        "<Iptc4xmpExt:DigitalSourceType>http://cv.iptc.org/newscodes/digitalsourcetype/"
        "trainedAlgorithmicMedia</Iptc4xmpExt:DigitalSourceType>"
    )
    material = checked(artist, encode(photo_like(1600, 1200), xmp=xmp(body)))
    assert Flag.SCREENSHOT_OR_AI in material.flags


def test_poster_fixture_is_flagged_and_photo_like_is_not(artist, storage):
    poster = checked(artist, encode(poster_image(1200, 1500)))
    photo = checked(artist, encode(other_photo()))
    assert Flag.POSTER in poster.flags
    assert Flag.POSTER not in photo.flags


def test_job_is_idempotent_and_skips_what_is_not_ready(artist, storage):
    material = checked(artist, encode(photo_like()))
    assert checks.check_material(material.pk) == "current"
    pending = upload(artist, encode(other_photo()))
    assert checks.check_material(pending.pk) == ""  # still pending: not ready
    assert checks.check_material(999999) == ""
    link = Material.objects.create(artist=artist, kind=MaterialKind.LINK, status="ready")
    assert checks.check_material(link.pk) == ""


def test_an_unreadable_stored_photo_leaves_the_version_old(artist, storage):
    material = checked(artist, encode(photo_like()))
    Material.objects.filter(pk=material.pk).update(checks_version=0)
    (storage / material.storage_key).write_bytes(b"not an image")
    assert checks.check_material(material.pk) == "checked"
    material.refresh_from_db()
    assert material.checks_version == 0


def test_scan_queues_the_check_job_for_photos_only(artist, storage, queue):
    photo = upload(artist, encode(photo_like()))
    materials.scan_material(photo.pk)
    names = [j["task_name"] for j in queue.jobs.values()]
    assert names.count("artists.check_material") == 1


def test_infected_photo_is_not_checked(artist, storage, queue, settings):
    settings.MALWARE_SCANNER_FAKE_RESULT = "infected"
    photo = upload(artist, encode(photo_like()))
    materials.scan_material(photo.pk)
    assert "artists.check_material" not in [j["task_name"] for j in queue.jobs.values()]


# --- main photo rule -------------------------------------------------------------------------


@pytest.mark.parametrize("flag", [Flag.STOCK, Flag.SCREENSHOT_OR_AI, Flag.POSTER])
def test_blocking_flags_keep_a_photo_from_being_main(artist, flag):
    flagged = ready_photo(artist, flags=[flag])
    good = ready_photo(artist)
    assert not checks.can_be_main(flagged)
    assert checks.can_be_main(good)
    assert checks.main_photo_candidates(artist) == [good]


def test_non_blocking_flags_do_not_block_and_3000x2000_unflagged_is_a_candidate(artist):
    soft = ready_photo(artist, flags=[Flag.LOW_RESOLUTION, Flag.HEAVY_COMPRESSION, Flag.DUPLICATE])
    big = ready_photo(artist, width=3000, height=2000)
    assert checks.can_be_main(soft) and checks.can_be_main(big)
    assert checks.main_photo_candidates(artist) == [soft, big]


def test_unchecked_pending_rejected_and_non_photos_are_never_candidates(artist):
    unchecked = ready_photo(artist, checks_version=0)
    pending = ready_photo(artist, status=ScanStatus.PENDING)
    rejected = ready_photo(artist, status=ScanStatus.REJECTED)
    pdf = ready_photo(artist, kind=MaterialKind.PDF)
    for item in (unchecked, pending, rejected, pdf):
        assert not checks.can_be_main(item)
    assert checks.main_photo_candidates(artist) == []


def test_candidates_are_per_artist(artist):
    other = Artist.objects.get(user=make_artist(email="inny@example.invalid"))
    ready_photo(other)
    assert checks.main_photo_candidates(artist) == []


# --- videos and frames (ffmpeg mocked) -------------------------------------------------------


@pytest.fixture
def fake_thumbnail(monkeypatch):
    """`ffmpeg.thumbnail` writes a real photo-like JPEG; `.calls` lists the seconds asked."""
    calls: list = []
    image = encode(photo_like(1280, 720))

    def thumbnail(source, target, *, at_seconds):
        calls.append(at_seconds)
        if thumbnail.error:
            raise thumbnail.error
        Path(target).write_bytes(image)

    thumbnail.error = None
    thumbnail.calls = calls
    thumbnail.image = image
    monkeypatch.setattr(ffmpeg, "thumbnail", thumbnail)
    return thumbnail


def frame_files(storage) -> list:
    return [p for p in stored_files(storage) if p.parent.name == "frame"]


def ready_video(artist, storage, **fields) -> Material:
    key = media.private_storage().save("converted/v.mp4", ContentFile(b"video"))
    values = {
        "kind": MaterialKind.VIDEO, "status": ScanStatus.READY, "storage_key": "video/v.mp4",
        "converted_key": key, "processing_status": ProcessingStatus.DONE,
        "duration_seconds": 10.0, "width": 480, "height": 854,
    }  # fmt: skip
    return Material.objects.create(artist=artist, **{**values, **fields})


def test_ready_video_gets_flags_and_four_frames_spread_over_its_duration(
    artist, storage, fake_thumbnail
):
    video = ready_video(artist, storage, duration_seconds=10.0)
    assert checks.check_material(video.pk) == "checked"
    video.refresh_from_db()
    assert set(video.flags) == {Flag.TOO_SHORT, Flag.VERTICAL, Flag.LOW_RESOLUTION}
    assert video.orientation == "portrait" and video.checks_version == checks.CHECKS_VERSION
    assert fake_thumbnail.calls == [2.0, 4.0, 6.0, 8.0]
    frames = list(video.frames.all())
    assert [f.position_seconds for f in frames] == [2.0, 4.0, 6.0, 8.0]
    for frame in frames:
        assert (frame.width, frame.height, frame.orientation) == (1280, 720, "landscape")
        assert frame.flags == []  # a photo-like 1280x720 frame is a clean candidate
        assert (storage / frame.storage_key).read_bytes()[:3] == b"\xff\xd8\xff"
    assert checks.main_photo_candidates(artist) == frames


def test_frame_flags_like_a_photo_and_duplicates_of_photos(artist, storage, fake_thumbnail):
    frame_image = Image.open(io.BytesIO(fake_thumbnail.image))
    ready_photo(artist, phash=checks.perceptual_hash(frame_image), flags=[])
    video = ready_video(artist, storage)
    checks.check_material(video.pk)
    assert all(Flag.DUPLICATE in f.flags for f in video.frames.all())


def test_a_poster_like_frame_is_not_a_candidate(artist, storage, monkeypatch):
    image = encode(poster_image(1280, 720))
    monkeypatch.setattr(
        ffmpeg, "thumbnail", lambda source, target, *, at_seconds: Path(target).write_bytes(image)
    )
    video = ready_video(artist, storage)
    checks.check_material(video.pk)
    assert all(Flag.POSTER in f.flags for f in video.frames.all())
    assert checks.main_photo_candidates(artist) == []


def test_a_second_run_does_not_duplicate_frames_and_force_replaces_them(
    artist, storage, fake_thumbnail, django_capture_on_commit_callbacks
):
    video = ready_video(artist, storage)
    checks.check_material(video.pk)
    first_keys = {f.storage_key for f in video.frames.all()}
    assert checks.check_material(video.pk) == "current"
    assert video.frames.count() == 4
    with django_capture_on_commit_callbacks(execute=True):
        assert checks.check_material(video.pk, force=True) == "checked"
    assert video.frames.count() == 4
    assert first_keys.isdisjoint({f.storage_key for f in video.frames.all()})
    assert len(frame_files(storage)) == 4  # the old frame files are gone
    assert not any(storage.joinpath(k).exists() for k in first_keys)


def test_ffmpeg_failure_keeps_the_flags_and_leaves_the_version_for_the_backfill(
    artist, storage, fake_thumbnail
):
    fake_thumbnail.error = ffmpeg.FFmpegError("missing", "ffmpeg")
    video = ready_video(artist, storage)
    assert checks.check_material(video.pk) == "checked"
    video.refresh_from_db()
    assert Flag.TOO_SHORT in video.flags and video.checks_version == 0
    assert video.frames.count() == 0
    fake_thumbnail.error = None
    assert checks.backfill() == {"checked": 1, "skipped": 0}
    video.refresh_from_db()
    assert video.checks_version == checks.CHECKS_VERSION and video.frames.count() == 4


def test_video_without_a_duration_gets_flags_but_no_frames(artist, storage, fake_thumbnail):
    video = ready_video(artist, storage, duration_seconds=None)
    checks.check_material(video.pk)
    assert video.frames.count() == 0 and fake_thumbnail.calls == []


def test_pending_video_is_not_checked(artist, storage, fake_thumbnail):
    video = ready_video(artist, storage, status=ScanStatus.PENDING)
    assert checks.check_material(video.pk) == ""


def test_video_deleted_while_frames_are_cut_leaves_no_files(
    artist, storage, monkeypatch, fake_thumbnail, django_capture_on_commit_callbacks
):
    video = ready_video(artist, storage)
    original = checks._make_frames

    def delete_then_return(material, hashes):
        frames = original(material, hashes)
        Material.objects.filter(pk=material.pk).delete()
        return frames

    monkeypatch.setattr(checks, "_make_frames", delete_then_return)
    with django_capture_on_commit_callbacks(execute=True):
        checks.check_material(video.pk)
    assert VideoFrame.objects.count() == 0
    assert frame_files(storage) == []


def test_deleting_the_video_removes_its_frame_files(
    artist, web, storage, fake_thumbnail, django_capture_on_commit_callbacks
):
    video = ready_video(artist, storage)
    checks.check_material(video.pk)
    assert len(frame_files(storage)) == 4
    with django_capture_on_commit_callbacks(execute=True):
        response = web.post(f"/artysta/profil/materialy/{video.pk}/usun/")
    assert response.status_code == 302
    assert VideoFrame.objects.count() == 0
    assert frame_files(storage) == []


def test_deleting_a_frame_removes_that_file_only(
    artist, web, storage, fake_thumbnail, django_capture_on_commit_callbacks
):
    video = ready_video(artist, storage)
    checks.check_material(video.pk)
    frame = video.frames.first()
    with django_capture_on_commit_callbacks(execute=True):
        response = web.post(f"/artysta/profil/materialy/klatki/{frame.pk}/usun/")
    assert response.status_code == 302
    assert video.frames.count() == 3
    assert not (storage / frame.storage_key).exists()
    assert len(frame_files(storage)) == 3


def test_another_artists_frame_is_404_and_get_is_refused(artist, web, storage, fake_thumbnail):
    other = Artist.objects.get(user=make_artist(email="inny@example.invalid"))
    video = ready_video(other, storage)
    checks.check_material(video.pk)
    frame = video.frames.first()
    url = f"/artysta/profil/materialy/klatki/{frame.pk}/usun/"
    assert web.post(url).status_code == 404
    assert web.get(url).status_code == 405
    assert VideoFrame.objects.filter(pk=frame.pk).exists()


def test_list_shows_video_flags_and_frame_candidates_with_their_flags(
    artist, web, storage, fake_thumbnail
):
    video = ready_video(artist, storage)
    checks.check_material(video.pk)
    html = web.get(PAGE).content.decode()
    assert "za krótkie" in html and "pionowe" in html and "niska rozdzielczość" in html
    assert "Film trwa krócej niż 15 s" in html
    assert html.count('data-frame="') == 4
    assert "Usuń klatkę" in html


def test_clean_processing_of_a_video_queues_the_check_job(artist, storage, queue):
    video = Material.objects.create(
        artist=artist, kind=MaterialKind.VIDEO, status=ScanStatus.PENDING,
        processing_status=ProcessingStatus.PENDING, storage_key="video/v.mp4",
    )  # fmt: skip
    outcome = recordings.Outcome(ready=True, duration=20.0, width=1280, height=720)
    assert recordings._record(video.pk, outcome) == ScanStatus.READY
    assert "artists.check_material" in [j["task_name"] for j in queue.jobs.values()]


def test_rejected_processing_does_not_queue_the_check_job(artist, storage, queue):
    video = Material.objects.create(
        artist=artist, kind=MaterialKind.VIDEO, status=ScanStatus.PENDING,
        processing_status=ProcessingStatus.PENDING, storage_key="video/v.mp4",
    )  # fmt: skip
    recordings._record(video.pk, recordings.Outcome(ready=False, message="x"))
    assert "artists.check_material" not in [j["task_name"] for j in queue.jobs.values()]


def test_task_runs_the_checks(artist, storage):
    from apps.artists import tasks

    material = upload(artist, encode(photo_like(1000, 800)))
    materials.scan_material(material.pk)
    tasks.check_material(material.pk)
    material.refresh_from_db()
    assert material.flags == [Flag.LOW_RESOLUTION]


# --- backfill command ------------------------------------------------------------------------


def test_backfill_checks_old_ready_materials_once_and_a_second_run_does_nothing(
    artist, storage, fake_thumbnail, capsys
):
    img = photo_like()
    old = upload(artist, encode(img))
    materials.scan_material(old.pk)
    copy = upload(artist, encode(img))
    materials.scan_material(copy.pk)
    video = ready_video(artist, storage)
    pdf = Material.objects.create(artist=artist, kind=MaterialKind.PDF, status=ScanStatus.READY)

    call_command("check_materials")
    assert "checked: 3, skipped: 0" in capsys.readouterr().out
    old.refresh_from_db(), copy.refresh_from_db(), video.refresh_from_db(), pdf.refresh_from_db()
    assert Flag.DUPLICATE not in old.flags and Flag.DUPLICATE in copy.flags
    assert video.frames.count() == 4 and pdf.checks_version == 0

    call_command("check_materials")
    assert "checked: 0, skipped: 0" in capsys.readouterr().out
    assert video.frames.count() == 4
    assert Material.objects.filter(checks_version=checks.CHECKS_VERSION).count() == 3

    call_command("check_materials", "--force")
    assert "checked: 3" in capsys.readouterr().out
    assert video.frames.count() == 4


def test_backfill_of_an_old_photo_never_guesses_screenshots(artist, storage):
    """Photos from before the checks have no origin data: size rules only."""
    material = upload(artist, encode(photo_like(1920, 1080), "PNG"), name="s.png",
                      content_type="image/png")  # fmt: skip
    Material.objects.filter(pk=material.pk).update(camera_metadata=None, origin_flags=[])
    materials.scan_material(material.pk)
    checks.backfill()
    material.refresh_from_db()
    assert Flag.SCREENSHOT_OR_AI not in material.flags


# --- real ffmpeg (CI) ------------------------------------------------------------------------


@needs_ffmpeg
def test_real_ten_second_vertical_480p_video_flags_and_frames(artist, storage, tmp_path):
    sample = make_sample(tmp_path / "v.mp4", seconds=10, size="480x854")
    probe = ffmpeg.probe(sample)
    key = media.private_storage().save("converted/real.mp4", ContentFile(sample.read_bytes()))
    video = Material.objects.create(
        artist=artist, kind=MaterialKind.VIDEO, status=ScanStatus.READY, storage_key=key,
        converted_key=key, processing_status=ProcessingStatus.DONE,
        duration_seconds=probe.duration, width=probe.width, height=probe.height,
    )  # fmt: skip
    assert checks.check_material(video.pk) == "checked"
    video.refresh_from_db()
    assert set(video.flags) == {Flag.TOO_SHORT, Flag.VERTICAL, Flag.LOW_RESOLUTION}
    frames = list(video.frames.all())
    assert len(frames) == checks.FRAME_COUNT
    for frame in frames:
        assert (frame.width, frame.height) == (480, 854)
        assert Flag.LOW_RESOLUTION in frame.flags
        assert Image.open(storage / frame.storage_key).size == (480, 854)
    assert checks.can_be_main(frames[0])  # low resolution alone does not block
