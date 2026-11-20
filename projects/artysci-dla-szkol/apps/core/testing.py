"""Helpers for tests that run jobs without PostgreSQL (SQLite fallback of the test settings)."""

from contextlib import contextmanager

from procrastinate.contrib.django import app, procrastinate_app
from procrastinate.periodic import PeriodicRegistry
from procrastinate.testing import InMemoryConnector


@contextmanager
def in_memory_queue():
    """Keep deferred jobs in memory for the duration of the block; yields the connector.

    The periodic (cron) tasks are switched off inside the block: otherwise a test worker started
    within a few minutes after a cron slot (e.g. `accounts.purge_expired` at 04:15) also defers
    and runs that job, and job counts in the tests depend on the time of day.
    """
    connector = InMemoryConnector()
    real_app = procrastinate_app.current_app  # `app` is a read-only proxy to it
    registry, real_app.periodic_registry = real_app.periodic_registry, PeriodicRegistry()
    try:
        with app.replace_connector(connector):
            yield connector
    finally:
        real_app.periodic_registry = registry
