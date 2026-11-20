"""Origin of an image read from the original bytes (US-2.4, D59): camera data, stock and AI
markers in the metadata only, JPEG quality estimate. Images are generated here."""

import io
import struct

import pytest
from django.core.files.storage import storages
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image

from apps.core import imagemeta, uploads
from apps.core.imagemeta import ImageOrigin, read_origin


def photo_like(width=400, height=300) -> Image.Image:
    """Smooth coloured blobs: compresses like a photo, not like a flat graphic."""
    noise = Image.effect_noise((width // 10, height // 10), 90).convert("RGB")
    return noise.resize((width, height), Image.Resampling.BICUBIC)


def jpeg_bytes(img=None, *, quality=90, **kwargs) -> bytes:
    out = io.BytesIO()
    (img or photo_like()).save(out, "JPEG", quality=quality, **kwargs)
    return out.getvalue()


def exif_with(**tags) -> Image.Exif:
    exif = Image.Exif()
    for tag, value in tags.items():
        exif[int(tag.removeprefix("t"), 16)] = value
    return exif


def xmp(body: str) -> bytes:
    return (
        '<x:xmpmeta xmlns:x="adobe:ns:meta/"><rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/'
        f'22-rdf-syntax-ns#"><rdf:Description>{body}</rdf:Description></rdf:RDF></x:xmpmeta>'
    ).encode()


def test_plain_jpeg_has_no_markers_and_a_quality():
    origin = read_origin(jpeg_bytes(quality=90))
    assert origin.camera is False and origin.stock is False and origin.ai is False
    assert 85 <= origin.jpeg_quality <= 95


@pytest.mark.parametrize("quality", [20, 40, 60, 75, 90])
def test_quality_estimate_is_close_to_the_saved_quality(quality):
    assert abs(read_origin(jpeg_bytes(quality=quality)).jpeg_quality - quality) <= 3


def test_quality_100_is_high_and_missing_tables_give_none():
    assert read_origin(jpeg_bytes(quality=100)).jpeg_quality >= 95
    assert imagemeta.estimate_jpeg_quality({}) is None
    assert imagemeta.estimate_jpeg_quality({0: [1, 2, 3]}) is None


def test_png_and_webp_have_no_jpeg_quality():
    for fmt in ("PNG", "WEBP"):
        out = io.BytesIO()
        photo_like(64, 64).save(out, fmt)
        assert read_origin(out.getvalue()).jpeg_quality is None


def test_camera_make_or_model_in_exif_means_camera_data():
    with_make = jpeg_bytes(exif=exif_with(t010F="Canon"))
    with_model = jpeg_bytes(exif=exif_with(t0110="Pixel 8"))
    only_software = jpeg_bytes(exif=exif_with(t0131="Editor 1.0"))
    assert read_origin(with_make).camera and read_origin(with_model).camera
    assert not read_origin(only_software).camera


@pytest.mark.parametrize(
    "credit",
    ["Shutterstock", "Getty Images", "iStock by Getty", "Adobe Stock", "Depositphotos", "Alamy"],
)
def test_stock_agency_in_exif_copyright_or_xmp(credit):
    in_exif = jpeg_bytes(exif=exif_with(t8298=f"© {credit}"))
    in_xmp = jpeg_bytes(xmp=xmp(f"<photoshop:Credit>{credit}</photoshop:Credit>"))
    assert read_origin(in_exif).stock
    assert read_origin(in_xmp).stock


def test_stock_word_in_pixels_or_unrelated_metadata_is_not_a_marker():
    assert not read_origin(jpeg_bytes(exif=exif_with(t010F="Canon"))).stock
    assert not read_origin(jpeg_bytes(xmp=xmp("<dc:title>Występ w szkole</dc:title>"))).stock


@pytest.mark.parametrize(
    "body",
    [
        "<Iptc4xmpExt:DigitalSourceType>http://cv.iptc.org/newscodes/digitalsourcetype/"
        "trainedAlgorithmicMedia</Iptc4xmpExt:DigitalSourceType>",
        "<xmp:CreatorTool>Midjourney</xmp:CreatorTool>",
        "<xmp:CreatorTool>Stable Diffusion 1.5</xmp:CreatorTool>",
        "<xmp:CreatorTool>Adobe Firefly</xmp:CreatorTool>",
    ],
)
def test_ai_markers_in_xmp(body):
    assert read_origin(jpeg_bytes(xmp=xmp(body))).ai


def test_ai_generator_in_exif_software():
    assert read_origin(jpeg_bytes(exif=exif_with(t0131="DALL-E 3"))).ai


def test_c2pa_alone_is_not_ai_but_with_the_ai_source_type_it_is():
    def with_app11(payload: bytes) -> bytes:
        data = jpeg_bytes()
        segment = b"\xff\xeb" + struct.pack(">H", len(payload) + 2) + payload
        return data[:2] + segment + data[2:]

    signed_camera = with_app11(b"JP\x00\x00jumbc2pa" + b"c2pa.created" * 4)
    generated = with_app11(b"JP\x00\x00jumbc2pa" + b"trainedAlgorithmicMedia")
    assert not read_origin(signed_camera).ai
    assert read_origin(generated).ai


def test_png_text_chunk_markers():
    out = io.BytesIO()
    img = photo_like(64, 64)
    from PIL.PngImagePlugin import PngInfo

    info = PngInfo()
    info.add_text("Software", "ComfyUI")
    info.add_text("Credit", "Shutterstock")
    img.save(out, "PNG", pnginfo=info)
    origin = read_origin(out.getvalue())
    assert origin.ai and origin.stock


def test_webp_xmp_chunk_marker():
    out = io.BytesIO()
    photo_like(64, 64).save(out, "WEBP", xmp=xmp("<xmp:CreatorTool>Midjourney</xmp:CreatorTool>"))
    assert read_origin(out.getvalue()).ai


def test_garbage_and_truncated_files_never_raise():
    assert read_origin(b"") == ImageOrigin()
    assert read_origin(b"not an image at all") == ImageOrigin()
    assert read_origin(jpeg_bytes()[:30]).stock is False
    assert imagemeta.metadata_bytes(b"\xff\xd8\xff\xe1\xff") == b""
    assert imagemeta.metadata_bytes(b"\x89PNG\r\n\x1a\n\x00\x00") == b""


@pytest.fixture
def private(settings, tmp_path):
    from config.settings.storage import build_storages

    settings.STORAGE_BACKEND = "filesystem"
    settings.STORAGES = build_storages(
        "filesystem",
        public_base_url="http://media.test:8101/",
        private_root=tmp_path / "private",
        public_root=tmp_path / "public",
        signed_url_ttl=settings.MEDIA_SIGNED_URL_TTL,
    )
    return storages["private"]


def test_store_upload_returns_the_origin_and_the_stored_file_has_no_metadata(private):
    data = jpeg_bytes(exif=exif_with(t010F="Canon", t8298="Getty Images"), quality=30)
    stored = uploads.store_upload(
        SimpleUploadedFile("a.jpg", data, content_type="image/jpeg"),
        kind="photo",
        visibility="private",
    )
    assert stored.origin.camera and stored.origin.stock and stored.origin.jpeg_quality < 40
    with private.open(stored.key, "rb") as handle:
        saved = handle.read()
    assert b"getty" not in saved.lower() and not Image.open(io.BytesIO(saved)).getexif()


def test_non_images_have_no_origin(private):
    pdf = b"%PDF-1.4\n" + b"x" * 100
    stored = uploads.store_upload(
        SimpleUploadedFile("a.pdf", pdf, content_type="application/pdf"),
        kind="pdf",
        visibility="private",
    )
    assert stored.origin is None
