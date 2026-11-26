"""The preview link cleanup is a daily cron job (US-3.7). Own module: the conftest's in-memory
queue switches the periodic registry off, so it is not used here."""

import pytest


@pytest.fixture
def _jobs_in_memory():  # overrides the autouse fixture of conftest.py for this module
    return None


def test_purge_job_is_scheduled_daily():
    from procrastinate.contrib.django import app

    crons = {t.task.name: t.cron for t in app.periodic_registry.periodic_tasks.values()}
    assert crons["profiles.purge_preview_links"] == "41 4 * * *"
