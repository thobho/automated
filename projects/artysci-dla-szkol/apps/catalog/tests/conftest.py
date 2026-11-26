"""Catalog tests that publish through the real code defer jobs: keep them in memory."""

import pytest

from apps.accounts.tests.conftest import queue  # noqa: F401  (fixture)


@pytest.fixture(autouse=True)
def _jobs_in_memory(queue):  # noqa: F811 - uses the imported fixture
    return queue
