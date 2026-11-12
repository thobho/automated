"""Helpers for tests that run jobs without PostgreSQL (SQLite fallback of the test settings)."""

from contextlib import contextmanager

from procrastinate.contrib.django import app
from procrastinate.testing import InMemoryConnector


@contextmanager
def in_memory_queue():
    """Keep deferred jobs in memory for the duration of the block; yields the connector."""
    connector = InMemoryConnector()
    with app.replace_connector(connector):
        yield connector
