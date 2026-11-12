from unittest import mock

import pytest
from django.core.management import CommandError, call_command


def test_worker_runs_procrastinate_on_all_queues(capsys):
    with mock.patch("apps.core.management.commands.worker.call_command") as run:
        call_command("worker", "--once", "--concurrency", "3")
    run.assert_called_once_with(
        "procrastinate",
        "worker",
        "--queues",
        "default,ai,media,email",
        "--concurrency",
        "3",
        "--one-shot",
    )
    assert "queues=default,ai,media,email" in capsys.readouterr().out


def test_worker_waits_by_default():
    with mock.patch("apps.core.management.commands.worker.call_command") as run:
        call_command("worker")
    assert "--one-shot" not in run.call_args.args


def test_worker_rejects_zero_concurrency():
    with (
        mock.patch("apps.core.management.commands.worker.call_command") as run,
        pytest.raises(CommandError),
    ):
        call_command("worker", "--concurrency", "0")
    run.assert_not_called()
