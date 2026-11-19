"""ffmpeg/ffprobe wrapper (US-2.3B): argument lists without a shell, timeout, memory limit and
error mapping with a mocked subprocess; real runs on generated samples where ffmpeg exists
(CI installs it; skipped locally without it)."""

import json
import resource
import shutil
import subprocess

import pytest

from apps.core import ffmpeg

HAVE_FFMPEG = bool(shutil.which("ffmpeg") and shutil.which("ffprobe"))
needs_ffmpeg = pytest.mark.skipif(not HAVE_FFMPEG, reason="ffmpeg not installed (runs in CI)")


class FakeRun:
    """Stands in for subprocess.run; records the call, then returns or raises `result`."""

    def __init__(self, result):
        self.result = result
        self.calls = []

    def __call__(self, args, **kwargs):
        self.calls.append((args, kwargs))
        if isinstance(self.result, BaseException):
            raise self.result
        return self.result


def done(returncode=0, stdout=b"", stderr=b""):
    return subprocess.CompletedProcess([], returncode, stdout, stderr)


@pytest.fixture
def fake_run(monkeypatch):
    def install(result):
        fake = FakeRun(result)
        monkeypatch.setattr(ffmpeg.subprocess, "run", fake)
        return fake

    return install


PROBE_JSON = {
    "format": {"format_name": "mov,mp4,m4a,3gp,3g2,mj2", "duration": "12.5"},
    "streams": [
        {"codec_type": "video", "width": 1920, "height": 1080},
        {"codec_type": "audio"},
    ],
}


def test_run_uses_an_argument_list_without_shell_with_timeout_and_memory_limit(
    fake_run, settings, tmp_path
):
    settings.FFMPEG_MEMORY_MB = 256
    fake = fake_run(done())
    ffmpeg.run(["ffmpeg", "-i", str(tmp_path / "a; rm -rf /")], timeout=7)
    ((args, kwargs),) = fake.calls
    assert args == ["ffmpeg", "-i", str(tmp_path / "a; rm -rf /")]
    assert kwargs["shell"] is False and kwargs["timeout"] == 7
    assert kwargs["stdin"] is subprocess.DEVNULL and kwargs["capture_output"] is True
    assert callable(kwargs["preexec_fn"])


def test_memory_limit_sets_rlimit_as(monkeypatch):
    calls = []
    monkeypatch.setattr(ffmpeg.resource, "setrlimit", lambda *a: calls.append(a))
    ffmpeg._limit_memory(100)()
    assert calls == [(resource.RLIMIT_AS, (100 * 1024 * 1024, 100 * 1024 * 1024))]


def test_run_refuses_a_string_command():
    with pytest.raises(TypeError):
        ffmpeg.run("ffmpeg -i x", timeout=1)


@pytest.mark.parametrize(
    "result, code",
    [
        (FileNotFoundError(), "missing"),
        (subprocess.TimeoutExpired(["ffmpeg"], 1), "timeout"),
        (PermissionError(), "failed"),
        (done(returncode=-9), "crash"),
        (done(returncode=1, stderr=b"line one\nInvalid data found\n"), "failed"),
        (done(returncode=1), "failed"),
    ],
)
def test_errors_are_mapped_to_stable_codes(fake_run, result, code):
    fake_run(result)
    with pytest.raises(ffmpeg.FFmpegError) as exc:
        ffmpeg.run(["ffmpeg"], timeout=1)
    assert exc.value.code == code


def test_failed_run_keeps_the_last_stderr_line(fake_run):
    fake_run(done(returncode=1, stderr=b"a\nInvalid data found when processing input\n"))
    with pytest.raises(ffmpeg.FFmpegError) as exc:
        ffmpeg.run(["ffmpeg"], timeout=1)
    assert exc.value.detail == "Invalid data found when processing input"


def test_probe_calls_ffprobe_with_json_output(fake_run, settings, tmp_path):
    settings.FFPROBE_PATH = "/opt/ff/ffprobe"
    settings.FFPROBE_TIMEOUT_SECONDS = 3
    fake = fake_run(done(stdout=json.dumps(PROBE_JSON).encode()))
    result = ffmpeg.probe(tmp_path / "in")
    ((args, kwargs),) = fake.calls
    assert args[0] == "/opt/ff/ffprobe" and args[-2:] == ["--", str(tmp_path / "in")]
    assert "-show_format" in args and "-show_streams" in args and kwargs["timeout"] == 3
    assert result == ffmpeg.Probe(
        frozenset({"mov", "mp4", "m4a", "3gp", "3g2", "mj2"}), 12.5, True, True, 1920, 1080
    )


@pytest.mark.parametrize("data", [b"", b"not json", b"[]", b'{"streams": []}'])
def test_unreadable_probe_output(data):
    with pytest.raises(ffmpeg.FFmpegError) as exc:
        ffmpeg.parse_probe(data)
    assert exc.value.code == "unreadable"


def test_probe_swaps_size_of_a_rotated_phone_video_and_ignores_cover_art():
    rotated = {
        "format": {"format_name": "mov,mp4", "duration": "3"},
        "streams": [
            {
                "codec_type": "video",
                "width": 1920,
                "height": 1080,
                "side_data_list": [{"rotation": -90}],
            }
        ],
    }
    result = ffmpeg.parse_probe(json.dumps(rotated).encode())
    assert (result.width, result.height) == (1080, 1920)
    old_style = {**rotated, "streams": [{"codec_type": "video", "width": 4, "height": 2,
                                         "tags": {"rotate": "270"}}]}  # fmt: skip
    assert ffmpeg.parse_probe(json.dumps(old_style).encode()).width == 2
    mp3 = {
        "format": {"format_name": "mp3", "duration": "nan"},
        "streams": [
            {"codec_type": "audio"},
            {"codec_type": "video", "disposition": {"attached_pic": 1}, "width": 500},
        ],
    }
    result = ffmpeg.parse_probe(json.dumps(mp3).encode())
    assert (result.has_video, result.has_audio, result.duration) == (False, True, None)


def test_convert_and_thumbnail_arguments(settings, tmp_path):
    settings.FFMPEG_PATH = "/opt/ff/ffmpeg"
    settings.FFMPEG_THREADS = 1
    args = ffmpeg.convert_args(tmp_path / "s", tmp_path / "o.mp4", max_seconds=600)
    assert args[0] == "/opt/ff/ffmpeg" and args[-1] == str(tmp_path / "o.mp4")
    for flag, value in [("-c:v", "libx264"), ("-c:a", "aac"), ("-t", "600"), ("-threads", "1"),
                        ("-f", "mp4"), ("-pix_fmt", "yuv420p")]:  # fmt: skip
        assert args[args.index(flag) + 1] == value
    assert "720" in args[args.index("-vf") + 1] and "-nostdin" in args
    thumb = ffmpeg.thumbnail_args(tmp_path / "o.mp4", tmp_path / "t.jpg", at_seconds=1)
    assert thumb[thumb.index("-frames:v") + 1] == "1" and thumb[thumb.index("-ss") + 1] == "1.000"


def test_convert_and_thumbnail_use_the_ffmpeg_timeout(fake_run, settings, tmp_path):
    settings.FFMPEG_TIMEOUT_SECONDS = 42
    fake = fake_run(done())
    ffmpeg.convert_video(tmp_path / "s", tmp_path / "o.mp4", max_seconds=10)
    ffmpeg.thumbnail(tmp_path / "o.mp4", tmp_path / "t.jpg", at_seconds=0.5)
    assert [kwargs["timeout"] for _args, kwargs in fake.calls] == [42, 42]


def test_tiny_time_limit_on_a_real_process_is_a_timeout(settings):
    # A real child process (the Python interpreter itself) killed by the wall-clock limit.
    import sys

    with pytest.raises(ffmpeg.FFmpegError) as exc:
        ffmpeg.run([sys.executable, "-c", "import time; time.sleep(5)"], timeout=0.2)
    assert exc.value.code == "timeout"


def test_missing_binary_is_reported(settings):
    with pytest.raises(ffmpeg.FFmpegError) as exc:
        ffmpeg.run(["/nonexistent/ffmpeg-binary"], timeout=1)
    assert exc.value.code == "missing"


# --- real ffmpeg on generated samples (CI) ---------------------------------------------------


def make_sample(path, *, seconds=2, size="1280x720", audio_only=False):
    """A short synthetic sample made by ffmpeg itself (test pattern and a sine tone)."""
    tone = ["-f", "lavfi", "-i", f"sine=frequency=440:duration={seconds}"]
    if audio_only:
        args = ["ffmpeg", "-nostdin", "-loglevel", "error", "-y", *tone, str(path)]
    else:
        pattern = ["-f", "lavfi", "-i", f"testsrc=duration={seconds}:size={size}:rate=10"]
        codecs = ["-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest"]
        args = ["ffmpeg", "-nostdin", "-loglevel", "error", "-y", *pattern, *tone, *codecs,
                str(path)]  # fmt: skip
    subprocess.run(args, check=True, timeout=60)  # noqa: S603
    return path


@needs_ffmpeg
def test_real_probe_convert_and_thumbnail(tmp_path):
    source = make_sample(tmp_path / "in.mp4", size="1920x1080")
    probe = ffmpeg.probe(source)
    assert "mp4" in probe.format_names and probe.has_video and probe.has_audio
    assert (probe.width, probe.height) == (1920, 1080) and 1.5 < probe.duration < 2.5
    ffmpeg.convert_video(source, tmp_path / "out.mp4", max_seconds=600)
    out = ffmpeg.probe(tmp_path / "out.mp4")
    assert (out.width, out.height) == (1280, 720) and out.has_audio
    ffmpeg.thumbnail(tmp_path / "out.mp4", tmp_path / "t.jpg", at_seconds=1)
    assert (tmp_path / "t.jpg").read_bytes()[:3] == b"\xff\xd8\xff"


@needs_ffmpeg
def test_real_portrait_video_keeps_its_aspect(tmp_path):
    source = make_sample(tmp_path / "in.mp4", seconds=1, size="1080x1920")
    ffmpeg.convert_video(source, tmp_path / "out.mp4", max_seconds=600)
    out = ffmpeg.probe(tmp_path / "out.mp4")
    assert (out.width, out.height) == (720, 1280)


@needs_ffmpeg
def test_real_probe_of_text_is_unreadable(tmp_path):
    path = tmp_path / "fake.mp4"
    path.write_text("to nie jest film\n" * 50)
    with pytest.raises(ffmpeg.FFmpegError) as exc:
        ffmpeg.probe(path)
    assert exc.value.code in ("failed", "unreadable")


@needs_ffmpeg
def test_real_ffmpeg_with_a_tiny_time_limit_is_a_timeout(tmp_path, settings):
    source = make_sample(tmp_path / "in.mp4", seconds=5, size="1920x1080")
    settings.FFMPEG_TIMEOUT_SECONDS = 0.01
    with pytest.raises(ffmpeg.FFmpegError) as exc:
        ffmpeg.convert_video(source, tmp_path / "out.mp4", max_seconds=600)
    assert exc.value.code == "timeout"
