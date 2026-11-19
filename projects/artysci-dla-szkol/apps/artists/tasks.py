"""Media jobs of artist materials (US-2.3A). Arguments are ids and storage keys only."""

from procrastinate.contrib.django import app

from apps.core.jobs import QUEUE_MEDIA, default_retry

from . import materials

# A scanner error retries 3 more times (after 5, 10, 20 s); then the job fails and the file
# stays "oczekuje na skan" (never counted). The jobs admin lists the failed job.
SCAN_RETRY = default_retry(max_attempts=3, base_wait=5)


@app.task(name="artists.scan_material", queue=QUEUE_MEDIA, retry=SCAN_RETRY)
def scan_material(material_id: int) -> None:
    materials.scan_material(material_id)


@app.task(name="artists.scan_poster", queue=QUEUE_MEDIA, retry=SCAN_RETRY)
def scan_poster(offer_id: int, key: str) -> None:
    materials.scan_poster(offer_id, key)


@app.task(name="artists.extract_pdf_text", queue=QUEUE_MEDIA)
def extract_pdf_text(material_id: int) -> None:
    """Never fails for a bad PDF: encrypted and broken files end as a text status."""
    materials.extract_pdf_text(material_id)
