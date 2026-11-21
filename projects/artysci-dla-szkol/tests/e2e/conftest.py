"""Playwright smoke tests run against a live server (CI e2e job). The normal `pytest` run skips
this folder (addopts ignores tests/e2e); run: `uv run --group e2e pytest tests/e2e --base-url http://127.0.0.1:8000`."""

import os
from pathlib import Path

import pytest

# Playwright's sync API keeps an event loop running in the test thread; tests that prepare data
# through the Django ORM (the live DB the server uses) would otherwise be refused by Django.
os.environ.setdefault("DJANGO_ALLOW_ASYNC_UNSAFE", "true")

SCREENSHOT_DIR = Path(os.environ.get("E2E_SCREENSHOT_DIR", "e2e-screenshots"))


def pytest_addoption(parser):
    parser.addoption(
        "--artist-session",
        default=os.environ.get("E2E_ARTIST_SESSION", ""),
        help="Session key (cookie `sessionid`) of a signed-in artist with ready materials.",
    )


@pytest.fixture
def artist_session(request) -> str:
    session = request.config.getoption("--artist-session")
    if not session:
        pytest.skip("no --artist-session (or E2E_ARTIST_SESSION) given")
    return session


@pytest.fixture(scope="session")
def shot_dir() -> Path:
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    return SCREENSHOT_DIR


@pytest.fixture
def shot(page, shot_dir):
    def take(name: str) -> None:
        page.screenshot(path=str(shot_dir / f"{name}.png"), full_page=True)

    return take
