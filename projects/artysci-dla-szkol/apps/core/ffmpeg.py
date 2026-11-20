"""ffprobe and ffmpeg as subprocesses with limits (US-2.3B, security row "Pliki").

- The command is an argument list (never a shell), with the binary path from settings
  (`FFMPEG_PATH`, `FFPROBE_PATH`).
- Every run has a wall-clock timeout (`FFMPEG_TIMEOUT_SECONDS`, `FFPROBE_TIMEOUT_SECONDS`) and
  an address-space limit (`FFMPEG_MEMORY_MB`, POSIX `RLIMIT_AS`) set in the child before exec.
- Input and output paths are files in a temporary directory the caller owns; stdin is closed.
- Any trouble is an `FFmpegError` with a stable `code`: ``missing`` (binary not found),
  ``timeout``, ``crash`` (killed by a signal, e.g. the memory limit), ``failed`` (non-zero
  exit), ``unreadable`` (ffprobe output that is not what we asked for). Callers turn it into a
  readable status; nothing here raises anything else for a bad file.
"""

import json
import math
import resource
import subprocess  # noqa: S404 - argument lists only, no shell
from dataclasses import dataclass
from pathlib import Path

from django.conf import settings

MAX_OUTPUT = 64 * 1024  # bytes of ffprobe JSON / ffmpeg stderr kept
MAX_EDGE = 720  # converted video: the shorter side is at most 720 px ("720p")


class FFmpegError(Exception):
    def __init__(self, code: str, detail: str = ""):
        super().__init__(code)
        self.code = code
        self.detail = detail[:300]


@dataclass(frozen=True)
class Probe:
    format_names: frozenset[str]
    duration: float | None
    has_video: bool
    has_audio: bool
    width: int | None
    height: int | None


def _limit_memory(megabytes: int):
    limit = megabytes * 1024 * 1024

    def apply() -> None:  # runs in the child between fork and exec: keep it minimal
        resource.setrlimit(resource.RLIMIT_AS, (limit, limit))

    return apply


def run(args: list[str], *, timeout: float) -> subprocess.CompletedProcess:
    """Run `args` (args[0] is the binary) with the timeout and the memory limit. Returns the
    finished process (exit code 0); raises `FFmpegError` otherwise."""
    if not isinstance(args, list) or not all(isinstance(a, str) for a in args):
        raise TypeError("args must be a list of strings")
    try:
        done = subprocess.run(  # noqa: S603 - fixed binary from settings, list arguments
            args,
            stdin=subprocess.DEVNULL,
            capture_output=True,
            timeout=timeout,
            shell=False,
            check=False,
            preexec_fn=_limit_memory(settings.FFMPEG_MEMORY_MB),  # noqa: PLW1509
        )
    except FileNotFoundError as exc:
        raise FFmpegError("missing", Path(args[0]).name) from exc
    except subprocess.TimeoutExpired as exc:
        raise FFmpegError("timeout", f"{timeout:g} s") from exc
    except OSError as exc:
        raise FFmpegError("failed", type(exc).__name__) from exc
    if done.returncode < 0:
        raise FFmpegError("crash", f"signal {-done.returncode}")
    if done.returncode != 0:
        stderr = done.stderr[-MAX_OUTPUT:].decode("utf-8", "replace").strip()
        raise FFmpegError("failed", stderr.splitlines()[-1] if stderr else "")
    return done


def _number(value) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) and number >= 0 else None


def _rotation(stream: dict) -> int:
    """Display rotation of a video stream (phones store portrait video rotated)."""
    raw = (stream.get("tags") or {}).get("rotate")
    for item in stream.get("side_data_list") or []:
        if isinstance(item, dict) and "rotation" in item:
            raw = item["rotation"]
            break
    try:
        return int(abs(float(raw))) % 360
    except (TypeError, ValueError, OverflowError):
        return 0


def parse_probe(data: bytes) -> Probe:
    """`ffprobe -print_format json -show_format -show_streams` output -> `Probe`.
    Raises FFmpegError("unreadable")."""
    try:
        info = json.loads(data[: MAX_OUTPUT * 16])
        fmt = info["format"]
        streams = info.get("streams") or []
        names = frozenset(str(fmt.get("format_name", "")).split(","))
    except (ValueError, KeyError, TypeError, AttributeError) as exc:
        raise FFmpegError("unreadable") from exc
    video = [
        s
        for s in streams
        if isinstance(s, dict)
        and s.get("codec_type") == "video"
        and not (s.get("disposition") or {}).get("attached_pic")  # cover art in an MP3
    ]
    audio = [s for s in streams if isinstance(s, dict) and s.get("codec_type") == "audio"]
    width = height = None
    if video:
        width, height = _number(video[0].get("width")), _number(video[0].get("height"))
        width, height = (int(width) if width else None), (int(height) if height else None)
        if width and height and _rotation(video[0]) in (90, 270):
            width, height = height, width
    duration = _number(fmt.get("duration"))
    return Probe(names - {""}, duration, bool(video), bool(audio), width, height)


def probe(path: Path) -> Probe:
    """Container, duration, streams and display size of the file at `path`."""
    done = run(
        [
            settings.FFPROBE_PATH,
            "-v",
            "error",
            "-print_format",
            "json",
            "-show_format",
            "-show_streams",
            "--",
            str(path),
        ],  # fmt: skip
        timeout=settings.FFPROBE_TIMEOUT_SECONDS,
    )
    return parse_probe(done.stdout)


def scale_filter() -> str:
    """Scale so the shorter side is at most MAX_EDGE px, keep the aspect, even sizes (H.264).
    Applied after ffmpeg's automatic rotation, so portrait phone videos work too."""
    edge = MAX_EDGE
    return (
        f"scale=w='if(gte(iw,ih),-2,trunc(min(iw,{edge})/2)*2)'"
        f":h='if(gte(iw,ih),trunc(min(ih,{edge})/2)*2,-2)'"
    )


def convert_args(source: Path, target: Path, *, max_seconds: float) -> list[str]:
    return [
        settings.FFMPEG_PATH,
        "-nostdin", "-hide_banner", "-loglevel", "error", "-y",
        "-i", str(source),
        "-map", "0:v:0", "-map", "0:a:0?",
        "-t", f"{max_seconds:g}",
        "-vf", scale_filter(),
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "23", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "128k", "-ac", "2",
        "-threads", str(settings.FFMPEG_THREADS),
        "-movflags", "+faststart",
        "-f", "mp4",
        str(target),
    ]  # fmt: skip


def thumbnail_args(source: Path, target: Path, *, at_seconds: float) -> list[str]:
    return [
        settings.FFMPEG_PATH,
        "-nostdin", "-hide_banner", "-loglevel", "error", "-y",
        "-ss", f"{at_seconds:.3f}",
        "-i", str(source),
        "-frames:v", "1",
        "-q:v", "4",
        "-threads", str(settings.FFMPEG_THREADS),
        "-f", "image2",
        str(target),
    ]  # fmt: skip


def convert_video(source: Path, target: Path, *, max_seconds: float) -> None:
    """Convert to MP4 (H.264 + AAC, at most 720p, fast start)."""
    run(convert_args(source, target, max_seconds=max_seconds),
        timeout=settings.FFMPEG_TIMEOUT_SECONDS)  # fmt: skip


def thumbnail(source: Path, target: Path, *, at_seconds: float) -> None:
    """One JPEG frame at `at_seconds`."""
    run(thumbnail_args(source, target, at_seconds=at_seconds),
        timeout=settings.FFMPEG_TIMEOUT_SECONDS)  # fmt: skip
