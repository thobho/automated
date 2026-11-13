"""Playwright smoke tests run against a live server (CI e2e job). The normal `pytest` run skips
this folder; run: `uv run --group e2e pytest tests/e2e --base-url http://127.0.0.1:8000`."""

import os
from pathlib import Path

import pytest

SCREENSHOT_DIR = Path(os.environ.get("E2E_SCREENSHOT_DIR", "e2e-screenshots"))


@pytest.fixture(scope="session")
def shot_dir() -> Path:
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    return SCREENSHOT_DIR


@pytest.fixture
def shot(page, shot_dir):
    def take(name: str) -> None:
        page.screenshot(path=str(shot_dir / f"{name}.png"), full_page=True)

    return take
