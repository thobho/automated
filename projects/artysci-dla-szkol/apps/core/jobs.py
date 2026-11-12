"""Job queue helpers: queue names, retry policy, idempotent deferral.

Tasks live in `tasks.py` modules (Procrastinate autodiscovers them). Deferring goes through
`enqueue()` so every caller gets the same idempotency behaviour.
"""

from procrastinate import RetryStrategy
from procrastinate.exceptions import AlreadyEnqueued

# One queue per kind of work; the worker listens to all of them.
QUEUE_DEFAULT = "default"
QUEUE_AI = "ai"
QUEUE_MEDIA = "media"
QUEUE_EMAIL = "email"
QUEUES = [QUEUE_DEFAULT, QUEUE_AI, QUEUE_MEDIA, QUEUE_EMAIL]


def default_retry(max_attempts: int = 5, base_wait: int = 5) -> RetryStrategy:
    """Retry with exponential backoff: waits base_wait * 2 ** attempts seconds (5, 10, 20, ...)."""
    return RetryStrategy(max_attempts=max_attempts, exponential_wait=base_wait)


def enqueue(task, *, idempotency_key: str | None = None, **kwargs) -> int | None:
    """Defer `task` with kwargs. Returns the job id, or None if the key is already queued.

    The key maps to Procrastinate's `queueing_lock`: while a job with that key is waiting
    (status `todo`), deferring it again is a no-op. Once it started, the key is free again, so
    tasks must still be safe to run twice.
    """
    configured = task.configure(queueing_lock=idempotency_key) if idempotency_key else task
    try:
        return configured.defer(**kwargs)
    except AlreadyEnqueued:
        return None
