"""Storage fixtures: every media test runs against the filesystem backend and, when
S3_ENDPOINT_URL is set (MinIO in CI / Compose full), against S3 as well."""

import os
import uuid

import pytest

from config.settings.storage import build_storages


@pytest.fixture(
    params=[
        "filesystem",
        pytest.param(
            "s3",
            marks=pytest.mark.skipif(
                not os.environ.get("S3_ENDPOINT_URL"), reason="S3_ENDPOINT_URL not set (no MinIO)"
            ),
        ),
    ]
)
def backend(request, settings, tmp_path, monkeypatch):
    """Configure STORAGES for the backend under test; returns its name."""
    name = request.param
    public_base = "http://media.test:8101/"
    if name == "s3":
        run = uuid.uuid4().hex[:10]  # isolate runs sharing one MinIO
        monkeypatch.setenv("S3_PRIVATE_BUCKET", f"test-private-{run}")
        monkeypatch.setenv("S3_PUBLIC_BUCKET", f"test-public-{run}")
        endpoint = os.environ["S3_ENDPOINT_URL"].rstrip("/")
        public_base = f"{endpoint}/test-public-{run}/"
    settings.STORAGE_BACKEND = name
    settings.MEDIA_PUBLIC_BASE_URL = public_base
    settings.MEDIA_PRIVATE_ROOT = tmp_path / "private"
    settings.MEDIA_PUBLIC_ROOT = tmp_path / "public"
    settings.STORAGES = build_storages(
        name,
        public_base_url=public_base,
        private_root=tmp_path / "private",
        public_root=tmp_path / "public",
        signed_url_ttl=settings.MEDIA_SIGNED_URL_TTL,
    )
    if name == "s3":
        from django.core.management import call_command

        call_command("ensure_buckets")
    return name
