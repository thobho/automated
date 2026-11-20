"""Quality checks of photos and videos, and frames as main-photo candidates (US-2.4, D59, D109).

Everything runs locally on the stored file and on what the original said about itself at upload
(`apps/core/imagemeta.py`): no AI and no external service. The `artists.check_material` job
(``media`` queue) runs after a photo or a video becomes ``ready`` and stores on the material its
size, orientation and flags together with `CHECKS_VERSION`; a video also gets a few frames
(`VideoFrame`, private storage, through the ffmpeg wrapper with its limits) that are measured and
flagged like photos. Flags only inform: the one rule that uses them is `can_be_main()`.

The flag codes are a closed list (`Flag`) with a Polish label and hint each. The thresholds are
named constants below (recorded in the decision log, D109). Raw metadata is never stored.
"""

import io
import logging
import secrets
import shutil
import tempfile
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.db import models, transaction
from django.utils.translation import gettext_lazy as _
from PIL import Image, UnidentifiedImageError

from apps.core import ffmpeg, media
from apps.core.imagemeta import ImageOrigin
from apps.core.logs import pseudonymise_user

from . import materials
from .models import (
    Artist,
    Material,
    MaterialKind,
    Orientation,
    ProcessingStatus,
    ScanStatus,
    VideoFrame,
)

logger = logging.getLogger("apps.artists.checks")

# Bump when a rule or a threshold changes: the backfill command then checks everything again.
CHECKS_VERSION = 1

# --- thresholds (named, see D109) ------------------------------------------------------------
PHOTO_MIN_LONG_SIDE = 1200  # px; below: low resolution
JPEG_MIN_QUALITY = 60  # estimated IJG quality of the ORIGINAL; below: heavy compression
DUPLICATE_MAX_DISTANCE = 5  # bits of 64 that may differ between two perceptual hashes
VIDEO_MIN_SECONDS = 15  # below: too short
VIDEO_MIN_SHORT_SIDE = 720  # px, the shorter side ("720p"); below: low resolution
FRAME_COUNT = 4  # frames per video, spread evenly over its duration
# Poster heuristic: the image is cut into 8x8 blocks of a downscaled grey copy.
POSTER_SAMPLE = 160  # px, longer side of the downscaled copy
POSTER_BLOCK = 8
POSTER_FLAT_RANGE = 12  # a block whose darkest and lightest pixel differ by at most this is flat
POSTER_TEXT_RANGE = 90  # a block with at least this contrast, in two tones, looks like lettering
POSTER_TEXT_TONE = 0.8  # share of a text block's pixels near its darkest or lightest tone
POSTER_MIN_FLAT = 0.55  # share of flat blocks
POSTER_MIN_TEXT = 0.12  # share of lettering-like blocks (fixtures: posters 0.14-0.22, shapes 0.10)
POSTER_MIN_DOMINANT = 0.4  # share of pixels in the single most common (coarse) colour

# Common screen sizes (either orientation). A match without camera metadata = a screenshot.
SCREEN_SIZES = frozenset(
    {
        (1280, 720), (1280, 800), (1366, 768), (1440, 900), (1536, 864), (1600, 900),
        (1680, 1050), (1920, 1080), (1920, 1200), (2048, 1152), (2560, 1080), (2560, 1440),
        (2560, 1600), (2880, 1800), (3440, 1440), (3840, 2160),
        (720, 1280), (750, 1334), (828, 1792), (1080, 1920), (1080, 2160), (1080, 2280),
        (1080, 2340), (1080, 2400), (1125, 2436), (1170, 2532), (1179, 2556), (1242, 2688),
        (1284, 2778), (1290, 2796), (1440, 3200),
    }
)  # fmt: skip


class Flag(models.TextChoices):
    """The closed list of flags (stored as the code)."""

    LOW_RESOLUTION = "low_resolution", _("niska rozdzielczość")
    HEAVY_COMPRESSION = "heavy_compression", _("mocna kompresja")
    DUPLICATE = "duplicate", _("duplikat")
    STOCK = "stock", _("zdjęcie stockowe")
    SCREENSHOT_OR_AI = "screenshot_or_ai", _("zrzut ekranu lub obraz AI")
    POSTER = "poster", _("plakat")
    TOO_SHORT = "too_short", _("za krótkie")
    VERTICAL = "vertical", _("pionowe")


HINTS = {
    Flag.LOW_RESOLUTION: _("Wgraj zdjęcie o dłuższym boku co najmniej %(px)d px."),
    Flag.HEAVY_COMPRESSION: _(
        "Zdjęcie jest mocno skompresowane i może wyglądać na rozmyte lub w kratkę. "
        "Wgraj oryginał z aparatu lub telefonu."
    ),
    Flag.DUPLICATE: _("Takie zdjęcie już masz. Usuń duplikat albo wgraj inne ujęcie."),
    Flag.STOCK: _("Wygląda na zdjęcie z banku zdjęć. Wgraj własne zdjęcia z występów."),
    Flag.SCREENSHOT_OR_AI: _(
        "Wygląda na zrzut ekranu lub obraz wygenerowany przez AI. "
        "Wgraj prawdziwe zdjęcie z występu."
    ),
    Flag.POSTER: _("Wygląda na plakat. Plakat dodaj przy ofercie, a tu wgraj zdjęcie z występu."),
    Flag.TOO_SHORT: _("Film trwa krócej niż %(seconds)d s. Dłuższy film lepiej pokaże występ."),
    Flag.VERTICAL: _("Film jest pionowy. Nagraj go poziomo, wtedy dobrze wygląda na stronie."),
}
VIDEO_LOW_RESOLUTION_HINT = _(
    "Nagraj film w rozdzielczości co najmniej 720p (krótszy bok co najmniej %(px)d px)."
)

# Flags that keep a photo or a frame from being the main photo (US-3.8 uses them too).
BLOCKING_FLAGS = frozenset({Flag.STOCK, Flag.SCREENSHOT_OR_AI, Flag.POSTER})
_ORDER = {code: index for index, code in enumerate(Flag.values)}


def hint_for(code: str, kind: str = MaterialKind.PHOTO) -> str:
    """The Polish hint of flag `code` for a photo (or frame) or a video."""
    if code == Flag.LOW_RESOLUTION and kind == MaterialKind.VIDEO:
        return str(VIDEO_LOW_RESOLUTION_HINT) % {"px": VIDEO_MIN_SHORT_SIDE}
    return str(HINTS[Flag(code)]) % {"px": PHOTO_MIN_LONG_SIDE, "seconds": VIDEO_MIN_SECONDS}


def flag_items(flags, kind: str = MaterialKind.PHOTO) -> list[dict]:
    """Flags for the list: code, label and hint, in the fixed order; unknown codes are dropped."""
    known = [code for code in flags or [] if code in _ORDER]
    return [
        {"code": code, "label": Flag(code).label, "hint": hint_for(code, kind)}
        for code in sorted(set(known), key=_ORDER.__getitem__)
    ]


# --- pure measurements -----------------------------------------------------------------------


def orientation_of(width: int, height: int) -> str:
    if width == height:
        return Orientation.SQUARE
    return Orientation.LANDSCAPE if width > height else Orientation.PORTRAIT


def perceptual_hash(img: Image.Image) -> str:
    """64-bit difference hash (9x8 grey, each bit: pixel brighter than its right neighbour)
    as 16 hex digits. Survives resizing and recompression."""
    grey = img.convert("L").resize((9, 8), Image.Resampling.LANCZOS)
    pixels = grey.tobytes()
    bits = 0
    for row in range(8):
        for col in range(8):
            bits = (bits << 1) | (pixels[row * 9 + col] > pixels[row * 9 + col + 1])
    return f"{bits:016x}"


def hash_distance(a: str, b: str) -> int:
    return (int(a, 16) ^ int(b, 16)).bit_count()


def looks_like_poster(img: Image.Image) -> bool:
    """Flat colour areas, one dominant colour and lettering-like blocks (two tones, high
    contrast). A heuristic: a photo with a big plain background and sharp dark-on-light shapes
    can be taken for a poster, which only keeps it from being the main photo."""
    small = img.convert("RGB")
    small.thumbnail((POSTER_SAMPLE, POSTER_SAMPLE), Image.Resampling.BOX)
    width, height = small.size
    if width < POSTER_BLOCK or height < POSTER_BLOCK:
        return False
    grey = small.convert("L").tobytes()
    flat = text = total = 0
    for top in range(0, height - POSTER_BLOCK + 1, POSTER_BLOCK):
        for left in range(0, width - POSTER_BLOCK + 1, POSTER_BLOCK):
            block = b"".join(
                grey[(top + r) * width + left : (top + r) * width + left + POSTER_BLOCK]
                for r in range(POSTER_BLOCK)
            )
            low, high = min(block), max(block)
            total += 1
            if high - low <= POSTER_FLAT_RANGE:
                flat += 1
            elif high - low >= POSTER_TEXT_RANGE:
                margin = (high - low) * 0.2
                near = sum(1 for p in block if p <= low + margin or p >= high - margin)
                if near >= POSTER_TEXT_TONE * len(block):
                    text += 1
    if not total or flat / total < POSTER_MIN_FLAT or text / total < POSTER_MIN_TEXT:
        return False
    raw = small.tobytes()
    colours = Counter(zip((v >> 5 for v in raw[0::3]), (v >> 5 for v in raw[1::3]),
                          (v >> 5 for v in raw[2::3]), strict=True))  # fmt: skip
    return colours.most_common(1)[0][1] / (width * height) >= POSTER_MIN_DOMINANT


def origin_flags(origin: ImageOrigin | None) -> list[str]:
    """Flags decided at upload from the original's metadata (the metadata is dropped after)."""
    if origin is None:
        return []
    flags = []
    if origin.stock:
        flags.append(Flag.STOCK)
    if origin.ai:
        flags.append(Flag.SCREENSHOT_OR_AI)
    if origin.jpeg_quality is not None and origin.jpeg_quality < JPEG_MIN_QUALITY:
        flags.append(Flag.HEAVY_COMPRESSION)
    return [str(flag) for flag in flags]


def is_screen_size(width: int, height: int) -> bool:
    return (width, height) in SCREEN_SIZES or (height, width) in SCREEN_SIZES


def image_flags(
    width: int, height: int, *, poster: bool, duplicate: bool, camera_metadata: bool | None,
    carried: list | tuple = (),
) -> list[str]:  # fmt: skip
    """Flags of a photo or frame from its measurements; `carried` are the flags decided at
    upload. A screenshot needs the original to be known to have had no camera metadata."""
    flags = {code for code in carried if code in _ORDER}
    if max(width, height) < PHOTO_MIN_LONG_SIDE:
        flags.add(Flag.LOW_RESOLUTION)
    if duplicate:
        flags.add(Flag.DUPLICATE)
    if poster:
        flags.add(Flag.POSTER)
    if camera_metadata is False and is_screen_size(width, height):
        flags.add(Flag.SCREENSHOT_OR_AI)
    return sorted((str(f) for f in flags), key=_ORDER.__getitem__)


def video_flags(duration: float | None, width: int | None, height: int | None) -> list[str]:
    """Flags of a ready video from the probe data kept on the material."""
    flags = []
    if duration is not None and duration < VIDEO_MIN_SECONDS:
        flags.append(Flag.TOO_SHORT)
    if width and height and height > width:
        flags.append(Flag.VERTICAL)
    if width and height and min(width, height) < VIDEO_MIN_SHORT_SIDE:
        flags.append(Flag.LOW_RESOLUTION)
    return sorted((str(f) for f in flags), key=_ORDER.__getitem__)


# --- main photo rule -------------------------------------------------------------------------


def can_be_main(item) -> bool:
    """A checked photo or video frame without a blocking flag (stock, screenshot or AI, poster).
    An unchecked one cannot be told apart yet, so it is not offered."""
    if isinstance(item, Material) and (
        item.kind != MaterialKind.PHOTO or item.status != ScanStatus.READY
    ):
        return False
    if item.checks_version < 1:
        return False
    return not (set(item.flags or []) & BLOCKING_FLAGS)


def main_photo_candidates(artist: Artist) -> list:
    """Photos and video frames that may be the main photo: ready photos first, then frames."""
    photos = Material.objects.filter(
        artist=artist, kind=MaterialKind.PHOTO, status=ScanStatus.READY
    ).order_by("created_at", "pk")
    frames = VideoFrame.objects.filter(
        material__artist=artist, material__status=ScanStatus.READY
    ).select_related("material")
    return [item for item in [*photos, *frames] if can_be_main(item)]


def frames_of(material: Material) -> list[VideoFrame]:
    return list(material.frames.all())


# --- the job ---------------------------------------------------------------------------------


@dataclass
class Measured:
    width: int
    height: int
    orientation: str
    phash: str
    poster: bool


def _log(event: str, material: Material, **extra) -> None:
    logger.info(
        event.replace("_", " "),
        extra={
            "event": event,
            "user": pseudonymise_user(material.artist.user_id),
            "material": material.pk,
            **extra,
        },
    )


def measure(img: Image.Image) -> Measured:
    width, height = img.size
    return Measured(width, height, orientation_of(width, height), perceptual_hash(img),
                    looks_like_poster(img))  # fmt: skip


def _open_image(path_or_key, *, from_storage: bool) -> Image.Image:
    if from_storage:
        with media.private_storage().open(path_or_key, "rb") as handle:
            img = Image.open(io.BytesIO(handle.read()))
    else:
        img = Image.open(path_or_key)
    img.load()
    return img


def _is_duplicate(phash: str, hashes) -> bool:
    return any(h and hash_distance(phash, h) <= DUPLICATE_MAX_DISTANCE for h in hashes)


def _check_photo(material: Material) -> None:
    try:
        img = _open_image(material.storage_key, from_storage=True)
    except (OSError, UnidentifiedImageError, Image.DecompressionBombError, SyntaxError):
        logger.warning(
            "photo could not be read for checks",
            extra={"event": "material_check_unreadable", "material": material.pk},
        )
        return
    measured = measure(img)
    older = Material.objects.filter(
        artist=material.artist, kind=MaterialKind.PHOTO, status=ScanStatus.READY,
        pk__lt=material.pk,
    ).values_list("phash", flat=True)  # fmt: skip
    flags = image_flags(
        measured.width, measured.height, poster=measured.poster,
        duplicate=_is_duplicate(measured.phash, older),
        camera_metadata=material.camera_metadata, carried=material.origin_flags or [],
    )  # fmt: skip
    Material.objects.filter(pk=material.pk).update(
        width=measured.width, height=measured.height, orientation=measured.orientation,
        phash=measured.phash, flags=flags, checks_version=CHECKS_VERSION,
    )  # fmt: skip
    _log("material_checked", material, flags=flags)


def _save_frame_file(path: Path) -> str:
    key = f"frame/{secrets.token_urlsafe(24)}.jpg"
    with path.open("rb") as handle:
        return media.private_storage().save(key, File(handle))


def _make_frames(material: Material, photo_hashes: list[str]) -> list[VideoFrame]:
    """Cut `FRAME_COUNT` frames from the ready video, store and measure them. Raises
    `ffmpeg.FFmpegError` when the first frame cannot be made."""
    duration = material.duration_seconds
    key = material.converted_key or material.storage_key
    if not duration or not key:
        return []
    frames: list[VideoFrame] = []
    failure = ffmpeg.FFmpegError("failed", "no frame could be read")
    try:
        with tempfile.TemporaryDirectory(
            prefix="frames-", dir=settings.MEDIA_WORK_DIR or None
        ) as work:
            source = Path(work) / "video"
            with media.private_storage().open(key, "rb") as handle, source.open("wb") as out:
                shutil.copyfileobj(handle, out, 1024 * 1024)
            for index in range(FRAME_COUNT):
                at = duration * (index + 1) / (FRAME_COUNT + 1)
                target = Path(work) / f"frame{index}.jpg"
                try:
                    ffmpeg.thumbnail(source, target, at_seconds=at)
                    img = _open_image(target, from_storage=False)
                except (ffmpeg.FFmpegError, OSError, UnidentifiedImageError, SyntaxError) as exc:
                    failure = exc if isinstance(exc, ffmpeg.FFmpegError) else failure
                    continue
                measured = measure(img)
                flags = image_flags(
                    measured.width, measured.height, poster=measured.poster,
                    duplicate=_is_duplicate(measured.phash, photo_hashes),
                    camera_metadata=None,
                )  # fmt: skip
                frames.append(
                    VideoFrame(
                        material=material,
                        storage_key=_save_frame_file(target),
                        position_seconds=round(at, 2),
                        width=measured.width,
                        height=measured.height,
                        orientation=measured.orientation,
                        flags=flags,
                        phash=measured.phash,
                        checks_version=CHECKS_VERSION,
                    )  # fmt: skip
                )
            if not frames:  # every frame failed: let the caller keep the old version number
                raise failure
    except Exception:
        materials.delete_files(f.storage_key for f in frames)
        raise
    return frames


def _check_video(material: Material) -> None:
    flags = video_flags(material.duration_seconds, material.width, material.height)
    orientation = (
        orientation_of(material.width, material.height) if material.width and material.height
        else ""
    )  # fmt: skip
    photo_hashes = list(
        Material.objects.filter(
            artist=material.artist, kind=MaterialKind.PHOTO, status=ScanStatus.READY
        ).values_list("phash", flat=True)
    )
    frames_ok = True
    try:
        frames = _make_frames(material, photo_hashes)
    except ffmpeg.FFmpegError as exc:
        # flags still stand; the version stays old so the backfill command tries the frames again
        frames, frames_ok = [], False
        logger.warning(
            "video frames failed: %s",
            exc.code,
            extra={"event": "material_frames_error", "material": material.pk},
        )
    with transaction.atomic():
        current = Material.objects.select_for_update().filter(
            pk=material.pk, status=ScanStatus.READY
        ).first()  # fmt: skip
        if current is None:  # deleted while we worked: leave no frame file behind
            transaction.on_commit(lambda: materials.delete_files(f.storage_key for f in frames))
            return
        old_keys = []
        if frames:
            old = list(current.frames.all())
            old_keys = [f.storage_key for f in old]
            current.frames.all().delete()
            VideoFrame.objects.bulk_create(frames)
            transaction.on_commit(lambda: materials.delete_files(old_keys))
        Material.objects.filter(pk=current.pk).update(
            orientation=orientation, flags=flags,
            checks_version=CHECKS_VERSION if frames_ok else current.checks_version,
        )  # fmt: skip
    _log("material_checked", material, flags=flags, frames=len(frames))


def check_material(material_id: int, *, force: bool = False) -> str:
    """Measure and flag a ready photo or video (and cut the frames of a video). Returns
    "checked", "current" (already done with this version) or "" (nothing to do). Safe to run
    twice: results sit on the material and a re-run replaces the frames."""
    material = (
        Material.objects.select_related("artist")
        .filter(pk=material_id, kind__in=(MaterialKind.PHOTO, MaterialKind.VIDEO),
                status=ScanStatus.READY)
        .first()
    )  # fmt: skip
    if material is None or not (material.storage_key or material.converted_key):
        return ""
    if material.kind == MaterialKind.VIDEO and material.processing_status != ProcessingStatus.DONE:
        return ""
    if material.checks_version >= CHECKS_VERSION and not force:
        return "current"
    if material.kind == MaterialKind.PHOTO:
        _check_photo(material)
    else:
        _check_video(material)
    return "checked"


def backfill(*, force: bool = False) -> dict:
    """Check every ready photo and video that has no result of the current version (all of
    them with `force`). Idempotent. Returns counts."""
    queryset = Material.objects.filter(
        kind__in=(MaterialKind.PHOTO, MaterialKind.VIDEO), status=ScanStatus.READY
    ).order_by("pk")
    if not force:
        queryset = queryset.filter(checks_version__lt=CHECKS_VERSION)
    counts = {"checked": 0, "skipped": 0}
    for pk in list(queryset.values_list("pk", flat=True)):
        result = check_material(pk, force=force)
        counts["checked" if result == "checked" else "skipped"] += 1
    return counts


def delete_frame(artist: Artist, frame_id) -> None:
    """Delete one frame of the artist's own video and, after the commit, its file. Raises
    `VideoFrame.DoesNotExist` for another artist's or a missing frame."""
    with transaction.atomic():
        frame = VideoFrame.objects.select_for_update().get(material__artist=artist, pk=frame_id)
        key = frame.storage_key
        frame.delete()
        transaction.on_commit(lambda: materials.delete_files([key]))
