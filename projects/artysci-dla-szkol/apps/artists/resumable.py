"""Resumable uploads of video and audio files (US-2.3B, D8, D62). A small own protocol, no
library and nothing provider-specific (D91):

1. `create_session(artist, kind, size, name)`: the kind, the declared size (D8: video 500 MB,
   audio 50 MB) and the remaining count are checked before any byte is sent, the count again
   under the artist row lock (D105).
2. `append_chunk(...)`: the client sends chunks of at most `UPLOAD_CHUNK_BYTES` with the
   offset it starts at. The offset must equal the bytes received so far, and the chunk may not
   reach past the declared size; anything else is refused and nothing is written. The first
   chunk's magic bytes must already look like an allowed type.
3. `state(session)` answers the received offset, so the client continues from there after a
   lost connection or a page reload.
4. `complete(...)`: the whole file goes through the T06 upload path (type sniffed from bytes,
   random key, private storage), becomes a pending `Material` and gets the D105 scan job;
   the temporary data is removed.

Received bytes live in one file per session under `UPLOAD_TEMP_DIR` (named after the random
session id, never served). A session belongs to one artist (another artist's id = not found)
and expires after `UPLOAD_SESSION_TTL_HOURS`; `cleanup_expired()` (a periodic job) removes
expired sessions, their data and stray temporary files.
"""

import logging
import time
import uuid
from datetime import timedelta
from pathlib import Path

from django.conf import settings
from django.db import transaction
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.core import uploads
from apps.core.logs import pseudonymise_user

from . import materials
from .models import Artist, Material, MaterialKind, ScanStatus, UploadSession

logger = logging.getLogger("apps.artists.resumable")

ALLOWED_TYPES = {
    MaterialKind.VIDEO: frozenset({"video/mp4", "video/quicktime", "video/webm"}),
    MaterialKind.AUDIO: frozenset({"audio/mpeg", "audio/mp4", "audio/wav"}),
}
SUFFIX = ".part"


class UploadRefused(Exception):
    """A session or chunk is not accepted. `status` is the HTTP answer, `message` (Polish) is
    shown to the artist, `offset` is the server's received offset for offset errors."""

    def __init__(self, code: str, message, *, status: int = 400, offset: int | None = None):
        super().__init__(code)
        self.code = code
        self.message = message
        self.status = status
        self.offset = offset


class SessionGone(Exception):
    """No such session for this artist (missing, another artist's, expired): HTTP 404."""


BAD_TYPE = _("Ten typ pliku nie jest dozwolony.")


def _log(event: str, artist: Artist, session_id=None, **extra) -> None:
    logger.info(
        event.replace("_", " "),
        extra={
            "event": event,
            "user": pseudonymise_user(artist.user_id),
            "session": str(session_id) if session_id else None,
            **extra,
        },
    )


# --- temporary files -------------------------------------------------------------------------


def temp_dir() -> Path:
    path = Path(settings.UPLOAD_TEMP_DIR)
    path.mkdir(mode=0o700, parents=True, exist_ok=True)
    return path


def temp_path(session_id) -> Path:
    """The data file of a session; the name comes only from the (validated) UUID."""
    return temp_dir() / f"{uuid.UUID(str(session_id)).hex}{SUFFIX}"


def _discard(session: UploadSession) -> None:
    session_id = session.pk
    UploadSession.objects.filter(pk=session_id).delete()
    temp_path(session_id).unlink(missing_ok=True)


# --- sessions --------------------------------------------------------------------------------


def max_bytes(kind: str) -> int:
    return uploads.KINDS[kind][0]


def create_session(artist: Artist, kind: str, size, name: str = "") -> UploadSession:
    """Open an upload of one `kind` file of `size` bytes. Raises `UploadRefused` (bad kind or
    size) or `materials.MaterialRejected` (limit reached); nothing is created then.

    An artist has at most as many open sessions of a kind as the kind's limit: a new one
    replaces the oldest (an upload abandoned without the page offering to resume it)."""
    if kind not in materials.AV_KINDS:
        raise UploadRefused("bad_kind", BAD_TYPE)
    try:
        size = int(size)
    except (TypeError, ValueError) as exc:
        raise UploadRefused("bad_size", _("Nieprawidłowy rozmiar pliku.")) from exc
    if size <= 0:
        raise UploadRefused("empty", _("Plik jest pusty."))
    limit = max_bytes(kind)
    if size > limit:
        raise UploadRefused(
            "too_large",
            _("Plik jest za duży (maksymalnie %(mb)d MB).") % {"mb": limit // uploads.MB},
            status=413,
        )
    materials.check_room(artist, kind, 1)
    with transaction.atomic():
        Artist.objects.select_for_update().filter(pk=artist.pk).first()
        if materials.is_full(artist, kind):  # a parallel upload finished meanwhile
            raise materials.limit_error(kind)
        open_sessions = list(
            UploadSession.objects.filter(artist=artist, kind=kind).order_by("created_at")
        )
        stale = open_sessions[: max(0, len(open_sessions) - materials.limit_for(kind) + 1)]
        now = timezone.now()
        session = UploadSession.objects.create(
            artist=artist,
            kind=kind,
            declared_size=size,
            original_name=materials.clean_name(name),
            created_at=now,
            expires_at=now + timedelta(hours=settings.UPLOAD_SESSION_TTL_HOURS),
        )
        temp_path(session.pk).write_bytes(b"")
    for old in stale:
        _discard(old)
    _log("upload_session_created", artist, session.pk, kind=kind)
    return session


def get_session(artist: Artist, session_id) -> UploadSession:
    """The artist's own unexpired session; raises `SessionGone` otherwise."""
    try:
        session_id = uuid.UUID(str(session_id))
    except ValueError as exc:
        raise SessionGone from exc
    session = UploadSession.objects.filter(
        pk=session_id, artist=artist, expires_at__gt=timezone.now()
    ).first()
    if session is None:
        raise SessionGone
    return session


def state(session: UploadSession) -> dict:
    """What the client needs to continue: the received offset and the sizes."""
    return {
        "id": str(session.pk),
        "kind": session.kind,
        "offset": session.received,
        "size": session.declared_size,
        "chunk_size": settings.UPLOAD_CHUNK_BYTES,
        "complete": session.received == session.declared_size,
    }


def append_chunk(artist: Artist, session_id, offset, length, stream) -> UploadSession:
    """Write `length` bytes read from `stream` at `offset`. Raises `SessionGone` or
    `UploadRefused` (409 wrong offset, 413 too long or past the declared size, 400 bad type or
    a short body); nothing is written when it raises."""
    session = get_session(artist, session_id)
    try:
        offset, length = int(offset), int(length)
    except (TypeError, ValueError) as exc:
        raise UploadRefused("bad_request", _("Nieprawidłowy fragment pliku.")) from exc
    if offset != session.received:
        raise UploadRefused(
            "offset", _("Nieprawidłowe miejsce fragmentu."), status=409, offset=session.received
        )
    if length <= 0 or length > settings.UPLOAD_CHUNK_BYTES:
        raise UploadRefused("chunk_size", _("Nieprawidłowy rozmiar fragmentu."), status=413)
    if offset + length > session.declared_size:
        raise UploadRefused(
            "beyond_size", _("Plik jest większy niż zadeklarowano."), status=413,
            offset=session.received,
        )  # fmt: skip
    data = stream.read(length)
    if len(data) != length:  # connection lost mid-chunk: the client sends it again
        raise UploadRefused("short", _("Fragment dotarł niepełny."), offset=session.received)
    if (
        offset == 0
        and uploads.sniff_content_type(data[: uploads.HEAD_BYTES])
        not in (ALLOWED_TYPES[session.kind])
    ):
        _discard(session)
        _log("upload_refused_type", artist, session.pk)
        raise UploadRefused("bad_type", BAD_TYPE)
    with transaction.atomic():
        session = UploadSession.objects.select_for_update().filter(pk=session.pk).first()
        if session is None:
            raise SessionGone
        if session.received != offset:  # a parallel request with the same chunk won
            raise UploadRefused(
                "offset", _("Nieprawidłowe miejsce fragmentu."), status=409,
                offset=session.received,
            )  # fmt: skip
        path = temp_path(session.pk)
        try:
            with path.open("r+b") as file:
                file.truncate(offset)  # drop bytes of a write that never got committed
                file.seek(offset)
                file.write(data)
        except FileNotFoundError as exc:
            raise SessionGone from exc
        session.received = offset + length
        session.save(update_fields=["received"])
    return session


def complete(artist: Artist, session_id) -> Material:
    """Turn a fully received session into a pending material with a scan job. Raises
    `SessionGone`, `UploadRefused` (not all bytes yet: 409; refused by content: 400) or
    `materials.MaterialRejected` (limit reached meanwhile). The session and its temporary
    data are gone afterwards unless the upload is simply not finished yet."""
    session = get_session(artist, session_id)
    if session.received != session.declared_size:
        raise UploadRefused(
            "incomplete", _("Plik nie został jeszcze wysłany w całości."), status=409,
            offset=session.received,
        )  # fmt: skip
    path = temp_path(session.pk)
    try:
        if path.stat().st_size != session.declared_size:
            raise UploadRefused("size_mismatch", _("Plik dotarł uszkodzony. Wyślij go ponownie."))
        with path.open("rb") as file:
            stored = uploads.store_upload(file, kind=session.kind, visibility="private")
    except FileNotFoundError as exc:
        _discard(session)
        raise SessionGone from exc
    except uploads.UploadRejected as exc:
        _discard(session)
        _log("upload_refused_type", artist, session.pk)
        raise UploadRefused(exc.code, exc.message) from exc
    except UploadRefused:
        _discard(session)
        raise
    if stored.content_type not in ALLOWED_TYPES[session.kind]:  # e.g. an OGG for "audio"
        materials.delete_files([stored.key])
        _discard(session)
        raise UploadRefused("bad_type", BAD_TYPE)
    try:
        with transaction.atomic():
            Artist.objects.select_for_update().filter(pk=artist.pk).first()
            if materials.is_full(artist, session.kind):
                raise materials.limit_error(session.kind)
            material = Material.objects.create(
                artist=artist,
                kind=session.kind,
                status=ScanStatus.PENDING,
                storage_key=stored.key,
                content_type=stored.content_type,
                size=stored.size,
                original_name=session.original_name,
            )
            materials._enqueue_scan(material)
            UploadSession.objects.filter(pk=session.pk).delete()
    except Exception:
        materials.delete_files([stored.key])
        _discard(session)
        raise
    path.unlink(missing_ok=True)
    _log("material_uploaded", artist, session.pk, material=material.pk)
    return material


# --- cleanup (periodic job) ------------------------------------------------------------------


def cleanup_expired(now=None) -> int:
    """Delete expired sessions with their data, and temporary files that belong to no session
    and are older than the session lifetime. Returns how many files or sessions went."""
    now = now or timezone.now()
    removed = 0
    for session in UploadSession.objects.filter(expires_at__lte=now):
        _discard(session)
        removed += 1
    live = {s.hex for s in UploadSession.objects.values_list("pk", flat=True)}
    cutoff = time.time() - settings.UPLOAD_SESSION_TTL_HOURS * 3600
    for path in temp_dir().glob(f"*{SUFFIX}"):
        try:
            if path.stem not in live and path.stat().st_mtime < cutoff:
                path.unlink()
                removed += 1
        except OSError:
            continue
    if removed:
        logger.info(
            "upload sessions cleaned up", extra={"event": "upload_cleanup", "count": removed}
        )
    return removed
