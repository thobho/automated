"""Artist materials (US-2.3A/B, D8, D62): photos, PDFs, YouTube/Vimeo links, video and audio
files, the malware scan and PDF text extraction jobs, and the school questionnaire.

Files go through the T06 upload path (`store_upload`, private storage: sniffed type, size limit,
EXIF stripped, random key). Each new file is a `Material` in ``pending`` and a scan job on the
``media`` queue: clean -> ``ready`` (a PDF then gets a text extraction job), infected -> the file
is deleted and the material is ``rejected``, scanner error -> the job retries and the material
stays ``pending``. Only ``ready`` materials count (`ready_materials`, used by US-2.5a).
Video and audio arrive through resumable uploads (`resumable.py`); after a clean scan they stay
``pending`` until the ffprobe/ffmpeg job (`recordings.py`) makes them ``ready`` or ``rejected``.

Links are checked against the fixed public oEmbed endpoints of YouTube and Vimeo only; any other
host is refused before a request is made. Log lines carry a pseudonymised user and ids only.
"""

import json
import logging
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass

from django.conf import settings
from django.db import transaction
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.core import jobs, media, scanning, uploads
from apps.core.logs import pseudonymise_user
from apps.core.scanning import ScanResult

from .models import (
    MAX_AGE,
    Artist,
    Material,
    MaterialKind,
    Offer,
    ProcessingStatus,
    ScanStatus,
    TextStatus,
    VideoProvider,
)

logger = logging.getLogger("apps.artists.materials")

FILE_KINDS = (MaterialKind.PHOTO, MaterialKind.PDF)
AV_KINDS = (MaterialKind.VIDEO, MaterialKind.AUDIO)


class MaterialRejected(Exception):
    """A material cannot be added. `message` is shown to the artist (Polish)."""

    def __init__(self, code: str, message):
        super().__init__(code)
        self.code = code
        self.message = message


class ScanNotFinished(Exception):
    """The scanner answered ERROR: the job raises this so Procrastinate retries it."""


def _log(event: str, artist_or_user_id, material_id=None, *, level=logging.INFO, **extra):
    user_id = getattr(artist_or_user_id, "user_id", artist_or_user_id)
    logger.log(
        level,
        event.replace("_", " "),
        extra={
            "event": event,
            "user": pseudonymise_user(user_id),
            "material": material_id,
            **extra,
        },
    )


# --- listing and limits ----------------------------------------------------------------------


def limit_for(kind: str) -> int:
    return {
        MaterialKind.PHOTO: settings.MATERIAL_MAX_PHOTOS,
        MaterialKind.PDF: settings.MATERIAL_MAX_PDFS,
        MaterialKind.VIDEO: settings.MATERIAL_MAX_VIDEOS,
        MaterialKind.AUDIO: settings.MATERIAL_MAX_AUDIO,
    }[kind]


def materials_for(artist: Artist):
    return Material.objects.filter(artist=artist).order_by("created_at", "pk")


def ready_materials(artist: Artist | None):
    """Materials that count: scanned clean (files) or checked links."""
    return Material.objects.filter(artist=artist, status=ScanStatus.READY)


def has_ready_materials(artist: Artist | None) -> bool:
    return artist is not None and ready_materials(artist).exists()


def _counted(artist: Artist, kind: str):
    """Materials that use up the limit: everything not rejected (a rejected file is gone)."""
    return Material.objects.filter(artist=artist, kind=kind).exclude(status=ScanStatus.REJECTED)


def remaining(artist: Artist, kind: str) -> int:
    return max(0, limit_for(kind) - _counted(artist, kind).count())


LIMIT_MESSAGES = {
    MaterialKind.PHOTO: _("Osiągnięto limit %(n)d zdjęć. Usuń któreś, aby dodać nowe."),
    MaterialKind.PDF: _("Osiągnięto limit %(n)d plików PDF. Usuń któryś, aby dodać nowy."),
    MaterialKind.VIDEO: _("Osiągnięto limit %(n)d filmów. Usuń któryś, aby dodać nowy."),
    MaterialKind.AUDIO: _("Osiągnięto limit %(n)d nagrań. Usuń któreś, aby dodać nowe."),
}


def limit_error(kind: str) -> MaterialRejected:
    return MaterialRejected("limit", LIMIT_MESSAGES[kind] % {"n": limit_for(kind)})


def is_full(artist: Artist, kind: str) -> bool:
    """The limit is used up. Call under the artist row lock to settle parallel uploads."""
    return _counted(artist, kind).count() >= limit_for(kind)


def check_room(artist: Artist, kind: str, count: int) -> None:
    """Raise `MaterialRejected` if `count` more files of `kind` do not fit the limit."""
    if count > remaining(artist, kind):
        raise limit_error(kind)


def get_material(artist: Artist, material_id) -> Material:
    """The artist's own material; `Material.DoesNotExist` for another artist's or a missing id."""
    return Material.objects.get(artist=artist, pk=material_id)


def file_url(material: Material) -> str:
    """Short-lived signed URL of a stored file ("" for links and deleted files). A converted
    video links to its MP4."""
    key = material.converted_key or material.storage_key
    return media.signed_url(key) if key else ""


def thumbnail_url(material: Material) -> str:
    return media.signed_url(material.thumbnail_key) if material.thumbnail_key else ""


def format_duration(seconds: float | None) -> str:
    """Duration for the list: "m:ss" ("" when unknown)."""
    if seconds is None:
        return ""
    total = round(seconds)
    return f"{total // 60}:{total % 60:02d}"


# --- files -----------------------------------------------------------------------------------


def delete_files(keys) -> None:
    for key in keys:
        _delete_file(key)


def _delete_file(key: str) -> None:
    if not key:
        return
    try:
        media.private_storage().delete(key)
    except Exception:  # storage down: the row change stands, the orphan is only logged
        logger.warning("material file could not be deleted", extra={"event": "material_orphan"})


def clean_name(name: str) -> str:
    """A file name safe to store and show: last path part, printable, at most 200 chars."""
    name = (name or "").replace("\\", "/").rsplit("/", 1)[-1]
    return "".join(ch for ch in name if ch.isprintable())[:200]


def add_file(artist: Artist, kind: str, file) -> Material:
    """Store one photo or PDF as a pending material and queue its scan.

    Raises `MaterialRejected` (limit reached) or `UploadRejected` (size, type, unreadable
    image); nothing is stored in either case.
    """
    if kind not in FILE_KINDS:
        raise ValueError(f"not a file kind: {kind!r}")
    check_room(artist, kind, 1)  # before storing anything
    stored = uploads.store_upload(file, kind=kind, visibility="private")
    try:
        with transaction.atomic():
            Artist.objects.select_for_update().filter(pk=artist.pk).first()
            if is_full(artist, kind):  # a parallel upload won
                raise limit_error(kind)
            material = Material.objects.create(
                artist=artist,
                kind=kind,
                status=ScanStatus.PENDING,
                storage_key=stored.key,
                content_type=stored.content_type,
                size=stored.size,
                original_name=clean_name(getattr(file, "name", "")),
            )
            _enqueue_scan(material)
    except Exception:
        _delete_file(stored.key)
        raise
    _log("material_uploaded", artist, material.pk)
    return material


def _enqueue_scan(material: Material) -> None:
    from . import tasks  # tasks import this module

    jobs.enqueue(
        tasks.scan_material,
        idempotency_key=f"artists.scan_material:{material.pk}",
        material_id=material.pk,
    )


def delete_material(artist: Artist, material_id) -> None:
    """Delete the artist's own material and, after the commit, its file. Raises
    `Material.DoesNotExist`."""
    with transaction.atomic():
        material = Material.objects.select_for_update().get(artist=artist, pk=material_id)
        keys = material.stored_keys()  # original, converted MP4, thumbnail
        material.delete()
        if keys:
            transaction.on_commit(lambda: delete_files(keys))
    _log("material_deleted", artist, material_id)


# --- malware scan (job on the media queue) ---------------------------------------------------


def scan_material(material_id: int) -> str:
    """Scan a pending material's file and record the verdict. Returns the new status.

    Raises `ScanNotFinished` on a scanner error (the job retries; the material stays pending).
    Safe to run twice: a material that is no longer pending is left alone.
    """
    material = Material.objects.filter(pk=material_id).first()
    if material is None or material.status != ScanStatus.PENDING or not material.storage_key:
        return material.status if material else ""
    result = scanning.scan_stored(media.private_storage(), material.storage_key)
    if result == ScanResult.ERROR:
        _log("material_scan_error", material.artist.user_id, material.pk, level=logging.WARNING)
        raise ScanNotFinished(material_id)
    with transaction.atomic():
        material = Material.objects.select_for_update().filter(pk=material_id).first()
        if material is None or material.status != ScanStatus.PENDING:
            return material.status if material else ""
        material.scanned_at = timezone.now()
        if result == ScanResult.CLEAN and material.kind in AV_KINDS:
            # still pending: ready only after ffprobe (and the conversion for a video)
            material.processing_status = ProcessingStatus.PENDING
            _enqueue_processing(material)
            material.save(update_fields=["scanned_at", "processing_status"])
        elif result == ScanResult.CLEAN:
            material.status = ScanStatus.READY
            if material.kind == MaterialKind.PDF:
                material.text_status = TextStatus.PENDING
                _enqueue_extraction(material)
            material.save(update_fields=["status", "scanned_at", "text_status"])
        else:  # INFECTED: the file goes, the row stays so the artist sees why
            key = material.storage_key
            material.status = ScanStatus.REJECTED
            material.storage_key = ""
            material.save(update_fields=["status", "scanned_at", "storage_key"])
            transaction.on_commit(lambda: _delete_file(key))
    _log(f"material_scan_{result}", material.artist.user_id, material.pk)
    return material.status


def _enqueue_processing(material: Material) -> None:
    from . import tasks

    jobs.enqueue(
        tasks.process_media,
        idempotency_key=f"artists.process_media:{material.pk}",
        material_id=material.pk,
    )


def _enqueue_extraction(material: Material) -> None:
    from . import tasks

    jobs.enqueue(
        tasks.extract_pdf_text,
        idempotency_key=f"artists.extract_pdf_text:{material.pk}",
        material_id=material.pk,
    )


def scan_poster(offer_id: int, key: str) -> str:
    """Scan an offer poster (the same scanner as materials). `key` is the poster the job was
    queued for: a poster replaced in the meantime is not touched. Returns the poster status.
    Raises `ScanNotFinished` on a scanner error."""
    offer = Offer.objects.filter(pk=offer_id, poster_key=key).first()
    if offer is None or offer.poster_status != ScanStatus.PENDING:
        return offer.poster_status if offer else ""
    result = scanning.scan_stored(media.private_storage(), key)
    if result == ScanResult.ERROR:
        raise ScanNotFinished(offer_id)
    with transaction.atomic():
        offer = Offer.objects.select_for_update().filter(pk=offer_id, poster_key=key).first()
        if offer is None or offer.poster_status != ScanStatus.PENDING:
            return offer.poster_status if offer else ""
        if result == ScanResult.CLEAN:
            offer.poster_status = ScanStatus.READY
        else:
            offer.poster_status = ScanStatus.REJECTED
            offer.poster_key = ""
            transaction.on_commit(lambda: _delete_file(key))
        offer.save(update_fields=["poster_status", "poster_key"])
    logger.info(
        "offer poster scanned %s",
        result,
        extra={"event": f"poster_scan_{result}", "offer": offer_id},
    )
    return offer.poster_status


def enqueue_poster_scan(offer_id: int, key: str) -> None:
    from . import tasks

    jobs.enqueue(
        tasks.scan_poster,
        idempotency_key=f"artists.scan_poster:{offer_id}:{key}",
        offer_id=offer_id,
        key=key,
    )


# --- PDF text (job on the media queue, after a clean scan) -----------------------------------


@dataclass(frozen=True)
class Extracted:
    text: str
    status: str


def extract_text(file, *, max_pages: int, max_chars: int, max_seconds: float) -> Extracted:
    """Text of a PDF within the limits. Never raises for a bad PDF: encrypted and broken files
    end as a status. The time limit is checked between pages."""
    from pypdf import PdfReader
    from pypdf.errors import PyPdfError

    try:
        reader = PdfReader(file)
        if reader.is_encrypted:
            return Extracted("", TextStatus.ENCRYPTED)
        started = time.monotonic()
        parts: list[str] = []
        length = 0
        truncated = len(reader.pages) > max_pages
        for index, page in enumerate(reader.pages):
            if index >= max_pages or time.monotonic() - started > max_seconds:
                truncated = True
                break
            chunk = (page.extract_text() or "").strip()
            if chunk:
                parts.append(chunk)
                length += len(chunk) + 2
            if length >= max_chars:
                truncated = True
                break
    except (PyPdfError, ValueError, KeyError, TypeError, AttributeError, IndexError,
            RecursionError, OSError, ZeroDivisionError):  # fmt: skip
        return Extracted("", TextStatus.BROKEN)
    text = "\n\n".join(parts)[:max_chars].replace("\x00", "")
    if not text.strip():
        return Extracted("", TextStatus.EMPTY)
    return Extracted(text, TextStatus.TRUNCATED if truncated else TextStatus.DONE)


def extract_pdf_text(material_id: int) -> str:
    """Store the text of a ready PDF material. Returns the text status ("" if skipped)."""
    material = Material.objects.filter(
        pk=material_id, kind=MaterialKind.PDF, status=ScanStatus.READY
    ).first()
    if material is None or not material.storage_key:
        return ""
    try:
        with media.private_storage().open(material.storage_key, "rb") as file:
            result = extract_text(
                file,
                max_pages=settings.PDF_TEXT_MAX_PAGES,
                max_chars=settings.PDF_TEXT_MAX_CHARS,
                max_seconds=settings.PDF_TEXT_MAX_SECONDS,
            )
    except OSError:
        result = Extracted("", TextStatus.BROKEN)
    Material.objects.filter(pk=material.pk).update(text=result.text, text_status=result.status)
    _log(
        "material_text_extracted",
        material.artist.user_id,
        material.pk,
        count=len(result.text),
    )
    return result.status


# --- YouTube / Vimeo links -------------------------------------------------------------------

OEMBED_ENDPOINTS = {
    VideoProvider.YOUTUBE: "https://www.youtube.com/oembed",
    VideoProvider.VIMEO: "https://vimeo.com/api/oembed.json",
}
YOUTUBE_HOSTS = {"youtube.com", "www.youtube.com", "m.youtube.com"}
VIMEO_HOSTS = {"vimeo.com", "www.vimeo.com"}
_YOUTUBE_ID = re.compile(r"^[A-Za-z0-9_-]{11}$")
_VIMEO_ID = re.compile(r"^[0-9]{1,12}$")
MAX_OEMBED_BYTES = 64 * 1024

UNSUPPORTED = _("Podaj link do filmu na YouTube (youtube.com, youtu.be) albo Vimeo (vimeo.com).")
NOT_FOUND = _("Nie znaleziono tego filmu albo jest prywatny. Sprawdź link i ustawienia filmu.")
UNAVAILABLE = _("Nie udało się teraz sprawdzić filmu. Spróbuj ponownie za chwilę.")


@dataclass(frozen=True)
class VideoRef:
    provider: str
    video_id: str

    @property
    def canonical_url(self) -> str:
        if self.provider == VideoProvider.YOUTUBE:
            return f"https://www.youtube.com/watch?v={self.video_id}"
        return f"https://vimeo.com/{self.video_id}"


def parse_video_url(url: str) -> VideoRef | None:
    """YouTube (watch, youtu.be, shorts) or Vimeo (vimeo.com/<id>) URL -> provider and id;
    None for anything else. Pure parsing, no request."""
    url = (url or "").strip()
    if len(url) > 500:
        return None
    try:
        parts = urllib.parse.urlsplit(url)
        port = parts.port
    except ValueError:
        return None
    if parts.scheme not in ("http", "https") or port is not None or parts.username:
        return None
    host = (parts.hostname or "").lower()
    segments = [s for s in parts.path.split("/") if s]
    candidate = ""
    if host in YOUTUBE_HOSTS:
        if segments == ["watch"]:
            candidate = urllib.parse.parse_qs(parts.query).get("v", [""])[0]
        elif len(segments) == 2 and segments[0] == "shorts":
            candidate = segments[1]
        return VideoRef(VideoProvider.YOUTUBE, candidate) if _YOUTUBE_ID.match(candidate) else None
    if host == "youtu.be":
        candidate = segments[0] if len(segments) == 1 else ""
        return VideoRef(VideoProvider.YOUTUBE, candidate) if _YOUTUBE_ID.match(candidate) else None
    if host in VIMEO_HOSTS:
        candidate = segments[0] if len(segments) == 1 else ""
        return VideoRef(VideoProvider.VIMEO, candidate) if _VIMEO_ID.match(candidate) else None
    return None


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    """The oEmbed answer must come from the fixed endpoint itself, never via a redirect."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


_opener = urllib.request.build_opener(_NoRedirect)


def urllib_transport(url: str, timeout: float) -> tuple[int, bytes]:
    """GET `url` (an https oEmbed endpoint) -> (status, body up to 64 KB). Raises OSError."""
    if not url.startswith(tuple(OEMBED_ENDPOINTS.values())):
        raise ValueError("only the fixed oEmbed endpoints may be called")
    request = urllib.request.Request(  # noqa: S310 - fixed https endpoints, checked above
        url, headers={"Accept": "application/json", "User-Agent": "artysci-dla-szkol/1.0"}
    )
    try:
        with _opener.open(request, timeout=timeout) as response:
            return response.status, response.read(MAX_OEMBED_BYTES)
    except urllib.error.HTTPError as exc:
        return exc.code, b""


# Tests replace this with a fake; it is the only way the module talks to the network.
transport = urllib_transport


def oembed_title(ref: VideoRef) -> str:
    """Title of the video from its provider's public oEmbed endpoint.

    Raises `MaterialRejected` "not_found" (404, private, embedding off) or "unavailable"
    (timeout, network error, unexpected answer).
    """
    query = urllib.parse.urlencode({"url": ref.canonical_url, "format": "json"})
    url = f"{OEMBED_ENDPOINTS[ref.provider]}?{query}"
    try:
        status, body = transport(url, settings.OEMBED_TIMEOUT_SECONDS)
    except (OSError, ValueError) as exc:
        raise MaterialRejected("unavailable", UNAVAILABLE) from exc
    if status in (400, 401, 403, 404):
        raise MaterialRejected("not_found", NOT_FOUND)
    if status != 200:
        raise MaterialRejected("unavailable", UNAVAILABLE)
    try:
        data = json.loads(body)
        title = data.get("title") if isinstance(data, dict) else None
    except ValueError as exc:
        raise MaterialRejected("unavailable", UNAVAILABLE) from exc
    if not isinstance(title, str):
        raise MaterialRejected("unavailable", UNAVAILABLE)
    return title.strip()[: Material._meta.get_field("title").max_length]


def add_link(artist: Artist, url: str) -> Material:
    """Add a YouTube or Vimeo link checked through oEmbed. Raises `MaterialRejected`
    ("unsupported" without any request, "duplicate", "not_found", "unavailable")."""
    ref = parse_video_url(url)
    if ref is None:
        raise MaterialRejected("unsupported", UNSUPPORTED)
    duplicate = Material.objects.filter(
        artist=artist, kind=MaterialKind.LINK, provider=ref.provider, video_id=ref.video_id
    )
    if duplicate.exists():
        raise MaterialRejected("duplicate", _("Ten film jest już na liście."))
    title = oembed_title(ref)
    with transaction.atomic():
        Artist.objects.select_for_update().filter(pk=artist.pk).first()
        if duplicate.exists():
            raise MaterialRejected("duplicate", _("Ten film jest już na liście."))
        material = Material.objects.create(
            artist=artist,
            kind=MaterialKind.LINK,
            status=ScanStatus.READY,
            provider=ref.provider,
            video_id=ref.video_id,
            canonical_url=ref.canonical_url,
            title=title,
        )
    _log("material_link_added", artist, material.pk)
    return material


# --- school questionnaire --------------------------------------------------------------------

QUESTIONNAIRE_FIELDS = (
    "q_age_from",
    "q_age_to",
    "q_duration_minutes",
    "q_max_audience",
    "q_tech_room",
    "q_tech_power",
    "q_tech_sound",
    "q_price_from_pln",
    "q_price_to_pln",
    "q_price_on_request",
)
_TEXT_FIELDS = ("q_tech_room", "q_tech_power", "q_tech_sound")
MAX_AUDIENCE = 10_000
MAX_DURATION = 24 * 60
MAX_PRICE = 1_000_000


class InvalidQuestionnaire(ValueError):
    def __init__(self, errors: dict):
        super().__init__(", ".join(sorted(errors)))
        self.errors = errors


def _int(value, field, errors, *, low, high):
    if value in (None, ""):
        return None
    try:
        number = int(value)
    except (TypeError, ValueError):
        errors[field] = _("Podaj liczbę całkowitą.")
        return None
    if not low <= number <= high:
        errors[field] = _("Podaj liczbę od %(low)d do %(high)d.") % {"low": low, "high": high}
        return None
    return number


def _clean_questionnaire(data) -> tuple[dict, dict]:
    errors: dict = {}
    cleaned = {
        "q_age_from": _int(data.get("q_age_from"), "q_age_from", errors, low=0, high=MAX_AGE),
        "q_age_to": _int(data.get("q_age_to"), "q_age_to", errors, low=0, high=MAX_AGE),
        "q_duration_minutes": _int(
            data.get("q_duration_minutes"), "q_duration_minutes", errors, low=1, high=MAX_DURATION
        ),
        "q_max_audience": _int(
            data.get("q_max_audience"), "q_max_audience", errors, low=1, high=MAX_AUDIENCE
        ),
        "q_price_from_pln": _int(
            data.get("q_price_from_pln"), "q_price_from_pln", errors, low=1, high=MAX_PRICE
        ),
        "q_price_to_pln": _int(
            data.get("q_price_to_pln"), "q_price_to_pln", errors, low=1, high=MAX_PRICE
        ),
        "q_price_on_request": bool(data.get("q_price_on_request")),
    }
    for field in _TEXT_FIELDS:
        text = (data.get(field) or "").strip()
        if len(text) > Artist._meta.get_field(field).max_length:
            errors[field] = _("Tekst jest za długi (maksymalnie 500 znaków).")
        cleaned[field] = text
    age_from, age_to = cleaned["q_age_from"], cleaned["q_age_to"]
    if age_from is not None and age_to is not None and age_from > age_to:
        errors["q_age_to"] = _("Wiek „do” nie może być mniejszy niż wiek „od”.")
    low, high = cleaned["q_price_from_pln"], cleaned["q_price_to_pln"]
    if low is not None and high is not None and low > high:
        errors["q_price_to_pln"] = _("Cena „do” nie może być mniejsza niż cena „od”.")
    if cleaned["q_price_on_request"] and (low is not None or high is not None):
        errors["q_price_on_request"] = _("Podaj kwotę albo zaznacz „na zapytanie” (jedno z dwóch).")
    return cleaned, errors


def questionnaire_errors(data) -> dict:
    """Field -> Polish message (empty: valid). The form and the service use these rules."""
    return _clean_questionnaire(data)[1]


def questionnaire_of(artist: Artist) -> dict:
    return {field: getattr(artist, field) for field in QUESTIONNAIRE_FIELDS}


def questionnaire_filled(artist: Artist | None) -> bool:
    if artist is None:
        return False
    values = questionnaire_of(artist)
    return any(value not in (None, "", False) for value in values.values())


def save_questionnaire(artist: Artist, data) -> Artist:
    """Store the school questionnaire (every field optional). Raises `InvalidQuestionnaire`
    (nothing saved)."""
    cleaned, errors = _clean_questionnaire(data)
    if errors:
        raise InvalidQuestionnaire(errors)
    Artist.objects.filter(pk=artist.pk).update(**cleaned)
    artist.refresh_from_db()
    _log("artist_questionnaire_saved", artist)
    return artist
