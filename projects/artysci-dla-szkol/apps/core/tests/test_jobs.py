"""Acceptance criteria of the job queue, on the in-memory connector (no PostgreSQL needed)."""

import asyncio

import pytest
from procrastinate import RetryStrategy
from procrastinate.contrib.django import app

from apps.core import jobs, tasks
from apps.core.models import PingRecord
from apps.core.testing import in_memory_queue


@pytest.fixture
def queue():
    with in_memory_queue() as connector:
        yield connector


def run_worker():
    """Process everything that is due, then return (no waiting)."""
    asyncio.run(app.run_worker_async(wait=False, install_signal_handlers=False))


def statuses(queue):
    return [job["status"] for job in queue.jobs.values()]


@pytest.mark.django_db(transaction=True)
def test_ping_runs_and_writes_row(queue):
    job_id = jobs.enqueue(tasks.ping, token="hello")
    assert job_id is not None
    run_worker()
    assert PingRecord.objects.filter(token="hello").count() == 1
    assert statuses(queue) == ["succeeded"]


def test_same_idempotency_key_runs_once(queue):
    first = jobs.enqueue(tasks.ping, idempotency_key="k1", token="a")
    second = jobs.enqueue(tasks.ping, idempotency_key="k1", token="a")
    assert first is not None
    assert second is None
    assert len(queue.jobs) == 1


def test_different_keys_both_queue(queue):
    assert jobs.enqueue(tasks.ping, idempotency_key="k1", token="a") is not None
    assert jobs.enqueue(tasks.ping, idempotency_key="k2", token="a") is not None
    assert len(queue.jobs) == 2


def test_job_failing_twice_is_retried_with_backoff_then_succeeds(queue):
    calls = []

    @app.task(
        name="tests.flaky",
        queue=jobs.QUEUE_DEFAULT,
        retry=RetryStrategy(max_attempts=5, exponential_wait=5),
    )
    def flaky():
        calls.append(1)
        if len(calls) < 3:
            raise RuntimeError("boom")

    flaky.defer()
    run_worker()  # attempt 1 fails, retry scheduled in the future
    (job,) = queue.jobs.values()
    assert job["status"] == "todo"
    assert job["attempts"] == 1
    first_wait = job["scheduled_at"]
    assert first_wait is not None

    # Pull the retry forward (the in-memory queue honours scheduled_at) and run again.
    job["scheduled_at"] = None
    run_worker()
    (job,) = queue.jobs.values()
    assert job["attempts"] == 2
    assert job["status"] == "todo"
    assert job["scheduled_at"] > first_wait  # backoff grows

    job["scheduled_at"] = None
    run_worker()
    assert statuses(queue) == ["succeeded"]
    assert len(calls) == 3


def test_default_retry_policy():
    retry = jobs.default_retry()
    assert retry.max_attempts == 5
    assert retry.exponential_wait == 5


def test_queues_cover_all_kinds():
    assert jobs.QUEUES == ["default", "ai", "media", "email"]


def test_periodic_scaffold_registered():
    assert "core.cleanup_old_jobs" in app.tasks
    assert app.periodic_registry.periodic_tasks
