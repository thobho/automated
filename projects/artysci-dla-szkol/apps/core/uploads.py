"""Upload helper: validate, sanitise and store a user file under a random key.

- Size limit per kind (D8): photo 15 MB, video 500 MB, audio 50 MB, PDF 20 MB.
- The content type comes from the file's magic bytes, never from the name or the browser.
- Object keys are random; the extension is derived from the sniffed type, not from the name.
- Images are re-encoded without metadata (EXIF/GPS stripped, orientation applied first).
"""

import io
import secrets
from dataclasses import dataclass
from typing import BinaryIO

from django.core.files.base import ContentFile, File
from django.core.files.storage import storages
from django.utils.translation import gettext_lazy as _
from PIL import Image, ImageOps, UnidentifiedImageError

MB = 1024 * 1024

# kind -> (max bytes, allowed sniffed content types)
KINDS: dict[str, tuple[int, frozenset[str]]] = {
    "photo": (15 * MB, frozenset({"image/jpeg", "image/png", "image/webp"})),
    "video": (500 * MB, frozenset({"video/mp4", "video/webm"})),
    "audio": (50 * MB, frozenset({"audio/mpeg", "audio/ogg", "audio/wav", "audio/mp4"})),
    "pdf": (20 * MB, frozenset({"application/pdf"})),
}

EXTENSIONS = {
    "image/jpeg": "jpg",
    "image/png": "png",
    "image/webp": "webp",
    "video/mp4": "mp4",
    "video/webm": "webm",
    "audio/mpeg": "mp3",
    "audio/ogg": "ogg",
    "audio/wav": "wav",
    "audio/mp4": "m4a",
    "application/pdf": "pdf",
}

PILLOW_FORMATS = {"image/jpeg": "JPEG", "image/png": "PNG", "image/webp": "WEBP"}
HEAD_BYTES = 64


class UploadRejected(Exception):
    """The file is not acceptable. `code` is stable, `message` is shown to the user (Polish)."""

    def __init__(self, code: str, message):
        super().__init__(code)
        self.code = code
        self.message = message


@dataclass(frozen=True)
class StoredFile:
    key: str
    content_type: str
    size: int
    visibility: str  # "private" or "public"


def sniff_content_type(head: bytes) -> str | None:
    """Content type from the first bytes of a file, or None when not recognised."""
    if head.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    if head.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if head[:4] == b"RIFF" and head[8:12] == b"WEBP":
        return "image/webp"
    if head[:4] == b"RIFF" and head[8:12] == b"WAVE":
        return "audio/wav"
    if head.startswith(b"%PDF-"):
        return "application/pdf"
    if head[4:8] == b"ftyp":
        return "audio/mp4" if head[8:12] in (b"M4A ", b"M4B ") else "video/mp4"
    if head.startswith(b"\x1a\x45\xdf\xa3"):
        return "video/webm"
    if head.startswith(b"OggS"):
        return "audio/ogg"
    if head.startswith(b"ID3") or (len(head) > 1 and head[0] == 0xFF and head[1] & 0xE0 == 0xE0):
        return "audio/mpeg"
    return None


def _size_of(file: BinaryIO) -> int:
    file.seek(0, io.SEEK_END)
    size = file.tell()
    file.seek(0)
    return size


def strip_image_metadata(data: bytes, content_type: str) -> bytes:
    """Re-encode an image without EXIF/XMP/ICC metadata, applying the EXIF orientation first."""
    try:
        with Image.open(io.BytesIO(data)) as img:
            img.load()
            img = ImageOps.exif_transpose(img)
            out = io.BytesIO()
            fmt = PILLOW_FORMATS[content_type]
            # Passing no exif/icc_profile/info keeps the output free of metadata.
            if fmt == "JPEG":
                img.convert("RGB").save(out, fmt, quality=90, optimize=True)
            else:
                img.save(out, fmt)
            return out.getvalue()
    except (UnidentifiedImageError, Image.DecompressionBombError, OSError, SyntaxError) as exc:
        raise UploadRejected("corrupt_image", _("Nie można odczytać zdjęcia.")) from exc


def store_upload(file: BinaryIO, *, kind: str, visibility: str) -> StoredFile:
    """Validate `file` as `kind` and store it in the `visibility` storage ("private"/"public").

    Raises UploadRejected. The returned key is random and safe to persist.
    """
    if kind not in KINDS:
        raise ValueError(f"Unknown upload kind {kind!r}")
    if visibility not in ("private", "public"):
        raise ValueError(f"Unknown visibility {visibility!r}")
    max_bytes, allowed = KINDS[kind]

    size = _size_of(file)
    if size == 0:
        raise UploadRejected("empty", _("Plik jest pusty."))
    if size > max_bytes:
        raise UploadRejected(
            "too_large", _("Plik jest za duży (maksymalnie %(mb)d MB).") % {"mb": max_bytes // MB}
        )

    content_type = sniff_content_type(file.read(HEAD_BYTES))
    file.seek(0)
    if content_type is None or content_type not in allowed:
        raise UploadRejected("bad_type", _("Ten typ pliku nie jest dozwolony."))

    if content_type in PILLOW_FORMATS:
        data = strip_image_metadata(file.read(), content_type)
        payload: File = ContentFile(data)
        size = len(data)
    else:
        payload = File(file)

    key = f"{kind}/{secrets.token_urlsafe(24)}.{EXTENSIONS[content_type]}"
    saved = storages[visibility].save(key, payload)
    return StoredFile(key=saved, content_type=content_type, size=size, visibility=visibility)
