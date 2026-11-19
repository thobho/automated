"""Processing of video and audio materials (US-2.3B, D8), the `artists.process_media` job on
the ``media`` queue, queued by a clean scan.

ffprobe checks the file really is a video (MP4/MOV/WebM) or an audio recording (MP3/M4A/WAV)
and reads its duration and size. A video over `MEDIA_MAX_DURATION_SECONDS` (10 minutes, D8)
or an unreadable file is ``rejected`` with a message and its file deleted. A video is then
converted to MP4 (H.264 + AAC, at most 720p, `apps.core.ffmpeg`) and gets a JPEG thumbnail,
both under random keys in the private storage; audio is kept as uploaded. Input and output
live in a temporary directory removed after the job.

The job never ends stuck: a timeout, a crash, a missing ffmpeg or any other error becomes a
``rejected`` material with a readable message (the file is removed and the slot is free).
"""

import logging
import secrets
import shutil
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.db import transaction
from django.utils.translation import gettext_lazy as _

from apps.core import ffmpeg, media
from apps.core.logs import pseudonymise_user

from . import materials
from .models import Material, MaterialKind, ProcessingStatus, ScanStatus

logger = logging.getLogger("apps.artists.recordings")

# ffprobe `format_name` parts accepted per kind (D8: MP4, MOV, WebM; MP3, M4A, WAV)
CONTAINERS = {
    MaterialKind.VIDEO: frozenset({"mov", "mp4", "webm", "matroska"}),
    MaterialKind.AUDIO: frozenset({"mp3", "wav", "mov", "mp4", "m4a"}),
}

UNREADABLE = {
    MaterialKind.VIDEO: _("Nie można odczytać tego pliku jako filmu (MP4, MOV lub WebM)."),
    MaterialKind.AUDIO: _("Nie można odczytać tego pliku jako nagrania (MP3, M4A lub WAV)."),
}
TOO_LONG = _("Film jest dłuższy niż %(minutes)d minut. Skróć go i dodaj ponownie.")
TIMEOUT = _(
    "Przetwarzanie trwało za długo i zostało przerwane. Spróbuj krótszego lub mniejszego pliku."
)
FAILED = _("Nie udało się przetworzyć pliku. Spróbuj ponownie później albo zapisz go inaczej.")
COPY_BYTES = 1024 * 1024


@dataclass
class Outcome:
    ready: bool
    message: str = ""
    duration: float | None = None
    width: int | None = None
    height: int | None = None
    new_keys: dict = field(default_factory=dict)  # converted_key / thumbnail_key


class Rejected(Exception):
    def __init__(self, message):
        super().__init__(str(message))
        self.message = message


def _copy_from_storage(key: str, target: Path) -> None:
    with media.private_storage().open(key, "rb") as source, target.open("wb") as out:
        shutil.copyfileobj(source, out, COPY_BYTES)


def _save(path: Path, prefix: str, extension: str) -> str:
    with path.open("rb") as file:
        key = f"{prefix}/{secrets.token_urlsafe(24)}.{extension}"
        return media.private_storage().save(key, File(file))


def check_probe(kind: str, probe: ffmpeg.Probe) -> None:
    """Raise `Rejected` unless the probe shows an allowed file of `kind` within the limits."""
    if not probe.format_names & CONTAINERS[kind]:
        raise Rejected(UNREADABLE[kind])
    if kind == MaterialKind.VIDEO and not (probe.has_video and probe.width and probe.height):
        raise Rejected(UNREADABLE[kind])
    if kind == MaterialKind.AUDIO and (not probe.has_audio or probe.has_video):
        raise Rejected(UNREADABLE[kind])
    if not probe.duration:
        raise Rejected(UNREADABLE[kind])
    limit = settings.MEDIA_MAX_DURATION_SECONDS
    if kind == MaterialKind.VIDEO and probe.duration > limit:
        raise Rejected(TOO_LONG % {"minutes": limit // 60})


def _probe(kind: str, path: Path) -> ffmpeg.Probe:
    try:
        return ffmpeg.probe(path)
    except ffmpeg.FFmpegError as exc:
        if exc.code in ("failed", "unreadable"):  # ffprobe could not read it: a bad file
            raise Rejected(UNREADABLE[kind]) from exc
        raise


def _work(material: Material, work: Path) -> Outcome:
    source = work / "source"
    _copy_from_storage(material.storage_key, source)
    probe = _probe(material.kind, source)
    check_probe(material.kind, probe)
    if material.kind == MaterialKind.AUDIO:
        return Outcome(ready=True, duration=probe.duration)
    converted, thumb = work / "converted.mp4", work / "thumbnail.jpg"
    ffmpeg.convert_video(source, converted, max_seconds=settings.MEDIA_MAX_DURATION_SECONDS)
    result = ffmpeg.probe(converted)
    duration = result.duration or probe.duration
    ffmpeg.thumbnail(converted, thumb, at_seconds=min(1.0, duration / 2))
    outcome = Outcome(ready=True, duration=duration, width=result.width, height=result.height)
    try:
        outcome.new_keys["converted_key"] = _save(converted, "converted", "mp4")
        outcome.new_keys["thumbnail_key"] = _save(thumb, "thumbnail", "jpg")
    except Exception:
        materials.delete_files(outcome.new_keys.values())
        raise
    return outcome


def _failure(exc: ffmpeg.FFmpegError) -> Outcome:
    return Outcome(ready=False, message=TIMEOUT if exc.code == "timeout" else FAILED)


def process_media(material_id: int) -> str:
    """Probe (and for a video convert) a scanned video or audio material. Returns the new
    status ("" when there was nothing to do). Safe to run twice."""
    material = Material.objects.filter(
        pk=material_id,
        kind__in=materials.AV_KINDS,
        status=ScanStatus.PENDING,
        processing_status=ProcessingStatus.PENDING,
    ).first()
    if material is None or not material.storage_key:
        return ""
    outcome = None
    try:
        with tempfile.TemporaryDirectory(
            prefix="media-", dir=settings.MEDIA_WORK_DIR or None
        ) as work:
            outcome = _work(material, Path(work))
    except Rejected as exc:
        outcome = Outcome(ready=False, message=exc.message)
        reason = "rejected"
    except ffmpeg.FFmpegError as exc:
        outcome = _failure(exc)
        reason = exc.code
        level = logging.ERROR if exc.code == "missing" else logging.WARNING
        logger.log(
            level,
            "ffmpeg %s: %s",
            exc.code,
            exc.detail,
            extra={"event": "media_processing_error", "material": material.pk},
        )
    except Exception:  # never leave the material stuck in "przetwarzanie"
        logger.exception(
            "media processing crashed",
            extra={"event": "media_processing_error", "material": material.pk},
        )
        outcome = Outcome(ready=False, message=FAILED)
        reason = "error"
    else:
        reason = "ready"
    status = _record(material_id, outcome)
    logger.info(
        "media processed %s",
        reason,
        extra={
            "event": f"media_processed_{'ready' if outcome.ready else 'rejected'}",
            "user": pseudonymise_user(material.artist.user_id),
            "material": material.pk,
            "reason": reason,
        },
    )
    return status


def _record(material_id: int, outcome: Outcome) -> str:
    new_keys = list(outcome.new_keys.values())
    with transaction.atomic():
        material = Material.objects.select_for_update().filter(pk=material_id).first()
        if (
            material is None
            or material.status != ScanStatus.PENDING
            or material.processing_status != ProcessingStatus.PENDING
        ):  # deleted (or handled) while we worked: keep no files of ours
            transaction.on_commit(lambda: materials.delete_files(new_keys))
            return material.status if material else ""
        if outcome.ready:
            material.status = ScanStatus.READY
            material.processing_status = ProcessingStatus.DONE
            material.processing_message = ""
            material.duration_seconds = outcome.duration
            material.width, material.height = outcome.width, outcome.height
            material.converted_key = outcome.new_keys.get("converted_key", "")
            material.thumbnail_key = outcome.new_keys.get("thumbnail_key", "")
        else:  # the file goes, the row stays so the artist sees why (like an infected file)
            old_keys = material.stored_keys() + new_keys
            material.status = ScanStatus.REJECTED
            material.processing_status = ProcessingStatus.FAILED
            material.processing_message = str(outcome.message)[:300]
            material.storage_key = material.converted_key = material.thumbnail_key = ""
            transaction.on_commit(lambda: materials.delete_files(old_keys))
        material.save()
    return material.status
