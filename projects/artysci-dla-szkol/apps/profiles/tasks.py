"""Background jobs of the profile generator (US-2.5A, US-2.6). Arguments are ids and keys only."""

from procrastinate.contrib.django import app

from apps.core.jobs import QUEUE_AI

from . import generation, sections


@app.task(name="profiles.generate_profile", queue=QUEUE_AI)
def generate_profile(generation_id: int) -> None:
    """Never retried: every failure ends as a readable status on the generation, and the artist
    can request a new run."""
    generation.run_generation(generation_id)


@app.task(name="profiles.regenerate_section", queue=QUEUE_AI)
def regenerate_section(generation_id: int, section: str) -> None:
    """One section of the page; never retried, like `generate_profile`."""
    sections.run_section(generation_id, section)
