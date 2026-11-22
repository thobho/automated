"""Background job of the profile generator (US-2.5A). Arguments are ids only."""

from procrastinate.contrib.django import app

from apps.core.jobs import QUEUE_AI

from . import generation


@app.task(name="profiles.generate_profile", queue=QUEUE_AI)
def generate_profile(generation_id: int) -> None:
    """Never retried: every failure ends as a readable status on the generation, and the artist
    can request a new run."""
    generation.run_generation(generation_id)
