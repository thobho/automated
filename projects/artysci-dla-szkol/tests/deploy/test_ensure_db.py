"""ensure-db.sh: recreates the compose stack only when nothing listens on the Postgres port."""

# ruff: noqa: S603, S607

import os
import socket
import subprocess
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[2] / "deploy/pirx/ensure-db.sh"


def free_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def run(tmp_path, port, compose_body):
    fake = tmp_path / "fakecompose"
    fake.write_text(f'#!/usr/bin/env bash\necho "$*" >> {tmp_path}/calls\n{compose_body}\n')
    fake.chmod(0o755)
    env = {
        **os.environ,
        "POSTGRES_PORT": str(port),
        "COMPOSE": str(fake),
        "ENSURE_DB_WAIT": "3",
    }
    result = subprocess.run(["bash", str(SCRIPT)], env=env, capture_output=True, text=True)
    calls = tmp_path / "calls"
    return result, calls.read_text().splitlines() if calls.exists() else []


def test_reachable_port_does_nothing(tmp_path):
    with socket.socket() as srv:
        srv.bind(("127.0.0.1", 0))
        srv.listen()
        result, calls = run(tmp_path, srv.getsockname()[1], "true")
    assert result.returncode == 0
    assert calls == []


def test_dead_port_recreates_stack_and_fails_if_still_dead(tmp_path):
    result, calls = run(tmp_path, free_port(), "true")
    assert calls == ["--profile lite down", "--profile lite up -d"]
    assert result.returncode == 1
    assert "FAILED" in result.stderr


def test_dead_port_recovers_after_recreate(tmp_path):
    port = free_port()
    # the fake `up -d` starts a listener that lives long enough for the re-check
    body = (
        'if [ "$3" = up ]; then python3 -c "import socket,time;'
        f"s=socket.socket();s.bind(('127.0.0.1',{port}));s.listen();time.sleep(5)\" & fi"
    )
    result, calls = run(tmp_path, port, body)
    assert calls == ["--profile lite down", "--profile lite up -d"]
    assert result.returncode == 0
