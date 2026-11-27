"""ensure-db.sh: repairs only when nothing listens on the Postgres port.

Outside ads-lite.service it restarts that unit; inside it (ENSURE_DB_IN_UNIT=1) it recreates
the compose stack, but never without ARTYSCI_STATE_DIR.
"""

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


def listen_body(port):
    """Shell snippet for a fake that starts a listener living long enough for the re-check."""
    return (
        'python3 -c "import socket,time;'
        f"s=socket.socket();s.bind(('127.0.0.1',{port}));s.listen();time.sleep(5)\" &"
    )


def fake(tmp_path, name, body):
    f = tmp_path / name
    f.write_text(f'#!/usr/bin/env bash\necho "{name} $*" >> {tmp_path}/calls\n{body}\n')
    f.chmod(0o755)
    return str(f)


def run(tmp_path, port, *, compose="true", systemctl="true", in_unit=False, state_dir="/x"):
    env = {
        **os.environ,
        "POSTGRES_PORT": str(port),
        "COMPOSE": fake(tmp_path, "compose", compose),
        "SYSTEMCTL": fake(tmp_path, "systemctl", systemctl),
        "ENSURE_DB_WAIT": "3",
    }
    env.pop("ENSURE_DB_IN_UNIT", None)
    env.pop("ARTYSCI_STATE_DIR", None)
    if in_unit:
        env["ENSURE_DB_IN_UNIT"] = "1"
    if state_dir:
        env["ARTYSCI_STATE_DIR"] = state_dir
    result = subprocess.run(["bash", str(SCRIPT)], env=env, capture_output=True, text=True)
    calls = tmp_path / "calls"
    return result, calls.read_text().splitlines() if calls.exists() else []


def test_reachable_port_does_nothing(tmp_path):
    with socket.socket() as srv:
        srv.bind(("127.0.0.1", 0))
        srv.listen()
        for in_unit in (False, True):
            result, calls = run(tmp_path, srv.getsockname()[1], in_unit=in_unit)
            assert result.returncode == 0
            assert calls == []


def test_outside_unit_restarts_ads_lite_not_compose(tmp_path):
    port = free_port()
    result, calls = run(tmp_path, port, systemctl=listen_body(port))
    assert calls == ["systemctl restart ads-lite.service"]
    assert result.returncode == 0
    assert "reachable again" in result.stderr


def test_outside_unit_fails_loudly_if_restart_does_not_help(tmp_path):
    result, calls = run(tmp_path, free_port())
    assert calls == ["systemctl restart ads-lite.service"]
    assert result.returncode == 1
    assert "FAILED" in result.stderr


def test_outside_unit_failed_restart_is_a_failure(tmp_path):
    result, _ = run(tmp_path, free_port(), systemctl="exit 1")
    assert result.returncode == 1
    assert "FAILED" in result.stderr


def test_in_unit_dead_port_recreates_stack_and_fails_if_still_dead(tmp_path):
    result, calls = run(tmp_path, free_port(), in_unit=True)
    assert calls == ["compose --profile lite down", "compose --profile lite up -d"]
    assert result.returncode == 1
    assert "FAILED" in result.stderr


def test_in_unit_dead_port_recovers_after_recreate(tmp_path):
    port = free_port()
    body = f'if [ "$3" = up ]; then {listen_body(port)} fi'
    result, calls = run(tmp_path, port, compose=body, in_unit=True)
    assert calls == ["compose --profile lite down", "compose --profile lite up -d"]
    assert result.returncode == 0


def test_in_unit_without_state_dir_never_runs_down(tmp_path):
    # #216: without pirx.env compose mounts /postgres, and `down` had already removed the db
    result, calls = run(tmp_path, free_port(), in_unit=True, state_dir=None)
    assert calls == []
    assert result.returncode == 1
    assert "ARTYSCI_STATE_DIR is not set" in result.stderr
