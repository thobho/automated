"""Media jobs of artist materials (US-2.3A/B). Arguments are ids and storage keys only."""

from procrastinate.contrib.django import app

from apps.core.jobs import QUEUE_DEFAULT, QUEUE_MEDIA, default_retry

from . import materials, recordings, resumable, website_import

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


@app.task(name="artists.process_media", queue=QUEUE_MEDIA)
def process_media(material_id: int) -> None:
    """ffprobe, and for a video the MP4 conversion and thumbnail (US-2.3B). Never fails: a
    timeout or crash ends as a rejected material with a readable message."""
    recordings.process_media(material_id)


@app.periodic(cron="17 * * * *")
@app.task(
    name="artists.cleanup_upload_sessions",
    queue=QUEUE_DEFAULT,
    queueing_lock="artists.cleanup_upload_sessions",
)
def cleanup_upload_sessions(timestamp: int) -> None:
    """Hourly: delete expired resumable-upload sessions and their temporary data."""
    resumable.cleanup_expired()


@app.task(name="artists.run_website_import", queue=QUEUE_MEDIA)
def run_website_import(import_id: int) -> None:
    """Import from the artist's website (US-2.2). Never retried: every failure ends as a
    readable status on the import, and the artist can start a new one."""
    website_import.run_import(import_id)
