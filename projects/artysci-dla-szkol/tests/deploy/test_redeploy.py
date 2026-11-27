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
  deploy-pirx)
    [ -e "$STATE/fail-deploy" ] && exit 1
    git checkout -q main && git merge -q --ff-only origin/main ;;
  smoke-pirx) [ -e "$STATE/fail-smoke" ] && exit 1 ;;
  rollback-pirx)
    [ -e "$STATE/fail-rollback" ] && exit 1
    git checkout -q --detach "${2#ROLLBACK_REF=}" ;;
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

    def run(self, ensure_db="true"):
        env = {
            **os.environ,
            "STATE": str(self.state),
            "ARTYSCI_STATE_DIR": str(self.state),
            "MAKE": str(self.fake),
            "ENSURE_DB": ensure_db,
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


def test_unfixable_database_is_logged_but_does_not_block_deploy(env):
    assert env.run(ensure_db="false").returncode == 0  # the green smoke test proves the db
    assert "DB DOWN" in env.log
    assert env.deployed is not None


def test_ensure_db_runs_every_tick_and_down_db_fails_the_run(env, tmp_path):
    env.run()
    counter = tmp_path / "ensure.calls"
    ensure = tmp_path / "ensure"
    ensure.write_text(f"#!/usr/bin/env bash\necho x >> {counter}\nexit 1\n")
    ensure.chmod(0o755)
    for _ in range(2):  # nothing to deploy: ensure-db still runs, the unit shows as failed
        assert env.run(ensure_db=str(ensure)).returncode == 1
    assert len(counter.read_text().splitlines()) == 2
    assert env.log.count("DB DOWN") == 2


def test_children_do_not_inherit_the_lock_fd(env, tmp_path):
    # #216: aardvark-dns started inside a deploy kept fd 9, so every later run skipped
    probe = tmp_path / "probe"
    probe.write_text(f"#!/usr/bin/env bash\n[ -e /dev/fd/9 ] && echo LEAK >> {tmp_path}/leak\nexit 0\n")
    probe.chmod(0o755)
    fake = env.fake.read_text().replace('echo "$*"', f'"{probe}"; echo "$*"', 1)
    env.fake.write_text(fake)
    assert env.run(ensure_db=str(probe)).returncode == 0
    assert env.calls  # the probe ran inside make too
    assert not (tmp_path / "leak").exists()


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
    assert "redeploy.lock is held" in env.log


def test_records_checked_out_head_not_fetched_target(env):
    env.run()
    new = env.commit("two")
    env.run()
    assert env.deployed == git(env.checkout, "rev-parse", "HEAD") == new


def test_fetch_failure_is_one_clear_line_and_no_deploy(env):
    env.run()
    env.commit("two")
    git(env.checkout, "remote", "set-url", "origin", str(env.checkout.parent / "nowhere"))
    before = len(env.calls)
    assert env.run().returncode == 1
    assert len(env.calls) == before
    assert env.log.count("git fetch failed") == 1


def test_dirty_checkout_is_logged_and_not_deployed(env):
    env.run()
    env.commit("two")
    (env.checkout / "one").write_text("local edit")
    before = len(env.calls)
    assert env.run().returncode == 1
    assert len(env.calls) == before
    assert env.log.count("local changes, not deploying") == 1
    assert env.deployed != git(env.origin, "rev-parse", "HEAD")


REFRESH = Path(__file__).resolve().parents[2] / "deploy/pirx/refresh-units.sh"


class Units:
    def __init__(self, tmp_path):
        self.project = tmp_path / "proj"
        (self.project / "deploy/pirx").mkdir(parents=True)
        self.unit_dir = tmp_path / "units"
        self.calls = tmp_path / "systemctl.calls"
        fake = tmp_path / "fakectl"
        fake.write_text(f'#!/usr/bin/env bash\necho "$*" >> {self.calls}\n')
        fake.chmod(0o755)
        self.fake = fake

    def write(self, name, body):
        (self.project / "deploy/pirx" / name).write_text(body)

    def run(self):
        env = {
            **os.environ,
            "PROJECT": str(self.project),
            "UV_BIN": "/bin/uv",
            "PIRX_UNIT_DIR": str(self.unit_dir),
            "SYSTEMCTL": str(self.fake),
        }
        return subprocess.run(["bash", str(REFRESH)], env=env, capture_output=True, text=True)

    @property
    def ctl(self):
        return self.calls.read_text().splitlines() if self.calls.exists() else []


def test_refresh_installs_new_timer_and_enables_it(tmp_path):
    u = Units(tmp_path)
    u.write("ads-redeploy.timer", "[Timer]\nOnCalendar=*:0/10\n")
    u.write("ads-web.service", "[Service]\nExecStart=@UV@ run @PROJECT@/x\n")
    assert u.run().returncode == 0
    assert (u.unit_dir / "ads-web.service").read_text().strip() == (
        f"[Service]\nExecStart=/bin/uv run {u.project}/x"
    )
    assert u.ctl[0] == "daemon-reload"
    assert "enable ads-redeploy.timer" in u.ctl
    assert "restart ads-redeploy.timer" in u.ctl
    assert not any("ads-web" in c for c in u.ctl)  # restarted by deploy-pirx, not here


def test_refresh_unchanged_does_nothing(tmp_path):
    u = Units(tmp_path)
    u.write("ads-redeploy.timer", "[Timer]\nOnCalendar=*:0/10\n")
    u.run()
    u.calls.unlink()
    r = u.run()
    assert r.returncode == 0
    assert "unchanged" in r.stdout
    assert u.ctl == []


def test_refresh_only_touches_changed_units(tmp_path):
    u = Units(tmp_path)
    u.write("ads-redeploy.timer", "[Timer]\nA=1\n")
    u.write("ads-lite.service", "[Service]\nA=1\n")
    u.run()
    u.calls.unlink()
    u.write("ads-lite.service", "[Service]\nA=2\n")
    assert u.run().returncode == 0
    assert u.ctl == ["daemon-reload", "restart ads-lite.service"]
