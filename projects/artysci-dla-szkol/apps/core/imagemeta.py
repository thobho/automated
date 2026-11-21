"""What an uploaded image's own metadata says, read from the ORIGINAL bytes before they are
stripped (US-2.4, D59). Local only: no AI and no external service.

`read_origin()` returns a small `ImageOrigin` (camera data present, stock or AI markers found,
estimated JPEG quality). Nothing else is kept: the raw metadata is dropped with the stripped
original, only the artist-facing flags derived from this result are stored (`apps.artists.checks`).

Markers are searched in the metadata segments only (JPEG APPn segments, PNG text / EXIF / C2PA
chunks, WebP EXIF / XMP / C2PA chunks), never in pixel data. A C2PA manifest alone does not mean
AI (cameras sign photos too); it counts only with the IPTC `trainedAlgorithmicMedia` source type
or a generator name inside it.
"""

import io
import struct
from dataclasses import dataclass

from PIL import Image

# Lower-case byte patterns. Stock: agency names in IPTC / XMP credit and rights fields.
STOCK_MARKERS = (
    b"shutterstock",
    b"getty images",
    b"gettyimages",
    b"istockphoto",
    b"istock by getty",
    b"adobe stock",
    b"depositphotos",
    b"alamy",
    b"dreamstime",
    b"123rf",
    b"bigstockphoto",
    b"stocksy",
    b"pond5",
    b"fotolia",
    b"canstockphoto",
    b"agefotostock",
)
# AI generation: IPTC digital source types and generator names (software / credit fields).
AI_MARKERS = (
    b"trainedalgorithmicmedia",
    b"compositewithtrainedalgorithmicmedia",
    b"midjourney",
    b"dall-e",
    b"dall\xc2\xb7e",
    b"stable diffusion",
    b"stablediffusion",
    b"adobe firefly",
    b"openai",
    b"leonardo.ai",
    b"comfyui",
    b"automatic1111",
    b"made with google ai",
)

MAX_METADATA_BYTES = 4 * 1024 * 1024  # metadata scanned per image
CAMERA_TAGS = (0x010F, 0x0110)  # EXIF Make, Model

# Standard IJG luminance quantisation table (quality 50); Pillow gives tables in zigzag order.
_STD_LUMA = (
    16, 11, 12, 14, 12, 10, 16, 14, 13, 14, 18, 17, 16, 19, 24, 40,
    26, 24, 22, 22, 24, 49, 35, 37, 29, 40, 58, 51, 61, 60, 57, 51,
    56, 55, 64, 72, 92, 78, 64, 68, 87, 69, 55, 56, 80, 109, 81, 87,
    95, 98, 103, 104, 103, 62, 77, 113, 121, 112, 100, 120, 92, 101, 103, 99,
)  # fmt: skip


@dataclass(frozen=True)
class ImageOrigin:
    """What the original file said about itself. `jpeg_quality` is None for non-JPEG files."""

    camera: bool = False
    stock: bool = False
    ai: bool = False
    jpeg_quality: int | None = None


def estimate_jpeg_quality(tables: dict) -> int | None:
    """IJG quality (1-100) estimated from the luminance quantisation table, None if absent.

    Tables built by the IJG formula scale the standard table, so the ratio of the mean values
    gives the scale factor. Near quality 100 the entries clamp to 1, so the estimate there is
    approximate (always high), which is all the check needs.
    """
    table = tables.get(0) if tables else None
    if not table or len(table) != 64:
        return None
    scale = (sum(table) / sum(_STD_LUMA)) * 100
    quality = (200 - scale) / 2 if scale <= 100 else 5000 / scale
    return max(1, min(100, round(quality)))


def _jpeg_segments(data: bytes):
    pos = 2
    while pos + 4 <= len(data) and data[pos] == 0xFF:
        marker = data[pos + 1]
        if marker == 0xFF:  # fill byte
            pos += 1
            continue
        if marker == 0xDA or marker == 0xD9:  # start of scan / end: metadata is before
            return
        if 0xD0 <= marker <= 0xD8 or marker == 0x01:  # markers without a length
            pos += 2
            continue
        (length,) = struct.unpack(">H", data[pos + 2 : pos + 4])
        if length < 2:
            return
        if 0xE0 <= marker <= 0xEF or marker == 0xFE:  # APPn and comments
            yield data[pos + 4 : pos + 2 + length]
        pos += 2 + length


def _png_chunks(data: bytes):
    pos = 8
    while pos + 8 <= len(data):
        (length,) = struct.unpack(">I", data[pos : pos + 4])
        kind = data[pos + 4 : pos + 8]
        if kind in (b"tEXt", b"iTXt", b"eXIf", b"caBX"):
            yield data[pos + 8 : pos + 8 + length]
        if kind == b"IEND":
            return
        pos += 12 + length


def _webp_chunks(data: bytes):
    pos = 12
    while pos + 8 <= len(data):
        kind = data[pos : pos + 4]
        (length,) = struct.unpack("<I", data[pos + 4 : pos + 8])
        if kind in (b"EXIF", b"XMP ", b"C2PA"):
            yield data[pos + 8 : pos + 8 + length]
        pos += 8 + length + (length & 1)


def metadata_bytes(data: bytes) -> bytes:
    """The metadata segments of a JPEG, PNG or WebP file, lower-cased and capped. Truncated or
    odd files give what could be read."""
    try:
        if data.startswith(b"\xff\xd8"):
            parts = _jpeg_segments(data)
        elif data.startswith(b"\x89PNG"):
            parts = _png_chunks(data)
        elif data[:4] == b"RIFF" and data[8:12] == b"WEBP":
            parts = _webp_chunks(data)
        else:
            return b""
        out, size = [], 0
        for part in parts:
            out.append(part)
            size += len(part)
            if size >= MAX_METADATA_BYTES:
                break
    except (struct.error, ValueError):
        return b""
    return b"\n".join(out).lower()[:MAX_METADATA_BYTES]


def read_origin(data: bytes) -> ImageOrigin:
    """Origin of the image in `data` (the original upload). Never raises for a bad file."""
    blob = metadata_bytes(data)
    stock = any(marker in blob for marker in STOCK_MARKERS)
    ai = any(marker in blob for marker in AI_MARKERS)
    camera, quality = False, None
    try:
        with Image.open(io.BytesIO(data)) as img:
            exif = img.getexif()
            camera = any(exif.get(tag) for tag in CAMERA_TAGS)
            if img.format == "JPEG":
                quality = estimate_jpeg_quality(getattr(img, "quantization", None) or {})
    except (OSError, ValueError, SyntaxError, Image.DecompressionBombError):
        pass
    return ImageOrigin(camera=camera, stock=stock, ai=ai, jpeg_quality=quality)
