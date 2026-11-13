import io
import re
import time
import urllib.error
import urllib.request

import pytest
from django.core.files.storage import storages
from PIL import Image

from apps.core import media, uploads
from apps.core.uploads import UploadRejected, sniff_content_type, store_upload


def make_jpeg_with_gps() -> bytes:
    img = Image.new("RGB", (40, 20), "red")
    exif = Image.Exif()
    exif[0x010F] = "TestCam"  # Make
    exif[0x0112] = 1  # Orientation
    gps = exif.get_ifd(0x8825)
    gps[1] = "N"
    gps[2] = (52.0, 13.0, 25.0)
    gps[3] = "E"
    gps[4] = (21.0, 0.0, 30.0)
    out = io.BytesIO()
    img.save(out, "JPEG", exif=exif)
    return out.getvalue()


def read_stored(visibility: str, key: str) -> bytes:
    with storages[visibility].open(key, "rb") as handle:
        return handle.read()


def http_status(url: str) -> int:
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:  # noqa: S310
            return resp.status
    except urllib.error.HTTPError as exc:
        return exc.code


def fetch_status(client, url: str) -> int:
    """Status of GET url: real HTTP for S3, the Django client for the filesystem token view."""
    if url.startswith("http"):
        return http_status(url)
    return client.get(url).status_code


def test_fixture_has_gps_exif():
    exif = Image.open(io.BytesIO(make_jpeg_with_gps())).getexif()
    assert exif.get_ifd(0x8825)


@pytest.mark.parametrize("visibility", ["private", "public"])
def test_jpeg_gps_exif_is_stripped_and_key_is_random(backend, visibility):
    original = make_jpeg_with_gps()
    stored = store_upload(io.BytesIO(original), kind="photo", visibility=visibility)
    again = store_upload(io.BytesIO(original), kind="photo", visibility=visibility)

    data = read_stored(visibility, stored.key)
    img = Image.open(io.BytesIO(data))
    assert img.format == "JPEG"
    assert not img.getexif()
    assert not img.getexif().get_ifd(0x8825)
    assert b"TestCam" not in data
    assert re.fullmatch(r"photo/[A-Za-z0-9_-]{32}\.jpg", stored.key)
    assert stored.key != again.key
    assert stored.content_type == "image/jpeg"


def test_exif_orientation_is_applied_before_stripping(backend):
    img = Image.new("RGB", (40, 20), "blue")
    exif = Image.Exif()
    exif[0x0112] = 6  # rotate 90 CW when displayed
    out = io.BytesIO()
    img.save(out, "JPEG", exif=exif)
    stored = store_upload(io.BytesIO(out.getvalue()), kind="photo", visibility="public")
    result = Image.open(io.BytesIO(read_stored("public", stored.key)))
    assert result.size == (20, 40)
    assert not result.getexif()


def test_html_renamed_to_jpg_is_rejected(backend):
    html = b"<html><script>alert(1)</script></html>"
    fake = io.BytesIO(html)
    fake.name = "holiday.jpg"
    with pytest.raises(UploadRejected) as err:
        store_upload(fake, kind="photo", visibility="public")
    assert err.value.code == "bad_type"


def test_wrong_kind_is_rejected(backend):
    pdf = io.BytesIO(b"%PDF-1.7\n%...")
    with pytest.raises(UploadRejected) as err:
        store_upload(pdf, kind="photo", visibility="private")
    assert err.value.code == "bad_type"


def test_pdf_is_stored_as_is(backend):
    body = b"%PDF-1.7\n" + b"x" * 100
    stored = store_upload(io.BytesIO(body), kind="pdf", visibility="private")
    assert read_stored("private", stored.key) == body
    assert stored.key.endswith(".pdf")


def test_empty_and_corrupt_images_are_rejected(backend):
    with pytest.raises(UploadRejected) as err:
        store_upload(io.BytesIO(b""), kind="photo", visibility="public")
    assert err.value.code == "empty"
    with pytest.raises(UploadRejected) as err:
        store_upload(
            io.BytesIO(b"\xff\xd8\xff" + b"garbage" * 10), kind="photo", visibility="public"
        )
    assert err.value.code == "corrupt_image"


@pytest.mark.parametrize(
    ("kind", "limit_mb", "head"),
    [
        ("photo", 15, b"\xff\xd8\xff\xe0"),
        ("video", 500, b"\x00\x00\x00\x18ftypmp42"),
        ("audio", 50, b"ID3\x04"),
        ("pdf", 20, b"%PDF-1.7"),
    ],
)
def test_size_limits_per_kind(kind, limit_mb, head):
    class Sized:
        """Reports a huge size without allocating it."""

        def __init__(self, size):
            self.size, self.pos = size, 0

        def seek(self, offset, whence=0):
            self.pos = self.size if whence == io.SEEK_END else offset
            return self.pos

        def tell(self):
            return self.pos

        def read(self, n=-1):
            return head[:n]

    limit = limit_mb * 1024 * 1024
    with pytest.raises(UploadRejected) as err:
        store_upload(Sized(limit + 1), kind=kind, visibility="private")
    assert err.value.code == "too_large"
    assert uploads.KINDS[kind][0] == limit


@pytest.mark.parametrize(
    ("head", "expected"),
    [
        (b"\xff\xd8\xff\xe0", "image/jpeg"),
        (b"\x89PNG\r\n\x1a\n", "image/png"),
        (b"RIFF\x00\x00\x00\x00WEBPVP8 ", "image/webp"),
        (b"RIFF\x00\x00\x00\x00WAVEfmt ", "audio/wav"),
        (b"\x00\x00\x00\x18ftypM4A ", "audio/mp4"),
        (b"\x00\x00\x00\x18ftypisom", "video/mp4"),
        (b"\x1a\x45\xdf\xa3\x01", "video/webm"),
        (b"OggS\x00", "audio/ogg"),
        (b"ID3\x03", "audio/mpeg"),
        (b"\xff\xfb\x90\x00", "audio/mpeg"),
        (b"<html>", None),
        (b"", None),
    ],
)
def test_sniffing(head, expected):
    assert sniff_content_type(head) == expected


def test_unknown_kind_or_visibility():
    with pytest.raises(ValueError):
        store_upload(io.BytesIO(b"x"), kind="exe", visibility="public")
    with pytest.raises(ValueError):
        store_upload(io.BytesIO(b"x"), kind="pdf", visibility="world")


def test_public_url_is_on_the_media_origin(backend, settings):
    stored = store_upload(io.BytesIO(make_jpeg_with_gps()), kind="photo", visibility="public")
    url = media.public_url(stored.key)
    assert url == settings.MEDIA_PUBLIC_BASE_URL + stored.key
    if backend == "s3":
        assert http_status(url) == 200  # anonymous read of the public bucket
    assert url.startswith("http://") and "/media/private" not in url


def test_private_file_is_reachable_through_signed_url(backend, client):
    body = b"%PDF-1.7\nsecret"
    stored = store_upload(io.BytesIO(body), kind="pdf", visibility="private")
    url = media.signed_url(stored.key)
    assert fetch_status(client, url) == 200
    if backend == "filesystem":
        resp = client.get(url)
        assert b"".join(resp.streaming_content) == body
        assert resp["Content-Disposition"].startswith("attachment")
        assert resp["X-Content-Type-Options"] == "nosniff"


def test_private_file_has_no_unsigned_access(backend, client):
    stored = store_upload(io.BytesIO(b"%PDF-1.7\nsecret"), kind="pdf", visibility="private")
    if backend == "s3":
        bare = f"{media.signed_url(stored.key).split('?')[0]}"
        assert http_status(bare) in (400, 403)
    else:
        assert client.get(f"/media/private/{stored.key}").status_code == 404
        assert client.get("/media/private/forged-token").status_code == 404


def test_expired_signed_url_is_denied(backend, client, monkeypatch):
    stored = store_upload(io.BytesIO(b"%PDF-1.7\nsecret"), kind="pdf", visibility="private")
    url = media.signed_url(stored.key, expires=1)
    assert fetch_status(client, url) == 200
    if backend == "s3":
        time.sleep(3)  # real clock: MinIO enforces the expiry
    else:
        real = time.time
        monkeypatch.setattr(time, "time", lambda: real() + 3)
    assert fetch_status(client, url) in (403, 404)


def test_tampered_token_is_denied(backend, client):
    if backend == "s3":
        pytest.skip("filesystem tokens only")
    stored = store_upload(io.BytesIO(b"%PDF-1.7\nsecret"), kind="pdf", visibility="private")
    url = media.signed_url(stored.key)
    assert client.get(url[:-3] + "xyz").status_code == 404
    with pytest.raises(media.SignedURLInvalid):
        media.resolve_token("not-a-token")
