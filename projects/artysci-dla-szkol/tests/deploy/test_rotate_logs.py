import importlib.util
from pathlib import Path

_SPEC = importlib.util.spec_from_file_location(
    "rotate_logs", Path(__file__).resolve().parents[2] / "deploy/pirx/rotate_logs.py"
)
rotate_logs = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(rotate_logs)


def test_small_files_are_left_alone(tmp_path):
    (tmp_path / "web.log").write_text("x" * 10)
    assert rotate_logs.rotate_dir(tmp_path, max_bytes=100, keep=3) == []
    assert not (tmp_path / "web.log.1").exists()


def test_big_file_is_copied_and_truncated(tmp_path):
    log = tmp_path / "web.log"
    log.write_text("x" * 200)
    assert rotate_logs.rotate_dir(tmp_path, max_bytes=100, keep=3) == [log]
    assert log.read_text() == ""
    assert (tmp_path / "web.log.1").read_text() == "x" * 200


def test_keeps_only_n_generations(tmp_path):
    log = tmp_path / "w.log"
    for gen in "abcde":
        log.write_text(gen * 200)
        rotate_logs.rotate_dir(tmp_path, max_bytes=100, keep=3)
    assert (tmp_path / "w.log.1").read_text()[0] == "e"
    assert (tmp_path / "w.log.3").read_text()[0] == "c"
    assert not (tmp_path / "w.log.4").exists()


def test_main_needs_a_directory(capsys):
    assert rotate_logs.main([]) == 2
