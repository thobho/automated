import logging

from procrastinate.contrib.django import app

from .jobs import QUEUE_DEFAULT, default_retry
from .models import PingRecord

logger = logging.getLogger(__name__)


@app.task(name="core.ping", queue=QUEUE_DEFAULT, retry=default_retry())
def ping(token: str) -> None:
    """Demo job: write one row so tests and smoke checks can see it ran."""
    PingRecord.objects.create(token=token)
    logger.info("ping job ran token=%s", token)


# Scaffold for cron-like jobs (reminders, cleanups): put `@app.periodic(cron="...")` above an
# `@app.task` whose first argument is `timestamp: int`; the worker defers it on schedule.
@app.periodic(cron="30 3 * * *")
@app.task(name="core.cleanup_old_jobs", queue=QUEUE_DEFAULT, queueing_lock="core.cleanup_old_jobs")
async def cleanup_old_jobs(timestamp: int) -> None:
    """Delete succeeded jobs older than a week (failed ones stay for the jobs admin page)."""
    await app.job_manager.delete_old_jobs(nb_hours=7 * 24, include_failed=False)
