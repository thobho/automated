"""redeploy.sh logic against a temporary git repo and a fake `make` (no real deploy)."""

# ruff: noqa: S603, S607

import fcntl
import os
import shutil
import subprocess
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[2] / "deploy/pirx/redeploy.sh"

FAKE_MAKE = """#!/usr/bin/env bash
echo "$*" >> "$STATE/make.calls"
case "$1" in
  deploy-pirx) [ -e "$STATE/fail-deploy" ] && exit 1 ;;
  smoke-pirx) [ -e "$STATE/fail-smoke" ] && exit 1 ;;
  rollback-pirx) [ -e "$STATE/fail-rollback" ] && exit 1 ;;
esac
exit 0
"""


def git(cwd, *args):
    return subprocess.run(
        ["git", *args], cwd=cwd, check=True, capture_output=True, text=True
    ).stdout.strip()


class Env:
    def __init__(self, tmp_path):
        self.origin = tmp_path / "origin"
        self.origin.mkdir()
        git(self.origin, "init", "-q", "-b", "main")
        for k, v in (("user.name", "t"), ("user.email", "t@example.invalid")):
            git(self.origin, "config", k, v)
        self.commit("one")
        self.checkout = tmp_path / "app"
        git(tmp_path, "clone", "-q", str(self.origin), str(self.checkout))
        (self.checkout / "deploy/pirx").mkdir(parents=True)
        shutil.copy(SCRIPT, self.checkout / "deploy/pirx/redeploy.sh")
        self.state = tmp_path / "state"
        self.state.mkdir()
        fake = tmp_path / "fakemake"
        fake.write_text(FAKE_MAKE)
        fake.chmod(0o755)
        self.fake = fake

    def commit(self, name):
        (self.origin / name).write_text(name)
        git(self.origin, "add", name)
        git(self.origin, "commit", "-q", "-m", name)
        return git(self.origin, "rev-parse", "HEAD")

    def run(self):
        env = {
            **os.environ,
            "STATE": str(self.state),
            "ARTYSCI_STATE_DIR": str(self.state),
            "MAKE": str(self.fake),
        }
        return subprocess.run(
            ["bash", str(self.checkout / "deploy/pirx/redeploy.sh")],
            env=env,
            capture_output=True,
            text=True,
        )

    @property
    def calls(self):
        f = self.state / "make.calls"
        return f.read_text().splitlines() if f.exists() else []

    @property
    def log(self):
        f = self.state / "logs/redeploy.log"
        return f.read_text() if f.exists() else ""

    @property
    def deployed(self):
        f = self.state / "deployed.commit"
        return f.read_text().strip() if f.exists() else None


@pytest.fixture
def env(tmp_path):
    return Env(tmp_path)


def test_first_run_deploys_and_records(env):
    head = git(env.origin, "rev-parse", "HEAD")
    assert env.run().returncode == 0
    assert env.deployed == head
    assert env.calls == ["deploy-pirx DEPLOY_REF=main", "smoke-pirx"]
    assert "smoke test green" in env.log


def test_equal_commit_does_nothing(env):
    env.run()
    before = env.log
    env.state.joinpath("make.calls").unlink()
    assert env.run().returncode == 0
    assert env.calls == []
    assert env.log == before


def test_new_commit_redeploys(env):
    env.run()
    new = env.commit("two")
    assert env.run().returncode == 0
    assert env.deployed == new


def test_failed_smoke_rolls_back_and_keeps_state(env):
    good = git(env.origin, "rev-parse", "HEAD")
    env.run()
    env.commit("two")
    (env.state / "fail-smoke").touch()
    assert env.run().returncode == 1
    assert env.deployed == good
    assert f"rollback-pirx ROLLBACK_REF={good}" in env.calls
    assert "FAILED deploy" in env.log
    assert "ROLLBACK to" in env.log  # the fake smoke fails for the rollback too


def test_failed_deploy_rollback_with_green_smoke(env):
    good = git(env.origin, "rev-parse", "HEAD")
    env.run()
    env.commit("two")
    (env.state / "fail-deploy").touch()
    env.run()
    assert env.deployed == good
    assert f"rolled back to {good[:12]}" in env.log


def test_failed_rollback_is_logged(env):
    env.run()
    env.commit("two")
    (env.state / "fail-deploy").touch()
    (env.state / "fail-rollback").touch()
    env.run()
    assert "ROLLBACK to" in env.log


def test_first_deploy_failing_has_nothing_to_roll_back(env):
    (env.state / "fail-deploy").touch()
    env.run()
    assert env.deployed is None
    assert not any(c.startswith("rollback") for c in env.calls)
    assert "nothing to roll back" in env.log


def test_retry_cap_of_three(env):
    env.run()
    env.commit("two")
    (env.state / "fail-deploy").touch()
    for _ in range(3):
        env.run()
    assert "GIVING UP" in env.log
    n = sum(c.startswith("deploy-pirx") for c in env.calls)
    assert env.run().returncode == 0
    assert sum(c.startswith("deploy-pirx") for c in env.calls) == n


def test_newer_commit_resets_retry_cap(env):
    env.run()
    env.commit("two")
    (env.state / "fail-deploy").touch()
    for _ in range(3):
        env.run()
    (env.state / "fail-deploy").unlink()
    newer = env.commit("three")
    assert env.run().returncode == 0
    assert env.deployed == newer
    assert not (env.state / "failed.commit").exists()


def test_lock_held_means_no_deploy(env):
    with open(env.state / "redeploy.lock", "w") as fh:
        fcntl.flock(fh, fcntl.LOCK_EX)
        assert env.run().returncode == 0
    assert env.calls == []
    assert env.deployed is None
